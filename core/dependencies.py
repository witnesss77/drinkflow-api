from core.models.database import get_session
from fastapi import Depends

from core.drinks.service import DrinkService


def get_drink_service(db = Depends(get_session)):
    return DrinkService(db)