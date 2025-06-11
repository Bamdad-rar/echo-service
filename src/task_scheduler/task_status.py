from dataclasses import dataclass
from enum import Enum


class Status(Enum):
    NEW = "new"
    SCHEDULED = "scheduled"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    FINISHED = "finished"
    FAILED = "failed"


@dataclass
class TaskStatus:
    status: Status


