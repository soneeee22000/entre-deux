import uuid
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.engine import get_session
from src.main import app


@pytest.fixture
def mock_session() -> AsyncMock:
    """Provide a mock AsyncSession with common operations stubbed."""
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()
    session.get = AsyncMock(return_value=None)
    session.execute = AsyncMock()
    return session


@pytest.fixture
def patient_id() -> uuid.UUID:
    """Provide a deterministic test patient UUID."""
    return uuid.UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture
def sample_patient_fhir(patient_id: uuid.UUID) -> dict[str, Any]:
    """Provide a sample FHIR Patient resource."""
    return {
        "resourceType": "Patient",
        "id": str(patient_id),
        "identifier": [
            {"system": "https://entre-deux.health", "value": "TEST-001"}
        ],
        "name": [{"given": ["Jean"], "family": "Dupont"}],
    }


@pytest.fixture
def sample_observation_fhir(patient_id: uuid.UUID) -> dict[str, Any]:
    """Provide a sample FHIR Observation resource."""
    return {
        "resourceType": "Observation",
        "id": str(uuid.uuid4()),
        "status": "final",
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "59261-8",
                    "display": "HbA1c",
                }
            ]
        },
        "subject": {"reference": f"Patient/{patient_id}"},
        "valueQuantity": {"value": 6.5, "unit": "%"},
    }


@pytest.fixture
def sample_consent_fhir(patient_id: uuid.UUID) -> dict[str, Any]:
    """Provide a sample FHIR Consent resource."""
    return {
        "resourceType": "Consent",
        "id": str(uuid.uuid4()),
        "status": "active",
        "subject": {"reference": f"Patient/{patient_id}"},
    }


@pytest.fixture
def sample_composition_fhir(patient_id: uuid.UUID) -> dict[str, Any]:
    """Provide a sample FHIR Composition resource."""
    return {
        "resourceType": "Composition",
        "id": str(uuid.uuid4()),
        "status": "final",
        "type": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "11503-0",
                    "display": "Medical records",
                }
            ]
        },
        "subject": [{"reference": f"Patient/{patient_id}"}],
        "title": "Visit Brief",
        "section": [
            {
                "title": "Changements cles",
                "text": {
                    "status": "generated",
                    "div": "<div>test</div>",
                },
            },
        ],
    }


@pytest.fixture
def sample_qr_fhir(patient_id: uuid.UUID) -> dict[str, Any]:
    """Provide a sample FHIR QuestionnaireResponse resource."""
    return {
        "resourceType": "QuestionnaireResponse",
        "id": str(uuid.uuid4()),
        "status": "completed",
        "subject": {"reference": f"Patient/{patient_id}"},
        "item": [
            {
                "linkId": "transcript",
                "text": "Raw transcript",
                "answer": [{"valueString": "Je me sens fatigue"}],
            },
            {
                "linkId": "ai_response",
                "text": "AI empathetic response",
                "answer": [{"valueString": "Je comprends..."}],
            },
        ],
    }


def make_table_row(
    fhir_resource: dict[str, Any],
    row_id: uuid.UUID | None = None,
    **extra: Any,
) -> MagicMock:
    """Create a mock table row with common attributes."""
    row = MagicMock()
    row.id = row_id or uuid.uuid4()
    row.fhir_resource = fhir_resource
    for key, value in extra.items():
        setattr(row, key, value)
    return row


@pytest.fixture
def override_session(mock_session: AsyncMock) -> AsyncMock:
    """Override the get_session dependency with a mock session."""
    async def _override() -> AsyncSession:  # type: ignore[misc]
        return mock_session  # type: ignore[return-value]

    app.dependency_overrides[get_session] = _override
    yield mock_session
    app.dependency_overrides.clear()


@pytest.fixture
def async_client() -> ASGITransport:
    """Provide an ASGI transport for the test app."""
    return ASGITransport(app=app)


def mock_mistral_chat_response(content: str) -> MagicMock:
    """Create a mock Mistral chat.complete_async response."""
    message = MagicMock()
    message.content = content
    choice = MagicMock()
    choice.message = message
    response = MagicMock()
    response.choices = [choice]
    return response


def mock_mistral_ocr_response(markdown: str) -> MagicMock:
    """Create a mock Mistral OCR process_async response."""
    page = MagicMock()
    page.markdown = markdown
    response = MagicMock()
    response.pages = [page]
    return response
