from dataclasses import dataclass
from datetime import datetime, timezone
from dateutil.rrule import rrulestr
from .base import Scheduler


@dataclass
class Recurring(Scheduler):
    rrule: str
    count: int | None = None
    timezone: str = "UTC"

    def next_after(self, t: datetime) -> datetime | None:
        rule = rrulestr(self.rrule, dtstart=t.astimezone(timezone.utc))
        return rule.after(t, inc=False)

    def __repr__(self) -> str:
        return f'recurring: {self.rrule} count={self.count} timezone={self.timezone}'

