from sqlalchemy import select
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from core.models.models import Stock


class StocksRepository:
    def __init__(self, db):
        self.db = db

    async def get_stock(self):
        query = select(Stock)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def set_stocks(self, request):
        stmt = select(Stock).where(Stock.drink_id == request.drink_id, Stock.warehouse_id == request.warehouse_id)
        query = await self.db.execute(stmt)
        res = query.scalars().all()
        if len(res) > 0:
            raise HTTPException(status_code=409, detail=f"This drink is already in stock, {res}")
                
        stock = Stock(
            drink_id = request.drink_id,
            warehouse_id = request.warehouse_id,
            quantity = request.quantity,
            reserved_quantity = request.reserved_quantity
        )
        try:
            self.db.add(stock)
            await self.db.commit()
            return stock
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status_code=409,
                detail="Stock already exists or unique constraint violated"
            )
    
    async def update_stocks(self, request, stock_id):
        query = select(Stock).where(Stock.id == stock_id)
        result = await self.db.execute(query)
        stock = result.scalar_one_or_none()
            
        if stock is None:
            raise HTTPException(status_code=404, detail="Stock doesn't exist")
            
        for k, v in request.model_dump(exclude_unset=True).items():
            setattr(stock, k, v)
                
        if stock.quantity < stock.reserved_quantity: 
            await self.db.rollback()
            raise HTTPException(status_code=409, detail="Stock's reserved quantity cannot be more than existing quantity")
            
        try:
            await self.db.commit()
            await self.db.refresh(stock)
            return stock
                
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(status_code=400, detail="Database error")
    
    async def delete_stocks(self, stock_id):
        query = select(Stock).where(Stock.id == stock_id)
        result = await self.db.execute(query)
        stock = result.scalar_one_or_none()
        
        if stock is None:
            raise HTTPException(
                status_code=404,
                detail="Stock doesnt exist"
            )
            
        await self.db.delete(stock)
        await self.db.commit()
        return stock