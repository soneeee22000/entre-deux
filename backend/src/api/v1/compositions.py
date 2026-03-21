import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from slowapi import Limiter

from src.api.dependencies import get_visit_brief_service
from src.middleware.auth import get_current_patient_id, require_patient_match
from src.middleware.consent import require_consent
from src.middleware.rate_limit import AI_RATE_LIMIT, get_rate_limit_key
from src.models.schemas import GenerateVisitBriefRequest
from src.services.pdf_service import generate_visit_brief_pdf
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


@router.get("/{composition_id}/pdf")
async def download_composition_pdf(
    composition_id: uuid.UUID,
    service: VisitBriefService = Depends(get_visit_brief_service),  # noqa: B008
    current_patient_id: uuid.UUID | None = Depends(get_current_patient_id),  # noqa: B008
) -> StreamingResponse:
    """Download a composition as a PDF."""
    result = await service.get_composition_by_id(composition_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Composition introuvable.")

    fhir_resource, patient_id = result
    require_patient_match(patient_id, current_patient_id)

    patient_name = _extract_patient_name(fhir_resource)
    pdf_bytes = generate_visit_brief_pdf(fhir_resource, patient_name)

    date_str = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    filename = f"bilan-visite-{date_str}.pdf"

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _extract_patient_name(fhir_resource: dict[str, Any]) -> str:
    """Extract patient name from composition subject reference."""
    subjects = fhir_resource.get("subject", [])
    if isinstance(subjects, list) and subjects:
        display = subjects[0].get("display", "")
        if display:
            return str(display)
    return "Patient"


@router.get("/patients/{patient_id}")
async def list_patient_compositions(
    patient_id: uuid.UUID,
    service: VisitBriefService = Depends(get_visit_brief_service),  # noqa: B008
    current_patient_id: uuid.UUID | None = Depends(get_current_patient_id),  # noqa: B008
) -> list[dict[str, Any]]:
    """List all compositions for a patient."""
    require_patient_match(patient_id, current_patient_id)
    return await service.list_compositions(patient_id)
