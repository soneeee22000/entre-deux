import uuid
from typing import Any

from fastapi import APIRouter, Depends

from src.api.dependencies import get_journal_service
from src.middleware.consent import require_consent
from src.models.schemas import CreateJournalEntryRequest
from src.services.journal_service import JournalService

router = APIRouter(
    prefix="/questionnaire-responses", tags=["questionnaire-responses"]
)


@router.post(
    "",
    status_code=201,
    dependencies=[require_consent("ai-processing")],
)
async def create_questionnaire_response(
    request: CreateJournalEntryRequest,
    service: JournalService = Depends(get_journal_service),  # noqa: B008
) -> dict[str, Any]:
    """Create a journal entry as a FHIR QuestionnaireResponse."""
    return await service.create_entry(request.patient_id, request.transcript)


@router.get("/patients/{patient_id}")
async def list_patient_questionnaire_responses(
    patient_id: uuid.UUID,
    service: JournalService = Depends(get_journal_service),  # noqa: B008
) -> list[dict[str, Any]]:
    """List all journal entries for a patient."""
    return await service.list_entries(patient_id)
