from fastapi import APIRouter, status, HTTPException, Depends
from models.database import get_session
from sqlalchemy.exc import IntegrityError
from models.schemas import CreateDrink, UpdateDrink
from sqlalchemy import select
from models.models import Drink

router = APIRouter(prefix="/drinks")

@router.get("")
async def get_items(page: int | None = None, db = Depends(get_session)):
    if page:
        items_offset =  (page - 1) * 10

        query = select(Drink).offset(items_offset).limit(10)
        result = await db.execute(query)
        return result.scalars().all()
    else:
        query = select(Drink)
        result = await db.execute(query)
        return result.scalars().all()

@router.post("", status_code=status.HTTP_201_CREATED)
async def set_items(request: CreateDrink, db = Depends(get_session)):
    request_obj = Drink(
        name = request.name,
        desc = request.desc,
        alcoholic = request.alcoholic,
        price = request.price,
        factory_id = request.factory_id
    )

    try:
        db.add(request_obj)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Drink already exists or unique constraint violated"
        )
    return {"status": status.HTTP_201_CREATED, "message": "Drink created successfully"}

@router.patch("/{drink_id:int}")
async def update_item(drink_id, update: UpdateDrink, db = Depends(get_session)):
    query = select(Drink).where(Drink.id == drink_id)
    result = await db.execute(query)
    drink = result.scalar_one_or_none()

    for k,v in update.model_dump(exclude_unset=True).items():
        try:
            if hasattr(drink, k):
                setattr(drink, k, v)
        except AttributeError:
            pass
    try:
        await db.commit()
        await db.refresh(drink)
        return drink
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Database error")
    
@router.delete("/{drink_id:int}")
async def delete_drink(drink_id, db = Depends(get_session)):
    query = select(Drink).where(Drink.id == drink_id)
    result = await db.execute(query)
    drink = result.scalar_one_or_none()

    if drink is None:
        raise HTTPException(
            status_code=404,
            detail="Drink doesnt exist"
        )
    await db.delete(drink)
    await db.commit()
    return {"status": status.HTTP_200_OK, "message": "Drink deleted successfully"}