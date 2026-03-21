import uuid
from typing import Any

from fastapi import APIRouter, Depends, Form, HTTPException, Request, UploadFile
from slowapi import Limiter

from src.agents.transcribe_agent import TranscribeAgent
from src.api.dependencies import get_journal_service, get_transcribe_agent
from src.middleware.auth import get_current_patient_id, require_patient_match
from src.middleware.consent import require_consent
from src.middleware.rate_limit import AI_RATE_LIMIT, get_rate_limit_key
from src.models.schemas import CreateJournalEntryRequest
from src.services.journal_service import JournalService

router = APIRouter(
    prefix="/questionnaire-responses", tags=["questionnaire-responses"]
)
limiter = Limiter(key_func=get_rate_limit_key)

ALLOWED_AUDIO_TYPES = {
    "audio/webm",
    "audio/wav",
    "audio/mp4",
    "audio/mpeg",
    "audio/ogg",
    "audio/x-wav",
}
MAX_AUDIO_SIZE_BYTES = 10 * 1024 * 1024


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


@router.post(
    "/audio",
    status_code=201,
    dependencies=[require_consent("ai-processing")],
)
@limiter.limit(AI_RATE_LIMIT)
async def create_questionnaire_response_audio(
    request: Request,
    patient_id: uuid.UUID = Form(...),  # noqa: B008
    audio: UploadFile = ...,  # type: ignore[assignment]
    transcriber: TranscribeAgent = Depends(get_transcribe_agent),  # noqa: B008
    service: JournalService = Depends(get_journal_service),  # noqa: B008
    current_patient_id: uuid.UUID | None = Depends(get_current_patient_id),  # noqa: B008
) -> dict[str, Any]:
    """Transcribe audio then create a journal entry."""
    require_patient_match(patient_id, current_patient_id)
    _validate_audio_upload(audio)

    audio_bytes = await audio.read()
    if len(audio_bytes) > MAX_AUDIO_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail="Fichier audio trop volumineux (max 10 Mo).",
        )

    patient_ref = f"Patient/{patient_id}"
    filename = audio.filename or "recording.webm"
    transcript = await transcriber.transcribe(
        audio_bytes, filename, patient_ref
    )
    return await service.create_entry(patient_id, transcript)


def _validate_audio_upload(audio: UploadFile) -> None:
    """Validate audio file content type."""
    content_type = audio.content_type or ""
    if content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status_code=415,
            detail=(
                f"Type audio non supporte: {content_type}. "
                f"Formats acceptes: webm, wav, mp4, mpeg."
            ),
        )


@router.get("/patients/{patient_id}")
async def list_patient_questionnaire_responses(
    patient_id: uuid.UUID,
    service: JournalService = Depends(get_journal_service),  # noqa: B008
    current_patient_id: uuid.UUID | None = Depends(get_current_patient_id),  # noqa: B008
) -> list[dict[str, Any]]:
    """List all journal entries for a patient."""
    require_patient_match(patient_id, current_patient_id)
    return await service.list_entries(patient_id)
