from .models import Task
from sqlalchemy import Engine, Table, insert, select, update, delete


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




















