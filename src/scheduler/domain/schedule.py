from dataclasses import dataclass
from datetime import datetime, timezone
from dateutil.rrule import rrulestr


class Scheduler:
    def next_after(self, t: datetime) -> datetime | None:
        raise NotImplemented

@dataclass(frozen=True)
class OneOff(Scheduler):
    trigger_at: datetime

    def next_after(self, t: datetime) -> datetime | None:
        return self.trigger_at if self.trigger_at > t else None
    
    def __repr__(self) -> str:
        return f'one-off: trigger_at={self.trigger_at}'

@dataclass
class Recurring(Scheduler):
    rrule: str
    count: int
    timezone: str = "UTC"

    def next_after(self, t: datetime) -> datetime | None:
        rule = rrulestr(self.rrule, dtstart=t.astimezone(timezone.utc))
        return rule.after(t, inc=False)

    def __repr__(self) -> str:
        return f'recurring: {self.rrule} count={self.count} timezone={self.timezone}'
    

