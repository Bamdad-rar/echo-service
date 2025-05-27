from messages import SchedulingEvent
from sqlalchemy import Engine, Table, insert
from time import time
import logging

log = logging.getLogger(__name__)

class Scheduler:
    def __init__(self, db: Engine, table: Table):
        self.db = db
        self.table = table

    def add_event(self, event: SchedulingEvent):
        log.info(f'adding event {event}')
        stmt = insert(self.table).values(
                event_id=event.event_id,
                event_timestamp=event.event_timestamp,
                action=event.action,
                start=event.start,
                repeat_for=event.repeat_for,
                repeated_for=event.repeated_for,
                unlimited=event.unlimited,
                period=event.period,
                action_data=event.action_data,
                next_run_time=time()
                )
        with self.db.connect() as conn:
            conn.execute(stmt)
            conn.commit()

    def update_event(self, event):
        log.info(f'updating event')
        ...

    def pause_event(self, event):
        log.info('pausing event')
        ...

    def cancel_event(self, event):

        log.info('canceling event')
        ...

    def get_top_due_events(self, top_n: int):
        log.info(f'getting top {top_n} events')
        ...
