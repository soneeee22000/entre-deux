import uuid
from typing import Any

from fastapi import APIRouter, Depends, Request
from slowapi import Limiter

from src.api.dependencies import get_lab_result_service
from src.middleware.auth import get_current_patient_id, require_patient_match
from src.middleware.consent import require_consent
from src.middleware.rate_limit import AI_RATE_LIMIT, get_rate_limit_key
from src.models.schemas import AnalyzeLabImageRequest, CreateObservationRequest
from src.services.lab_result_service import LabResultService

router = APIRouter(prefix="/observations", tags=["observations"])
limiter = Limiter(key_func=get_rate_limit_key)


@router.post(
    "/analyze-image",
    status_code=201,
    dependencies=[require_consent("ai-processing")],
)
@limiter.limit(AI_RATE_LIMIT)
async def analyze_lab_image(
    request: Request,
    body: AnalyzeLabImageRequest,
    service: LabResultService = Depends(get_lab_result_service),  # noqa: B008
    current_patient_id: uuid.UUID | None = Depends(get_current_patient_id),  # noqa: B008
) -> dict[str, Any]:
    """OCR a lab image, create Observations + DiagnosticReport."""
    require_patient_match(body.patient_id, current_patient_id)
    return await service.analyze_image(body.patient_id, body.image_base64)


@router.post("", status_code=201)
async def create_observation(
    body: CreateObservationRequest,
    service: LabResultService = Depends(get_lab_result_service),  # noqa: B008
    current_patient_id: uuid.UUID | None = Depends(get_current_patient_id),  # noqa: B008
) -> dict[str, Any]:
    """Create a single observation manually."""
    require_patient_match(body.patient_id, current_patient_id)
    row = await service.create_observation(
        patient_id=body.patient_id,
        loinc_code=body.loinc_code,
        loinc_display=body.loinc_display,
        value=body.value,
        unit=body.unit,
        reference_range_low=body.reference_range_low,
        reference_range_high=body.reference_range_high,
    )
    return row.fhir_resource


@router.get("/patients/{patient_id}")
async def list_patient_observations(
    patient_id: uuid.UUID,
    service: LabResultService = Depends(get_lab_result_service),  # noqa: B008
    current_patient_id: uuid.UUID | None = Depends(get_current_patient_id),  # noqa: B008
) -> list[dict[str, Any]]:
    """List all observations for a patient."""
    require_patient_match(patient_id, current_patient_id)
    return await service.list_observations(patient_id)
