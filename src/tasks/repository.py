from __future__ import annotations
from tasks.task import Task
from sqlalchemy import Engine, Table, insert, select, update, delete

from datetime import datetime, timezone
from typing import Iterable, List, Mapping, MutableMapping
from uuid import UUID
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Optional
from uuid import UUID

from tasks.task import Task


class DBTaskRepository:
    def __init__(self, engine: Engine, table: Table):
        self._engine = engine
        self._table = table

    def add(self, task: Task):
        stmt = insert(self._table).values(
            id=task.id,
            callback_data=task.callback_data,
            schedule=task.schedule,
            next_run=task.next_run,
            last_run=task.last_run,
            created_at=task.created_at,
        )
        with self._engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

    def get(self, task_id: str):
        stmt = select(self._table).where(self._table.c.id == task_id)
        with self._engine.connect() as conn:
            rows = conn.execute(stmt)
            return rows

    def update(self, task):
        """Update an existing task using its ID"""
        stmt = (
            update(self._table)
            .where(self._table.c.id == task.id)
            .values(
                event_id=task.event_id,
                event_timestamp=task.event_timestamp,
                action=task.action,
                start=task.start,
                repeat_for=task.repeat_for,
                repeated_for=task.repeated_for,
                unlimited=task.unlimited,
                period=task.period,
                action_data=task.action_data,
                next_run_time=task.next_run_time,
            )
        )
        with self._engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

    def delete(self, task_id):
        """Delete a task by its ID"""
        stmt = delete(self._table).where(self._table.c.id == task_id)
        with self._engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()



class InMemoryTaskRepository:
    """
    Development-time, in-memory store for Task objects.

    Methods
    -------
    add(task)            – insert a new Task
    update(task)         – overwrite an existing Task (recomputes next_run)
    delete(task_id)      – remove by UUID
    get(task_id)         – fetch by UUID (or None)
    all()                – iterate over all tasks
    due(at=now_utc)      – tasks with next_run <= at
    """
    def __init__(self) -> None:
        self._store: Dict[UUID, Task] = {}

    # ─── CRUD ───────────────────────────────────────────────────────────────
    def add(self, task: Task) -> None:
        if task.id in self._store:
            raise ValueError(f"Task {task.id} already exists")
        self._store[task.id] = task

    def update(self, task: Task) -> None:
        if task.id not in self._store:
            raise KeyError(f"Task {task.id} not found")
        self._store[task.id] = task

    def delete(self, task_id: UUID) -> None:
        if task_id not in self._store:
            raise KeyError(f"Task {task_id} not found")
        del self._store[task_id]

    # ─── Queries ────────────────────────────────────────────────────────────
    def get(self, task_id: UUID) -> Optional[Task]:
        return self._store.get(task_id)

    def all(self) -> Iterable[Task]:
        # Return a shallow copy so callers can’t mutate the internal dict
        return list(self._store.values())

    def due(self, *, at: Optional[datetime] = None) -> List[Task]:
        """
        Return tasks whose «next_run» is **<= at**.
        Defaults to the current UTC time.
        """
        at = at or datetime.now(timezone.utc)
        return [
            t for t in self._store.values()
            if t.next_run is not None and t.next_run <= at
        ]

    # ─── Convenience ────────────────────────────────────────────────────────
    def __len__(self) -> int:
        return len(self._store)

    def __repr__(self) -> str:
        return f"<TaskRepository size={len(self)}>"

