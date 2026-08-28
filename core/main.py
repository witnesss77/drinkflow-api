from fastapi import FastAPI
from contextlib import asynccontextmanager
from core.messages.rabbitmq import connect_rabbitmq, declare_exchange, declare_queue, USER_EXCHANGE, ORDER_EXCHANGE, USERS_QUEUE, NOTIFICATIONS_QUEUE, USER_ROUTING_KEY, ORDER_ROUTING_KEY
from core.drinks.router import router as drinks_router
from core.factories.router import router as factories_router
from core.warehouse.router import router as warehouses_router
from core.stock.router import router as stocks_router
from core.orders.router import router as orders_router
from core.auth.router import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    connection = await connect_rabbitmq()
    channel = await connection.channel()

    user_channel = await connection.channel()
    exchange = await declare_exchange(channel, ORDER_EXCHANGE)
    user_exchange = await declare_exchange(channel, USER_EXCHANGE)

    await declare_queue(user_channel, user_exchange, USERS_QUEUE, USER_ROUTING_KEY)
    await declare_queue(channel, exchange, NOTIFICATIONS_QUEUE, ORDER_ROUTING_KEY)
    
    app.state.orders_exchange = exchange
    app.state.users_exchange = user_exchange


    yield 
    await connection.close()


app = FastAPI(lifespan=lifespan)

app.include_router(drinks_router, tags = ["Drinks"])
app.include_router(factories_router, tags = ["Factories"])
app.include_router(stocks_router, tags = ["Stocks"])
app.include_router(warehouses_router, tags = ["Warehouses"])
app.include_router(orders_router, tags = ["Orders"])
app.include_router(auth_router, tags = ["Users"])

@app.get("/")
async def main_page():
    return {"status":"up"}

