import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_consent_service
from src.db.engine import get_session
from src.db.repositories.consent_repository import ConsentRepository
from src.models.schemas import CreateConsentRequest
from src.services.consent_service import ConsentService

router = APIRouter(prefix="/consents", tags=["consents"])


@router.post("", status_code=201)
async def create_consent(
    request: CreateConsentRequest,
    service: ConsentService = Depends(get_consent_service),  # noqa: B008
) -> dict[str, Any]:
    """Record a new patient consent."""
    row = await service.record_consent(request.patient_id, request.scope)
    return row.fhir_resource


@router.put("/{consent_id}/revoke")
async def revoke_consent(
    consent_id: uuid.UUID,
    service: ConsentService = Depends(get_consent_service),  # noqa: B008
) -> dict[str, Any]:
    """Revoke an existing consent."""
    row = await service.revoke_consent(consent_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Consent not found")
    return row.fhir_resource


@router.get("/patients/{patient_id}")
async def list_patient_consents(
    patient_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> list[dict[str, Any]]:
    """List all consents for a patient."""
    repo = ConsentRepository(session)
    rows = await repo.list_by_patient(patient_id)
    return [row.fhir_resource for row in rows]
