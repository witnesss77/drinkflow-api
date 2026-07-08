from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, Depends
from models.models import User, Stock, Warehouse, Order, OrderItem
from models.database import get_session



class OrderService:
    async def add_order_item(request, warehouse_id: int, db):
        query = select(User).options(selectinload(User.orders)).where(User.id == request.user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        query = select(Order).where(Order.id == request.order_id)
        result = await db.execute(query)
        order = result.scalar_one_or_none()

        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")

        stock_query = select(Stock).where(
            Stock.warehouse_id == warehouse_id,
            Stock.drink_id == request.drink_id
        )

        result = await db.execute(stock_query)
        stock = result.scalar_one_or_none()

        if stock is None:
            raise HTTPException(status_code=404, detail="Stock not found")

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
        await db.refresh(new_item)
        return new_item
        