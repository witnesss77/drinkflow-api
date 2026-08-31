import aio_pika
from core.cfg import rabbitmq_url
from aio_pika.abc import AbstractChannel, AbstractQueue, AbstractExchange

NOTIFICATIONS_QUEUE = "notifications.order_created"
ORDER_EXCHANGE = "order"
ORDER_ROUTING_KEY = "order.*"

USER_ROUTING_KEY = "user.registered"
USER_EXCHANGE = "user"
USERS_QUEUE = "users.registered"

async def connect_rabbitmq():
    return await aio_pika.connect_robust(rabbitmq_url)

async def declare_exchange(channel: AbstractChannel, exchange):
    return await channel.declare_exchange(exchange, aio_pika.ExchangeType.TOPIC)

async def declare_queue(channel: AbstractChannel, exchange: AbstractExchange, queue_param, routing):
    queue: AbstractQueue = await channel.declare_queue(queue_param, durable=True)
    await queue.bind(exchange, routing_key=routing)

    return queue
