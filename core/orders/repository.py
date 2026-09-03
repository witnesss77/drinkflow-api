from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from core.models.models import Order, OrderItem, User


class OrdersRepository:
    def __init__(self, db):
        self.db = db

    async def get_orders(self, user, page, warehouse_id, status, is_paid):
        q = select(User).where(User.id == int(user['id']))
        res = await self.db.execute(q)
        user = res.scalar_one_or_none()

        if user.role in ("admin", "manager"):
            query = select(Order)
        else:
            query = select(Order).where(Order.user_id == user.id)
        if warehouse_id is not None:
            query = query.where(Order.warehouse_id == warehouse_id)
        if status is not None:
            query = query.where(Order.status == status)
        if is_paid is not None:
            query = query.where(Order.is_paid == is_paid)
                
        if page:
            items_offset = (page - 1) * 10
            query = query.offset(items_offset).limit(10)
            if query is None:
                query = select(Order).offset(items_offset).limit(10)
            result = await self.db.execute(query)
            return result.scalars().all()
        else:
            result = await self.db.execute(query)
            return result.scalars().all()
        
    async def set_order(self, request, user_id):
        order = Order(
                user_id = user_id,
                warehouse_id = request.warehouse_id,
                status = "created",
                is_paid = False
            )
        
        try:
            self.db.add(order)
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status_code=409,
                detail="Order already exists or unique constraint violated"
            )
        
        return order

    async def get_order_by_id(self, order_id) -> Order:
        query = select(Order).options(selectinload(Order.items)).where(Order.id == order_id).with_for_update()
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_order_payment(self, order_id, user):
        query = select(Order).where(Order.id == order_id, int(user['id']) == Order.user_id).with_for_update()
        result = await self.db.execute(query)
        order = result.scalar_one_or_none()

        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        
        query2 = select(OrderItem).where(OrderItem.order_id == order.id)
        result2 = await self.db.execute(query2)
        items = result2.scalars().all()
        
        if not items:
            raise HTTPException(status_code=409, detail="order is empty")
        
        if order.is_paid == True or order.status == "paid":
            raise HTTPException(status_code=409, detail="order is already paid")
            
        order.is_paid = True
        order.status = "paid"
        
        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def update_order_status(self, request, order_id, requested_user):
        user_ = select(User).where(User.id == int(requested_user['id']))
        query = await self.db.execute(user_)
        res = query.scalar_one_or_none()
        
        if res is None:
            raise HTTPException(status_code=403, detail="role is not allowed")
            
        query = select(Order).where(Order.id == order_id)
        result = await self.db.execute(query)
        order = result.scalar_one_or_none()
        query2 = select(OrderItem).where(OrderItem.order_id == order.id)
        result2 = await self.db.execute(query2)
        items = result2.scalars().all()
        
        if order is None:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )
            
        if not items:
            raise HTTPException(status_code=409, detail="order is empty")
            
        order.status = request.status
        order.is_paid = request.is_paid
        
        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def get_items(self, user,
        order_id: int | None = None,
        drink_id: int | None = None,
        quantity: int | None = None,
        pricier: int | None = None) -> list[OrderItem]:

        query = select(User).where(User.id == int(user['id']))
        result = await self.db.execute(query)
        res = result.scalar_one_or_none()

        if res.role in ('admin', 'manager'):
            query = select(OrderItem)
        else:
            query = select(OrderItem).where(int(user['id']) == OrderItem.user_id)
        
        if order_id:
            query = query.where(OrderItem.order_id == order_id)
        if drink_id:
            query = query.where(OrderItem.drink_id == drink_id)
        if quantity:
            query = query.where(OrderItem.quantity == quantity)
        if pricier:
            query = query.where(OrderItem.price_per_item >= pricier)
        
        query = query.order_by(OrderItem.id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_item_by_id(self, item_id) -> Order:
        query = select(OrderItem).where(OrderItem.id == item_id).with_for_update()
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def delete_item(self, item_id):
        query = select(OrderItem).where(OrderItem.id == item_id)
        result = await self.db.execute(query)
        item = result.scalar_one_or_none()
        
        if not item:
            raise HTTPException(
                status_code=404,
                detail="OrderItem doesnt exist"
            )
        
        await self.db.delete(item)
        await self.db.commit()
        return item