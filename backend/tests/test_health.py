from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture(autouse=True)
def _override_db(override_session: AsyncMock) -> None:
    """Auto-apply session override for health test."""


@pytest.mark.asyncio
async def test_health_check_returns_healthy(
    async_client: ASGITransport,
    override_session: AsyncMock,
) -> None:
    """Smoke test: health endpoint returns 200 with expected payload."""
    async with AsyncClient(
        transport=async_client, base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "entre-deux-api"
