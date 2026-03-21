import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.fixture(autouse=True)
def _override_db(override_session: AsyncMock) -> None:
    """Auto-apply session override for all tests in this module."""


@pytest.fixture
def _disable_rate_limit() -> None:  # type: ignore[misc]
    """Disable rate limiting for tests."""
    with patch("src.main.limiter") as mock_limiter:
        mock_limiter.enabled = False
        yield


@pytest.mark.asyncio
async def test_register_returns_tokens() -> None:
    """POST /auth/register should return access and refresh tokens."""
    transport = ASGITransport(app=app)
    mock_user = MagicMock()
    mock_user.id = uuid.uuid4()
    mock_user.patient_id = uuid.uuid4()

    mock_patient = MagicMock()
    mock_patient.id = mock_user.patient_id

    with (
        patch("src.api.v1.auth.AuthService") as mock_auth_service,
        patch("src.middleware.auth.settings") as mock_settings,
    ):
        mock_settings.demo_api_token = ""
        mock_settings.jwt_secret_key = ""

        instance = mock_auth_service.return_value
        instance.register = AsyncMock(return_value=(mock_user, mock_patient))
        instance.create_access_token = MagicMock(return_value="access-tok")
        instance.create_refresh_token = MagicMock(return_value="refresh-tok")

        async with AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": "test@test.com",
                    "password": "password123",
                    "given_name": "Marie",
                    "family_name": "Dupont",
                    "identifier": "TEST-001",
                },
            )

    assert response.status_code == 201
    body = response.json()
    assert body["access_token"] == "access-tok"
    assert body["refresh_token"] == "refresh-tok"
    assert body["patient_id"] == str(mock_patient.id)


@pytest.mark.asyncio
async def test_login_returns_tokens() -> None:
    """POST /auth/login should return access and refresh tokens."""
    transport = ASGITransport(app=app)
    mock_user = MagicMock()
    mock_user.id = uuid.uuid4()
    mock_user.patient_id = uuid.uuid4()

    with (
        patch("src.api.v1.auth.AuthService") as mock_auth_service,
        patch("src.middleware.auth.settings") as mock_settings,
    ):
        mock_settings.demo_api_token = ""
        mock_settings.jwt_secret_key = ""

        instance = mock_auth_service.return_value
        instance.authenticate = AsyncMock(return_value=mock_user)
        instance.create_access_token = MagicMock(return_value="access-tok")
        instance.create_refresh_token = MagicMock(return_value="refresh-tok")

        async with AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/auth/login",
                json={"email": "test@test.com", "password": "password123"},
            )

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"] == "access-tok"
    assert body["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials_returns_401() -> None:
    """POST /auth/login with wrong creds should return 401."""
    transport = ASGITransport(app=app)

    with (
        patch("src.api.v1.auth.AuthService") as mock_auth_service,
        patch("src.middleware.auth.settings") as mock_settings,
    ):
        mock_settings.demo_api_token = ""
        mock_settings.jwt_secret_key = ""

        instance = mock_auth_service.return_value
        instance.authenticate = AsyncMock(
            side_effect=ValueError("Invalid credentials")
        )

        async with AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/auth/login",
                json={"email": "wrong@test.com", "password": "wrong"},
            )

    assert response.status_code == 401
    assert "Identifiants invalides" in response.json()["detail"]


@pytest.mark.asyncio
async def test_auth_endpoints_are_public() -> None:
    """Auth endpoints should not require bearer token even when demo token is set."""
    transport = ASGITransport(app=app)

    with (
        patch("src.api.v1.auth.AuthService") as mock_auth_service,
        patch("src.middleware.auth.settings") as mock_settings,
    ):
        mock_settings.demo_api_token = "some-secret"
        mock_settings.jwt_secret_key = ""

        instance = mock_auth_service.return_value
        instance.authenticate = AsyncMock(
            side_effect=ValueError("Invalid credentials")
        )

        async with AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/auth/login",
                json={"email": "test@test.com", "password": "password123"},
            )

    assert response.status_code == 401
    assert "Identifiants" in response.json()["detail"]
