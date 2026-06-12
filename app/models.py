from typing import Optional
from pydantic import BaseModel

class Weather(BaseModel):
    longitude: float
    latitude: float
    temperature: Optional[float] = None
    wind_speed: Optional[float] = None
    city: str

