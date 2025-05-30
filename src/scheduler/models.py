from datetime import datetime
from pydantic import BaseModel
from typing import Literal, Optional


class RecurringPackage(BaseModel):
    action: Literal["order", "cancel", "update"]
    user_recurring_package_id: int
    recurring_package_id: int
    user_id: int


class Task(BaseModel):
    id: Optional[int] = None  # only we're newly creating a task, otherwise it has an id
    event_id: int
    event_timestamp: float
    start: float
    repeat_for: int | None
    repeated_for: int = 0
    unlimited: bool
    period: Literal["seconds", "minutes", "hours", "days", "weeks", "months", "jmonths"]
    data: RecurringPackage
    created_at: datetime
    updated_at: datetime
    next_run_time: float
