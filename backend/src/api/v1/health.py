import logging
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import settings
from src.db.engine import get_session

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> dict[str, Any]:
    """Health check with database connectivity and API key status."""
    db_status = "healthy"
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        logger.exception("Database health check failed")
        db_status = "unhealthy"

    mistral_configured = bool(settings.mistral_api_key)

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "service": "entre-deux-api",
        "database": db_status,
        "mistral_configured": mistral_configured,
    }
