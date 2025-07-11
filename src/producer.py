"""
Checks Postgres for due jobs, publishes ScheduleDue events to RabbitMQ,
and reschedules or completes the job row.

Environment variables:
    LOCK_BATCH      (optional)  max rows per SELECT ... SKIP LOCKED   [default 500]
    TICK_MS         (optional)  sleep time when no work (milliseconds) [default 500]
"""
from __future__ import annotations

import asyncio
import logging
import os
import signal
from datetime import timedelta

# from prometheus_client import Counter, start_http_server

from amqp import (
    AMQPConfig,
    open_connection,
    declare_topology,
    JSONPublisher,
)
from repo import JobRepo
from models import Job
from clock import now
from config import settings

LOG = logging.getLogger("scheduler.producer")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


# Metrics ✨ -------------------------------------------------
# JOBS_QUEUED     = Counter("jobs_queued_total",     "ScheduleRequest events inserted")
# JOBS_CANCELLED  = Counter("jobs_cancelled_total",  "ScheduleCancel handled")
# JOBS_DUE        = Counter("jobs_due_total",        "ScheduleDue emitted")

# start_http_server(int(os.getenv("METRICS_PORT", 8000)))

# ────────────────────────────────────────────────────────────────────────────────
class ProducerService:
    def __init__(
        self,
        repo: JobRepo,
        publisher: JSONPublisher,
        *,
        lock_batch: int = 500,
        tick_ms: int = 500,
    ):
        self.repo = repo
        self.pub = publisher
        self.lock_batch = lock_batch
        self.tick_ms = tick_ms
        self._stop_event = asyncio.Event()

    # -------------------------------------------------------------------------
    async def _process_batch(self):
        """Grab due rows, emit events, and reschedule / mark done."""
        due_jobs = await self.repo.lock_due_jobs(limit=self.lock_batch)
        if not due_jobs:
            return False   # nothing processed

        for job in due_jobs:
            await self._fire_job(job)

        return True        # processed at least one job

    async def _fire_job(self, job: Job):
        """Publish ScheduleDue and update DB row accordingly."""
        fired_at = now()
        event = {
            "id": str(job.id),
            "job_type": job.job_type,
            "payload": job.payload,
            "fired_at": fired_at.isoformat(),
            "attempt": job.retries + 1,
        }

        await self.pub.publish("due", event)

        # ── Reschedule or finish ────────────────────────────────────────────
        if job.is_recurring:
            nxt = job.spec.next_after(job.next_run_at + timedelta(microseconds=1))
            if nxt:
                job.retries += 1
                await self.repo.reschedule(job, nxt)
                LOG.info("Rescheduled %s → next %s", job.id, nxt.isoformat())
            else:
                await self.repo.mark_done(job.id)
                LOG.info("Series finished %s", job.id)
        else:
            await self.repo.mark_done(job.id)
            LOG.info("Done one-shot %s", job.id)

    # -------------------------------------------------------------------------
    async def run(self):
        """Main loop until stop requested."""
        LOG.info("Producer started (batch=%d, tick=%d ms)", self.lock_batch, self.tick_ms)

        while not self._stop_event.is_set():
            worked = await self._process_batch()
            if not worked:
                await asyncio.sleep(self.tick_ms / 1000)

        LOG.info("Producer stopping…")

    def stop(self):
        self._stop_event.set()


# ────────────────────────────────────────────────────────────────────────────────
async def main():
    # 1) Config ----------------------------------------------------------------
    pg_dsn     = settings.PG_DSN
    rabbit_url = settings.RABBIT_URL
    lock_batch = settings.LOCK_BATCH
    tick_ms    = settings.TICK_MS

    cfg = AMQPConfig(rabbit_url)

    # 2) Postgres --------------------------------------------------------------
    repo = await JobRepo.create(pg_dsn, min_size=2, max_size=10)

    # 3) RabbitMQ publisher ----------------------------------------------------
    async with open_connection(cfg) as conn:
        await declare_topology(conn, cfg)

        pub_ch = await conn.channel(publisher_confirms=True)
        publisher = JSONPublisher(pub_ch, cfg.evt_ex)
        await publisher.init()

        # 4) Service -----------------------------------------------------------
        svc = ProducerService(
            repo,
            publisher,
            lock_batch=lock_batch,
            tick_ms=tick_ms,
        )

        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, svc.stop)

        try:
            await svc.run()
        finally:
            await pub_ch.close()

if __name__ == "__main__":
    asyncio.run(main())
