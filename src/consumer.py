"""
Consumes ScheduleRequest / ScheduleCancel commands from RabbitMQ
and persists them into Postgres (or marks them cancelled).

Run with:
    python -m scheduler.cmd.consumer
Environment:
    PG_DSN       postgres://postgres:example@postgres:5432/postgres
    RABBIT_URL   amqp://guest:guest@rabbitmq:5672/
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import signal
import uuid
from typing import Any, Dict

from aio_pika import IncomingMessage
# from prometheus_client import Counter, start_http_server

from amqp import (
    AMQPConfig,
    open_connection,
    declare_topology,
    start_consumer,
)
from repo import JobRepo
from models import Job
from config import settings

LOG = logging.getLogger("scheduler.consumer")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


# Metrics -------------------------------------------------
# JOBS_QUEUED     = Counter("jobs_queued_total",     "ScheduleRequest events inserted")
# JOBS_CANCELLED  = Counter("jobs_cancelled_total",  "ScheduleCancel handled")
# JOBS_DUE        = Counter("jobs_due_total",        "ScheduleDue emitted")

# start_http_server(int(os.getenv("METRICS_PORT", 8000)))
# ---------------------------------------------------------------------------

class ConsumerService:
    def __init__(self, repo: JobRepo, cfg: AMQPConfig):
        self.repo = repo
        self.cfg  = cfg
        self._stopping = asyncio.Event()

    # ---------- Rabbit handler ---------------------------------------------
    async def handle_command(self, message: IncomingMessage, payload: Dict[str, Any]):
        """
        Determine whether the message is a request or cancel based on its
        routing-key.  Assumes we bound the queue with keys 'request' + 'cancel'.
        """
        rk = message.routing_key
        try:
            if rk == "request":
                await self._handle_request(payload)
            elif rk == "cancel":
                await self._handle_cancel(payload)
            else:
                LOG.warning("Unknown routing-key %s -> drop", rk)
        except ValueError as exc:
            LOG.exception("Rejecting bad message: %s"% exc)
            await message.reject(requeue=False)
        except Exception as exc:
            LOG.exception("Error handling %s: %s", rk, exc)
            # Let start_consumer() nack & requeue
            raise

    async def _handle_request(self, payload: Dict[str, Any]):
        job = Job.from_request_event(payload)
        inserted = await self.repo.insert_job(job)
        if inserted:
            LOG.info("Queued new job %s due %s", job.id, job.next_run_at.isoformat())
        else:
            LOG.info("Duplicate request %s ignored", job.id)

    async def _handle_cancel(self, payload: Dict[str, Any]):
        try:
            jid = uuid.UUID(payload["id"])
        except (KeyError, ValueError):
            raise ValueError("ScheduleCancel payload must contain valid 'id'")
        rows = await self.repo.cancel_job(jid)
        LOG.info("Cancelled job %s (rows=%d)", jid, rows)

    # ---------- Bootstrap / main loop --------------------------------------
    async def run(self):
        async with open_connection(self.cfg) as conn:
            await declare_topology(conn, self.cfg)

            channel = await conn.channel()
            # Commands are incoming only → set smallish prefetch for fairness
            await start_consumer(
                channel,
                queue_name=self.cfg.cmd_q,
                handler=self.handle_command,
                prefetch=256,
            )
            # The iterator inside start_consumer() blocks; we park here
            await self._stopping.wait()

    def stop(self):
        self._stopping.set()


# ---------------------------------------------------------------------------

async def main():
    # 1) Config -----------------------------------------------------------------
    pg_dsn     = settings.PG_DSN
    rabbit_url = settings.RABBIT_URL
    cfg        = AMQPConfig(rabbit_url)

    # 2) DB pool -----------------------------------------------------------------
    repo = await JobRepo.create(pg_dsn, min_size=2, max_size=10)

    # 3) Service -----------------------------------------------------------------
    svc = ConsumerService(repo, cfg)

    # 4) Graceful-shutdown plumbing ---------------------------------------------
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, svc.stop)

    LOG.info("Consumer starting…")
    await svc.run()
    LOG.info("Consumer shut down.")


if __name__ == "__main__":
    asyncio.run(main())
