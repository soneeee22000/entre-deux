import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_create_observation_validates_input() -> None:
    """Missing required fields should return 422."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/v1/observations",
            json={"patient_id": str(uuid.uuid4())},
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_observation_routes_are_registered() -> None:
    """Verify observation routes exist in the app."""
    route_paths = [r.path for r in app.routes]  # type: ignore[union-attr]
    assert "/api/v1/observations" in route_paths
    assert "/api/v1/observations/analyze-image" in route_paths
    assert "/api/v1/observations/patients/{patient_id}" in route_paths
