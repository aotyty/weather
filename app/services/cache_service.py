import redis.asyncio as redis
import json
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CACHE_TTL = 600

redis_client = redis.from_url(REDIS_URL)

async def get_cached(key: str) -> dict | None:
    data = await redis_client.get(key)
    if data:
        return json.loads(data)
    return None

async def set_cached(key: str, value: dict) -> None:
    await redis_client.set(key, json.dumps(value), ex=CACHE_TTL)
