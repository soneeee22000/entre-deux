import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.journal_service import JournalService


@pytest.fixture
def mock_journal_agent() -> AsyncMock:
    """Provide a mocked JournalAgent."""
    agent = AsyncMock()
    agent.structure_entry = AsyncMock(
        return_value={
            "symptoms": ["fatigue", "maux de tete"],
            "emotional_state": "anxieux",
            "medications_mentioned": [],
            "severity": "medium",
        }
    )
    agent.generate_response = AsyncMock(
        return_value="Je comprends que tu te sentes fatigue."
    )
    return agent


@pytest.mark.asyncio
async def test_create_entry_calls_agent_and_persists(
    mock_session: AsyncMock,
    mock_journal_agent: AsyncMock,
) -> None:
    """create_entry calls structure + response agents, then persists."""
    patient_id = uuid.uuid4()
    transcript = "Je me sens fatigue aujourd'hui"
    service = JournalService(mock_journal_agent, mock_session)

    with patch.object(
        service._repo, "create", new_callable=AsyncMock
    ) as mock_create:
        mock_row = MagicMock()
        mock_create.return_value = mock_row

        result = await service.create_entry(patient_id, transcript)

    mock_journal_agent.structure_entry.assert_called_once_with(
        transcript, f"Patient/{patient_id}"
    )
    mock_journal_agent.generate_response.assert_called_once()
    mock_create.assert_called_once()
    mock_session.commit.assert_called_once()
    assert result["resourceType"] == "QuestionnaireResponse"
    assert result["status"] == "completed"


@pytest.mark.asyncio
async def test_list_entries_returns_fhir_resources(
    mock_session: AsyncMock,
    mock_journal_agent: AsyncMock,
) -> None:
    """list_entries returns fhir_resource from each row."""
    patient_id = uuid.uuid4()
    service = JournalService(mock_journal_agent, mock_session)

    mock_row = MagicMock()
    mock_row.fhir_resource = {"resourceType": "QuestionnaireResponse"}

    with patch.object(
        service._repo,
        "list_by_patient",
        new_callable=AsyncMock,
        return_value=[mock_row],
    ):
        result = await service.list_entries(patient_id)

    assert len(result) == 1
    assert result[0]["resourceType"] == "QuestionnaireResponse"
