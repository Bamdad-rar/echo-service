from logging import getLogger
import pika
import json
import time

from pydantic import ValidationError
from tasks.repository import InMemoryTaskRepository
from tasks.task import Task

logger = getLogger(__name__)


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
def main():
    connection = pika.BlockingConnection(params)
    ch = connection.channel()
    ch.exchange_declare(EXCHANGE_NAME, EXCHANGE_TYPE, durable=True)
    ch.queue_declare(INBOX_QUEUE, durable=True)
    ch.queue_bind(INBOX_QUEUE, EXCHANGE_NAME, routing_key="schedule.create.*")
    ch.basic_qos(prefetch_count=PREFETCH_COUNT)

    task_repo = InMemoryTaskRepository()

    def callback(channel, method, properties, body):
        msg = json.loads(body)
        try:
            
            task = Task(**msg)
            task_repo.add(task)
            print(task_repo)
            
            channel.basic_ack(method.delivery_tag)
        except ValidationError as e:
            logger.error('invalid message:', e)
            channel.basic_nack(method.delivery_tag, requeue=True)
        except Exception as exc:
            logger.error("error:", exc)
            channel.basic_nack(method.delivery_tag, requeue=True)

    ch.basic_consume(INBOX_QUEUE, callback)
    print(" [*] Waiting for schedule.create …")
    ch.start_consuming()

if __name__ == "__main__":
    main()

