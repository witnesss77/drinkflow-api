from fastapi import FastAPI
from core.drinks.router import router as drinks_router
from core.factories.router import router as factories_router
from core.warehouse.router import router as warehouses_router
from core.stock.router import router as stocks_router
from core.orders.router import router as orders_router
from core.auth.router import router as auth_router

app = FastAPI()

app.include_router(drinks_router, tags = ["Drinks"])
app.include_router(factories_router, tags = ["Factories"])
app.include_router(stocks_router, tags = ["Stocks"])
app.include_router(warehouses_router, tags = ["Warehouses"])
app.include_router(orders_router, tags = ["Orders"])
app.include_router(auth_router, tags = ["Users"])

@app.get("/")
async def main_page():
    return {"status":"up"}

