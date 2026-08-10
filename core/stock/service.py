from fastapi import HTTPException
from core.stock.repository import StocksRepository
from cache.cache import RedisCache


class StockService:
    def __init__(self, db):
        self.repository = StocksRepository(db)
        self.redis = RedisCache

    async def get_stocks(self):
        return await self.repository.get_stock()

    async def set_stocks(self, request):
        if request.quantity < request.reserved_quantity:
            raise HTTPException(
                status_code=409,
                detail="Stock's reserved quantity cannot be more than existing quantity"
            )
        return await self.repository.set_stocks(request)


    async def update_stocks(self, request, stock_id):
        return await self.repository.update_stocks(request, stock_id)

    async def delete_stocks(self, stock_id):
        return await self.repository.delete_stocks(stock_id)