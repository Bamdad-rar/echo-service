from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from dateutil.rrule import rrulestr, rruleset, rrule
from dateutil.parser import isoparse


class JobStatus(str, Enum):
    PENDING   = "pending"
    DONE      = "done"
    CANCELLED = "cancelled"


@dataclass(slots=True)
class ScheduleSpec:
    """
    A single-fire timestamp *or* an RRULE string.
    Exactly one of `at` or `rrule` is set.
    """
    at: Optional[datetime] = None
    rrule: Optional[str]   = None

    def __post_init__(self) -> None:
        if bool(self.at) == bool(self.rrule):
            raise ValueError("Must supply exactly one of 'at' or 'rrule'")

    def next_after(self, now: datetime) -> Optional[datetime]:
        if self.at:
            return self.at if self.at > now else None
        _rule = rrulestr(self.rrule, forceset=True)  # forceset handles RRULE+EXDATE
        return _rule.after(now, inc=True)


@dataclass(slots=True)
class Job:
    id: uuid.UUID
    job_type: str
    payload: Dict[str, Any]
    spec: ScheduleSpec
    next_run_at: datetime
    retries: int            = 0
    status: JobStatus       = JobStatus.PENDING
    created_at: datetime    = field(default_factory=lambda: datetime.now(timezone.utc))

    # ------------ Convenience ------------
    @property
    def is_recurring(self) -> bool:
        return self.spec.rrule is not None

    @classmethod
    def from_request_event(cls, evt: Dict[str, Any]) -> "Job":
        """
        Build a Job from the JSON of a ScheduleRequest event.
        Expects:
            {
              "id": "<uuid>",
              "job_type": "notification",
              "payload": {...},
              "schedule": {"at": "..."} | {"rrule": "..."}
            }
        """
        jid = uuid.UUID(evt["id"])
        schedule = evt["schedule"]
        spec = ScheduleSpec(
            at=isoparse(schedule["at"]).astimezone(timezone.utc)
                if "at" in schedule else None,
            rrule=schedule.get("rrule"),
        )
        now = datetime.now(timezone.utc)
        next_time = spec.next_after(now)
        if next_time is None:
            raise ValueError("Schedule is already in the past")

        return cls(
            id=jid,
            job_type=evt["job_type"],
            payload=evt.get("payload", {}),
            spec=spec,
            next_run_at=next_time,
        )

    def to_dict(self) -> Dict[str, Any]:
        """JSON-serialisable representation (for tests or logging)."""
        return {
            "id": str(self.id),
            "job_type": self.job_type,
            "payload": self.payload,
            "schedule": (
                {"at": self.spec.at.isoformat()}
                if self.spec.at
                else {"rrule": self.spec.rrule}
            ),
            "next_run_at": self.next_run_at.isoformat(),
            "status": self.status.value,
            "retries": self.retries,
            "created_at": self.created_at.isoformat(),
        }
