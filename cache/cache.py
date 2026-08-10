from redis import Redis
import json


class RedisCache:
    def __init__(self, redis_url: str, cache_ttl_seconds: int | None = None):
        self.redis = Redis.from_url(url=redis_url, decode_responses = True)
        self.cache_ttl_seconds = cache_ttl_seconds
    
    async def set(self, key: str, value: dict):
        self.redis.set(key, json.dumps(value), ex = self.cache_ttl_seconds)

    async def get(self, key: str):
        return await self.redis.get(key)

    def delete(self, key: str):
        self.redis.delete(key)