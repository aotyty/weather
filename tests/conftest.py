from httpx import AsyncClient, ASGITransport
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
