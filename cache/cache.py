from redis import Redis
import json


class RedisCache:
    def __init__(self, redis_url: str, cache_ttl_seconds: int):
        self.redis = Redis.from_url(url=redis_url, decode_responses = True)
        self.cache_ttl_seconds = cache_ttl_seconds
    
    def set(self, key: str, value):
        self.redis.set(key, json.dumps(value), ex = self.cache_ttl_seconds)

    def get(self, key: str):
        value = self.redis.get(key)

        if value is None:
            return None

        return json.loads(value)

    def delete(self, key: str):
        self.redis.delete(key)

    def delete_by_pattern(self, pattern: str):
        keys = self.redis.keys(pattern)

        if keys:
            self.redis.delete(*keys)