from fastapi import FastAPI, Query, Request
from sqlalchemy import text 
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.limiter import limiter

from app.schemas import Weather, ForecastDay, Forecast
from app.services.weather_service import get_coordinates, get_current_weather, get_forecast
from app.services.http_client import lifespan
from app.services.cache_service import get_cached, set_cached, redis_client
from app.db.database import AsyncSessionLocal
from app.db.crud import save_request

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/health/")
async def health_status():
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        await redis_client.ping()
        return {"status": "ok", "database": "ok", "cache": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.get("/weather/")
@limiter.limit("10/minute")
async def weather_endpoint(request: Request, city: str = Query(..., min_length=1, max_length=100)):
    logger.info(f"Incoming request for city {city}")
    cached = await get_cached(f"weather:{city.lower()}") 
    if cached:
        async with AsyncSessionLocal() as session:
            await save_request(
                session=session,
                city=city,
                temperature=cached.get("temperature"),
                wind_speed=cached.get("wind_speed"),
                from_cache=True,
            )
        return Weather(**cached)

    client = request.app.state.client
    lat, lon = await get_coordinates(client, city)
    current = await get_current_weather(client, lat, lon)

    weather = Weather(
        longitude=lon,
        latitude=lat,
        temperature=current.get("temperature_2m"),
        wind_speed=current.get("wind_speed_10m"),
        city=city
    )

    await set_cached(f"weather:{city.lower()}", weather.model_dump())
    async with AsyncSessionLocal() as session:
        await save_request(
            session=session,
            city=city,
            temperature=weather.temperature,
            wind_speed=weather.wind_speed,
            from_cache=False,
        )
    return weather

@app.get("/forecast/")
@limiter.limit("10/minute")
async def forecast_endpoint(request: Request, city: str = Query(..., min_length=1, max_length=100)):
    logger.info(f"Incoming request for city {city}")
    cached = await get_cached(f"forecast:{city.lower()}") 
    if cached:
        return Forecast(**cached)

    client = request.app.state.client
    lat, lon = await get_coordinates(client, city)
    daily = await get_forecast(client, lat, lon)

    days = [
        ForecastDay(
            date=daily["time"][i],
            temperature_max=daily["temperature_2m_max"][i],
            temperature_min=daily["temperature_2m_min"][i],
            wind_speed_max=daily["wind_speed_10m_max"][i],
            precipitation=daily["precipitation_sum"][i],
        )
        for i in range(len(daily["time"]))
    ]

    forecast = Forecast(
        city=city,
        latitude=lat,
        longitude=lon,
        days=days,
    )

    await set_cached(f"forecast:{city.lower()}", forecast.model_dump())
    return forecast
