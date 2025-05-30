import pika
from uuid import uuid4
import json

RABBITMQ_HOST = "localhost"
RABBITMQ_PORT = 5672
RABBITMQ_EXCHANGE_TYPE = "topic"
RABBITMQ_INBOUND_QUEUE_NAME = "scheduler-main-queue"
RABBITMQ_OUTBOUND_QUEUE_NAME = "reminder-main-queue"
RABBITMQ_EXCHANGE = "task.scheduling.exchange"
RABBITMQ_INBOUND_ROUTING_KEY = "task.schedule.*"
RABBITMQ_OUTBOUND_ROUTING_KEY = "task.reminder.*"
RETRY_ON_CONNECTION_FAILURE = True
PREFETCH_COUNT = 1

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=pika.PlainCredentials(username="admin", password="1234"),
    )
)

channel = connection.channel()
channel.exchange_declare(
    exchange=RABBITMQ_EXCHANGE, exchange_type=RABBITMQ_EXCHANGE_TYPE
)
channel.queue_declare(queue=RABBITMQ_INBOUND_QUEUE_NAME, durable=True)
channel.queue_bind(
    exchange=RABBITMQ_EXCHANGE,
    queue=RABBITMQ_INBOUND_QUEUE_NAME,
    routing_key=RABBITMQ_INBOUND_ROUTING_KEY,
)


for i in range(100):
    data = {
        "event_id": i,
        "event_timestamp": i,
        "action": "order_package",
        "start": 10,
        "repeat_for": 10,
        "repeated_for": 0,
        "unlimited": False,
        "period": "seconds",
        "action_data": {
            "user_recurring_package_id": i,
            "recurring_package_id": i,
            "user_id": i,
        },
    }
    channel.basic_publish(
        exchange=RABBITMQ_EXCHANGE,
        routing_key="task.schedule.create",
        body=json.dumps(data),
        properties=pika.BasicProperties(content_type="application/json"),
    )
