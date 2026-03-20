import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_create_consent_validates_input() -> None:
    """Missing required fields should return 422."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/v1/consents",
            json={"patient_id": str(uuid.uuid4())},
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_consent_routes_are_registered() -> None:
    """Verify consent routes exist in the app."""
    route_paths = [r.path for r in app.routes]  # type: ignore[union-attr]
    assert "/api/v1/consents" in route_paths
    assert "/api/v1/consents/{consent_id}/revoke" in route_paths
    assert "/api/v1/consents/patients/{patient_id}" in route_paths


@pytest.mark.asyncio
async def test_patient_routes_are_registered() -> None:
    """Verify patient routes exist in the app."""
    route_paths = [r.path for r in app.routes]  # type: ignore[union-attr]
    assert "/api/v1/patients" in route_paths
    assert "/api/v1/patients/{patient_id}" in route_paths
    assert "/api/v1/patients/{patient_id}/timeline" in route_paths


@pytest.mark.asyncio
async def test_all_fhir_routes_are_registered() -> None:
    """Verify all FHIR routes are wired up."""
    route_paths = [r.path for r in app.routes]  # type: ignore[union-attr]
    expected = [
        "/api/v1/health",
        "/api/v1/patients",
        "/api/v1/observations",
        "/api/v1/observations/analyze-image",
        "/api/v1/questionnaire-responses",
        "/api/v1/compositions/visit-brief",
        "/api/v1/consents",
        "/api/v1/audit-events",
    ]
    for path in expected:
        assert path in route_paths, f"Route {path} not registered"
