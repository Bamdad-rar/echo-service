from logs import setup_logging
from scheduler.services import TaskScheduler
from adapters.message_broker import message_broker
from scheduler import task_repository

setup_logging()


class TaskRouting:
    CREATE = "task.schedule.create"
    UPDATE = "task.schedule.update"
    REMINDER = "task.reminder.trigger"

message_broker.setup_channel()
TaskScheduler().consume_events(message_broker, task_repository)
