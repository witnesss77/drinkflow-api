from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status, Depends
from core.auth.router import get_current_user
from core.models.schemas import OrderSchema
from core.messages.producer import OrderProducer
from core.models.models import User, Stock, Order, OrderItem, Drink, Warehouse
from fastapi import HTTPException
from core.orders.repository import OrdersRepository
from cache.cache import RedisCache



class OrderLogicService:
    async def add_order_item(request, payload, db, id_):
        query = select(User).options(selectinload(User.orders)).where(User.id == (id_.id))
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        query = select(Order).where(Order.id == payload.order_id, Order.user_id == id_.id)
        result = await db.execute(query)
        order = result.scalar_one_or_none()

        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        
        query = select(Warehouse).where(Warehouse.id == Order.warehouse_id)
        result = await db.execute(query)
        warehouse = result.scalars().all()

        warehouse = warehouse[0]

        stock_query = select(Stock).where(
            Stock.warehouse_id == warehouse.id,
            Stock.drink_id == payload.drink_id
        ).with_for_update()

        result = await db.execute(stock_query)
        stock = result.scalar_one_or_none()

        if stock is None:
            raise HTTPException(status_code=404, detail="Stock not found or in use right now")

        if payload.quantity > stock.quantity:
            raise HTTPException(status_code=409, detail="too much items")

        query = select(Drink).where(Drink.id == payload.drink_id)
        result = await db.execute(query)
        drink = result.scalar_one_or_none()

        stock.reserved_quantity += payload.quantity
        stock.quantity -= payload.quantity
        
        new_item = OrderItem(
            order_id = payload.order_id,
            user_id = user.id,
            drink_id = payload.drink_id,
            quantity = payload.quantity,
            price_per_item = drink.price
        )

        db.add(new_item)
        await db.commit()
        
        producer = OrderProducer(request.app.state.orders_exchange)
        await producer.add_order_items(order_id = order.id)
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
            query = select(Stock).where(item.drink_id == Stock.drink_id, Stock.warehouse_id == order.warehouse_id)
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
    
    async def remove_item(item_id, request, db):
        query = select(OrderItem).where(OrderItem.id == item_id)
        result = await db.execute(query)
        item = result.scalar_one_or_none()

        if not item:
            raise HTTPException(status_code=409, detail="orderitem doesn't exist")

        query  = select(Order).where(Order.id == item.order_id)
        result = await db.execute(query)
        order = result.scalar_one_or_none()

        query = select(Stock).where(item.drink_id == Stock.drink_id, Stock.warehouse_id == order.warehouse_id)
        res = await db.execute(query)
        stock = res.scalar_one_or_none()

        stock.reserved_quantity -= item.quantity
        stock.quantity += item.quantity
        await db.delete(item)
        await db.commit()
        producer = OrderProducer(request.app.state.orders_exchange)
        await producer.deleted_order_item(item.order_id, item.quantity, item.price_per_item)
        
        return "done"
    
    async def change_quantity(item_id, payload, request, db):
        query = select(OrderItem).where(OrderItem.id == item_id)
        result = await db.execute(query)
        item = result.scalar_one_or_none()

        query  = select(Order).where(Order.id == item.order_id)
        result = await db.execute(query)
        order = result.scalar_one_or_none()

        query = select(Stock).where(Stock.drink_id == item.drink_id, Stock.warehouse_id == order.warehouse_id)
        res = await db.execute(query)
        stock = res.scalar_one_or_none()

        old_quantity = item.quantity
        old_price = item.price_per_item

        new_quantity = payload.quantity
        new_price = payload.price_per_item

        quantity_delta = new_quantity - old_quantity

        if quantity_delta > stock.quantity:
            raise HTTPException(
                status_code=409,
                detail="not enough in stock"
            )

        old_total = old_quantity * old_price
        new_total = new_quantity * new_price

        price_delta = new_total - old_total

        stock.quantity -= quantity_delta
        stock.reserved_quantity += quantity_delta

        item.quantity = new_quantity
        item.price_per_item = new_price

        await db.commit()
        await db.refresh(item)

        producer = OrderProducer(request.app.state.orders_exchange)

        await producer.changed_order_quantity(
            order_id=item.order_id,
            price_delta=price_delta,
            quantity_delta=quantity_delta
            )

        return item


class OrderService:
    def __init__(self, db, redis_url, cache_ttl, cache_key):
        self.repository = OrdersRepository(db)
        self.redis = RedisCache(redis_url, cache_ttl)
        self.key = cache_key

    async def get_orders(self,
            user,
            page = None, 
            warehouse_id = None, 
            status = None, 
            is_paid = None,
            item_count = None,
            total_price = None, 
            ):
        
        params = {
        "user_id": int(user["id"]),
        "page": page,
        "warehouse_id": warehouse_id,
        "status": status,
        "is_paid": is_paid,
        "item_count": item_count,
        "total_price": total_price
        }
        
        key = f"{self.key}:{params}"

        cached_orders = await self.redis.get(key)
        if cached_orders:
            return cached_orders
                
        items = await self.repository.get_orders(user, page,warehouse_id, status, is_paid)
        cache = [OrderSchema.model_validate(item).model_dump() for item in items]
        await self.redis.set(key, cache)
        return cache

    async def set_order(self, payload, request, user_id):
        await self.redis.delete_by_pattern(f"{self.key}:*")
        order = await self.repository.set_order(payload, user_id)
        producer = OrderProducer(request.app.state.orders_exchange)
        await producer.created_order(order_id = order.id)

        return order

    async def update_order_payment(self, order_id, user):
        await self.redis.delete_by_pattern(f"{self.key}:*")
        return await self.repository.update_order_payment(order_id, user)

    async def update_order_status(self, request, order_id, requested_user):
        await self.redis.delete_by_pattern(f"{self.key}:*")
        return await self.repository.update_order_status(request, order_id, requested_user)

    async def get_items(self, order_id, drink_id,quantity,pricier, user):
        return await self.repository.get_items(user, order_id,drink_id, quantity, pricier)

    async def delete_item(self, item_id, request):
        await self.redis.delete_by_pattern(f"{self.key}:*")
        item = await self.repository.get_item_by_id(item_id)

        producer = OrderProducer(request.app.state.orders_exchange)
        await producer.deleted_order_item(item.order_id, item.quantity, item.price_per_item)
        return await self.repository.delete_item(item_id)