from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

class RequestHistory(Base):
    __tablename__ = "request_history"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, nullable=False)
    temperature = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    from_cache = Column(Boolean, default=False)
    requested_at = Column(DateTime, server_default=func.now())
