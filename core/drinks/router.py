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