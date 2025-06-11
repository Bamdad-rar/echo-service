from task_scheduler.repository.in_memory import InMemoryTaskRepository
from task_scheduler.repository.database import DatabaseTaskRepository
from task_scheduler.repository.base import TaskRepository
from task_scheduler.schedulers.one_off import OneOff
from task_scheduler.schedulers.recurring import Recurring
from task_scheduler.schedulers.jalali import PersianRecurring
from pika.channel import Channel
import logging
import json
from pydantic import ValidationError
from datetime import datetime
from time import sleep
from typing import Literal
from uuid import uuid4
from task_scheduler.task import Task


log = logging.getLogger(__name__)

def create_task(scheduler_type: Literal['one-off', 'rrule', 'jrrule'], scheduler_value, callback_data: dict, extra_info: dict | None, repo: TaskRepository, calendar: Literal['gregorian', 'jalali']="gregorian", timezone: str = "Asia/Tehran"):
    match scheduler_type:
        case 'one-off':
            scheduler = OneOff(scheduler_value)
        case 'rrule':
            scheduler = Recurring(scheduler_value)
        case 'jrrule':
            scheduler = PersianRecurring(scheduler_value)
        case _:
            raise ValueError('No Scheudler found for scheduler value {scheduler_value}')
    new_task = Task(uuid4(), callback_data, scheduler, extra_info=extra_info) 
    new_task.schedule()
    repo.add(new_task)


def process_due_tasks(repo, callback):
    while True:
        tasks = repo.get_top_n_due_tasks()
        messages = []
        tasks_not_due = []
        for task in tasks:
            if task.is_due():
                messages.append(task.to_message())
                task.schedule()
                repo.update(task)
            else:
                tasks_not_due.append(task)
        if tasks_not_due:
            # not trying to solve problems we dont have, at least not yet.
            log.warning(f'some tasks were prematurely fetched {[str(t) for t in tasks_not_due]}')

        sleep(0.1)
    # create message from due tasks, especially from their payload and where they should be sent, their event id and timestamp are important too
    # schedule their next trigger time if they have any
    # call the callback function on the created messages
    # add the newly scheduled tasks to repo
    ...


def import_recurring_package_tasks(src_repo, dest_repo):
    # read all tasks from the repository
    # create Task Objects from them
    # schedule their next trigger time
    # add them to our repo.
    ...


def receive_message_callback(channel: Channel, method_frame, header_frame, body):
    try:
        # validation
        data = json.loads(body)
        # calculate next run
        # save to database

    except json.JSONDecodeError as e:
        log.warning(f"Could not decode the following data: {body}")
    except ValidationError as e:
        log.warning(f"Incompatible data received, {e}")
    except Exception as e:
        log.warning(f"Unexpected error: {e=}")
    finally:
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)
