import uuid
from typing import Any

from fastapi import APIRouter, Depends, Request
from slowapi import Limiter

from src.api.dependencies import get_visit_brief_service
from src.middleware.auth import get_current_patient_id, require_patient_match
from src.middleware.consent import require_consent
from src.middleware.rate_limit import AI_RATE_LIMIT, get_rate_limit_key
from src.models.schemas import GenerateVisitBriefRequest
from src.services.visit_brief_service import VisitBriefService

router = APIRouter(prefix="/compositions", tags=["compositions"])
limiter = Limiter(key_func=get_rate_limit_key)


@router.post(
    "/visit-brief",
    status_code=201,
    dependencies=[require_consent("ai-processing")],
)
@limiter.limit(AI_RATE_LIMIT)
async def generate_visit_brief(
    request: Request,
    body: GenerateVisitBriefRequest,
    service: VisitBriefService = Depends(get_visit_brief_service),  # noqa: B008
    current_patient_id: uuid.UUID | None = Depends(get_current_patient_id),  # noqa: B008
) -> dict[str, Any]:
    """Generate a visit brief Composition from patient data."""
    require_patient_match(body.patient_id, current_patient_id)
    return await service.generate(body.patient_id)


@router.get("/patients/{patient_id}")
async def list_patient_compositions(
    patient_id: uuid.UUID,
    service: VisitBriefService = Depends(get_visit_brief_service),  # noqa: B008
    current_patient_id: uuid.UUID | None = Depends(get_current_patient_id),  # noqa: B008
) -> list[dict[str, Any]]:
    """List all compositions for a patient."""
    require_patient_match(patient_id, current_patient_id)
    return await service.list_compositions(patient_id)
