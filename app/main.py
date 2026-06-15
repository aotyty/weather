from fastapi import FastAPI, Query, Request

from app.models import Weather
from app.services.weather_service import get_coordinates, get_current_weather
from app.services.http_client import lifespan
from app.services.cache_service import get_cached, set_cached

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(lifespan=lifespan)

@app.get("/weather/")
async def get_weather(request: Request, city: str = Query(..., min_length=1)):
    logger.info(f"Incoming request for city {city}")
    cached = await get_cached(f"weather:{city.lower()}") 
    if cached:
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
    return weather
