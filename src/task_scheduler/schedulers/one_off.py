from dataclasses import dataclass
from .base import Scheduler


@dataclass(frozen=True)
class OneOff(Scheduler):
    trigger_at: datetime

    def next_after(self, t: datetime) -> datetime | None:
        return self.trigger_at if self.trigger_at > t else None
    
    def __repr__(self) -> str:
        return f'one-off: trigger_at={self.trigger_at}'


