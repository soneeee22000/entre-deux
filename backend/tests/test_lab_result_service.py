import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.lab_result_service import LabResultService


@pytest.fixture
def mock_ocr_agent() -> AsyncMock:
    """Provide a mocked OCRAgent."""
    agent = AsyncMock()
    agent.extract_lab_results = AsyncMock(
        return_value=[
            {
                "loinc_code": "59261-8",
                "loinc_display": "HbA1c",
                "value": 6.5,
                "unit": "%",
                "reference_range_low": 4.0,
                "reference_range_high": 5.6,
            }
        ]
    )
    return agent


@pytest.fixture
def mock_explanation_agent() -> AsyncMock:
    """Provide a mocked ExplanationAgent."""
    agent = AsyncMock()
    agent.explain_results = AsyncMock(
        return_value="Votre HbA1c est legerement elevee."
    )
    return agent


@pytest.mark.asyncio
async def test_analyze_image_full_pipeline(
    mock_session: AsyncMock,
    mock_ocr_agent: AsyncMock,
    mock_explanation_agent: AsyncMock,
) -> None:
    """analyze_image calls OCR, creates observations, explains."""
    patient_id = uuid.uuid4()
    service = LabResultService(
        mock_ocr_agent, mock_explanation_agent, mock_session
    )

    mock_obs_row = MagicMock()
    mock_obs_row.id = uuid.uuid4()
    mock_obs_row.fhir_resource = {"resourceType": "Observation", "id": "temp"}

    with (
        patch.object(
            service._obs_repo,
            "create",
            new_callable=AsyncMock,
            return_value=mock_obs_row,
        ),
        patch.object(
            service._dr_repo,
            "create",
            new_callable=AsyncMock,
        ),
    ):
        result = await service.analyze_image(patient_id, "base64data")

    mock_ocr_agent.extract_lab_results.assert_called_once()
    mock_explanation_agent.explain_results.assert_called_once()
    assert "diagnostic_report" in result
    assert "observations" in result
    assert "explanation" in result
    assert result["explanation"] == "Votre HbA1c est legerement elevee."
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_create_observation_persists(
    mock_session: AsyncMock,
    mock_ocr_agent: AsyncMock,
    mock_explanation_agent: AsyncMock,
) -> None:
    """create_observation creates and persists a single observation."""
    patient_id = uuid.uuid4()
    service = LabResultService(
        mock_ocr_agent, mock_explanation_agent, mock_session
    )

    mock_row = MagicMock()
    mock_row.id = uuid.uuid4()
    mock_row.fhir_resource = {"resourceType": "Observation", "id": "temp"}

    with patch.object(
        service._obs_repo,
        "create",
        new_callable=AsyncMock,
        return_value=mock_row,
    ):
        result = await service.create_observation(
            patient_id=patient_id,
            loinc_code="59261-8",
            loinc_display="HbA1c",
            value=6.5,
            unit="%",
        )

    assert result.fhir_resource["resourceType"] == "Observation"
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_list_observations(
    mock_session: AsyncMock,
    mock_ocr_agent: AsyncMock,
    mock_explanation_agent: AsyncMock,
) -> None:
    """list_observations returns fhir_resources."""
    patient_id = uuid.uuid4()
    service = LabResultService(
        mock_ocr_agent, mock_explanation_agent, mock_session
    )

    mock_row = MagicMock()
    mock_row.fhir_resource = {"resourceType": "Observation"}

    with patch.object(
        service._obs_repo,
        "list_by_patient",
        new_callable=AsyncMock,
        return_value=[mock_row],
    ):
        result = await service.list_observations(patient_id)

    assert len(result) == 1
    assert result[0]["resourceType"] == "Observation"
