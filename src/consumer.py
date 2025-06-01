from logs import setup_logging
from scheduler.services import TaskScheduler
from adapters.message_broker import message_broker
from scheduler import task_repository, recurring_pacakge_repo

setup_logging()

message_broker.setup_channel()
task_scheduler = TaskScheduler()
task_scheduler.recreate_recurring_package_tasks(recurring_pacakge_repo)
task_scheduler.consume_events(message_broker, task_repository)
