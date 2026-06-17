# Weather
FastAPI weather app with current conditions and 7-day forecasts.

## Features
- Current weather + 7-day forecast via Open-Meteo API
- City geocoding via Nominatim (OpenStreetMap)
- PostgreSQL persistence (request history)
- Redis caching (600s TTL)
- Health check endpoint

## Quick Start
```bash
git clone <url>
cd weather
docker compose up -d
curl http://localhost:8000/weather/?city=London
```

## API


| Endpoint             | Description             |
| -------------------- | ----------------------- |
| GET /health/         | DB + Redis health check |
| GET /weather/?city=  | Current weather         |
| GET /forecast/?city= | 7-day forecast          |

## Tech Stack
- FastAPI 
- PostgreSQL
- Redis 
- SQLAlchemy 
- Docker
