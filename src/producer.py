from models import metadata as scheduled_events_metadata
from sqlalchemy import create_engine
import pika
from pika.channel import Channel
from pika.exceptions import AMQPConnectionError

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




DB_URL = "sqlite:///:memory:"
DB_CONNECTION_POOL_SIZE = 20

"""db setup"""
engine = create_engine(DB_URL, pool_size=DB_CONNECTION_POOL_SIZE)
scheduled_events_metadata.create_all(engine, checkfirst=True)

if __name__ == "__main__":
   ... 
