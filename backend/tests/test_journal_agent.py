import json
from unittest.mock import AsyncMock, patch

import pytest

from src.agents.journal_agent import JournalAgent
from tests.conftest import mock_mistral_chat_response


@pytest.mark.asyncio
async def test_structure_entry_returns_structured_data(
    mock_session: AsyncMock,
) -> None:
    """structure_entry parses LLM response into structured dict."""
    agent = JournalAgent("fake-key", mock_session)

    structured = {
        "symptoms": ["fatigue", "maux de tete"],
        "emotional_state": "anxieux",
        "medications_mentioned": ["metformine"],
        "severity": "medium",
    }
    chat_response = mock_mistral_chat_response(json.dumps(structured))

    with (
        patch.object(
            agent._client.chat,
            "complete_async",
            new_callable=AsyncMock,
            return_value=chat_response,
        ),
        patch.object(
            agent._audit,
            "log_ai_call",
            new_callable=AsyncMock,
        ),
    ):
        result = await agent.structure_entry(
            "Je me sens fatigue", "Patient/123"
        )

    assert result["symptoms"] == ["fatigue", "maux de tete"]
    assert result["emotional_state"] == "anxieux"
    assert result["severity"] == "medium"


@pytest.mark.asyncio
async def test_generate_response_returns_empathetic_text(
    mock_session: AsyncMock,
) -> None:
    """generate_response returns an empathetic response string."""
    agent = JournalAgent("fake-key", mock_session)

    response_text = "Je comprends que tu te sentes fatigue."
    chat_response = mock_mistral_chat_response(
        json.dumps({"response": response_text})
    )

    with (
        patch.object(
            agent._client.chat,
            "complete_async",
            new_callable=AsyncMock,
            return_value=chat_response,
        ),
        patch.object(
            agent._audit,
            "log_ai_call",
            new_callable=AsyncMock,
        ),
    ):
        result = await agent.generate_response(
            "Je me sens fatigue",
            {"symptoms": ["fatigue"]},
            "Patient/123",
        )

    assert result == response_text
