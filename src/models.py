from sqlalchemy import Table, Column, Integer, String, JSON, DateTime, MetaData

metadata = MetaData()


scheduled_events_table = Table(
    "scheduled_events",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("times_to_run", Integer, nullable=True),
    Column("times_ran", Integer, nullable=True),
    Column("created_at", DateTime),
    Column("updated_at", DateTime),
    Column("next_run_time", DateTime),
    Column("last_run_time", DateTime),
    Column("event_id", Integer, nullable=False),
    Column("event_method", String(255)),
    Column("event_payload", JSON()),
)


