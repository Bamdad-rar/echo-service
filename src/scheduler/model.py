from sqlalchemy import Boolean, Table, Column, Integer, String, JSON, TIMESTAMP, MetaData, DateTime
from sqlalchemy import create_engine
import logging

log = logging.getLogger(__name__)

metadata = MetaData()

__all__ = ["scheduled_events_table", "engine"]

scheduled_events_table = Table(
    "scheduled_events",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("event_id", Integer, nullable=False),
    Column("event_timestamp", Integer), # timestamp of when the event was created on producer side
    Column("action", String),
    Column("start", TIMESTAMP),
    Column("repeat_for", Integer, nullable=True),
    Column("repeated_for", Integer, default=0),
    Column("unlimited", Boolean),
    Column("period", String),
    Column("action_data", JSON()),
    Column("created_at", DateTime),
    Column("updated_at", DateTime),
    Column("next_run_time", TIMESTAMP),
)

try:
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)
    metadata.create_all(engine)
except Exception as e:
    log.error(f'Something went wrong while connectin and creating tables on database, {e}')
    raise
    

