import httpx
import logging

from fastapi import HTTPException

logger = logging.getLogger(__name__)

TIMEOUT = httpx.Timeout(10.0, connect=5.0)

async def get_coordinates(client: httpx.AsyncClient, city:str) -> tuple[float, float]:
    logger.info(f"Fetching coordinates for {city}")
    try:
        response = await client.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": city, "format": "json", "limit": 1},
            headers={"User-Agent": "weather_app/1.0"},
            timeout=TIMEOUT
        )
        response.raise_for_status()
    except httpx.TimeoutException:
        logger.error(f"Timeout fetching coordinates for {city}")
        raise HTTPException(status_code=504, 
                        detail="Geocoding service timed out")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching coordinates: {e.response.status_code}")
        raise HTTPException(status_code=502, 
                        detail=f"Geocoding error: {e.response.status_code}")

    data = response.json()
    if not data:
        logger.warning(f"City not found: {city}")
        raise HTTPException(status_code=404, 
                        detail=f"City {city} not found")

    return float(data[0]["lat"]), float(data[0]["lon"])

async def get_current_weather(client: httpx.AsyncClient, lat: float, lon: float) -> dict:
    logger.info(f"Fetching weather for coordinates: {lat}, {lon}")
    try:
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,wind_speed_10m",
                "timezone": "auto",
            },
            timeout=TIMEOUT,
        )
        response.raise_for_status()
    except httpx.TimeoutException:
        logger.error(f"Timeout fetching weather for: {lat}, {lon}")
        raise HTTPException(status_code=504, 
                        detail="Weather service timed out")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching weather {e.response.status_code}")
        raise HTTPException(status_code=502, 
                        detail=f"Weather API error: {e.response.status_code}")

    logger.info(f"Weather data received for: {lat}, {lon}")
    return response.json().get("current", {})

async def get_forecast(client: httpx.AsyncClient, lat: float, lon: float) -> dict:
    logger.info(f"Fetching forecast for coordinates: {lat}, {lon}")
    try:
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": "temperature_2m_max,temperature_2m_min,wind_speed_10m_max,precipitation_sum",
                "timezone": "auto",
            },
            timeout=TIMEOUT,
        )
        response.raise_for_status()
    except httpx.TimeoutException:
        logger.error(f"Timeout fetching forecast for: {lat}, {lon}")
        raise HTTPException(status_code=504, 
                        detail="Weather service timed out")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching forecast {e.response.status_code}")
        raise HTTPException(status_code=502, 
                        detail=f"Weather API error: {e.response.status_code}")

    logger.info(f"Forecast data received for: {lat}, {lon}")
    return response.json().get("daily", {})
