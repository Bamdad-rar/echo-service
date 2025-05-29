from pydantic import BaseModel
from typing import Literal

# you can add more classes to support more types of events here
class OrderPackageActionData(BaseModel):
    user_recurring_package_id: int
    recurring_package_id: int
    user_id: int

class Task(BaseModel):
    event_id: int
    event_timestamp: int
    action: Literal['order_package']
    start: int
    repeat_for: int | None
    repeated_for: int = 0
    unlimited: bool
    period: Literal['seconds', 'minutes', 'hours', 'days', 'weeks', 'months', 'jmonths']
    action_data: OrderPackageActionData # can later be extended to different actions that need to be scheduled 


