from sqlalchemy import Engine, Table, insert, select, update, delete, func
from uuid import UUID
from datetime import datetime, timezone
from abc import ABC, abstractmethod
from typing import Optional
from scheduler.domain.task import Task
from scheduler.domain.task_status import Status


class TaskRepository(ABC):
    """
    Abstract interface for a collection of Tasks. Defines the contract
    that all persistence implementations must adhere to.
    """

    @abstractmethod
    def add(self, task: Task) -> None:
        """Adds a new task to the repository."""
        raise NotImplementedError

    @abstractmethod
    def get(self, reference) -> Optional[Task]:
        """Retrieves a task by its unique ID."""
        raise NotImplementedError

    @abstractmethod
    def update(self, task: Task) -> None:
        """Updates an existing task."""
        raise NotImplementedError

    @abstractmethod
    def remove(self, reference) -> None:
        """Removes a task by its unique ID."""
        raise NotImplementedError

    @abstractmethod
    def get_due_tasks(self, limit: int) -> list[Task]:
        """Retrieves tasks that are due to be processed."""
        raise NotImplementedError

    @abstractmethod
    def get_all(self, limit: int = 100, offset: int = 0) -> list[Task]:
        """Retrieves all tasks, with pagination."""
        raise NotImplementedError

    @abstractmethod
    def count(self) -> int:
        """Counts the total number of tasks."""
        raise NotImplementedError

class InMemoryTaskRepository(TaskRepository):
    """
    In-memory implementation of the TaskRepository. Ideal for fast unit tests.
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


class DatabaseTaskRepository(TaskRepository):
    """
    SQLAlchemy Core implementation of the TaskRepository.
    This class is responsible for mapping domain objects to database rows.
    """
    def __init__(self, engine: Engine, tasks_table: Table):
        self._engine = engine
        self._table = tasks_table

    # --- Private Mapper ---
    # This is the most important addition. This method translates a database row
    # into a rich domain object. You will need to build the `Scheduler` object
    # based on the stored data. This is a simplified example.
    def _map_row_to_task(self, row) -> Task:
        # NOTE: This mapping is highly dependent on your `Task` and `Scheduler` classes.
        # You'll need to deserialize the `rrule` back into a `Recurring` schedule, etc.
        # This is a placeholder for that logic.
        from scheduler.domain.schedule import OneOff, Recurring # Local import to avoid circular dependency
        
        schedule_info = row.schedule_info or {}
        if row.schedule_type == 'one_off':
            schedule = OneOff(trigger_at=row.next_trigger)
        elif row.schedule_type == 'recurring':
            schedule = Recurring(
                rrule=schedule_info.get('rrule'),
                count=schedule_info.get('count', 0),
                timezone=schedule_info.get('timezone', 'UTC')
            )
        else:
            raise ValueError(f"Unknown schedule type '{row.schedule_type}' for task {row.id}")

        return Task(
            id=row.id,
            callback_data=row.callback_data,
            scheduler=schedule,
            created_at=row.created_at,
            status=Status(row.status), # Convert string from DB to Enum
            retry_count=row.retry_count,
            next_trigger=row.next_trigger,
            last_trigger=row.last_trigger,
            event_id=row.event_id,
            event_timestamp=row.event_timestamp
        )

    def add(self, task: Task):
        stmt = insert(self._table).values(
            id=task.id,
            callback_data=task.callback_data,
            # NOTE: How you store the schedule is a key design decision.
            # Storing type and a JSONB blob of details is flexible.
            schedule_type=type(task.schedule).__name__.lower(), # 'oneoff' or 'recurring'
            schedule_info={"rrule": task.schedule.rrule, "count": task.schedule.count} if hasattr(task.schedule, 'rrule') else {},
            created_at=task.created_at,
            status=task.status.value, # Store the string value of the Enum
            retry_count=task.retry_count,
            next_trigger=task.next_trigger,
            last_trigger=task.last_trigger,
            event_id=task.event_id,
            event_timestamp=task.event_timestamp,
        )
        with self._engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

    def get(self, task_id: UUID) -> Optional[Task]:
        stmt = select(self._table).where(self._table.c.id == task_id)
        with self._engine.connect() as conn:
            row = conn.execute(stmt).first()
            return self._map_row_to_task(row) if row else None

    def update(self, task: Task):
        stmt = (
            update(self._table)
            .where(self._table.c.id == task.id)
            .values(
                status=task.status.value,
                retry_count=task.retry_count,
                next_trigger=task.next_trigger,
                last_trigger=task.last_trigger,
                # You might not want to update all fields, only mutable ones.
                # For example, callback_data and schedule might be immutable.
            )
        )
        with self._engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

    def remove(self, task_id: UUID):
        stmt = delete(self._table).where(self._table.c.id == task_id)
        with self._engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

    def get_due_tasks(self, limit: int) -> List[Task]:
        stmt = (
            select(self._table)
            .where(self._table.c.status == Status.SCHEDULED.value)
            .where(self._table.c.next_trigger <= text("CURRENT_TIMESTAMP")) # Use database's clock
            .order_by(self._table.c.next_trigger.asc())
            .limit(limit)
        )
        with self._engine.connect() as conn:
            rows = conn.execute(stmt).fetchall()
            return [self._map_row_to_task(row) for row in rows]

    def get_all(self, limit: int = 100, offset: int = 0) -> List[Task]:
        stmt = select(self._table).limit(limit).offset(offset)
        with self._engine.connect() as conn:
            rows = conn.execute(stmt).fetchall()
            return [self._map_row_to_task(row) for row in rows]
    
    def count(self) -> int:
        stmt = select(func.count()).select_from(self._table)
        with self._engine.connect() as conn:
            return conn.execute(stmt).scalar_one()


class RecurringPackagePollingRepo:
    def __init__(self, engine, user_recurring_package_table) -> None:
        self._engine = engine
        self._table = user_recurring_package_table

    def get_tasks(self):
        stmt = select(self._table)
        with self._engine.connect() as conn:
            rows = conn.execute(stmt)
            return rows




















