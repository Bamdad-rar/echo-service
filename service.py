from models import metadata as scheduled_events_metadata
from sqlalchemy import create_engine
import pika
from pika.channel import Channel


DB_URL = 'sqlite:///:memory:'
DB_CONNECTION_POOL_SIZE=20

RABBITMQ_HOST="localhost"
RABBITMQ_PORT=5672
RABBITMQ_EXCHANGE_TYPE='topic'
RABBITMQ_INBOUND_QUEUE_NAME='scheduler-main-queue'
RABBITMQ_OUTBOUND_QUEUE_NAME='reminder-main-queue'
RABBITMQ_EXCHANGE = 'task.scheduling.exchange'
RABBITMQ_INBOUND_ROUTING_KEY='task.schedule.*'
RABBITMQ_OUTBOUND_ROUTING_KEY='task.reminder.*'

"""db setup"""
engine = create_engine(DB_URL, pool_size=DB_CONNECTION_POOL_SIZE)
scheduled_events_metadata.create_all(engine, checkfirst=True)

"""rabbit setup"""
connectiion_credentials = pika.PlainCredentials(username='admin', password='1234')
connection_params = pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=connectiion_credentials)
connection = pika.BlockingConnection(connection_params)
channel_inbound = connection.channel()
channel_outbound = connection.channel()

# declare exchange
channel_inbound.exchange_declare(exchange=RABBITMQ_EXCHANGE, exchange_type=RABBITMQ_EXCHANGE_TYPE)
channel_outbound.exchange_declare(exchange=RABBITMQ_EXCHANGE, exchange_type=RABBITMQ_EXCHANGE_TYPE)

# declare queues
channel_inbound.queue_declare(queue=RABBITMQ_INBOUND_QUEUE_NAME, durable=True)
channel_outbound.queue_declare(queue=RABBITMQ_OUTBOUND_QUEUE_NAME, durable=True)

# declare bindings
# telling rabbit how to route messages from exchange to queues.
channel_inbound.queue_bind(exchange=RABBITMQ_EXCHANGE, queue=RABBITMQ_INBOUND_QUEUE_NAME, routing_key=RABBITMQ_INBOUND_ROUTING_KEY)
channel_outbound.queue_bind(exchange=RABBITMQ_EXCHANGE, queue=RABBITMQ_OUTBOUND_QUEUE_NAME, routing_key=RABBITMQ_OUTBOUND_ROUTING_KEY)

class TaskRouting:
    CREATE = "task.schedule.create"
    UPDATE = "task.schedule.update"
    REMINDER = "task.reminder.trigger"

# basic consumation declaring
# telling our application what to do when a message is recieved.
def consume_scheduling_message(channel: Channel, method_frame, header_frame, body):
    print(f'{channel=}')
    print(f'{method_frame.delivery_tag=}')
    print(f'{header_frame=}')
    print(f'{body=}')
    channel.basic_ack(delivery_tag=method_frame.delivery_tag)

channel_inbound.basic_consume(RABBITMQ_INBOUND_QUEUE_NAME, consume_scheduling_message)


if __name__ == "__main__":
    try:
        channel_inbound.start_consuming()
    except KeyboardInterrupt as e:
        print(f'stopping because user stopped me [{e=}]')
        channel_inbound.stop_consuming()
    except Exception as e:
        print(f'unexpected stop because [{e=}]')
        channel_inbound.stop_consuming()
    finally:
        connection.close()



