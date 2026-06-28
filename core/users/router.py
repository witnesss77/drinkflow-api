from fastapi import APIRouter, status, HTTPException, Depends
from models.database import get_session
from sqlalchemy.exc import IntegrityError
import bcrypt
from models.schemas import CreateUser, UpdateUser
from sqlalchemy import select
from models.models import User

router = APIRouter(prefix="/users")
