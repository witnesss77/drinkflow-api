from fastapi import APIRouter, Depends, status
from models.models import User
import bcrypt
from models.schemas import CreateUser
from models.database import get_session
import jwt


router = APIRouter(prefix='/auth')


@router.get("/token")
def get_token(db = Depends(get_session)):
    ...

@router.post("/register", status_code=status.HTTP_201_CREATED)
def create_user(request: CreateUser, db = Depends(get_session)):
    salt = bcrypt.gensalt()
    user = User(
        name = request.name,
        email = request.email,
        hashed_password = bcrypt.hashpw(request.password, salt),
        role = request.role
    )

    db.add(user)
    db.commit()
