import asyncio
import json
from core.messages.rabbitmq import connect_rabbitmq, declare_queue, declare_exchange

async def handle_order_created(message):
    event_data = json.loads(message.body.decode())
    print(f"Получено сообщение: {event_data}")

    await message.ack()



async def main():
    connection = await connect_rabbitmq()
    channel = await connection.channel()
    exchange = await declare_exchange(channel)
    queue = await declare_queue(channel, exchange)

    await queue.consume(handle_order_created)
    await asyncio.Future()
    await connection.close()


if __name__ == "__main__":
    asyncio.run(main())