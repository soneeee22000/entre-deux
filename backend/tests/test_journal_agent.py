import json
from unittest.mock import AsyncMock, patch

import pytest

from src.agents.journal_agent import JournalAgent


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

    with (
        patch(
            "src.agents.journal_agent.safe_chat_complete",
            new_callable=AsyncMock,
            return_value=json.dumps(structured),
        ),
        patch(
            "src.agents.journal_agent.safe_json_parse",
            return_value=structured,
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

    with (
        patch(
            "src.agents.journal_agent.safe_chat_complete",
            new_callable=AsyncMock,
            return_value=json.dumps({"response": response_text}),
        ),
        patch(
            "src.agents.journal_agent.safe_json_parse",
            return_value={"response": response_text},
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
