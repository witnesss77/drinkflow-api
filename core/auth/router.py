from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import EmailStr
from typing import Annotated
from sqlalchemy import select
from cfg import algorithms, secret_key
from models.models import User
from datetime import datetime, timedelta, timezone
import bcrypt
from passlib.context import CryptContext
from models.schemas import CreateUser, Token
from models.database import get_session
import jwt


router = APIRouter(prefix='/auth')


ACCESS_TOKEN_EXPIRE_MINUTES = 30
password_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')


async def authenticate_user(request_username: str , request_password: str, db = Depends(get_session)):
    query = select(User).where(User.name == request_username)
    result = db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        return False
    
    if not password_context.verify(request_password, user.hashed_password): 
        return False
    
    return user
    
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithms)
    return encoded_jwt

@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db = Depends(get_session)) -> Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.name}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(request: CreateUser, db = Depends(get_session)):
    salt = bcrypt.gensalt()
    pw = request.password
    encrypted = pw.encode('utf-8')
    user = User(
        name = request.name,
        email = request.email,
        hashed_password = bcrypt.hashpw(encrypted, salt).decode('utf-8'),
        role = request.role
    )

    db.add(user)
    await db.commit()

