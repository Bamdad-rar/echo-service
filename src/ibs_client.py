import pika
import json
from config import settings
from time import time

RABBITMQ_HOST = settings.rabbitmq_host
RABBITMQ_PORT = settings.rabbitmq_port
RABBITMQ_EXCHANGE = settings.rabbitmq_exchange
RABBITMQ_EXCHANGE_TYPE = settings.rabbitmq_exchange_type
RABBITMQ_INBOUND_QUEUE_NAME = settings.rabbitmq_scheduler_queue_name
RABBITMQ_INBOUND_ROUTING_KEY = settings.rabbitmq_scheduler_routing_key


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
        "event_timestamp": time(),
        "start": time(),
        "repeat_for": 10,
        "repeated_for": 0,
        "unlimited": False,
        "period": "seconds",
        "data": {
            "user_recurring_package_id": i+1,
            "action": "order",
            "recurring_package_id": i+1,
            "user_id": i+1,
        },
    }
    channel.basic_publish(
        exchange=RABBITMQ_EXCHANGE,
        routing_key="task.schedule.create",
        body=json.dumps(data),
        properties=pika.BasicProperties(content_type="application/json"),
    )


connection.close()
print('closed rabbit connection, exiting...')
