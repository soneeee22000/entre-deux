import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.middleware.auth import get_current_patient_id

PATIENT_A = uuid.UUID("00000000-0000-0000-0000-000000000001")
PATIENT_B = uuid.UUID("00000000-0000-0000-0000-000000000002")


@pytest.fixture(autouse=True)
def _override_db(override_session: AsyncMock) -> None:
    """Auto-apply session override for all tests in this module."""


@pytest.fixture
def _inject_patient_a() -> None:  # type: ignore[misc]
    """Override current_patient_id to return PATIENT_A."""

    async def _override() -> uuid.UUID:
        return PATIENT_A

    app.dependency_overrides[get_current_patient_id] = _override
    yield
    del app.dependency_overrides[get_current_patient_id]


@pytest.mark.asyncio
async def test_patient_cannot_access_other_patient_data(
    _inject_patient_a: None,
) -> None:
    """GET /patients/{other_id} should return 403 when patient IDs don't match."""
    transport = ASGITransport(app=app)

    with patch("src.middleware.auth.settings") as mock_settings:
        mock_settings.demo_api_token = ""
        mock_settings.jwt_secret_key = ""

        async with AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            response = await client.get(
                f"/api/v1/patients/{PATIENT_B}",
            )

    assert response.status_code == 403
    assert "autre patient" in response.json()["detail"]


@pytest.mark.asyncio
async def test_patient_can_access_own_data(
    _inject_patient_a: None,
    mock_session: AsyncMock,
) -> None:
    """GET /patients/{own_id} should succeed."""
    transport = ASGITransport(app=app)

    mock_row = MagicMock()
    mock_row.fhir_resource = {"resourceType": "Patient", "id": str(PATIENT_A)}

    with patch("src.middleware.auth.settings") as mock_settings:
        mock_settings.demo_api_token = ""
        mock_settings.jwt_secret_key = ""

        mock_session.get = AsyncMock(return_value=mock_row)

        async with AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            response = await client.get(
                f"/api/v1/patients/{PATIENT_A}",
            )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_observations_isolation(
    _inject_patient_a: None,
) -> None:
    """GET /observations/patients/{other_id} should return 403."""
    transport = ASGITransport(app=app)

    with patch("src.middleware.auth.settings") as mock_settings:
        mock_settings.demo_api_token = ""
        mock_settings.jwt_secret_key = ""

        async with AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            response = await client.get(
                f"/api/v1/observations/patients/{PATIENT_B}",
            )

    assert response.status_code == 403
