from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_rate_limit_key_function_returns_ip() -> None:
    """Rate limit key should fall back to client IP when no JWT."""
    from src.middleware.rate_limit import get_rate_limit_key

    mock_request = type("Request", (), {
        "headers": {},
        "client": type("Client", (), {"host": "1.2.3.4"})(),
    })()

    with patch("src.middleware.rate_limit.settings") as mock_settings:
        mock_settings.jwt_secret_key = ""
        key = get_rate_limit_key(mock_request)  # type: ignore[arg-type]

    assert key == "1.2.3.4"


@pytest.mark.asyncio
async def test_health_endpoint_not_rate_limited() -> None:
    """Health check should always be accessible."""
    transport = ASGITransport(app=app)

    with (
        patch("src.api.v1.health.settings") as mock_settings,
        patch("src.middleware.auth.settings") as mock_auth_settings,
    ):
        mock_settings.mistral_api_key = True
        mock_auth_settings.demo_api_token = ""
        mock_auth_settings.jwt_secret_key = ""

        async with AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            for _ in range(10):
                response = await client.get("/api/v1/health")
                assert response.status_code == 200
