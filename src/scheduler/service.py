from scheduler.repository import TaskRepo
from pika.channel import Channel
import logging
import json
from pydantic import ValidationError
from datetime import datetime
from time import sleep

log = logging.getLogger(__name__)

def create_task(repo):
    # create a task with the provided paramters
    # schedule next trigger time
    # add them to repo
    ...


def import_tasks(src_repo, dest_repo):
    # read all tasks from the repository
    # create Task Objects from them
    # schedule their next trigger time
    # add them to our repo.
    ...


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
