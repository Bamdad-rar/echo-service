from dataclasses import dataclass
from typing import Literal
from uuid import UUID
from scheduler.domain.schedule import Scheduler
from scheduler.domain.task_status import TaskStatus
from datetime import datetime, timedelta, timezone

Status = Literal['new','scheduled', 'paused', 'cancelled', 'finished', 'failed']

@dataclass 
class Task:
    id: UUID
    callback_data: dict # what
    scheduler: Scheduler # when
    # callback_url: str # where
    created_at: datetime
    status: TaskStatus = "new"
    retry_count: int = 0
    next_trigger: datetime | None = None
    last_trigger: datetime | None = None

    def __post_init__(self):
        if not isinstance(self.schedule, Scheduler):
            raise ValueError("Invalid Schedule.")

    def __repr__(self) -> str:
        return f'Task {self.id}'

    def schedule(self):
        self.next_trigger = self.scheduler.next_after(datetime.now(timezone.utc))
        self.status = "finished" if self.next_trigger is None else "scheduled"

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

    def resume(self):
        if self.status == "paused":
            self.status = "scheduled"

    def cancel(self):
        self.status = "cancelled"
        self.next_trigger = None

    def is_scheduled(self):
        return self.status == "scheduled"

    def is_due(self):
        ...


