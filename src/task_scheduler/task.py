from dataclasses import dataclass, field
from typing import Literal
from uuid import UUID
from task_scheduler.schedulers.base import Scheduler
from datetime import datetime, timedelta, timezone

Status = Literal['new','scheduled', 'paused', 'cancelled', 'finished', 'failed']

@dataclass 
class Task:
    id: UUID
    callback_data: dict # what
    scheduler: Scheduler # when
    # callback_dst: str # where
    created_at: datetime = field(default=datetime.now().astimezone(timezone.utc))
    event_id: UUID | None = None # provided by other services
    event_timestamp: int | None = None # provided by other services
    status: Status = "new"
    retry_count: int = 0
    next_trigger: datetime | None = None
    last_trigger: datetime | None = None

    def __post_init__(self):
        if not isinstance(self.scheduler, Scheduler):
            raise ValueError("Invalid Schedule.")
        
    def __repr__(self) -> str:
        return f'Task(id={self.id}, status={self.status}, next_trigger={self.next_trigger})'

    def __eq__(self, other) -> bool:
        if not isinstance(other, Task):
            return False
        return self.callback_data == other.callback_data

    def __hash__(self) -> int:
        return hash(self.callback_data)

    def schedule(self):
        self.next_trigger = self.scheduler.next_after(datetime.now(timezone.utc))
        self.status = "finished" if self.next_trigger is None else "scheduled"

    def delay(self, seconds: int):
        if self.next_trigger is None:
            raise ValueError("Cannot put delay on task with next_trigger time of None")
        self.next_trigger += timedelta(seconds=seconds)

    def fail(self, error: str, max_retries: int = 3, backoff_sec: int = 60):
        self.retry_count += 1
        if self.retry_count > max_retries:
            self.status = "failed"
            return
        self.next_trigger = datetime.now(timezone.utc) + timedelta(seconds=backoff_sec * self.retry_count)
        self.status = "scheduled"

    def pause(self):
        if self.status == "scheduled":
            self.status = "paused"
            return True
        return False

    def resume(self):
        if self.status == "paused":
            self.status = "scheduled"
            return True
        return False

    def cancel(self):
        self.status = "cancelled"
        self.next_trigger = None

    def is_scheduled(self):
        return self.status == "scheduled"

    def is_due(self):
        if not self.is_scheduled() or self.next_trigger is None:
            return False
        return self.next_trigger <= datetime.now(timezone.utc)

