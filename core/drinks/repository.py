from sqlalchemy import select
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from core.models.models import Drink
from core.models.schemas import CreateDrink

class DrinkRepository:
    def __init__(self, db):
        self.db = db


    async def get_all(self):
        result = await self.db.execute(
            select(Drink)
        )

        return result.scalars().all()

    async def get_all_filter(self, 
        page: int | None = None,
        name: str | None = None,
        desc: str | None = None,
        alcoholic: bool | None = None,
        price: int | None = None,
        factory_id: int | None = None):

        query = select(Drink)
        
        if name:
            query = query.where(Drink.name == name)
        if desc:
            query = query.where(Drink.desc == desc)
        if alcoholic is not None:
            query = query.where(Drink.alcoholic == alcoholic)
        if price is not None:
            query = query.where(Drink.price == price)
        if factory_id is not None:
            query = query.where(Drink.factory_id == factory_id)
            
        if page:
            if page < 0: 
                raise HTTPException(status_code=409, detail="Invalid page")
            items_offset =  (page - 1) * 10
            query = query.offset(items_offset).limit(10)
            if query is None:
                query = select(Drink).offset(items_offset).limit(10)
            result = await self.db.execute(query)
            return result.scalars().all()
    
        result = await self.db.execute(query)
        return result.scalars().all()

    async def set_drink(self, request: CreateDrink):
        request_obj = Drink(
                name = request.name,
                desc = request.desc,
                alcoholic = request.alcoholic,
                price = request.price,
                factory_id = request.factory_id
        )
        
        try:
            self.db.add(request_obj)
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status_code=409,
                detail="Drink already exists or unique constraint violated"
            )
        
        return request_obj

    async def update_drink(self, drink_id, request):
        query = select(Drink).where(Drink.id == drink_id)
        result = await self.db.execute(query)
        drink = result.scalar_one_or_none()
        
        if drink is None:
            raise HTTPException(status_code=404, detail = "Drink not found")
        
        for k,v in request.model_dump(exclude_unset=True).items():
            try:
                if hasattr(drink, k):
                    setattr(drink, k, v)
            except AttributeError:
                    pass
            try:
                await self.db.commit()
                await self.db.refresh(drink)
                return drink
            except IntegrityError:
                await self.db.rollback()
                raise HTTPException(status_code=400, detail="Database error")

    async def delete_drink(self, drink_id):
        query = select(Drink).where(Drink.id == drink_id)
        result = await self.db.execute(query)
        drink = result.scalar_one_or_none()
        
        if drink is None:
            raise HTTPException(
                status_code=404,
                detail="Drink doesnt exist"
            )
        await self.db.delete(drink)
        await self.db.commit()
        return drink