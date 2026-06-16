from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import RequestHistory

import logging

logger = logging.getLogger(__name__)

async def save_request(
    session: AsyncSession,
    city: str,
    temperature: float | None,
    wind_speed: float | None,
    from_cache: bool
) -> None:
    try:
        record = RequestHistory(
            city=city,
            temperature=temperature,
            wind_speed=wind_speed,
            from_cache=from_cache,
        )
        session.add(record)
        await session.commit()
        logger.info(f"Saved request for {city} to database")
    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to save request: {e}")
