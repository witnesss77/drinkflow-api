from celery import Celery
from core.cfg import rabbitmq_url, redis_url
from core.models.database import CelerySessionLocal
import asyncio
from core.orders.repository import OrdersRepository

celery = Celery("main", broker=rabbitmq_url, backend=redis_url)

#сделать пересчет или пофиксить то что селери ложится




async def process_order_(order_id):
    """считает общую статистику заказа: колво айтемов в заказе + общую цену"""
    async with CelerySessionLocal() as db:
        repo = OrdersRepository(db)

        order_items = await repo.get_items(order_id)

        count = 0
        total_price = 0
        for item in order_items:
            count += item.quantity
            total_price += item.price_per_item * item.quantity
            await db.refresh(item)
            await db.commit()

        return {
            "order_id": order_id,
            "item_count": count,
            "total_price": total_price
        }

async def changed_order(order_id, price_delta, quantity_delta):
    """при изменении/удалении ордер айтема меняет общую статистику заказа"""
    async with CelerySessionLocal() as db:
        repo = OrdersRepository(db)
    
        order = await repo.get_order_by_id(order_id)

    
        order.item_count += quantity_delta
        order.total_price += price_delta

        await db.refresh(order)
        await db.commit()

        return {
            "order_id": order_id,
            "item_count": order.item_count,
            "total_price": order.total_price
        }

async def deleted_item(order_id, quantity, price_per_item):
    async with CelerySessionLocal() as db:
        repo = OrdersRepository(db)
        
        order = await repo.get_order_by_id(order_id)
    
        
        order.item_count -= quantity
        order.total_price -= quantity * price_per_item
    
        await db.commit()
    
        return {
            "order_id": order_id,
            "item_count": order.item_count,
            "total_price": order.total_price
        }

    
@celery.task
def process_order(order_id):
    return asyncio.run(process_order_(order_id))

@celery.task
def update_order(order_id, price_delta, quantity_delta):
    return asyncio.run(changed_order(order_id, price_delta, quantity_delta))

@celery.task
def delete_item_from_order(order_id, quantity, price_per_item):
    return asyncio.run(deleted_item(order_id,quantity,price_per_item))
