import argparse
import asyncio
import json
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone

from amqp import AMQPConfig, JSONPublisher, open_connection, declare_topology


# ────────────────────────────── helpers ────────────────────────────────────
def build_event(
    job_type: str,
    payload: dict,
    *,
    at: str | None = None,
    rrule: str | None = None,
    delay: int | None = None,
) -> dict:
    if sum(bool(x) for x in (at, rrule, delay)) != 1:
        raise ValueError("Specify exactly one of --at, --rrule or --delay")

    if delay is not None:
        fire_time = datetime.now(timezone.utc) + timedelta(seconds=delay)
        schedule = {"at": fire_time.isoformat()}
    elif at is not None:
        schedule = {"at": at}
    else:  # rrule
        schedule = {"rrule": rrule}

    return {
        "id": str(uuid.uuid4()),
        "job_type": job_type,
        "payload": payload,
        "schedule": schedule,
    }


async def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Schedule test jobs")
    parser.add_argument("--rabbit", default=os.getenv("RABBIT_URL", "amqp://guest:guest@localhost/"),
                        help="AMQP URL (default: env RABBIT_URL or local)")
    parser.add_argument("--job-type", required=True, help="Logical job type")
    parser.add_argument("--payload", default="{}", help="JSON payload")
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--delay", type=int, help="Fire N seconds from now")
    g.add_argument("--at", help="Absolute UTC timestamp, ISO-8601, e.g. 2025-07-10T12:00:00Z")
    g.add_argument("--rrule", help="RFC-5545 RRULE string, e.g. FREQ=MINUTELY")
    args = parser.parse_args(argv)

    try:
        payload_dict = json.loads(args.payload)
    except json.JSONDecodeError as e:
        sys.exit(f"Invalid JSON for --payload: {e}")

    event = build_event(
        args.job_type,
        payload_dict,
        at=args.at,
        rrule=args.rrule,
        delay=args.delay,
    )

    cfg = AMQPConfig(args.rabbit)

    # one connection, one channel, confirms enabled via JSONPublisher
    async with open_connection(cfg) as conn:
        await declare_topology(conn, cfg)      # idempotent - safe even in prod
        ch = await conn.channel()
        pub = JSONPublisher(ch, cfg.cmd_ex)
        await pub.init()
        await pub.publish("request", event)
        print("Sent:\n", json.dumps(event, indent=2))

    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())


"""Examples


python scripts/send_job.py \
    --job-type notification \
    --payload '{"user_id": 1}' \
    --delay 5


"""
