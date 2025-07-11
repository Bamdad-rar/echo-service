import json, os, pika
from datetime import datetime, timedelta


RABBIT_URL        = "amqp://admin:1234@localhost:5672" 
EXCHANGE_NAME     = "sched"
EXCHANGE_TYPE     = "topic"
INBOX_QUEUE       = "sched.inbox"   # schedule.create.*
DUE_QUEUE         = "sched.due"     # schedule.due.*
PREFETCH_COUNT    = 100             # tune per worker

credentials = pika.PlainCredentials("admin", "1234")
params = pika.ConnectionParameters(
    host="localhost",
    port=5672,
    virtual_host="/",
    credentials=credentials,
    heartbeat=60,              # keep-alive; good practice
    blocked_connection_timeout=30
)
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.exchange_declare(EXCHANGE_NAME, EXCHANGE_TYPE, durable=True)
channel.queue_declare(INBOX_QUEUE, durable=True)
channel.queue_bind(INBOX_QUEUE, EXCHANGE_NAME, routing_key='schedule.create.*')

def publish_task(task_type: str, payload: dict) -> None:
    """
    task_type: 'reminder' | 'recurring' | …
    payload  : JSON-serialisable dict
    routing_suffix: optional e.g. '.tenant42' for sharding
    """
    routing_key = f"schedule.create.{task_type}"
    channel.basic_publish(
        exchange    = EXCHANGE_NAME,
        routing_key = routing_key,
        body        = json.dumps(payload).encode(),
        properties  = pika.BasicProperties(
            delivery_mode = 2   # make message persistent
        )
    )


for i in range(1000):
    payload = {
            'callback_data': {'a':i},
            'schedule': str(int((datetime.now()+timedelta(seconds=i)).timestamp()))
            }
    publish_task('notification', payload=payload)
