import uuid
from typing import Any

from fastapi import APIRouter, Depends, Request
from slowapi import Limiter

from src.api.dependencies import get_journal_service
from src.middleware.auth import get_current_patient_id, require_patient_match
from src.middleware.consent import require_consent
from src.middleware.rate_limit import AI_RATE_LIMIT, get_rate_limit_key
from src.models.schemas import CreateJournalEntryRequest
from src.services.journal_service import JournalService

router = APIRouter(
    prefix="/questionnaire-responses", tags=["questionnaire-responses"]
)
limiter = Limiter(key_func=get_rate_limit_key)


@router.post(
    "",
    status_code=201,
    dependencies=[require_consent("ai-processing")],
)
@limiter.limit(AI_RATE_LIMIT)
async def create_questionnaire_response(
    request: Request,
    body: CreateJournalEntryRequest,
    service: JournalService = Depends(get_journal_service),  # noqa: B008
    current_patient_id: uuid.UUID | None = Depends(get_current_patient_id),  # noqa: B008
) -> dict[str, Any]:
    """Create a journal entry as a FHIR QuestionnaireResponse."""
    require_patient_match(body.patient_id, current_patient_id)
    return await service.create_entry(body.patient_id, body.transcript)


@router.get("/patients/{patient_id}")
async def list_patient_questionnaire_responses(
    patient_id: uuid.UUID,
    service: JournalService = Depends(get_journal_service),  # noqa: B008
    current_patient_id: uuid.UUID | None = Depends(get_current_patient_id),  # noqa: B008
) -> list[dict[str, Any]]:
    """List all journal entries for a patient."""
    require_patient_match(patient_id, current_patient_id)
    return await service.list_entries(patient_id)
