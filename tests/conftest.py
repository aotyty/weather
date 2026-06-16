from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch
from app.main import app

import pytest 
import httpx

@pytest.fixture
async def client():
    async with httpx.AsyncClient() as http_client:
        app.state.client = http_client
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as ac:
            yield ac

@pytest.fixture()
def mock_redis():
    with patch("app.services.cache_service.redis_client") as mock:
        mock.get = AsyncMock(return_value=None)
        mock.set = AsyncMock(return_value=True)
        yield mock
