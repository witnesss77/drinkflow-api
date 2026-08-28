import asyncio
import json
from core.messages.rabbitmq import connect_rabbitmq, declare_queue, declare_exchange, USER_EXCHANGE, USER_ROUTING_KEY, USERS_QUEUE

async def handle_message(message):
    event_data = json.loads(message.body.decode())
    print(f"Получено сообщение: {event_data}")

    await message.ack()



async def main():
    connection = await connect_rabbitmq()
    channel = await connection.channel()
    exchange = await declare_exchange(channel,USER_EXCHANGE)
    queue = await declare_queue(channel, exchange, USERS_QUEUE, USER_ROUTING_KEY)

    await queue.consume(handle_message)
    await asyncio.Future()
    await connection.close()


if __name__ == "__main__":
    asyncio.run(main())