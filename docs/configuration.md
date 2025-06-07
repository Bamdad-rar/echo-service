# Configuration

The application is configured using environment variables. All settings are defined and validated in the `config.py` module using `pydantic-settings`.

!!! tip "Development Environment"
    For local development, you can create a `.env` file in the project root, and `pydantic-settings` will automatically load variables from it.

## RabbitMQ

These variables control the connection and behavior of the RabbitMQ consumer.

*   `RABBITMQ_USERNAME`: Username for RabbitMQ. Default: `admin`.
*   `RABBITMQ_PASSWORD`: Password for RabbitMQ. Default: `1234`.
*   `RABBITMQ_HOST`: Hostname or IP address of the RabbitMQ server. Default: `localhost`.
*   `RABBITMQ_PORT`: Port for the RabbitMQ server. Default: `5672`.
*   `RABBITMQ_EXCHANGE`: The topic exchange to bind to. Default: `task.scheduling.exchange`.
*   `RABBITMQ_SCHEDULER_QUEUE_NAME`: The queue for incoming schedule events. Default: `scheduler-queue`.
*   `RABBITMQ_SCHEDULER_ROUTING_KEY`: The routing key pattern for schedule events. Default: `task.schedule.*`.
*   `RABBITMQ_PREFETCH_COUNT`: The number of messages the consumer can fetch at once. Default: `1`.
*   `RABBITMQ_RETRY_ON_CONNECTION_FAILURE`: Whether to enable connection retries. Default: `True`.

## Database

These variables configure the connections to the service's primary database and the polling database.

*   `DB_URL`: SQLAlchemy connection string for the main task database. Default: `sqlite+pysqlite:///foo.db`.
*   `DB_ECHO`: If `True`, SQLAlchemy will log all generated SQL. Default: `True`.
*   `POLL_DB_URL`: SQLAlchemy connection string for the database being polled for recurring packages. Default: `sqlite+pysqlite:///foo.db`.
*   `POLL_DB_ECHO`: If `True`, logs SQL for the polling database connection. Default: `True`.

For a complete list of settings and their types, please refer to the `Settings` class in the [config module](reference.md#config.Settings).

