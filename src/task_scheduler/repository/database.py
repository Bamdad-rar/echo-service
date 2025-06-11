from sqlalchemy import Table, Column, Integer, String, DateTime, JSON, Enum, ForeignKey, MetaData
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from uuid import uuid4

metadata = MetaData()


tasks = Table('tasks', metadata, 
    Column('id', UUID(as_uuid=True), primary_key=True, default=uuid4),
    Column('callback_data', JSON, nullable=False),
    Column('scheduler', JSON, nullable=False),  # Assuming a 'schedulers' table
    Column('created_at', DateTime, default=datetime.now, nullable=False),
    Column('status', String, nullable=False),
    Column('retry_count', Integer, default=0, nullable=False),
    Column('next_trigger', DateTime, nullable=True),
    Column('last_trigger', DateTime, nullable=True),
    Column('extra_info', JSON, nullable=True)
)


