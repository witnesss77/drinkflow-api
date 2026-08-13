from fastapi import HTTPException
from core.stock.repository import StocksRepository
from core.models.schemas import StockSchema
from core.cfg import redis_url, cache_ttl_seconds
from cache.cache import RedisCache


class StockService:
    def __init__(self, db, redis_url, cache_ttl_seconds, cache_key):
        self.repository = StocksRepository(db)
        self.redis = RedisCache(redis_url, cache_ttl_seconds)
        self.key = cache_key

    async def get_stocks(self):
        cached_stocks = self.redis.get(self.key)
        if cached_stocks:
            return cached_stocks
        
        items = await self.repository.get_stock()
        cache = [StockSchema.model_validate(item).model_dump() for item in items]
        self.redis.set(self.key, cache)
        return await self.repository.get_stock()

    async def set_stocks(self, request):
        if request.quantity < request.reserved_quantity:
            raise HTTPException(
                status_code=409,
                detail="Stock's reserved quantity cannot be more than existing quantity"
            )
        self.redis.delete(self.key)
        return await self.repository.set_stocks(request)


    async def update_stocks(self, request, stock_id):
        self.redis.delete(self.key)
        return await self.repository.update_stocks(request, stock_id)

    async def delete_stocks(self, stock_id):
        self.redis.delete(self.key)
        return await self.repository.delete_stocks(stock_id)