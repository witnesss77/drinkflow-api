from sqlalchemy import select
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from core.models.models import Warehouse


class WarehouseRepository:
    def __init__(self, db):
        self.db = db

    async def get_warehouses(self):
        query = select(Warehouse)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def set_warehouse(self, request):
        warehouse = Warehouse(
                name = request.name,
                address = request.address
            )
            
        try:
            self.db.add(warehouse)
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status_code=409,
                detail="Warehouse already exists or unique constraint violated"
            )
            
        return warehouse

    async def update_warehouse(self, request, warehouse_id):
        query = select(Warehouse).where(Warehouse.id == warehouse_id)
        result = await self.db.execute(query)
        warehouse = result.scalar_one_or_none()
        
        if warehouse is None:
            raise HTTPException(
                status_code=404,
                detail="Warehouse doesn't exist"
            )
        
        for k,v in request.model_dump(exclude_unset=True).items():
            if hasattr(warehouse, k):
                setattr(warehouse, k, v)
        try:
            await self.db.commit()
            await self.db.refresh(warehouse)
            return warehouse
            
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(status_code=400, detail="Database error")

    async def delete_warehouse(self, warehouse_id):
        query = select(Warehouse).where(Warehouse.id == warehouse_id)
        result = await self.db.execute(query)
        warehouse = result.scalar_one_or_none()
        
        if warehouse is None:
            raise HTTPException(
                status_code=404,
                detail="Warehouse doesnt exist"
            )
        try:
            await self.db.delete(warehouse)
            await self.db.commit()
        except IntegrityError:
            raise HTTPException(status_code=409, detail="Warehouse has active orders, undeletable")
        return warehouse