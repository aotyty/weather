from typing import Optional
from pydantic import BaseModel

class Weather(BaseModel):
    longitude: float
    latitude: float
    temperature: Optional[float] = None
    wind_speed: Optional[float] = None
    city: str

class ForecastDay(BaseModel):
    date: str
    temperature_max: float
    temperature_min: float
    wind_speed_max: float
    precipitation: float

class Forecast(BaseModel):
    city: str
    latitude: float
    longitude: float
    days: list[ForecastDay]
