from fastapi import FastAPI
from drinks.router import router as drinks_router

app = FastAPI()

app.include_router(drinks_router)

@app.get("/")
async def main_page():
    return {"status":"up"}

