from celery import Celery
from cfg import rabbitmq_url, redis_url

celery = Celery("main", broker=rabbitmq_url, backend=redis_url)

@celery.task
def process_order(order_id):
    ... 