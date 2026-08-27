import aio_pika
from core.cfg import rabbitmq_url
from aio_pika.abc import AbstractChannel, AbstractQueue, AbstractExchange

NOTIFICATIONS_QUEUE = "notifications.order_created"
ORDER_EXCHANGE = "order"
ORDER_ROUTING_KEY = "order.created"



async def connect_rabbitmq():
    return await aio_pika.connect_robust(rabbitmq_url)

async def declare_exchange(channel: AbstractChannel):
    return await channel.declare_exchange(ORDER_EXCHANGE)

async def declare_queue(channel: AbstractChannel, exchange: AbstractExchange):
    queue: AbstractQueue = await channel.declare_queue(NOTIFICATIONS_QUEUE, durable=True)
    await queue.bind(exchange, routing_key=ORDER_ROUTING_KEY)

    return queue
