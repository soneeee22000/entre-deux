import json
from unittest.mock import AsyncMock, patch

import pytest

from src.agents.brief_agent import BriefAgent
from tests.conftest import mock_mistral_chat_response


@pytest.mark.asyncio
async def test_generate_brief_returns_sections(
    mock_session: AsyncMock,
) -> None:
    """generate_brief returns structured sections from LLM."""
    agent = BriefAgent("fake-key", mock_session)

    brief_data = {
        "sections": [
            {"title": "Changements cles", "text": "HbA1c en hausse"},
            {"title": "Evolution des symptomes", "text": "Fatigue"},
            {"title": "Tendances biologiques", "text": "Stable"},
            {"title": "Questions suggerees", "text": "Demander ajustement"},
        ]
    }
    chat_response = mock_mistral_chat_response(json.dumps(brief_data))

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
        result = await agent.generate_brief(
            observations=[],
            questionnaire_responses=[],
            patient_ref="Patient/123",
        )

    assert len(result["sections"]) == 4
    assert result["sections"][0]["title"] == "Changements cles"


def test_build_context_formats_data() -> None:
    """_build_context formats observations and journal entries."""
    agent = BriefAgent.__new__(BriefAgent)

    observations = [
        {
            "code": {"coding": [{"display": "HbA1c"}]},
            "valueQuantity": {"value": 6.5, "unit": "%"},
        }
    ]
    qr_data = [
        {
            "item": [
                {
                    "linkId": "transcript",
                    "answer": [{"valueString": "Je me sens bien"}],
                }
            ]
        }
    ]

    context = agent._build_context(observations, qr_data)

    assert "HbA1c" in context
    assert "6.5" in context
    assert "Je me sens bien" in context
