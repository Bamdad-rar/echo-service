from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ValidationError

__all__ = ["settings"]


class Settings(BaseSettings):
    """Settings are read from environment"""

    # RABBITMQ
    rabbitmq_username: str = "guest"
    rabbitmq_password: str = "guest"
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

    PG_DSN: str = "postgres://postgres:example@localhost:5432/postgres"
    RABBIT_URL: str = "amqp://guest:guest@localhost/"
    LOCK_BATCH: int = 500
    TICK_MS: int = 500

    POLL_DB_URL: str = "sqlite+pysqlite:///foo.db"
    POLL_DB_ECHO: bool = True

    #MISC
    PYDANTIC_ERRORS_INCLUDE_URL: int = 0


try:
    settings = Settings()
except ValidationError as e:
    print(f"Invalid Settings: {e}")
    raise
