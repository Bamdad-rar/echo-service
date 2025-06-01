from sqlalchemy import (
    Boolean,
    Table,
    Column,
    Integer,
    String,
    JSON,
    TIMESTAMP,
    MetaData,
    DateTime,
)
from sqlalchemy import create_engine
import logging
from config import settings

__all__ = ["task_table", "engine"]

SCHEDULER_DB_URL = settings.DB_URL
SCHEDULER_DB_URL_ECHO = settings.DB_ECHO

POLL_DB_URL = settings.POLL_DB_URL
POLL_DB_ECHO = settings.POLL_DB_ECHO

log = logging.getLogger(__name__)

metadata = MetaData()
poll_metadata = MetaData()

task_table = Table(
    "tasks",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("event_id", Integer, nullable=False),
    # timestamp of when the event was created on producer side
    Column("event_timestamp", TIMESTAMP, nullable=False),
    Column("start", TIMESTAMP, nullable=False),
    Column("repeat_for", Integer, nullable=True),
    Column("repeated_for", Integer, default=0),
    Column("unlimited", Boolean),
    Column("period", String),
    Column("data", JSON()),
    Column("created_at", DateTime),
    Column("updated_at", DateTime),
    Column("next_run_time", TIMESTAMP),
)

user_recurring_package_table = Table(
    "user_recurring_package",
    poll_metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_recurring_package_id", Integer),
    Column("user_id", Integer),
    Column("recurring_package_id", Integer),
    )

recurring_package_table = Table(
        "recurring_package",
        poll_metadata,
        Column("id",)
        )

try:
    engine = create_engine(DB_URL, echo=DB_URL_ECHO)
    metadata.create_all(engine)
except Exception as e:
    log.error(
        f"Something went wrong while connectin and creating tables on database, {e}"
    )
    raise

try:
    poll_engine = create_engine(POLL_DB_URL, echo=POLL_DB_ECHO)
except Exception as e:
    log.error(
        f"Something went wrong while connectin and creating tables on database, {e}"
    )
    raise
