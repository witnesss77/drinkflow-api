from fastapi import APIRouter, Depends, status, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from jwt.exceptions import DecodeError, ExpiredSignatureError, InvalidSignatureError
from core.cfg import algorithms, secret_key, access_token_expire_minutes, refresh_token_expire_minutes
from core.models.models import User
from datetime import datetime, timedelta, timezone
import bcrypt
from passlib.context import CryptContext
from core.models.schemas import CreateUser, RefreshRequest, CreateUser_admin
from core.models.database import get_session
import jwt
from jwt.exceptions import InvalidTokenError


router = APIRouter(prefix='/auth')


password_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

def create_jwt(token_type: str, data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    to_encode.update({"type": token_type})
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithms)
    return encoded_jwt


async def authenticate_user(request_username: str, request_password: str, db = Depends(get_session)):
    query = select(User).where(User.name == request_username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        return False
    
    if not password_context.verify(request_password, user.hashed_password): 
        return False
    
    return user
    

@router.post("/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db = Depends(get_session)):
    user = await authenticate_user(form_data.username, form_data.password, db) 
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=int(access_token_expire_minutes))
    refresh_token_expires = timedelta(minutes=int(refresh_token_expire_minutes))

    access_token = create_jwt(
        token_type = "access_token", data={"sub": user.email, "id": str(user.id)}, 
        expires_delta=access_token_expires)

    refresh_token = create_jwt(
        token_type = "refresh_token", data={"sub": str(user.id)}, 
        expires_delta= refresh_token_expires)

    return {"access_token":access_token,
            "token_type": "Bearer",
            "refresh_token": refresh_token,
            }


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(payload: CreateUser, db = Depends(get_session)):
    salt = bcrypt.gensalt()
    pw = payload.password
    encrypted = pw.encode('utf-8')
    user = User(
        name = payload.name,
        email = payload.email,
        hashed_password = bcrypt.hashpw(encrypted, salt).decode('utf-8'),
        role = "user"
    )

    try:
        db.add(user)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail = "Email already exists in the system"
        )

    return {"id": user.id, "role": user.role, "username": user.name}
    
def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, key = secret_key, algorithms=[algorithms])
        if payload.get("type") == "access_token":
            username: str = payload.get('sub')
            user_id: str = payload.get('id')
            if username is None or user_id is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            return {'username': username, 'id': user_id}
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    else:
        raise HTTPException(status_code=401, detail="Invalid token")

async def admin_check(
    res = Depends(get_current_user),
    db = Depends(get_session)):

    query = select(User).where(User.id == int(res["id"]))
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    if user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return user


@router.get("/me")
async def protected_route(user = Depends(get_current_user)):
    return user

@router.post("/refresh")
async def refresh_access_token(refresh_token: RefreshRequest, db = Depends(get_session)):
    try:
        payload = jwt.decode(refresh_token.refresh_token, key = secret_key, algorithms=[algorithms])
        try:
            token_type = payload.get("type") == "refresh_token"
            if token_type is False:
                raise HTTPException(
                                status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid refresh token"
                            )
            user_id = int(payload.get("sub"))

            query = select(User).where(User.id == user_id)
            result = await db.execute(query)
            user_obj = result.scalar_one_or_none()

            if user_obj is None:
                raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

            access_token_expires = timedelta(minutes=int(access_token_expire_minutes))
            access_token = create_jwt(
            token_type = "access_token", data={"sub": user_obj.email, "id": user_obj.id}, 
            expires_delta=access_token_expires)

            return {
                "access_token": access_token,
                "token_type": "bearer"
            }
        
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    except DecodeError:
        raise HTTPException(status_code=401, detail="Wrong token")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except InvalidSignatureError:
        raise HTTPException(status_code=401, detail="Wrong token")

@router.post("/register/admin", status_code=status.HTTP_201_CREATED)
async def create_user_(payload: CreateUser_admin, db = Depends(get_session), admin = Depends(admin_check)):
    salt = bcrypt.gensalt()
    pw = payload.password
    encrypted = pw.encode('utf-8')
    user = User(
        name = payload.name,
        email = payload.email,
        hashed_password = bcrypt.hashpw(encrypted, salt).decode('utf-8'),
        role = payload.role
    )

    try:
        db.add(user)
        await db.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail = "Email already exists in the system"
        )

    return {"id" :user.id, "role": user.role, "username": user.name}