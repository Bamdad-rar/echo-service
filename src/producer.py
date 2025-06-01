from logs import setup_logging
from scheduler.services import TaskScheduler
from adapters.message_broker import message_broker
from scheduler import task_repository

setup_logging()

message_broker.setup_channel()
task_scheduler = TaskScheduler()
task_scheduler.produce_events(message_broker, task_repository)
