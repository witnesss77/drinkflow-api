import asyncio
import json
from core.celery_worker import process_order
from core.messages.rabbitmq import connect_rabbitmq, declare_queue, declare_exchange, ORDER_EXCHANGE, NOTIFICATIONS_QUEUE, ORDER_ROUTING_KEY

async def handle_message(message):
    event_data = json.loads(message.body.decode())
    print(f"Получено сообщение: {event_data}")
    if event_data["event"] == "order.created":
        result = process_order.delay(event_data["order_id"])
        print(result.id)

    await message.ack()



async def main():
    connection = await connect_rabbitmq()
    channel = await connection.channel()
    exchange = await declare_exchange(channel,ORDER_EXCHANGE)
    queue = await declare_queue(channel, exchange, NOTIFICATIONS_QUEUE, ORDER_ROUTING_KEY)

    await queue.consume(handle_message)
    await asyncio.Future()
    await connection.close()


if __name__ == "__main__":
    asyncio.run(main())