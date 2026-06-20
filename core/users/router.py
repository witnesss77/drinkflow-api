from fastapi import APIRouter, status, HTTPException, Depends
from models.database import get_session
from sqlalchemy.exc import IntegrityError
import bcrypt
from models.schemas import CreateUser, UpdateUser
from sqlalchemy import select
from models.models import User

router = APIRouter(prefix="/users")

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(request: CreateUser, db = Depends(get_session)):
    user = User(
        name = request.name,
        email = request.email,
        hashed_password = bcrypt.hashpw(request.password, bcrypt.gensalt()).decode("utf-8"),
        role = request.role
    )
    try:
        db.add(user)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Database error")
    
    return "done"

