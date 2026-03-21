from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.fixture(autouse=True)
def _override_db(override_session: AsyncMock) -> None:
    """Auto-apply session override for all tests in this module."""


@pytest.mark.asyncio
async def test_health_check_bypasses_auth() -> None:
    """Health endpoint should be accessible without auth token."""
    transport = ASGITransport(app=app)

    with patch("src.api.v1.health.settings") as mock_settings:
        setattr(mock_settings, "mistral_api_key", "test-value")

        async with AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/health")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_valid_token_passes() -> None:
    """Requests with valid Bearer token should pass auth."""
    transport = ASGITransport(app=app)

    with patch("src.middleware.auth.settings") as mock_settings:
        mock_settings.demo_api_token = "test-secret"

        async with AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/v1/patients/00000000-0000-0000-0000-000000000001",
                headers={"Authorization": "Bearer test-secret"},
            )

    assert response.status_code != 401


@pytest.mark.asyncio
async def test_missing_token_returns_401() -> None:
    """Requests without token should return 401 when token is configured."""
    transport = ASGITransport(app=app)

    with patch("src.middleware.auth.settings") as mock_settings:
        mock_settings.demo_api_token = "test-secret"

        async with AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/v1/patients/00000000-0000-0000-0000-000000000001",
            )

    assert response.status_code == 401
    assert "Missing" in response.json()["detail"]


@pytest.mark.asyncio
async def test_invalid_token_returns_401() -> None:
    """Requests with wrong token should return 401."""
    transport = ASGITransport(app=app)

    with patch("src.middleware.auth.settings") as mock_settings:
        mock_settings.demo_api_token = "test-secret"

        async with AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/v1/patients/00000000-0000-0000-0000-000000000001",
                headers={"Authorization": "Bearer wrong-token"},
            )

    assert response.status_code == 401
    assert "Invalid" in response.json()["detail"]


@pytest.mark.asyncio
async def test_no_token_configured_skips_auth() -> None:
    """When no demo_api_token is set, auth should be skipped."""
    transport = ASGITransport(app=app)

    with patch("src.middleware.auth.settings") as mock_settings:
        mock_settings.demo_api_token = ""

        async with AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/v1/patients/00000000-0000-0000-0000-000000000001",
            )

    assert response.status_code != 401
