"""
Emit one-off **ScheduleDue** events to RabbitMQ – handy for smoke-testing the
consumer stack without having to insert rows in Postgres.

Environment & CLI options
-------------------------
• RABBIT_URL  – AMQP URL (amqp://user:pass@host:5672/vhost)  
                falls back to config.settings.RABBIT_URL

Example usages
--------------
# simplest – single notification
$ python send_job.py --to alice@example.com

# custom job_type & payload, and fire ten of them
$ python send_job.py -j recurring_package \
    -p '{"report_id": 42, "format": "csv"}' -c 10
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import uuid

from amqp import AMQPConfig, open_connection, declare_topology, JSONPublisher
from clock import now                       # or: from datetime import datetime, timezone; now = lambda: datetime.now(timezone.utc)
from config import settings                 # your existing config wrapper

LOG = logging.getLogger("send_job")
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")


# ────────────────────────────── CLI ────────────────────────────────────
def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Emit ScheduleDue test events")
    ap.add_argument("-u", "--rabbit-url",
                    default=os.getenv("RABBIT_URL", settings.RABBIT_URL),
                    help="AMQP URL (env RABBIT_URL overrides; "
                         f"default: {settings.RABBIT_URL})")
    ap.add_argument("-j", "--job-type", default="notification",
                    help="value for event['job_type']  (default: notification)")
    ap.add_argument("-p", "--payload", default="{}",
                    help="JSON string for event['payload'] (default: empty dict)")
    ap.add_argument("-c", "--count", type=int, default=1,
                    help="number of events to publish (default: 1)")
    return ap.parse_args()


# ─────────────────────────── main routine ──────────────────────────────
async def _run() -> None:
    args = _parse_args()

    # validate / parse JSON payload once
    try:
        payload_template = json.loads(args.payload)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"--payload is not valid JSON: {exc}") from None

    cfg = AMQPConfig(args.rabbit_url)

    async with open_connection(cfg) as conn:
        # make sure exchange + queue exist (noop if already declared)
        await declare_topology(conn, cfg)

        ch  = await conn.channel(publisher_confirms=True)
        pub = JSONPublisher(ch, cfg.evt_ex)
        await pub.init()

        for i in range(args.count):
            evt = {
                "id": str(uuid.uuid4()),
                "job_type": args.job_type,
                "payload": payload_template,
                "fired_at": now().isoformat(),
                "attempt": 1,
            }
            # routing-key ⟶ schedule.events → "due"
            await pub.publish("due", evt)
            LOG.info("sent %s (%d/%d)", evt["id"], i + 1, args.count)

        await ch.close()


if __name__ == "__main__":
    asyncio.run(_run())


"""Example

python src/scripts/send_due_job.py \
  -j notification \
  -p '{"user_id": 1}'
"""
