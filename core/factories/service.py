from core.factories.repository import FactoryRepository
from cache.cache import RedisCache


class FactoryService:
    def __init__(self, db):
        self.repository = FactoryRepository(db)
        self.redis = RedisCache

    async def get_factories(self):
        return await self.repository.get_factories()

    async def set_factory(self, request):
        return await self.repository.set_factory(request)

    async def update_factory(self, request, factory_id):
        return await self.repository.update_factory(request, factory_id)

    async def delete_factory(self, factory_id):
        return await self.repository.delete_factory(factory_id)