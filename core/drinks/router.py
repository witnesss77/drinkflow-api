from fastapi import APIRouter, status, HTTPException, Depends
from core.models.database import get_session
from sqlalchemy.exc import IntegrityError
from core.dependencies import get_drink_service
from core.models.schemas import CreateDrink, UpdateDrink
from sqlalchemy import select
from core.models.models import Drink

router = APIRouter(prefix="/drinks")

@router.get("")
async def get_items(
    service = Depends(get_drink_service), 
    page: int | None = None, 
    name: str | None = None,
    desc: str | None = None, 
    alcoholic: bool | None  = None,
    price: int | None = None, 
    factory_id: int | None = None):

    return await service.get_drinks(page, name, desc, alcoholic, price, factory_id)

@router.get("/{drink_id:int}")
async def get_item(drink_id: int, db = Depends(get_session)):
    query = select(Drink).where(Drink.id == drink_id)
    res = await db.execute(query)
    result = res.scalar_one_or_none()

    if result is None:
        raise HTTPException(
                    status_code=404,
                    detail="Drink not found"
                )
    
    return result

@router.post("", status_code=status.HTTP_201_CREATED)
async def set_items(request: CreateDrink, service = Depends(get_drink_service)):
    return await service.set_drink(request)

@router.patch("/{drink_id:int}")
async def update_item(drink_id, update: UpdateDrink, service = Depends(get_drink_service)):
    return await service.update_drink(drink_id, update)
    
@router.delete("/{drink_id:int}")
async def delete_drink(drink_id, service = Depends(get_drink_service)):
    return await service.delete_drink(drink_id)