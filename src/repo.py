from __future__ import annotations

import asyncpg
import uuid
from datetime import datetime, timezone
from typing import List, Sequence
import json

from models import Job, JobStatus, ScheduleSpec


class JobRepo:
    """Thin asyncpg pool wrapper"""
    def __init__(self, pool: asyncpg.Pool):
        self._pool = pool

    @classmethod
    async def create(cls, dsn: str, *, min_size=1, max_size=10) -> "JobRepo":
        """Factory"""
        pool = await asyncpg.create_pool(dsn, min_size=min_size, max_size=max_size)
        return cls(pool)

    # Helpers --------------------------------------------------
    @staticmethod
    def _row_to_job(row: asyncpg.Record) -> Job:
        spec = (
            ScheduleSpec(at=row["next_run_at"])      # one-shot
            if row["rrule"] is None
            else ScheduleSpec(rrule=row["rrule"])
        )
        return Job(
            id=row["id"],
            job_type=row["job_type"],
            payload=row["payload"],
            spec=spec,
            next_run_at=row["next_run_at"],
            retries=row["retries"],
            status=JobStatus(row["status"]),
            created_at=row["created_at"],
        )

    # CRUD -----------------------------------------------------
    async def insert_job(self, job: Job) -> bool:
        """
        Returns True if inserted, False if duplicate (idempotent).
        """
        q = """
        INSERT INTO jobs (id, job_type, payload, rrule, next_run_at, created_at)
        VALUES ($1,$2,$3,$4,$5,$6)
        ON CONFLICT (id) DO NOTHING;
        """
        async with self._pool.acquire() as conn:
            res = await conn.execute(
                q,
                job.id,
                job.job_type,
                json.dumps(job.payload),
                job.spec.rrule,
                job.next_run_at,
                job.created_at,
            )
            return res.endswith("INSERT 0 1")

    async def cancel_job(self, job_id: uuid.UUID) -> int:
        """
        Mark cancelled; returns # of rows affected (0 or 1).
        """
        q = "UPDATE jobs SET status='cancelled' WHERE id=$1 AND status='pending';"
        async with self._pool.acquire() as conn:
            res = await conn.execute(q, job_id)
            return int(res.split()[-1])

    async def lock_due_jobs(
        self, *, now: datetime | None = None, limit: int = 500
    ) -> Sequence[Job]:
        """
        Atomically selects and locks due rows.
        Other replicas skip the same rows.
        """
        now = now or datetime.now(timezone.utc)
        q = """
        SELECT id, job_type, payload, rrule, next_run_at,
               retries, status, created_at
        FROM   jobs
        WHERE  status = 'pending'
          AND  next_run_at <= $1
        ORDER  BY next_run_at
        LIMIT  $2
        FOR UPDATE SKIP LOCKED;
        """
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(q, now, limit)
            return [self._row_to_job(r) for r in rows]

    async def reschedule(self, job: Job, next_time: datetime) -> None:
        q = """
        UPDATE jobs
        SET next_run_at = $2,
            retries     = $3
        WHERE id = $1;
        """
        async with self._pool.acquire() as conn:
            await conn.execute(q, job.id, next_time, job.retries)

    async def mark_done(self, job_id: uuid.UUID) -> None:
        q = "UPDATE jobs SET status='done' WHERE id=$1;"
        async with self._pool.acquire() as conn:
            await conn.execute(q, job_id)
