import uuid
from typing import Any

from fastapi import APIRouter, Depends

from src.api.dependencies import get_visit_brief_service
from src.middleware.consent import require_consent
from src.models.schemas import GenerateVisitBriefRequest
from src.services.visit_brief_service import VisitBriefService

router = APIRouter(prefix="/compositions", tags=["compositions"])


@router.post(
    "/visit-brief",
    status_code=201,
    dependencies=[require_consent("ai-processing")],
)
async def generate_visit_brief(
    request: GenerateVisitBriefRequest,
    service: VisitBriefService = Depends(get_visit_brief_service),  # noqa: B008
) -> dict[str, Any]:
    """Generate a visit brief Composition from patient data."""
    return await service.generate(request.patient_id)


@router.get("/patients/{patient_id}")
async def list_patient_compositions(
    patient_id: uuid.UUID,
    service: VisitBriefService = Depends(get_visit_brief_service),  # noqa: B008
) -> list[dict[str, Any]]:
    """List all compositions for a patient."""
    return await service.list_compositions(patient_id)
