from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Optional, List
import jdatetime
from .base import Scheduler

@dataclass
class PersianRecurring(Scheduler):
    def __init__(self, jrrule) -> None:
        raise NotImplemented
    def next_after(self, t: datetime) -> datetime | None:
        raise NotImplemented
