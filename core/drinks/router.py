from fastapi import APIRouter, status, HTTPException, Depends
from models.database import get_session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from models.models import Drink

router = APIRouter(prefix="/drinks")

@router.get("")
async def get_items(db = Depends(get_session)):
    query = select(Drink)
    result = await db.execute(query)
    return result

@router.post("")
async def set_items(request, db = Depends(get_session)):
    request_obj = Drink(
        id = request.args.id,
        name = request.args.name,
        desc = request.args.desc,
        alcoholic = request.args.alcoholic,
        price = request.args.price,
        factory_id = request.args.price)
    try:
        db.add(request_obj)
        await db.commit()
    except IntegrityError:
        await db.rollback
        raise HTTPException(
            status_code=409,
            detail="Drink already exists or unique constraint violated"
        )
    return {"status": status.HTTP_201_CREATED, "message": "Drink created successfully"}
