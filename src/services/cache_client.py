import redis
import json
from src.config import settings

redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True
)

def cache_set(key, value, ttl):
    redis_client.setex(key, ttl, json.dumps(value))

def cache_get(key):
    data = redis_client.get(key)
    return json.loads(data) if data else None
