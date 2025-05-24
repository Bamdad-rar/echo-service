from models import metadata as scheduled_events_metadata
from sqlalchemy import create_engine
import pika
from pika.channel import Channel
from pika.exceptions import AMQPConnectionError

DB_URL = "sqlite:///:memory:"
DB_CONNECTION_POOL_SIZE = 20

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
"""db setup"""
engine = create_engine(DB_URL, pool_size=DB_CONNECTION_POOL_SIZE)
scheduled_events_metadata.create_all(engine, checkfirst=True)

"""rabbit setup"""


class BlockingConsumer:
    def __init__(
        self, amqp_username: str, amqp_password: str, amqp_host: str, amqp_port: int
    ):
        self.connection = None
        self.channel = None
        self.connection_params = pika.ConnectionParameters(
            heartbeat=600,
            host=amqp_host,
            port=amqp_port,
            credentials=pika.PlainCredentials(amqp_username, amqp_password),
        )
        self.prefetch_count = PREFETCH_COUNT
        self.should_reconnect = RETRY_ON_CONNECTION_FAILURE 
        self.max_retries = 20
        self.retry_attemps = 0
        self.shutdown_flag = False

    def connect(self):
        while not self.shutdown_flag:
            try:
                self.connection = pika.BlockingConnection(self.connection_params)
            except AMQPConnectionError as e:
                print(f"could not establish a connection to rabbitmq, reason: {e}")
                raise

    def establish_channel(self):
        if not self.connection:
            raise AttributeError("No connection found, establish one first.")
        channel = self.connection.channel()
        self.channel = channel 

    def declare_exchange(self):
        if not self.channel:
            raise AttributeError("No channel found, establish one first")
        self.channel.exchange_declare(
            exchange=RABBITMQ_EXCHANGE, exchange_type=RABBITMQ_EXCHANGE_TYPE
        )

    def declare_queue(self):
        """Telling RabbitMQ what what queues to create"""
        if not self.channel:
            raise AttributeError("No channel found, establish one first")
        self.channel.queue_declare(queue=RABBITMQ_INBOUND_QUEUE_NAME, durable=True)

    def bind(self):
        """Telling RabbitMQ how to route messages from exchange to queues"""
        if not self.channel:
            raise AttributeError("No channel found, establish one first")
        self.channel.queue_bind(
            exchange=RABBITMQ_EXCHANGE,
            queue=RABBITMQ_INBOUND_QUEUE_NAME,
            routing_key=RABBITMQ_INBOUND_ROUTING_KEY,
        )

    def consume_callback(self, channel: Channel, method_frame, header_frame, body):
        if not self.channel:
            raise AttributeError("No channel found, establish one first")
        print(f"{channel=}")
        print(f"{method_frame.delivery_tag=}")
        print(f"{header_frame=}")
        print(f"{body=}")
        self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    def setup(self):
        # setting connection to rabbitmq
        self.connect()
        self.establish_channel()
        # preparing rabbit
        self.declare_exchange()
        self.declare_queue()
        self.bind()
    
    def run(self):
        self.setup()
        self.channel.basic_consume(RABBITMQ_INBOUND_QUEUE_NAME, self.consume_callback)

        try:
            self.channel.start_consuming()
        except KeyboardInterrupt as e:
            print(f"Stopping Consumer, [{e=}]")
        except Exception as e:
            print(f"Stopping Consumer, an unexpected error occurred [{e=}]")
        finally:
            self.connection.close()


class TaskRouting:
    CREATE = "task.schedule.create"
    UPDATE = "task.schedule.update"
    REMINDER = "task.reminder.trigger"




if __name__ == "__main__":
    consumer = BlockingConsumer("admin", "1234", RABBITMQ_HOST, RABBITMQ_PORT)
    consumer.run()

