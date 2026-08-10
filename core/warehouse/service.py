from fastapi import HTTPException
from core.warehouse.repository import WarehouseRepository
from cache.cache import RedisCache


class WarehouseService:
    def __init__(self, db):
        self.repository = WarehouseRepository(db)
        self.redis = RedisCache

    async def get_warehouses(self):
        return await self.repository.get_warehouses()

    async def set_warehouse(self, request):
        return await self.repository.set_warehouse(request)

    async def update_warehouse(self, request, warehouse_id):
        return await self.repository.update_warehouse(request, warehouse_id)

    async def delete_warehouse(self, warehouse_id):
        return await self.repository.delete_warehouse(warehouse_id)