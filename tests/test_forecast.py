from httpx import Response 

import respx 
import httpx
import pytest

FAKE_GEO = [{"lat": "55.75", "lon": "37.61", "display_name": "Moscow"}]
FAKE_WEATHER_FORECAST = {
    "daily": {
        "time": ["2024-01-01", "2024-01-02", "2024-01-03"],
        "temperature_2m_max": [2.1, 3.5, 1.8],
        "temperature_2m_min": [-1.2, 0.3, -2.1],
        "wind_speed_10m_max": [3.2, 4.1, 2.8],
        "precipitation_sum": [0.0, 1.2, 0.5],
    }
}

@respx.mock
async def test_get_forecast_succes(client):
    respx.get("https://nominatim.openstreetmap.org/search").mock(
        return_value=Response(200, json=FAKE_GEO)
    )
    respx.get("https://api.open-meteo.com/v1/forecast").mock(
        return_value=Response(200, json=FAKE_WEATHER_FORECAST)
    )

    response = await client.get("/forecast/?city=Moscow")

    assert response.status_code == 200
    assert response.json()["city"] == "Moscow"
    assert len(response.json()["days"]) == 3
    assert response.json()["days"][0]["date"] == "2024-01-01"
    assert response.json()["days"][0]["temperature_max"] == 2.1
    assert response.json()["days"][0]["temperature_min"] == -1.2
    assert response.json()["days"][0]["wind_speed_max"] == 3.2
    assert response.json()["days"][0]["precipitation"] == 0.0


@respx.mock
async def test_get_forecast_city_not_found(client):
    respx.get("https://nominatim.openstreetmap.org/search").mock(
        return_value=Response(200, json=[])
    )

    response = await client.get("/forecast/?city=fakecity123")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]



@respx.mock
async def test_get_forecast_timeout(client):
    respx.get("https://nominatim.openstreetmap.org/search").mock(
        side_effect=httpx.TimeoutException("timeout")
    )

    response = await client.get("/forecast/?city=Moscow")

    assert response.status_code == 504

