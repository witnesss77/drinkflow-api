from redis.asyncio import Redis
import json


class RedisCache:
    def __init__(self, redis_url: str, cache_ttl_seconds: int):
        self.redis = Redis.from_url(url=redis_url, decode_responses = True)
        self.cache_ttl_seconds = cache_ttl_seconds
    
    async def set(self, key: str, value):
        await self.redis.set(key, json.dumps(value), ex = self.cache_ttl_seconds)

    async def get(self, key: str):
        value = await self.redis.get(key)

        if value is None:
            return None

        return json.loads(value)

    async def delete(self, key: str):
        await self.redis.delete(key)

    async def delete_by_pattern(self, pattern: str):
        keys = await self.redis.keys(pattern)

        if keys:
            await self.redis.delete(*keys)