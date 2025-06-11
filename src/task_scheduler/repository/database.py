from sqlalchemy import Table, Column, Integer, String, DateTime, JSON, ForeignKey, MetaData
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from uuid import uuid4

metadata = MetaData()


tasks = Table('tasks', metadata, 
    Column('id', UUID(as_uuid=True), primary_key=True, default=uuid4),
    Column('callback_data', JSON, nullable=False),
    Column('scheduler_type', String, nullable=False),
    Column('scheduler', JSON, nullable=False),
    Column('created_at', DateTime, default=datetime.now, nullable=False),
    Column('status', String, nullable=False),
    Column('retry_count', Integer, default=0, nullable=False),
    Column('next_trigger', DateTime, nullable=True),
    Column('last_trigger', DateTime, nullable=True),
    Column('extra_info', JSON, nullable=True)
)


