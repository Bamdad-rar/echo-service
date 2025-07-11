from scheduler.services import Scheduler
from scheduler.models import Task, OrderPackageActionData
from time import time


def test_add_task_to_scheduler():
    scheduler = Scheduler(db=None, table=None)
    task = Task(
        event_id=1,
        event_timestamp=int(time()),
        action="order_package",
        start=int(time()),
        repeat_for=10,
        repeated_for=0,
        unlimited=False,
        period="minutes",
        action_data=OrderPackageActionData(
            user_id=1, user_recurring_package_id=1, recurring_package_id=1
        ),
    )

    scheduler.add_task(task)

    assert scheduler.get_task(task.event_id) != None
