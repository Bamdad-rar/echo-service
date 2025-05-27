from logs import setup_logging
from consumers.blocking_consumer import BlockingConsumer
from config import settings



setup_logging()

           
class TaskRouting:
    CREATE = "task.schedule.create"
    UPDATE = "task.schedule.update"
    REMINDER = "task.reminder.trigger"

consumer = BlockingConsumer(
    settings.rabbitmq_username,
    settings.rabbitmq_password,
    settings.rabbitmq_host,
    settings.rabbitmq_port
)
consumer.run()

