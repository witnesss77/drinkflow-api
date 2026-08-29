from celery import Celery
from core.cfg import rabbitmq_url, redis_url
from core.models.database import AsyncSessionLocal
import asyncio
from core.orders.repository import OrdersRepository

celery = Celery("main", broker=rabbitmq_url, backend=redis_url)

async def process_order_(order_id):
    """считает общую статистику заказа: колво айтемов в заказе + общую цену"""
    async with AsyncSessionLocal() as db:
        repo = OrdersRepository(db)

        order_items = await repo.get_items(order_id)

        count = 0
        total_price = 0
        for item in order_items:
            count += item.quantity
            total_price += item.price_per_item * item.quantity

        return {
            "order_id": order_id,
            "item_count": count,
            "total_price": total_price
        }

@celery.task
def process_order(order_id):
    return asyncio.run(process_order_(order_id))


@celery.task
def user_registrated(email):
    ...