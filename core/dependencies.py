from core.models.database import get_session
from fastapi import Depends
from core.cfg import cache_ttl_seconds, redis_url, drink_cache_key

from core.drinks.service import DrinkService
from core.factories.service import FactoryService
from core.stock.service import StockService
from core.warehouse.service import WarehouseService
from core.orders.service import OrderService


def get_drink_service(db = Depends(get_session)):
    return DrinkService(db, redis_url, cache_ttl_seconds, cache_key=drink_cache_key)

def get_factory_service(db = Depends(get_session)):
    return FactoryService(db)

def get_stocks_service(db = Depends(get_session)):
    return StockService(db)

def get_warehouse_service(db = Depends(get_session)):
    return WarehouseService(db)

def get_order_service(db = Depends(get_session)):
    return OrderService(db)