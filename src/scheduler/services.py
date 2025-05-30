from adapters.message_broker import MessageBroker, message_broker
from models import Task
from dto import TaskEvent
from repository import TaskRepo
from pika.channel import Channel
from functools import partial
import logging
import json
from pydantic import ValidationError

log = logging.getLogger(__name__)

class TaskScheduler:
    def _consume_callback(self, channel: Channel, method_frame, header_frame, body, repo: TaskRepo):
        try:
            # validation
            data = json.loads(body)
            task_event = TaskEvent(**data)

            # calculate next run
            task = Task()
            # save to database
            repo.add(task)

        except json.JSONDecodeError as e:
            log.warning(f"Could not decode the following data: {body}")
        except ValidationError as e:
            log.warning(f"Incompatible data received, {e}")
        except Exception as e:
            log.warning(f"Unexpected error: {e=}")
        finally:
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    def recreate_tasks(self, ):
        ...

    def consume_events(self, message_broker: MessageBroker, repo: TaskRepo):
        consume_callback = partial(self._consume_callback, repo=repo)
        message_broker.register_callback(consume_callback)
        message_broker.run()

    def produce_events(self, message_broker: MessageBroker, repo: TaskRepo):
        while True:
            # select update lock
            ...

