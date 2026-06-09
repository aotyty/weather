from typing import Optional
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from geopy.geocoders import Nominatim

import httpx
import asyncio


app = FastAPI()

class Weather(BaseModel):
    longitude: float
    latitude: float
    temperature: Optional[float] = None
    wind_speed: Optional[float] = None
    city: str

@app.get("/weather/")
async def get_weather(city: str = Query(..., min_length=1, description="City's name.")):
    async with httpx.AsyncClient() as client:
        geo_responce = await client.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": city, "format": "json", "limit": 1},
            headers={"User-Agent": "weather_app/1.0"}
        )
        geo_data = geo_responce.json()

        if not geo_data:
            raise HTTPException(status_code=404, detail="City not found...")

        lat = float(geo_data[0]["lat"])
        lon = float(geo_data[0]["lon"])

        weather_responce = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,wind_speed_10m",
                "timezone": "auto"
            }
        )

        data = weather_responce.json()
        current = data.get("current", {})

        return Weather(
            longitude=lon,
            latitude=lat,
            temperature=current.get("temperature_2m"),
            wind_speed=current.get("wind_speed_10m"),
            city=city
        )
