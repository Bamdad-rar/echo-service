# Deployment & Running

This guide covers how to run the service components.

## Prerequisites

Before running the service, ensure you have:
1.  Installed all Python dependencies (e.g., from a `requirements.txt` file).
2.  A running RabbitMQ instance.
3.  A running SQL database instance.
4.  Configured all necessary environment variables as described in [Configuration](configuration.md).

## Running the Consumer

The consumer is the primary process for the Scheduler Service. It connects to RabbitMQ and listens for incoming task events.

To start the consumer, run the `consumer.py` script:
```bash
python consumer.py
```
This script initializes the database tables (if they don't exist), sets up the RabbitMQ connection, and starts the consuming loop via `message_broker.run()`.

## Running the Producer

The `producer.py` entrypoint is intended to query the database for due tasks and publish them for execution. Its implementation is currently a placeholder.

To run the producer process:
```bash
python producer.py
```

## Seeding Test Data

A helper script, `client.py`, is provided to publish sample messages to RabbitMQ for testing purposes. This can be used to simulate upstream services that create scheduling events.

```bash
python client.py
```
This will send 100 sample messages to the `task.schedule.create` routing key.

## Database Schema

The database tables required by the service are defined in `adapters.database`. They are created automatically by SQLAlchemy's `metadata.create_all(engine)` call when the application starts, so no manual schema migration is needed for initial setup.
