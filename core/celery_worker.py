from celery import Celery
from core.cfg import rabbitmq_url, redis_url
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











































# async def changed_order(order_id, price_delta, quantity_delta):
#     """при изменении/удалении ордер айтема меняет общую статистику заказа"""
#     async with CelerySessionLocal() as db:
#         repo = OrdersRepository(db)
    
#         order = await repo.get_order_by_id(order_id)

    
#         order.item_count += quantity_delta
#         order.total_price += price_delta

#         await db.commit()
#         await db.refresh(order)

#         return {
#             "order_id": order_id,
#             "item_count": order.item_count,
#             "total_price": order.total_price
#         }

# async def deleted_item(order_id, quantity, price_per_item):
#     async with CelerySessionLocal() as db:
#         repo = OrdersRepository(db)
        
#         order = await repo.get_order_by_id(order_id)
    
        
#         order.item_count -= quantity
#         order.total_price -= quantity * price_per_item
    
#         await db.commit()
    
#         return {
#             "order_id": order_id,
#             "item_count": order.item_count,
#             "total_price": order.total_price
#         }

    
@celery.task
def process_order(order_id):
    return asyncio.run(process_order_(order_id))

