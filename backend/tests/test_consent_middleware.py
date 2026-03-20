import uuid
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.fixture(autouse=True)
def _override_db(override_session: AsyncMock) -> None:
    """Auto-apply session override for all tests in this module."""


@pytest.mark.asyncio
async def test_request_with_active_consent_passes(
    override_session: AsyncMock,
) -> None:
    """Consent middleware allows requests when active consent exists."""
    patient_id = uuid.uuid4()
    transport = ASGITransport(app=app)

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
            return_value={"resourceType": "QuestionnaireResponse"}
        )

        async with AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/questionnaire-responses",
                json={
                    "patient_id": str(patient_id),
                    "transcript": "Je me sens bien",
                },
            )

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_request_without_consent_returns_403(
    override_session: AsyncMock,
) -> None:
    """Consent middleware rejects requests when no active consent."""
    patient_id = uuid.uuid4()
    transport = ASGITransport(app=app)

    with patch(
        "src.middleware.consent.ConsentService"
    ) as mock_consent_cls:
        mock_consent_cls.return_value.verify_consent = AsyncMock(
            return_value=False
        )

        async with AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/questionnaire-responses",
                json={
                    "patient_id": str(patient_id),
                    "transcript": "Je me sens bien",
                },
            )

    assert response.status_code == 403
    assert "No active consent" in response.json()["detail"]


@pytest.mark.asyncio
async def test_request_without_patient_id_returns_400(
    override_session: AsyncMock,
) -> None:
    """Consent middleware returns 400 when patient_id is missing."""
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport, base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/v1/questionnaire-responses",
            json={"transcript": "test"},
        )

    # Consent middleware runs before Pydantic validation and returns 400
    assert response.status_code == 400
