# Scheduler Service

This service provides a resilient mechanism for scheduling recurring tasks based on events from a message broker. It consumes events, calculates the next execution time for a task, and persists it for a producer process to later pick up and execute.

## Key Features

*   **Event-Driven**: Reacts to messages from a RabbitMQ topic exchange.
*   **Persistent**: Stores scheduled tasks in a SQL database.
*   **Resilient**: Includes connection retry logic for the message broker.
*   **Configurable**: All key parameters are configurable via environment variables.
*   **Pluggable Scheduling**: Uses a strategy pattern to calculate next run times for different periods (seconds, minutes, days, etc.).

## Getting Started

To understand how the service works, start with the [Architecture Overview](architecture.md). To see how data moves through the system, read about the [Data Flow](flow.md).

For setup and execution, see the [Configuration](configuration.md) and [Deployment](deployment.md) guides.

