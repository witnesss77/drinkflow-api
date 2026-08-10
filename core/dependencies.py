from core.models.database import get_session
from fastapi import Depends

from core.drinks.service import DrinkService
from core.factories.service import FactoryService


def get_drink_service(db = Depends(get_session)):
    return DrinkService(db)

def get_factory_service(db = Depends(get_session)):
    return FactoryService(db)
