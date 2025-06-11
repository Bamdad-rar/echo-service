from uuid import UUID
from datetime import datetime, timezone
from typing import Optional
from task_scheduler.task import Task
from task_scheduler.task_status import Status
from task_scheduler.repository.base import TaskRepository


class InMemoryTaskRepository(TaskRepository):
    """
    In-memory implementation of the TaskRepository. can be used for development and unit tests.
    """
    def __init__(self):
        # A simple dictionary is sufficient. The keys are already a unique set.
        self._tasks: dict[UUID, Task] = {}

    def add(self, task: Task):
        if not task.id or task.id in self._tasks:
            raise ValueError(f"Task with ID {task.id} is invalid or already exists.")
        self._tasks[task.id] = task

    def get(self, reference: UUID) -> Optional[Task]:
        return self._tasks.get(reference)

    def update(self, task: Task):
        if not task.id or task.id not in self._tasks:
            raise ValueError(f"Task with ID {task.id} not found for update.")
        self._tasks[task.id] = task

    def remove(self, reference: UUID) -> None:
        if reference in self._tasks:
            del self._tasks[reference]

    def get_due_tasks(self, limit: int) -> list[Task]:
        now = datetime.now(timezone.utc)
        
        due_tasks = [
            task for task in self._tasks.values()
            if task.status == Status.SCHEDULED and task.next_trigger and task.next_trigger <= now
        ]
        
        # Sort by next_trigger (earliest first) to process in order
        due_tasks.sort(key=lambda t: t.next_trigger)
        
        return due_tasks[:limit]

    def get_all(self, limit: int = 100, offset: int = 0) -> list[Task]:
        # Correctly implement limit and offset for pagination
        all_tasks = list(self._tasks.values())
        return all_tasks[offset : offset + limit]

    def count(self) -> int:
        return len(self._tasks)
    
    def clear(self):
        """Helper method for cleaning up between tests."""
        self._tasks.clear()





















