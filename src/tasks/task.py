from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, field_validator, Field
from dateutil.rrule import rrulestr
from dateutil.parser import isoparse
from datetime import datetime, timezone
from uuid import uuid4
from typing import Union

class Task(BaseModel):
    """
    A schedulable task.

    * **schedule** accepts:
        • Unix-epoch seconds (float or int); or  
        • an RFC 5545 RRULE string, optionally preceded by “RRULE:”.
    """
    id: UUID = Field(default_factory=uuid4)
    callback_data: dict            # what
    schedule: Union[float, int, str]  # when
    # callback_url: str            # where
    next_run: datetime | None = None
    last_run: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("schedule", mode="before")
    @classmethod
    def _validate_schedule(cls, v) -> Union[float, int, str]:
        """
        Accept only:
          • a number (Unix epoch seconds), or
          • an RFC 5545 RRULE string.

        Raises `ValueError` otherwise.
        """
        # 1) Numeric timestamp (int / float / numeric-string)
        if isinstance(v, (int, float)):
            return v

        if isinstance(v, str):
            v_clean = v.strip()

            # numeric string?
            try:
                return float(v_clean) if "." in v_clean else int(v_clean)
            except ValueError:
                pass

            # 2) RFC 5545 RRULE
            try:
                rule_str = (
                    v_clean if v_clean.upper().startswith("RRULE")
                    else f"RRULE:{v_clean}"
                )
                rrulestr(rule_str)       # -> raises if invalid
                return v_clean           # keep original form
            except ValueError:
                pass

        raise ValueError(
            "schedule must be a Unix-epoch timestamp (int/float) "
            "or a valid RFC 5545 RRULE string"
        )

    def set_next_run(self, *, after: datetime | None = None) -> datetime | None:
        """
        Compute **and store** the next execution time.

        * Numeric timestamp → that moment (if still in the future)  
        * RRULE             → first occurrence strictly after *after*
                              (defaults to “now”, UTC)

        Returns **None** when the schedule is a past-tense one-shot timestamp
        or the RRULE has no further occurrences.
        """
        after = after or datetime.now(timezone.utc)

        if isinstance(self.schedule, (int, float)):
            ts_dt = datetime.fromtimestamp(self.schedule, tz=timezone.utc)
            self.next_run = ts_dt if ts_dt > after else None
            return self.next_run

        # ── RFC 5545 RRULE ──────────────────────────────────────────────────
        rule_str = (
            self.schedule.strip()
            if self.schedule.upper().startswith("RRULE")
            else f"RRULE:{self.schedule.strip()}"
        )
        rule = rrulestr(rule_str)
        next_dt = rule.after(after, inc=False)

        # `dateutil` returns naïve datetimes unless TZ info is present in rule
        # Keep original behaviour and just store what we get
        self.next_run = next_dt
        return self.next_run

    def __repr__(self) -> str:
        return f"Task(schedule={self.schedule!r}, next_run={self.next_run})"

    

