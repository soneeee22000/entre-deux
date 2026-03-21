import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.visit_brief_service import VisitBriefService


@pytest.fixture
def mock_brief_agent() -> AsyncMock:
    """Provide a mocked BriefAgent."""
    agent = AsyncMock()
    agent.generate_brief = AsyncMock(
        return_value={
            "sections": [
                {
                    "title": "Changements cles",
                    "text": "Augmentation de l'HbA1c",
                },
                {
                    "title": "Evolution des symptomes",
                    "text": "Fatigue persistante",
                },
            ]
        }
    )
    return agent


@pytest.mark.asyncio
async def test_generate_calls_agent_and_persists(
    mock_session: AsyncMock,
    mock_brief_agent: AsyncMock,
) -> None:
    """generate fetches data, calls agent, persists composition."""
    patient_id = uuid.uuid4()
    service = VisitBriefService(mock_brief_agent, mock_session)

    with (
        patch.object(
            service._obs_repo,
            "list_by_patient",
            new_callable=AsyncMock,
            return_value=[],
        ),
        patch.object(
            service._qr_repo,
            "list_by_patient",
            new_callable=AsyncMock,
            return_value=[],
        ),
        patch.object(
            service._comp_repo,
            "create",
            new_callable=AsyncMock,
        ),
    ):
        result = await service.generate(patient_id)

    mock_brief_agent.generate_brief.assert_called_once()
    mock_session.commit.assert_called_once()
    assert result["resourceType"] == "Composition"
    assert result["title"] == "Bilan de visite"


@pytest.mark.asyncio
async def test_list_compositions(
    mock_session: AsyncMock,
    mock_brief_agent: AsyncMock,
) -> None:
    """list_compositions returns fhir_resources."""
    patient_id = uuid.uuid4()
    service = VisitBriefService(mock_brief_agent, mock_session)

    mock_row = MagicMock()
    mock_row.fhir_resource = {"resourceType": "Composition"}

    with patch.object(
        service._comp_repo,
        "list_by_patient",
        new_callable=AsyncMock,
        return_value=[mock_row],
    ):
        result = await service.list_compositions(patient_id)

    assert len(result) == 1
    assert result[0]["resourceType"] == "Composition"
