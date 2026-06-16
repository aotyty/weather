from app.services.cache_service import get_cached, set_cached
from unittest.mock import AsyncMock

import json
import pytest

FAKE_DATA = {"city": "Moscow", "temperature": 20.5}

@pytest.mark.asyncio 
async def test_get_cached_hit(mock_redis):
    mock_redis.get = AsyncMock(return_value=json.dumps(FAKE_DATA).encode())
    result = await get_cached("weather:moscow")
    assert result == FAKE_DATA
    mock_redis.get.assert_called_once_with("weather:moscow")

async def test_get_cached_miss(mock_redis):
    mock_redis.get = AsyncMock(return_value=None)
    result = await get_cached("weather:moscow")
    assert result is None

async def test_set_cached(mock_redis):
    mock_redis.set = AsyncMock(return_value=True)
    await set_cached("weather:moscow", FAKE_DATA)
    mock_redis.set.assert_called_once_with(
        "weather:moscow",
        json.dumps(FAKE_DATA),
        ex=600
    )
