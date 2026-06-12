import httpx
from fastapi import HTTPException

TIMEOUT = httpx.Timeout(10.0, connect=5.0)

async def get_coordinates(client: httpx.AsyncClient, city:str) -> tuple[float, float]:
    try:
        response = await client.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": city, "format": "json", "limit": 1},
            headers={"User-Agent": "weather_app/1.0"},
            timeout=TIMEOUT
        )
        response.raise_for_status()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, 
                        detail="Geocoding service timed out")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, 
                        detail=f"Geocoding error: {e.response.status_code}")

    data = response.json()
    if not data:
        raise HTTPException(status_code=404, 
                        detail=f"City {city} not found")

    return float(data[0]["lat"]), float(data[0]["lon"])

async def get_current_weather(client: httpx.AsyncClient, lat: float, lon: float) -> dict:
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
        raise HTTPException(status_code=504, 
                        detail="Weather service timed out")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, 
                        detail=f"Weather API error: {e.response.status_code}")

    return response.json().get("current", {})
