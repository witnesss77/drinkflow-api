from celery import Celery
from cache.cache import RedisCache
from core.cfg import rabbitmq_url, redis_url, cache_ttl_seconds, order_cache_key
from core.models.database import CelerySessionLocal
import asyncio
from core.orders.repository import OrdersRepository

celery = Celery("main", broker=rabbitmq_url, backend=redis_url)


async def process_order_(order_id):
    """считает общую статистику заказа: колво айтемов в заказе + общую цену"""
    async with CelerySessionLocal() as db:
        repo = OrdersRepository(db)

        order = await repo.get_order_by_id(order_id)

        price = 0
        count = 0

        for item in order.items:
            price += item.price_per_item * item.quantity
            count += item.quantity

        order.total_price = price
        order.item_count = count

        await db.commit()
        redis = RedisCache(redis_url, cache_ttl_seconds)
        await redis.delete_by_pattern(f"{order_cache_key}:*")

@celery.task
def process_order(order_id):
    return asyncio.run(process_order_(order_id))

