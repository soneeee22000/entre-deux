import uuid
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from tests.conftest import make_table_row


@pytest.fixture(autouse=True)
def _override_db(override_session: AsyncMock) -> None:
    """Auto-apply session override for all tests in this module."""


@pytest.mark.asyncio
async def test_register_patient_creates_and_returns_fhir(
    async_client: ASGITransport,
    override_session: AsyncMock,
    patient_id: uuid.UUID,
    sample_patient_fhir: dict[str, Any],
) -> None:
    """POST /patients creates a patient and returns FHIR resource."""
    row = make_table_row(sample_patient_fhir, patient_id)

    with (
        patch(
            "src.api.v1.patients.PatientRepository"
        ) as mock_repo_cls,
    ):
        mock_repo = AsyncMock()
        mock_repo_cls.return_value = mock_repo
        mock_repo.get_by_identifier = AsyncMock(return_value=None)
        mock_repo.create = AsyncMock(return_value=row)

        async with AsyncClient(
            transport=async_client, base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/patients",
                json={
                    "given_name": "Jean",
                    "family_name": "Dupont",
                    "identifier": "TEST-001",
                },
            )

    assert response.status_code == 201
    data = response.json()
    assert data["resourceType"] == "Patient"


@pytest.mark.asyncio
async def test_register_patient_duplicate_returns_409(
    async_client: ASGITransport,
    override_session: AsyncMock,
    patient_id: uuid.UUID,
    sample_patient_fhir: dict[str, Any],
) -> None:
    """POST /patients with existing identifier returns 409."""
    existing_row = make_table_row(sample_patient_fhir, patient_id)

    with patch(
        "src.api.v1.patients.PatientRepository"
    ) as mock_repo_cls:
        mock_repo = AsyncMock()
        mock_repo_cls.return_value = mock_repo
        mock_repo.get_by_identifier = AsyncMock(return_value=existing_row)

        async with AsyncClient(
            transport=async_client, base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/patients",
                json={
                    "given_name": "Jean",
                    "family_name": "Dupont",
                    "identifier": "TEST-001",
                },
            )

    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_patient_returns_fhir(
    async_client: ASGITransport,
    override_session: AsyncMock,
    patient_id: uuid.UUID,
    sample_patient_fhir: dict[str, Any],
) -> None:
    """GET /patients/{id} returns the FHIR Patient resource."""
    row = make_table_row(sample_patient_fhir, patient_id)

    with patch(
        "src.api.v1.patients.PatientRepository"
    ) as mock_repo_cls:
        mock_repo = AsyncMock()
        mock_repo_cls.return_value = mock_repo
        mock_repo.get_by_id = AsyncMock(return_value=row)

        async with AsyncClient(
            transport=async_client, base_url="http://test"
        ) as client:
            response = await client.get(f"/api/v1/patients/{patient_id}")

    assert response.status_code == 200
    assert response.json()["resourceType"] == "Patient"


@pytest.mark.asyncio
async def test_get_patient_not_found_returns_404(
    async_client: ASGITransport,
    override_session: AsyncMock,
    patient_id: uuid.UUID,
) -> None:
    """GET /patients/{id} returns 404 when patient doesn't exist."""
    with patch(
        "src.api.v1.patients.PatientRepository"
    ) as mock_repo_cls:
        mock_repo = AsyncMock()
        mock_repo_cls.return_value = mock_repo
        mock_repo.get_by_id = AsyncMock(return_value=None)

        async with AsyncClient(
            transport=async_client, base_url="http://test"
        ) as client:
            response = await client.get(f"/api/v1/patients/{patient_id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_patient_timeline(
    async_client: ASGITransport,
    override_session: AsyncMock,
    patient_id: uuid.UUID,
    sample_patient_fhir: dict[str, Any],
    sample_observation_fhir: dict[str, Any],
) -> None:
    """GET /patients/{id}/timeline returns aggregated resources."""
    patient_row = make_table_row(sample_patient_fhir, patient_id)
    obs_row = make_table_row(sample_observation_fhir)

    with (
        patch(
            "src.api.v1.patients.PatientRepository"
        ) as mock_patient_cls,
        patch(
            "src.db.repositories.observation_repository.ObservationRepository",
        ) as mock_obs_cls,
        patch(
            "src.db.repositories.questionnaire_response_repository.QuestionnaireResponseRepository",
        ) as mock_qr_cls,
        patch(
            "src.db.repositories.composition_repository.CompositionRepository",
        ) as mock_comp_cls,
    ):
        mock_patient_cls.return_value.get_by_id = AsyncMock(
            return_value=patient_row
        )
        mock_obs_cls.return_value.list_by_patient = AsyncMock(
            return_value=[obs_row]
        )
        mock_qr_cls.return_value.list_by_patient = AsyncMock(
            return_value=[]
        )
        mock_comp_cls.return_value.list_by_patient = AsyncMock(
            return_value=[]
        )

        async with AsyncClient(
            transport=async_client, base_url="http://test"
        ) as client:
            response = await client.get(
                f"/api/v1/patients/{patient_id}/timeline"
            )

    assert response.status_code == 200
    data = response.json()
    assert "patient" in data
    assert "observations" in data
    assert len(data["observations"]) == 1


@pytest.mark.asyncio
async def test_register_patient_validates_input(
    async_client: ASGITransport,
    override_session: AsyncMock,
) -> None:
    """POST /patients with missing fields returns 422."""
    async with AsyncClient(
        transport=async_client, base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/v1/patients",
            json={"given_name": "Jean"},
        )
    assert response.status_code == 422
