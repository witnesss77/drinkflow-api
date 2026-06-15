from fastapi import APIRouter, status, HTTPException
from sqlalchemy.exc import IntegrityError

router = APIRouter()