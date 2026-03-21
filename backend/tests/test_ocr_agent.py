import json
from unittest.mock import AsyncMock, patch

import pytest

from src.agents.ocr_agent import OCRAgent, _normalize_results
from tests.conftest import mock_mistral_ocr_response


@pytest.mark.asyncio
async def test_extract_lab_results_full_pipeline(
    mock_session: AsyncMock,
) -> None:
    """extract_lab_results runs OCR then parses structured results."""
    agent = OCRAgent("fake-key", mock_session)

    ocr_response = mock_mistral_ocr_response("HbA1c: 6.5%")
    parsed_results = [
        {
            "test_name": "HbA1c",
            "loinc_code": "59261-8",
            "loinc_display": "HbA1c",
            "value": 6.5,
            "unit": "%",
            "reference_range_low": 4.0,
            "reference_range_high": 5.6,
        }
    ]

    with (
        patch.object(
            agent._client.ocr,
            "process_async",
            new_callable=AsyncMock,
            return_value=ocr_response,
        ),
        patch(
            "src.agents.ocr_agent.safe_chat_complete",
            new_callable=AsyncMock,
            return_value=json.dumps({"results": parsed_results}),
        ),
        patch(
            "src.agents.ocr_agent.safe_json_parse",
            return_value={"results": parsed_results},
        ),
        patch.object(
            agent._audit,
            "log_ai_call",
            new_callable=AsyncMock,
        ),
    ):
        results = await agent.extract_lab_results("base64data", "Patient/123")

    assert len(results) == 1
    assert results[0]["loinc_code"] == "59261-8"
    assert results[0]["value"] == 6.5
    assert results[0]["unit"] == "%"


def test_normalize_results_valid_data() -> None:
    """_normalize_results handles well-formed data."""
    raw = [
        {
            "test_name": "Glucose",
            "loinc_code": "2339-0",
            "loinc_display": "Glucose",
            "value": 5.2,
            "unit": "mmol/L",
            "reference_range_low": 3.9,
            "reference_range_high": 5.6,
        }
    ]
    result = _normalize_results(raw)
    assert len(result) == 1
    assert result[0]["loinc_code"] == "2339-0"
    assert result[0]["value"] == 5.2
    assert result[0]["reference_range_low"] == 3.9


def test_normalize_results_skips_invalid_values() -> None:
    """_normalize_results skips items with non-numeric values."""
    raw = [
        {"test_name": "Bad", "value": "not-a-number", "unit": "mg"},
        {"test_name": "Good", "value": 1.0, "unit": "mg"},
    ]
    result = _normalize_results(raw)
    assert len(result) == 1
    assert result[0]["value"] == 1.0


def test_normalize_results_handles_missing_ranges() -> None:
    """_normalize_results returns None for missing reference ranges."""
    raw = [
        {
            "test_name": "Test",
            "loinc_code": "unknown",
            "value": 10.0,
            "unit": "U/L",
        }
    ]
    result = _normalize_results(raw)
    assert result[0]["reference_range_low"] is None
    assert result[0]["reference_range_high"] is None
