from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.database import engine, Base

import httpx

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with httpx.AsyncClient(timeout=httpx.Timeout(10.0, connect=5.0)) as client:
        app.state.client = client
        yield
