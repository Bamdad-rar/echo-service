from logs import setup_logging
from scheduler.services import Scheduler
from adapters.message_broker import message_broker
from scheduler import task_repository

setup_logging()


class TaskRouting:
    CREATE = "task.schedule.create"
    UPDATE = "task.schedule.update"
    REMINDER = "task.reminder.trigger"

Scheduler().consume_events(message_broker, task_repository)
