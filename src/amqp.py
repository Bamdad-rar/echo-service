import json
import asyncio
from contextlib import asynccontextmanager
from aio_pika import connect_robust, Message, ExchangeType

class AMQPConfig:
    def __init__(self, url: str):
        self.url = url
        # exchange/queue names centralised here
        self.cmd_ex   = "schedule.commands"
        self.evt_ex   = "schedule.events"
        self.cmd_q    = "schedule_inbox"
        self.due_q    = "schedule_due"

# ──────────────────────────────────────────────────────────────
@asynccontextmanager
async def open_connection(cfg: AMQPConfig):
    """Yields a robust connection that auto-reconnects."""
    conn = await connect_robust(cfg.url)
    try:
        yield conn
    finally:
        await conn.close()

async def declare_topology(conn, cfg: AMQPConfig):
    """Idempotent exchange/queue declarations (run at startup)."""
    ch = await conn.channel()

    # normal exchanges
    cmd_ex = await ch.declare_exchange(cfg.cmd_ex, ExchangeType.TOPIC, durable=True)
    evt_ex = await ch.declare_exchange(cfg.evt_ex, ExchangeType.TOPIC, durable=True)

    # dead-letter exchange / queue
    dlx = await ch.declare_exchange("schedule.dlq", ExchangeType.FANOUT, durable=True)
    dlq  = await ch.declare_queue("schedule_dead", durable=True)
    await dlq.bind(dlx, routing_key="#")

    # inbox queue that dead-letters into the DLX
    inbox = await ch.declare_queue(cfg.cmd_q, durable=True, arguments={"x-dead-letter-exchange": "schedule.dlq"})

    await inbox.bind(cmd_ex, routing_key="request")
    await inbox.bind(cmd_ex, routing_key="cancel")
    
    # schedule due queue
    due   = await ch.declare_queue(cfg.due_q,  durable=True)
    await due.bind(evt_ex,   routing_key="due")

    await ch.close()

# ──────────────────────────────────────────────────────────────
class JSONPublisher:
    """Lightweight JSON publisher with confirms enabled."""
    def __init__(self, channel, exchange_name: str):
        self._ch    = channel
        self._ex    = None
        self._name  = exchange_name

    async def init(self):
        self._ex = await self._ch.declare_exchange(
            self._name, ExchangeType.TOPIC, durable=True)
        await self._ch.set_qos(prefetch_count=0)      # publisher, no need to limit

    async def publish(self, rk: str, payload: dict):
        body = json.dumps(payload).encode()
        msg = Message(body, content_type="application/json", delivery_mode=2)
        await self._ex.publish(msg, routing_key=rk)   # confirm-mode default in aio-pika

# ──────────────────────────────────────────────────────────────
async def start_consumer(ch, queue_name: str, handler, *, prefetch: int = 100):
    """Subscribe to a queue; handler(message, payload) coroutine must ack/nack."""
    await ch.set_qos(prefetch_count=prefetch)
    queue = await ch.declare_queue(queue_name, passive=True)
    async with queue.iterator() as q:
        async for message in q:
            async with message.process(requeue=True):
                payload = json.loads(message.body)
                await handler(message, payload)
