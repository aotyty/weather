from fastapi import FastAPI, Query, Request

from app.models import Weather, ForecastDay, Forecast
from app.services.weather_service import get_coordinates, get_current_weather, get_forecast
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

@app.get("/forecast/")
async def forecast_endpoint(request: Request, city: str = Query(..., min_length=1)):
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
