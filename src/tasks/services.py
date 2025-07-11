from adapters.message_broker import MessageBroker, message_broker
from scheduler.models import Task
from scheduler.dto import TaskEvent
from scheduler.repository import TaskRepo, UserRecurringPackageRepo
from pika.channel import Channel
from functools import partial
import logging
import json
from pydantic import ValidationError
from scheduler.strategies import get_calculation_strategy
from datetime import datetime


log = logging.getLogger(__name__)



class TaskScheduler:
    def message_broker_handler(
        self, channel: Channel, method_frame, header_frame, body, repo: TaskRepo
    ):
        try:
            # validation
            data = json.loads(body)
            task_event = TaskEvent(**data)

            # calculate next run
            next_run_time = get_calculation_strategy(task_event.period).calculate(
                task_event.start,
                task_event.repeat_for,
                task_event.repeated_for,
                task_event.unlimited,
            )

            task = Task(
                created_at=datetime.now(),
                updated_at=datetime.now(),
                next_run_time=next_run_time,
                **task_event,
            )

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

    def create_schedule(self,
                        start_timestamp: int,
                        repeat_for: int,
                        repeated_for: int,
                        unlimited: bool,
                        period: str,
                        data
                        ):
        """
            class RecurringPackage(BaseModel):
                action: Literal["order", "cancel", "update"]
                user_recurring_package_id: int
                recurring_package_id: int
                user_id: int


            class TaskEvent(BaseModel):
                event_id: int
                event_timestamp: int
                start: int
                repeat_for: int | None
                repeated_for: int = 0
                unlimited: bool
                period: Literal["seconds", "minutes", "hours", "days", "weeks", "months", "jmonths"]
                # extension can happen here
                data: RecurringPackage
        """
        

    def recreate_recurring_package_tasks(self, repo: UserRecurringPackageRepo):
        # get all tasks from a starting db, and sync them with the service db.
        rows = repo.get_all()
        for row in rows:
            print(row)
            # task = 

    def consume_events(self, message_broker: MessageBroker, repo: TaskRepo):
        consume_callback = partial(self._consume_callback, repo=repo)
        message_broker.register_callback(consume_callback)
        message_broker.run()

    def produce_events(self, message_broker: MessageBroker, repo: TaskRepo):
        while True:
            # select update lock
            ...
