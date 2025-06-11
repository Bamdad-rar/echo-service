from sqlalchemy import Engine, Table, insert, select, update, delete
from uuid import UUID
from datetime import datetime, timezone

class TaskRepository:
    def add(self, task)-> None:
        raise NotImplemented

    def get(self, reference)-> None:
        raise NotImplemented

    def update(self, task)-> None:
        raise NotImplemented

    def get_due_tasks(self, limit):
        raise NotImplemented
    
    def remove(self, reference)-> None:
        raise NotImplemented

    def bulk_add(self, tasks) -> None:
        raise NotImplemented

    def get_by_status(self, status):
        raise NotImplemented

    def count(self):
        raise NotImplemented

    def get_all(self, limit):
        raise NotImplemented


class InMemoryTaskRepo(TaskRepository):
    def __init__(self) -> None:
        # Using dict for O(1) lookups by ID, but keeping set for uniqueness
        self._memory = {}  # Changed to dict for efficient lookups
        self._task_set = set()  # Keep set for uniqueness checks

    def add(self, task):
        """Add a single task to memory"""
        if task.id in self._memory:
            raise ValueError(f"Task with ID {task.id} already exists")
        
        self._memory[task.id] = task
        self._task_set.add(task)

    def get(self, reference):
        """Get task by ID (UUID) or by the task object itself"""
        if isinstance(reference, UUID):
            # Get by ID
            return self._memory.get(reference)
        elif hasattr(reference, 'id'):
            # Get by task object (return same object if exists)
            return self._memory.get(reference.id)
        else:
            # Try to find by other attributes (fallback)
            for task in self._memory.values():
                if task == reference:
                    return task
            return None

    def update(self, task):
        """Update an existing task"""
        if task.id not in self._memory:
            raise ValueError(f"Task with ID {task.id} not found")
        
        # Remove old version from set
        old_task = self._memory[task.id]
        self._task_set.discard(old_task)
        
        # Add updated version
        self._memory[task.id] = task
        self._task_set.add(task)

    def get_due_tasks(self, limit):
        """Get tasks that are due for execution, sorted by next_trigger"""
        now = datetime.now(timezone.utc)
        
        # Filter for due tasks
        due_tasks = [
            task for task in self._memory.values()
            if (task.status == "scheduled" 
                and task.next_trigger is not None 
                and task.next_trigger <= now)
        ]
        
        # Sort by next_trigger (earliest first)
        due_tasks.sort(key=lambda t: t.next_trigger)
        
        return due_tasks[:limit]

    def remove(self, reference):
        """Remove task by ID (UUID) or by the task object itself"""
        task_id = None
        task_to_remove = None
        
        if isinstance(reference, UUID):
            task_id = reference
            task_to_remove = self._memory.get(reference)
        elif hasattr(reference, 'id'):
            task_id = reference.id
            task_to_remove = reference
        else:
            # Try to find the task first
            for task in self._memory.values():
                if task == reference:
                    task_id = task.id
                    task_to_remove = task
                    break
        
        if task_id is None or task_to_remove is None:
            raise ValueError(f"Task {reference} not found")
        
        del self._memory[task_id]
        self._task_set.discard(task_to_remove)

    def bulk_add(self, tasks):
        """Add multiple tasks at once"""
        for task in tasks:
            if task.id in self._memory:
                raise ValueError(f"Task with ID {task.id} already exists")
        
        for task in tasks:
            self._memory[task.id] = task
            self._task_set.add(task)

    def get_all(self, limit) -> list:
        """Get all tasks (useful for debugging/admin)"""
        return list(self._memory.values())
    
    def count(self) -> int:
        """Get total number of tasks"""
        return len(self._memory)
    
    def get_by_status(self, status: str) -> list:
        """Get all tasks with a specific status"""
        return [task for task in self._memory.values() if task.status == status]
    
    def clear(self):
        """Clear all tasks (useful for testing)"""
        self._memory.clear()
        self._task_set.clear()




class DataBaseTaskRepo(TaskRepository):
    def __init__(self, engine, table) -> None:
        self._engine = engine
        self._table = table

    def add(self, task):
        stmt = insert(self._table).values(

                )


class TaskRepo:
    def __init__(self, engine: Engine, table: Table):
        self._engine = engine
        self._table = table

    def add(self, task: Task):
        stmt = insert(self._table).values(
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

    def bulk_add(self, tasks: list[Task]):
        """Bulk insert multiple tasks in a single transaction"""
        data = [
            {
                "event_id": t.event_id,
                "event_timestamp": t.event_timestamp,
                "action": t.action,
                "start": t.start,
                "repeat_for": t.repeat_for,
                "repeated_for": t.repeated_for,
                "unlimited": t.unlimited,
                "period": t.period,
                "action_data": t.action_data,
                "next_run_time": t.next_run_time,
            }
            for t in tasks
        ]

        with self._engine.begin() as conn:
            conn.execute(insert(self._table), data)

    def bulk_get(self, task_ids: list[int]):
        """Fetch multiple tasks by their IDs"""
        stmt = select(self._table).where(self._table.c.id.in_(task_ids))
        with self._engine.connect() as conn:
            result = conn.execute(stmt)
            return [Task(**row._asdict()) for row in result]




class RecurringPackagePollingRepo:
    def __init__(self, engine, user_recurring_package_table, recurring_package_table) -> None:
        self._engine = engine
        self._user_recurring_package_table = user_recurring_package_table
        self._recurring_package_table = recurring_package_table


    def get_tasks(self):
        stmt = select(self._table)
        with self._engine.connect() as conn:
            rows = conn.execute(stmt)
            return rows




















