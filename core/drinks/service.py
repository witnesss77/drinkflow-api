from core.drinks.repository import DrinkRepository
import json
from core.models.schemas import DrinkSchema
from cache.cache import RedisCache

class DrinkService:
    def __init__(self, db, cache_redis_url:str, cache_ttl, cache_key):
        self.repository = DrinkRepository(db)
        self.redis = RedisCache(redis_url=cache_redis_url, cache_ttl_seconds=cache_ttl)
        self.key = cache_key

    async def get_drinks(self, 
        page = None,
        name = None,
        desc = None,
        alcoholic = None,
        price = None,
        factory_id = None):


        cached_drinks = self.redis.get(self.key)
        if cached_drinks:
            return cached_drinks

        items = await self.repository.get_all()
        cache = [DrinkSchema.model_validate(item).model_dump() for item in items]
        self.redis.set(self.key, cache)

        return await self.repository.get_all_filter(page, name,desc,alcoholic,price, factory_id)

    async def set_drink(self, request):
        self.redis.delete(self.key)
        return await self.repository.set_drink(request)

    async def update_drink(self, drink_id, request):
        self.redis.delete(self.key)
        return await self.repository.update_drink(drink_id, request)

    async def delete_drink(self, drink_id):
        self.redis.delete(self.key)
        return await self.repository.delete_drink(drink_id)