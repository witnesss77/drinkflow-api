import aio_pika
from aio_pika.abc import AbstractExchange
from core.messages.rabbitmq import ORDER_ROUTING_KEY, USER_ROUTING_KEY
import json


async def publish_json(exchange: AbstractExchange, routing_key: str, data: dict):
    message = aio_pika.Message(json.dumps(data).encode())
    await exchange.publish(message, routing_key)

class OrderProducer:
    def __init__(self, exchange):
        self.exchange = exchange

    async def created_order(self, order_id):
        event_data = {
            "event": "order.created",
            "order_id": order_id
        }
        
        await publish_json(
            exchange=self.exchange, 
            routing_key=ORDER_ROUTING_KEY,
            data = event_data)

class UserProducer:
    def __init__(self, exchange):
        self.exchange = exchange

    async def created_user(self, user_mail):
        event_data = {
            "event": "user.registered",
            "email": user_mail
        }

        await publish_json(
            exchange=self.exchange,
            routing_key=USER_ROUTING_KEY,
            data = event_data
        )
        