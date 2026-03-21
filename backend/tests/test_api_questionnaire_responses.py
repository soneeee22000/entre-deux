import io
import uuid
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture(autouse=True)
def _override_db(override_session: AsyncMock) -> None:
    """Auto-apply session override for all tests in this module."""


@pytest.mark.asyncio
async def test_create_journal_entry(
    async_client: ASGITransport,
    override_session: AsyncMock,
    patient_id: uuid.UUID,
    sample_qr_fhir: dict[str, Any],
) -> None:
    """POST /questionnaire-responses creates entry with mocked agent."""
    with (
        patch(
            "src.middleware.consent.ConsentService"
        ) as mock_consent_cls,
        patch(
            "src.api.dependencies.JournalAgent"
        ),
        patch(
            "src.api.dependencies.JournalService"
        ) as mock_svc_cls,
    ):
        mock_consent_cls.return_value.verify_consent = AsyncMock(
            return_value=True
        )
        mock_svc_cls.return_value.create_entry = AsyncMock(
            return_value=sample_qr_fhir
        )

        async with AsyncClient(
            transport=async_client, base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/questionnaire-responses",
                json={
                    "patient_id": str(patient_id),
                    "transcript": "Je me sens fatigue aujourd'hui",
                },
            )

    assert response.status_code == 201
    data = response.json()
    assert data["resourceType"] == "QuestionnaireResponse"


@pytest.mark.asyncio
async def test_list_journal_entries(
    async_client: ASGITransport,
    override_session: AsyncMock,
    patient_id: uuid.UUID,
    sample_qr_fhir: dict[str, Any],
) -> None:
    """GET /questionnaire-responses/patients/{id} returns list."""
    with (
        patch(
            "src.api.dependencies.JournalAgent"
        ),
        patch(
            "src.api.dependencies.JournalService"
        ) as mock_svc_cls,
    ):
        mock_svc_cls.return_value.list_entries = AsyncMock(
            return_value=[sample_qr_fhir]
        )

        async with AsyncClient(
            transport=async_client, base_url="http://test"
        ) as client:
            response = await client.get(
                f"/api/v1/questionnaire-responses/patients/{patient_id}"
            )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["resourceType"] == "QuestionnaireResponse"


@pytest.mark.asyncio
async def test_create_journal_entry_validates_input(
    async_client: ASGITransport,
    override_session: AsyncMock,
    patient_id: uuid.UUID,
) -> None:
    """POST /questionnaire-responses with missing transcript returns 422."""
    async with AsyncClient(
        transport=async_client, base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/v1/questionnaire-responses",
            json={"patient_id": str(patient_id)},
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_journal_entry_audio(
    async_client: ASGITransport,
    override_session: AsyncMock,
    patient_id: uuid.UUID,
    sample_qr_fhir: dict[str, Any],
) -> None:
    """POST /questionnaire-responses/audio transcribes and creates entry."""
    with (
        patch(
            "src.middleware.consent.ConsentService"
        ) as mock_consent_cls,
        patch(
            "src.api.dependencies.TranscribeAgent"
        ) as mock_transcribe_cls,
        patch(
            "src.api.dependencies.JournalAgent"
        ),
        patch(
            "src.api.dependencies.JournalService"
        ) as mock_svc_cls,
    ):
        mock_consent_cls.return_value.verify_consent = AsyncMock(
            return_value=True
        )
        mock_transcribe_cls.return_value.transcribe = AsyncMock(
            return_value="Je me sens bien"
        )
        mock_svc_cls.return_value.create_entry = AsyncMock(
            return_value=sample_qr_fhir
        )

        audio_content = b"fake-audio-data"
        async with AsyncClient(
            transport=async_client, base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/questionnaire-responses/audio",
                data={"patient_id": str(patient_id)},
                files={"audio": ("test.webm", io.BytesIO(audio_content), "audio/webm")},
            )

    assert response.status_code == 201
    data = response.json()
    assert data["resourceType"] == "QuestionnaireResponse"


@pytest.mark.asyncio
async def test_audio_endpoint_rejects_invalid_content_type(
    async_client: ASGITransport,
    override_session: AsyncMock,
    patient_id: uuid.UUID,
) -> None:
    """POST /questionnaire-responses/audio with non-audio file returns 415."""
    with (
        patch("src.middleware.consent.ConsentService") as mock_consent_cls,
        patch("src.api.dependencies.TranscribeAgent"),
        patch("src.api.dependencies.JournalAgent"),
        patch("src.api.dependencies.JournalService"),
    ):
        mock_consent_cls.return_value.verify_consent = AsyncMock(
            return_value=True
        )

        async with AsyncClient(
            transport=async_client, base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/questionnaire-responses/audio",
                data={"patient_id": str(patient_id)},
                files={"audio": ("test.txt", io.BytesIO(b"not audio"), "text/plain")},
            )

    assert response.status_code == 415
