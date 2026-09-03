import os
import dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

dotenv.load_dotenv(BASE_DIR / ".env")

db_str = os.environ.get("db_url")
tests_db_url = os.environ.get("test_db_url")
redis_url = os.environ.get("redis_url")
drink_cache_key = os.environ.get("drink_cache_key")
stocks_cache_key = os.environ.get("stock_cache_key")
order_cache_key = os.environ.get("order_cache_key")
cache_ttl_seconds = os.environ.get("cache_ttl_seconds")
secret_key = os.environ.get("SECRET_KEY")
algorithms = os.environ.get("ALGORITHMS")
access_token_expire_minutes = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")
refresh_token_expire_minutes = os.environ.get("REFRESH_TOKEN_EXPIRE_MINUTES")
rabbitmq_url = os.environ.get("rabbitmq_url")