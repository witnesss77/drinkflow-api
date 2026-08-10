from sqlalchemy import select
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from core.models.models import Factory
from core.models.schemas import CreateFactory, UpdateFactory


class FactoryRepository:
    def __init__(self, db):
        self.db = db

    async def get_factories(self):
        query = select(Factory)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def set_factory(self, request):
        factory = Factory(
                name = request.name,
                location = request.location
            )
        
        try:
            self.db.add(factory)
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status_code=409,
                detail="Factory already exists or unique constraint violated"
            )
            
        return factory

    async def update_factory(self, request, factory_id):
        query = select(Factory).where(Factory.id == factory_id)
        result = await self.db.execute(query)
        factory = result.scalar_one_or_none()
        
        if factory is None:
            raise HTTPException(
                status_code=404,
                detail="Factory doesn't exist"
            )
        
        for k,v in request.model_dump(exclude_unset=True).items():
            if hasattr(factory, k):
                setattr(factory, k, v)
        try:
            await self.db.commit()
            await self.db.refresh(factory)
            return factory
            
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(status_code=400, detail="Database error")

    async def delete_factory(self, factory_id):
        query = select(Factory).where(Factory.id == factory_id)
        result = await self.db.execute(query)
        factory = result.scalar_one_or_none()
        
        if factory is None:
            raise HTTPException(
                status_code=404,
                detail="Factory doesnt exist"
            )
            
        await self.db.delete(factory)
        await self.db.commit()
        return factory
    