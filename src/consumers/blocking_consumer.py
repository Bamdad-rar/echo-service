import pika
import sqlalchemy
import json
import time
from pika.channel import Channel
from pika.exceptions import AMQPChannelError, AMQPConnectionError
import logging

from pydantic import ValidationError
from messages import SchedulingEvent
from errors import UnrecoverableConnectionError
from config import settings
from database import engine as db
from database import scheduled_events_table
from sqlalchemy import insert



log = logging.getLogger(__name__)

PREFETCH_COUNT = settings.rabbitmq_prefetch_count
RETRY_ON_CONNECTION_FAILURE = settings.rabbitmq_retry_on_connection_failure
RABBITMQ_EXCHANGE_TYPE = settings.rabbitmq_exchange_type
RABBITMQ_EXCHANGE = settings.rabbitmq_exchange
RABBITMQ_SCHEDULER_ROUTING_KEY = settings.rabbitmq_scheduler_routing_key
RABBITMQ_SCHEDULER_QUEUE_NAME = settings.rabbitmq_scheduler_queue_name


class BlockingConsumer:
    def __init__(
            self, amqp_username: str, amqp_password: str, amqp_host: str, amqp_port: int, amqp_heartbeat: int = 600
    ):
        self.connection = None
        self.channel = None
        self.connection_params = pika.ConnectionParameters(
            heartbeat=amqp_heartbeat,
            host=amqp_host,
            port=amqp_port,
            credentials=pika.PlainCredentials(amqp_username, amqp_password),
        )
        self.prefetch_count = PREFETCH_COUNT
        self.should_reconnect = RETRY_ON_CONNECTION_FAILURE 

    def get_connection(self):
        if self.connection is None or self.connection.is_closed:
            self._reconnect_with_backoff()
        return self.connection
    
    def _reconnect_with_backoff(self):
        base_delay = 1
        for attempts in range(5):
            try:
                self.connection = pika.BlockingConnection(
                        parameters=self.connection_params
                        )
                return
            except AMQPConnectionError as e:
                log.warning(f'could not get connection to rabbitmq: {e}, retrying in {(base_delay+attempts)*5}...')
                time.sleep((base_delay+attempts)*5)
        raise UnrecoverableConnectionError()

    def setup_channel(self):
        self.channel = self.get_connection().channel()
        self.channel.basic_qos(prefetch_count=PREFETCH_COUNT)
        
        self.channel.exchange_declare(
            exchange=RABBITMQ_EXCHANGE,
            exchange_type=RABBITMQ_EXCHANGE_TYPE,
        )
        self.channel.queue_declare(
            queue=RABBITMQ_SCHEDULER_QUEUE_NAME,
            durable=True
        )
        self.channel.queue_bind(
            exchange=RABBITMQ_EXCHANGE,
            queue=RABBITMQ_SCHEDULER_QUEUE_NAME,
            routing_key=RABBITMQ_SCHEDULER_ROUTING_KEY
        )
        self.channel.basic_consume(
        queue=RABBITMQ_SCHEDULER_QUEUE_NAME,
        on_message_callback=self.consume_callback,
        auto_ack=False
        )
        log.info("Channel setup completed")
            

    def close_connection(self):
        """Safely close connection if it exists"""
        try:
            if self.connection and self.connection.is_open:
                self.connection.close()
        except Exception as e:
            log.error(f"Error closing connection: {e}")

    def consume_callback(self, channel: Channel, method_frame, header_frame, body):
        log.info(f"{body=}")
        try:
            # validation
            data = json.loads(body)
            scheduling_event = SchedulingEvent(**data)

            # save to db
            stmt = insert(scheduled_events_table).values(**data)
            log.debug(f'statement | {stmt}')
            with db.connect() as conn:
                conn.execute(stmt)
                conn.commit()


        except json.JSONDecodeError as e:
            log.warning(f'Could not decode the following data: {body}')

            # TODO put in dead letter queue
        except ValidationError as e:
            log.warning(f'Incompatible data recieved, {e}')
            # TODO put in dead letter queue
        except Exception as e:
            log.warning(f'Unexpected error: {e=}')
            # TODO put in dead letter queue
        finally:
            self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    def run(self):
        while True:
            try:
                self.get_connection()
                self.setup_channel()
                self.channel.start_consuming()
            except UnrecoverableConnectionError:
                log.error('could not connect to rabbit, shutting down...')
                self.close_connection()
                break
            except AMQPChannelError as e:
                log.error(f'an error occurred on rabbit channel, {e}. retrying...')
            except KeyboardInterrupt as e:
                log.info(f"Manually stopping consumer...")
                self.close_connection()
                # sys.stdout.flush()
                break
            except Exception as e:
                log.info(f"Stopping Consumer, an unexpected error occurred [{e=}]")
 
