from app.config import settings

import redis.asyncio as redis
import logging
import json

logger = logging.getLogger(__name__)

CACHE_TTL = 600

redis_client = redis.from_url(settings.redis_url)

async def get_cached(key: str) -> dict | None:
    try: 
        data = await redis_client.get(key)
        if data:
            logger.info(f"Cache HIT: {key}")
            return json.loads(data)
        logger.info(f"Cache MISS: {key}")
        return None
    except Exception as e:
        logger.error(f"Redis error: {e}")
        return None

async def set_cached(key: str, value: dict) -> None:
    try: 
        await redis_client.set(key, json.dumps(value), ex=CACHE_TTL)
        logger.info(f"Cached: {key} for {CACHE_TTL} seconds")
    except Exception as e:
        logger.error(f"Redis set error: {e}")
