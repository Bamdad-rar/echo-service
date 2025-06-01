from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ValidationError

__all__ = ["settings"]


class Settings(BaseSettings):
    """Settings are read from environment"""

    # RABBITMQ
    rabbitmq_username: str = "admin"
    rabbitmq_password: str = "1234"
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_exchange_type: str = "topic"
    rabbitmq_scheduler_queue_name: str = "scheduler-queue"
    rabbitmq_reminder_queue_name: str = "reminder-queue"
    rabbitmq_exchange: str = "task.scheduling.exchange"
    rabbitmq_scheduler_routing_key: str = "task.schedule.*"
    rabbitmq_reminder_routing_key: str = "task.reminder.*"
    rabbitmq_retry_on_connection_failure: bool = True
    rabbitmq_prefetch_count: int = 1

    # DATABASE
    DB_URL: str = "sqlite+pysqlite:///foo.db"
    DB_ECHO: bool = True

    POLL_DB_URL: str = "sqlite+pysqlite:///foo.db"
    POLL_DB_ECHO: bool = True


try:
    settings = Settings()
except ValidationError as e:
    print(f"Invalid Settings: {e}")
    raise
