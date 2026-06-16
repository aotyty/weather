from httpx import Response 

import respx 
import httpx
import pytest

FAKE_GEO = [{"lat": "55.75", "lon": "37.61", "display_name": "Moscow"}]
FAKE_WEATHER = {
    "current": {
        "temperature_2m": 20.5,
        "wind_speed_10m": 3.2
    }
}

@respx.mock
async def test_get_weather_succes(client):
    respx.get("https://nominatim.openstreetmap.org/search").mock(
        return_value=Response(200, json=FAKE_GEO)
    )
    respx.get("https://api.open-meteo.com/v1/forecast").mock(
        return_value=Response(200, json=FAKE_WEATHER)
    )

    response = await client.get("/weather/?city=Moscow")

    assert response.status_code == 200
    assert response.json()["city"] == "Moscow"
    assert response.json()["temperature"] == 20.5
    assert response.json()["wind_speed"] == 3.2


@respx.mock
async def test_get_weather_city_not_found(client):
    respx.get("https://nominatim.openstreetmap.org/search").mock(
        return_value=Response(200, json=[])
    )

    response = await client.get("/weather/?city=fakecity123")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]



@respx.mock
async def test_get_weather_timeout(client):
    respx.get("https://nominatim.openstreetmap.org/search").mock(
        side_effect=httpx.TimeoutException("timeout")
    )

    response = await client.get("/weather/?city=Moscow")

    assert response.status_code == 504
