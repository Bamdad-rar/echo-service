import pika
import time
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import AMQPChannelError, AMQPConnectionError
import logging

from errors import UnrecoverableConnectionError, MaxRetriesReached
from config import settings

__all__ = ["message_broker", "MessageBroker"]

log = logging.getLogger(__name__)

class RabbitMQ:
    """
    definition of responsibility:
        what does this code protect me from having to know? - Kevlin Henney
    responsibility: Establishing, Maintaining a connection to rabbitmq, and registring a callback function to it

    prefetch count : 
    controls how many unacknowledged messages a consumer can receive from the broker before acknowledging one.
    It essentially sets a limit on the number of messages a consumer is allowed to hold in its local buffer.        
    
    heartbeat:
    a periodic signal sent between the server and client to ensure a connection is alive and to detect network issues or unresponsive peers.
    useful for catching dead connections faster.
    """

    PREFETCH_COUNT = settings.rabbitmq_prefetch_count
    RETRY_ON_CONNECTION_FAILURE = settings.rabbitmq_retry_on_connection_failure
    RABBITMQ_EXCHANGE_TYPE = settings.rabbitmq_exchange_type
    RABBITMQ_EXCHANGE = settings.rabbitmq_exchange
    RABBITMQ_SCHEDULER_ROUTING_KEY = settings.rabbitmq_scheduler_routing_key
    RABBITMQ_SCHEDULER_QUEUE_NAME = settings.rabbitmq_scheduler_queue_name

    def __init__(self, username: str, password: str, host: str, port: int, heartbeat: int = 600):
        self._credentials = pika.PlainCredentials(username, password)
        self._connection_params = pika.ConnectionParameters(
            heartbeat=heartbeat,
            host=host,
            port=port,
            credentials=self._credentials
        )

        # reconnection configurations
        self._reconnect_enabled = True
        self._reconnect_backoff = True
        self._reconnect_base_delay = 5 # seconds
        self._reconnect_max_retries = 12

        self._is_connected = False
        self._connection: pika.BlockingConnection | None = None
        self._channel: BlockingChannel | None = None

    def connect(self):
        for attempts in range(self._reconnect_max_retries):
            try:
                self._connection = pika.BlockingConnection(parameters=self._connection_params)
                self._channel = self._connection.channel()
            except AMQPConnectionError as e:
                retry_delay = self._reconnect_base_delay * (attempts+1) if self._reconnect_backoff else self._reconnect_base_delay
                log.warning(f"could not get connection to rabbitmq: {e}, retrying in {retry_delay}")
                time.sleep(retry_delay)
        else:
            msg = f"Could not establish a connection with rabbitmq after {self._reconnect_max_retries} retries."
            log.error(msg)
            raise MaxRetriesReached(msg)

    def close_connection(self):
        """Safely close connection if it exists"""
        try:
            if self._connection and self._connection.is_open:
                self._connection.close()
        except Exception as e:
            log.error(f"Error closing connection: {e}")

    def ensure_connection(self):
        if not self._is_connected or self._connection is None or self._connection.is_closed:
            self.connect()
 
    def setup_consumer(self):
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=self.prefetch_count)
        self.channel.exchange_declare(
            exchange=self.RABBITMQ_EXCHANGE,
            exchange_type=self.RABBITMQ_EXCHANGE_TYPE,
        )
        self.channel.queue_declare(queue=self.RABBITMQ_SCHEDULER_QUEUE_NAME, durable=True)
        self.channel.queue_bind(
            exchange=self.RABBITMQ_EXCHANGE,
            queue=self.RABBITMQ_SCHEDULER_QUEUE_NAME,
            routing_key=self.RABBITMQ_SCHEDULER_ROUTING_KEY,
        )
        log.info("Channel setup completed")

    def register_callback(self, callback):
        self.channel.basic_consume(
            queue=RABBITMQ_SCHEDULER_QUEUE_NAME,
            on_message_callback=callback,
            auto_ack=False,
        )

    def run(self):
        while True:
            try:
                self.channel.start_consuming()
            
            except AMQPChannelError as e:
                log.error(f"an error occurred on rabbit channel, {e}. retrying...")
            
            except UnrecoverableConnectionError:
                log.error("could not connect to rabbit, shutting down...")
                self.close_connection()
                break
            except KeyboardInterrupt as e:
                log.info(f"Manually stopping consumer...")
                self.close_connection()
                # sys.stdout.flush()
                break
            except Exception as e:
                log.error(f"Stopping Consumer, an unexpected error occurred [{e=}]")


