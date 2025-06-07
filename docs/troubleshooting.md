# Troubleshooting

This page provides guidance on common issues and how to diagnose them.

## Logging

The service uses structured JSON logging, which is configured in `logs.py`.

*   **Output**: Logs are sent to standard output (`stdout`) and a rotating file handler at `app.log`.
*   **Format**: Each log entry is a JSON object containing a timestamp, level, module name, and message.
*   **Pika Logs**: Logging from the `pika` library is suppressed to `WARNING` level to reduce noise.

An example log entry:
```json
{
  "timestamp": "2023-10-27T10:30:00.123456Z",
  "level": "INFO",
  "module": "adapters.message_broker",
  "message": "Channel setup completed"
}
```

## Connection Failures

### RabbitMQ

The `RabbitMQ` adapter in `adapters.message_broker` has built-in connection retry logic.

*   **Behavior**: If the initial connection fails or is lost, the service will attempt to reconnect.
*   **Configuration**: The number of retries is controlled by `_reconnect_max_retries` within the class.
*   **Failure**: If all retries fail, an `errors.MaxRetriesReached` exception is raised, and the consumer will shut down gracefully after logging an error.

### Database

Database connection issues are typically fatal on startup.
*   **Behavior**: If the application cannot connect to the database when initializing the SQLAlchemy engine in `adapters.database`, an exception will be raised, and the service will terminate.
*   **Diagnosis**: Check the application logs for SQLAlchemy connection errors and verify your `DB_URL` and network connectivity.

## Message Processing Errors

The `_consume_callback` in `scheduler.services` is designed to handle bad messages gracefully.

*   **Invalid JSON**: If a message body is not valid JSON, a `json.JSONDecodeError` is caught.
*   **Schema Mismatch**: If a message's structure doesn't match the `scheduler.dto.TaskEvent` schema, a `pydantic.ValidationError` is caught.

!!! info "Dead Letter Queues"
    In both cases, an error is logged, and the message is **acknowledged** to prevent it from being re-delivered infinitely. For more robust error handling, a Dead Letter Exchange (DLX) could be configured in RabbitMQ to route failed messages for later inspection.
