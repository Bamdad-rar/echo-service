from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ValidationError

__all__ = ["settings"]


class Settings(BaseSettings):
    """Settings are read from environment"""
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
