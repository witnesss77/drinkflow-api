from fastapi import FastAPI
from drinks.router import router as drinks_router
from factories.router import router as factories_router
from warehouse.router import router as warehouses_router

app = FastAPI()

app.include_router(drinks_router, tags = ["Drinks"])
app.include_router(factories_router, tags = ["Factories"])
app.include_router(warehouses_router, tags = ["Warehouses"])

@app.get("/")
async def main_page():
    return {"status":"up"}

