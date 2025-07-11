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
    Column("callback_data", JSON(), nullable=False),
    Column("schedule", String, nullable=False),
    Column("next_run", TIMESTAMP, nullable=False),
    Column("last_run", Integer, nullable=True),
    Column("created_at", Integer, default=0),
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
    engine = create_engine(SCHEDULER_DB_URL, echo=SCHEDULER_DB_URL_ECHO)
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
