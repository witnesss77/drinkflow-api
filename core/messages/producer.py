import aio_pika
from aio_pika.abc import AbstractExchange
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
            routing_key="order.created",
            data = event_data)

    async def changed_order_quantity(self, order_id, quantity_delta):
        event_data = {
            "event": "order.changed_quantity",
            "order_id": order_id,
            "quantity_delta": quantity_delta
        }
                
        await publish_json(
            exchange=self.exchange, 
            routing_key="order.changed_quantity",
            data = event_data)

    async def add_order_items(self, order_id):
        event_data = {
            "event": "order.added_items",
            "order_id": order_id,
        }
        await publish_json(
            exchange=self.exchange, 
            routing_key="order.added_items",
            data = event_data)

    async def deleted_order_item(self, order_id, quantity, price_per_item):
        event_data = {
            "event": "order.deleted_item",
            "order_id": order_id,
            "quantity": quantity, 
            "price_per_item": price_per_item
        }

        await publish_json(
            exchange=self.exchange, 
            routing_key="order.deleted_item",
            data = event_data)
