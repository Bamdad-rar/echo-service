import logging.config
from datetime import datetime, UTC
import json


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "module": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


def setup_logging():
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"json": {"()": JSONFormatter}},
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "json",
                "stream": "ext://sys.stdout",
            },
            "app": {
                "level": "DEBUG",
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "json",
                "filename": "app.log",
                "maxBytes": 1024 * 1024 * 10,
                "backupCount": 10,
            },
        },
        "root": {"level": "DEBUG", "handlers": ["console"]},
    }
    logging.config.dictConfig(config)
    logging.getLogger("pika").setLevel(logging.WARNING)

