# Configuration Reference

Everything in the scheduler stack can be driven by **environment variables** so that
Docker Compose, Kubernetes, and plain `docker run` all work the same way.  
This page lists every tunable knob, its default, and why (or why not) you might
change it.

---

## 1 Core Settings

| Variable | Applies to | Default | Description |
|----------|-----------|---------|-------------|
| **`PG_DSN`** | *consumer*, *producer* | `postgres://postgres:example@postgres:5432/postgres` | Standard Postgres DSN. Set `sslmode=require` for cloud DBs. |
| **`RABBIT_URL`** | *consumer*, *producer* | `amqp://guest:guest@rabbitmq:5672/` | Full AMQP URI including vhost. |
| **`CMD_EXCHANGE`** | all | `schedule.commands` | Topic exchange for ScheduleRequest / Cancel. Change only if you have naming conventions. |
| **`EVT_EXCHANGE`** | all | `schedule.events` | Topic exchange for ScheduleDue events. |
| **`CMD_QUEUE`** | consumer | `scheduler_inbox` | The queue the consumer listens on. |
| **`DUE_QUEUE`** | main app | `mainapp_due` | Where your monolith consumes ScheduleDue. |

---

## 2 Producer Tuning

| Variable | Default | Effect |
|----------|---------|--------|
| **`LOCK_BATCH`** | `500` | Max rows selected per `SELECT … SKIP LOCKED`. Increase for fewer DB round-trips; decrease for lower per-batch latency. |
| **`TICK_MS`** | `500` ms | Sleep duration when no due rows. Lower → faster wake-ups, more idle queries. |
| **`METRICS_PORT`** | `8000` | Port that exposes Prometheus `/metrics`. |
| **`RETRY_BACKOFF_MS`** | *(unset)* | Optional fixed back-off before resending duplicates. Leave unset for immediate retry behaviour. |

**Rule of thumb**

```mermaid
flowchart LR
    A[Low latency needs<br/>(< 200 ms)] -->|lower| B[TICK_MS&nbsp;= 100]
    A2[Heavy DB traffic<br/>(> 1 k&nbsp;TPS)] -->|higher| C[LOCK_BATCH ≥ 1000]
    style A fill:#eef
    style A2 fill:#eef
````

---

## 3 Consumer Tuning

| Variable           | Default | Effect                                                                                                            |
| ------------------ | ------- | ----------------------------------------------------------------------------------------------------------------- |
| **`PREFETCH`**     | `256`   | RabbitMQ `basic_qos` prefetch for the command queue. Raise for higher insert throughput; lower to control memory. |
| **`METRICS_PORT`** | `8000`  | Prometheus endpoint (use a different port than producer if co-located).                                           |

---

## 4 RabbitMQ Options

All shipped from the official `rabbitmq:management` image.

| Environment variable                             | Why change                                                                 |
| ------------------------------------------------ | -------------------------------------------------------------------------- |
| `RABBITMQ_DEFAULT_USER`, `RABBITMQ_DEFAULT_PASS` | Use strong, non-guest credentials in production.                           |
| `RABBITMQ_SERVER_ADDITIONAL_ERL_ARGS`            | E.g., `'+S 4:4'` to pin Erlang schedulers to 4 cores.                      |
| `RABBITMQ_VM_MEMORY_HIGH_WATERMARK`              | Lower it (e.g., `0.4`) to start flow-control sooner under memory pressure. |

**Plugins enabled by default**

* `rabbitmq_management` – Web UI & HTTP API
* `rabbitmq_prometheus` – Prometheus `/metrics` on port 15692

---

## 5 Postgres Pool

`repo.py` uses `asyncpg.create_pool(min_size, max_size)`.

| Variable      | Default | Applies to    |
| ------------- | ------- | ------------- |
| `PG_MIN_SIZE` | `2`     | both services |
| `PG_MAX_SIZE` | `10`    | both services |

Adjust for high concurrency: rule of thumb = (# producer replicas × 2) + 2.

---

## 6 Observability

| Service    | Variable                     | Default                     | Purpose                                                   |
| ---------- | ---------------------------- | --------------------------- | --------------------------------------------------------- |
| Prometheus | `SCRAPE_INTERVAL`            | `15s` (in `prometheus.yml`) | Faster scrape for near-real-time charts, but higher load. |
| Grafana    | `GF_SECURITY_ADMIN_PASSWORD` | `admin`                     | Set a strong admin password before exposing Grafana.      |
|            | `GF_SERVER_ROOT_URL`         | *(unset)*                   | Needed if Grafana is served behind a reverse proxy.       |

### Sample local `prometheus.yml`

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: scheduler
    static_configs:
      - targets: ["consumer:8000", "producer:8000"]

  - job_name: rabbitmq
    static_configs:
      - targets: ["rabbitmq:15692"]
```

---

## 7 Example `.env` for Compose

```dotenv
### Database
PG_DSN=postgres://postgres:example@postgres:5432/postgres
PG_MIN_SIZE=2
PG_MAX_SIZE=10

### RabbitMQ
RABBIT_URL=amqp://guest:guest@rabbitmq:5672/
CMD_EXCHANGE=schedule.commands
EVT_EXCHANGE=schedule.events

### Producer knobs
LOCK_BATCH=500
TICK_MS=500

### Metrics
METRICS_PORT=8000
```

Load it automatically:

```bash
docker compose --env-file .env up -d
```

---

## 8 Runtime Overrides (Kubernetes)

Use a `ConfigMap` + `Secret` pattern:

```yaml
kind: Secret
metadata: { name: scheduler-cred }
type: Opaque
stringData:
  PG_DSN: postgres://user:${PASSWORD}@postgres:5432/scheduler

kind: ConfigMap
metadata: { name: scheduler-cfg }
data:
  LOCK_BATCH: "1000"
  TICK_MS:    "200"

# Deployment snippet
envFrom:
  - secretRef: { name: scheduler-cred }
  - configMapRef: { name: scheduler-cfg }
```

---

### Cheatsheet

* **Lower latency** → `TICK_MS ↓`
* **Higher throughput** → `LOCK_BATCH ↑`, `PREFETCH ↑`
* **Memory guard** → `RABBITMQ_VM_MEMORY_HIGH_WATERMARK ↓`, `PREFETCH ↓`

Tweak, measure in Grafana, repeat. 🪄

```
