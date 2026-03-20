import uuid
from typing import Any

from fastapi import APIRouter, Depends

from src.api.dependencies import get_lab_result_service
from src.middleware.consent import require_consent
from src.models.schemas import AnalyzeLabImageRequest, CreateObservationRequest
from src.services.lab_result_service import LabResultService

router = APIRouter(prefix="/observations", tags=["observations"])


@router.post(
    "/analyze-image",
    status_code=201,
    dependencies=[require_consent("ai-processing")],
)
async def analyze_lab_image(
    request: AnalyzeLabImageRequest,
    service: LabResultService = Depends(get_lab_result_service),  # noqa: B008
) -> dict[str, Any]:
    """OCR a lab image, create Observations + DiagnosticReport."""
    return await service.analyze_image(request.patient_id, request.image_base64)


@router.post("", status_code=201)
async def create_observation(
    request: CreateObservationRequest,
    service: LabResultService = Depends(get_lab_result_service),  # noqa: B008
) -> dict[str, Any]:
    """Create a single observation manually."""
    row = await service.create_observation(
        patient_id=request.patient_id,
        loinc_code=request.loinc_code,
        loinc_display=request.loinc_display,
        value=request.value,
        unit=request.unit,
        reference_range_low=request.reference_range_low,
        reference_range_high=request.reference_range_high,
    )
    return row.fhir_resource


@router.get("/patients/{patient_id}")
async def list_patient_observations(
    patient_id: uuid.UUID,
    service: LabResultService = Depends(get_lab_result_service),  # noqa: B008
) -> list[dict[str, Any]]:
    """List all observations for a patient."""
    return await service.list_observations(patient_id)
