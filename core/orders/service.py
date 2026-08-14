from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from core.models.schemas import OrderSchema
from core.models.models import User, Stock, Order, OrderItem
from fastapi import HTTPException
from core.orders.repository import OrdersRepository
from cache.cache import RedisCache



class OrderLogicService:
    async def add_order_item(request, warehouse_id: int, db):
        query = select(User).options(selectinload(User.orders)).where(User.id == request.user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        query = select(Order).where(Order.id == request.order_id, Order.user_id == request.user_id)
        result = await db.execute(query)
        order = result.scalar_one_or_none()

        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")

        stock_query = select(Stock).where(
            Stock.warehouse_id == warehouse_id,
            Stock.drink_id == request.drink_id
        ).with_for_update()

        result = await db.execute(stock_query)
        stock = result.scalar_one_or_none()

        if stock is None:
            raise HTTPException(status_code=404, detail="Stock not found or in use right now")

        if request.quantity > stock.quantity:
            raise HTTPException(status_code=409, detail="too much items")

        stock.reserved_quantity += request.quantity
        stock.quantity -= request.quantity
        
        new_item = OrderItem(
            order_id = request.order_id,
            user_id = user.id,
            drink_id = request.drink_id,
            quantity = request.quantity,
            price_per_item = request.price_per_item
        )

        db.add(new_item)
        await db.commit()
        return new_item
    

    async def cancel_order(order_id, db):
        query = select(Order).where(Order.id == order_id)
        result = await db.execute(query)
        order = result.scalar_one_or_none()

        if order is None:
            raise HTTPException(status_code=409, detail="order doesn't exist")

        query = select(OrderItem).where(OrderItem.order_id == order_id)
        res = await db.execute(query)
        items = res.scalars().all()
            
        for item in items:
            query = select(Stock).where(item.drink_id == Stock.drink_id)
            res = await db.execute(query)
            stock = res.scalar_one_or_none()
            if stock.drink_id == item.drink_id:
            #1 - вернуть в колво стока колво указанное в заказе
                stock.reserved_quantity -= item.quantity
                stock.quantity += item.quantity
            #2 - удалить ордер айтем
                await db.delete(item)

        order.status = "cancelled"
        await db.commit()
        return status.HTTP_200_OK
    
    async def remove_item(item_id, db):
        query = select(OrderItem).where(OrderItem.id == item_id)
        result = await db.execute(query)
        item = result.scalar_one_or_none()

        if item is None:
            raise HTTPException(status_code=409, detail="orderitem doesn't exist")
        
        query = select(Stock).where(item.drink_id == Stock.drink_id)
        res = await db.execute(query)
        stock = res.scalar_one_or_none()

        stock.reserved_quantity -= item.quantity
        stock.quantity += item.quantity
        await db.delete(item)
        await db.commit()
        return "done"
    
    async def change_quantity(item_id, request, db):
        query = select(OrderItem).where(OrderItem.id == item_id)
        result = await db.execute(query)
        item = result.scalar_one_or_none()

        query = select(Stock).where(item.drink_id == Stock.drink_id)
        res = await db.execute(query)
        stock = res.scalar_one_or_none()

        old_quantity = item.quantity
        new_quantity = request.quantity

        delta = new_quantity - old_quantity

        if delta > stock.quantity:
            raise HTTPException(status_code=409, detail="not enough in stock")

        stock.quantity -= delta
        stock.reserved_quantity += delta

        item.quantity = new_quantity
        item.price_per_item = request.price_per_item

        await db.commit()
        await db.refresh(item)

        return item


class OrderService:
    def __init__(self, db, redis_url, cache_ttl, cache_key):
        self.repository = OrdersRepository(db)
        self.redis = RedisCache(redis_url, cache_ttl)
        self.key = cache_key

    async def get_orders(self, page, user_id, warehouse_id, status, is_paid):

        params = {
        "user_id": user_id,
        "warehouse_id": warehouse_id,
        "status": status,
        "is_paid": is_paid,
        }
        
        key = f"{self.key}:{params}"

        cached_orders = self.redis.get(key)
        if cached_orders:
            return cached_orders
                
        items = await self.repository.get_orders()
        cache = [OrderSchema.model_validate(item).model_dump() for item in items]
        self.redis.set(key, cache)
        return await self.repository.get_orders(page, user_id, warehouse_id, status, is_paid)

    async def set_order(self, request):
        self.redis.delete_by_pattern(f"{self.key}:*")
        return await self.repository.set_order(request)

    async def update_order_payment(self, order_id):
        self.redis.delete_by_pattern(f"{self.key}:*")
        return await self.repository.update_order_payment(order_id)

    async def update_order_status(self, request, order_id, requested_user):
        self.redis.delete_by_pattern(f"{self.key}:*")
        return await self.repository.update_order_status(request, order_id, requested_user)

    async def get_items(self, order_id,user_id,drink_id,quantity,pricier):
        return await self.repository.get_items(order_id, user_id, drink_id, quantity, pricier)

    async def delete_item(self, item_id):
        self.redis.delete_by_pattern(f"{self.key}:*")
        return await self.repository.delete_item(item_id)