from logs import setup_logging
from message_brokers.rabbitmq import RabbitMQ
from config import settings



setup_logging()

           
class TaskRouting:
    CREATE = "task.schedule.create"
    UPDATE = "task.schedule.update"
    REMINDER = "task.reminder.trigger"

msg_broker = RabbitMQ(
    settings.rabbitmq_username,
    settings.rabbitmq_password,
    settings.rabbitmq_host,
    settings.rabbitmq_port
)
msg_broker.run()

