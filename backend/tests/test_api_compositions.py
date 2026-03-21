import uuid
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture(autouse=True)
def _override_db(override_session: AsyncMock) -> None:
    """Auto-apply session override for all tests in this module."""


@pytest.mark.asyncio
async def test_generate_visit_brief(
    async_client: ASGITransport,
    override_session: AsyncMock,
    patient_id: uuid.UUID,
    sample_composition_fhir: dict[str, Any],
) -> None:
    """POST /compositions/visit-brief generates a brief with mocked agent."""
    with (
        patch(
            "src.middleware.consent.ConsentService"
        ) as mock_consent_cls,
        patch(
            "src.api.dependencies.BriefAgent"
        ),
        patch(
            "src.api.dependencies.VisitBriefService"
        ) as mock_svc_cls,
    ):
        mock_consent_cls.return_value.verify_consent = AsyncMock(
            return_value=True
        )
        mock_svc_cls.return_value.generate = AsyncMock(
            return_value=sample_composition_fhir
        )

        async with AsyncClient(
            transport=async_client, base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/compositions/visit-brief",
                json={
                    "patient_id": str(patient_id),
                    "period_start": "2025-01-01T00:00:00",
                    "period_end": "2025-03-01T00:00:00",
                },
            )

    assert response.status_code == 201
    data = response.json()
    assert data["resourceType"] == "Composition"


@pytest.mark.asyncio
async def test_list_compositions(
    async_client: ASGITransport,
    override_session: AsyncMock,
    patient_id: uuid.UUID,
    sample_composition_fhir: dict[str, Any],
) -> None:
    """GET /compositions/patients/{id} returns composition list."""
    with (
        patch(
            "src.api.dependencies.BriefAgent"
        ),
        patch(
            "src.api.dependencies.VisitBriefService"
        ) as mock_svc_cls,
    ):
        mock_svc_cls.return_value.list_compositions = AsyncMock(
            return_value=[sample_composition_fhir]
        )

        async with AsyncClient(
            transport=async_client, base_url="http://test"
        ) as client:
            response = await client.get(
                f"/api/v1/compositions/patients/{patient_id}"
            )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Visit Brief"


@pytest.mark.asyncio
async def test_download_composition_pdf(
    async_client: ASGITransport,
    override_session: AsyncMock,
    patient_id: uuid.UUID,
    sample_composition_fhir: dict[str, Any],
) -> None:
    """GET /compositions/{id}/pdf returns a PDF file."""
    comp_id = uuid.uuid4()
    with (
        patch(
            "src.api.dependencies.BriefAgent"
        ),
        patch(
            "src.api.dependencies.VisitBriefService"
        ) as mock_svc_cls,
    ):
        mock_svc_cls.return_value.get_composition_by_id = AsyncMock(
            return_value=(sample_composition_fhir, patient_id)
        )

        async with AsyncClient(
            transport=async_client, base_url="http://test"
        ) as client:
            response = await client.get(
                f"/api/v1/compositions/{comp_id}/pdf"
            )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content[:5] == b"%PDF-"


@pytest.mark.asyncio
async def test_download_composition_pdf_not_found(
    async_client: ASGITransport,
    override_session: AsyncMock,
) -> None:
    """GET /compositions/{id}/pdf returns 404 for missing composition."""
    comp_id = uuid.uuid4()
    with (
        patch(
            "src.api.dependencies.BriefAgent"
        ),
        patch(
            "src.api.dependencies.VisitBriefService"
        ) as mock_svc_cls,
    ):
        mock_svc_cls.return_value.get_composition_by_id = AsyncMock(
            return_value=None
        )

        async with AsyncClient(
            transport=async_client, base_url="http://test"
        ) as client:
            response = await client.get(
                f"/api/v1/compositions/{comp_id}/pdf"
            )

    assert response.status_code == 404
