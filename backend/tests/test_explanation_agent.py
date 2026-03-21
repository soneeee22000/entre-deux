import json
from unittest.mock import AsyncMock, patch

import pytest

from src.agents.explanation_agent import ExplanationAgent


@pytest.mark.asyncio
async def test_explain_results_returns_french_text(
    mock_session: AsyncMock,
) -> None:
    """explain_results returns a plain-French explanation string."""
    agent = ExplanationAgent("fake-key", mock_session)

    explanation = "Votre HbA1c est a 6.5%, ce qui est legerement au-dessus."

    with (
        patch(
            "src.agents.explanation_agent.safe_chat_complete",
            new_callable=AsyncMock,
            return_value=json.dumps({"explanation": explanation}),
        ),
        patch(
            "src.agents.explanation_agent.safe_json_parse",
            return_value={"explanation": explanation},
        ),
        patch.object(
            agent._audit,
            "log_ai_call",
            new_callable=AsyncMock,
        ),
    ):
        result = await agent.explain_results(
            [
                {
                    "loinc_display": "HbA1c",
                    "value": 6.5,
                    "unit": "%",
                    "reference_range_low": 4.0,
                    "reference_range_high": 5.6,
                }
            ],
            "Patient/123",
        )

    assert result == explanation


def test_format_observations_includes_ranges() -> None:
    """_format_observations includes reference ranges when present."""
    agent = ExplanationAgent.__new__(ExplanationAgent)

    observations = [
        {
            "loinc_display": "HbA1c",
            "value": 6.5,
            "unit": "%",
            "reference_range_low": 4.0,
            "reference_range_high": 5.6,
        }
    ]
    result = agent._format_observations(observations)

    assert "HbA1c" in result
    assert "6.5" in result
    assert "4.0" in result
    assert "5.6" in result


def test_format_observations_without_ranges() -> None:
    """_format_observations handles missing ranges."""
    agent = ExplanationAgent.__new__(ExplanationAgent)

    observations = [
        {
            "loinc_display": "Glucose",
            "value": 5.2,
            "unit": "mmol/L",
        }
    ]
    result = agent._format_observations(observations)

    assert "Glucose" in result
    assert "ref" not in result
