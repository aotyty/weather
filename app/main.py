from fastapi import FastAPI, Query
import httpx

from app.models import Weather
from app.services.weather_service import get_coordinates, get_current_weather

app = FastAPI()

@app.get("/weather/")
async def get_weather(city: str = Query(..., min_length=1)):
    async with httpx.AsyncClient() as client:
        lat, lon = await get_coordinates(client, city)
        current = await get_current_weather(client, lat, lon)

        return Weather(
            longitude=lon,
            latitude=lat,
            temperature=current.get("temperature_2m"),
            wind_speed=current.get("wind_speed_10m"),
            city=city
        )
