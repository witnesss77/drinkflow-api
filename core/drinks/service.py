from core.drinks.repository import DrinkRepository

from cache.cache import RedisCache

class DrinkService:
    def __init__(self, db):
        self.repository = DrinkRepository(db)
        self.redis = RedisCache

    async def get_drinks(self, 
            page = None,
            name = None,
            desc = None,
            alcoholic = None,
            price = None,
            factory_id = None):
        
        return await self.repository.get_all_filter(page, name,desc,alcoholic,price,factory_id)

    async def set_drink(self, request):
        return await self.repository.set_drink(request)

    async def update_drink(self, drink_id, request):
        return await self.repository.update_drink(drink_id, request)

    async def delete_drink(self, drink_id):
        return await self.repository.delete_drink(drink_id)