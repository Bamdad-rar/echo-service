from pydantic import BaseModel
from typing import Literal


class RecurringPackage(BaseModel):
    action: Literal["order", "cancel", "update"]
    user_recurring_package_id: int
    recurring_package_id: int
    user_id: int


class TaskEvent(BaseModel):
    event_id: int
    event_timestamp: int
    start: int
    repeat_for: int | None
    repeated_for: int = 0
    unlimited: bool
    period: Literal["seconds", "minutes", "hours", "days", "weeks", "months", "jmonths"]
    # extension can happen here
    data: RecurringPackage
