from typing import Any

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_audit_service
from src.middleware.auth import get_current_patient_id
from src.services.audit_service import AuditService

router = APIRouter(prefix="/audit-events", tags=["audit-events"])


@router.get("")
async def list_audit_events(
    patient_ref: str = Query(description="FHIR patient reference"),  # noqa: B008
    limit: int = Query(default=100, le=1000),  # noqa: B008
    service: AuditService = Depends(get_audit_service),  # noqa: B008
    current_patient_id: str | None = Depends(get_current_patient_id),  # noqa: B008
) -> list[dict[str, Any]]:
    """List audit events for a patient."""
    if current_patient_id is not None:
        expected_ref = f"Patient/{current_patient_id}"
        if patient_ref != expected_ref:
            from fastapi import HTTPException

            raise HTTPException(
                status_code=403,
                detail="Acces interdit aux donnees d'un autre patient",
            )
    rows = await service.get_audit_trail(patient_ref, limit)
    return [row.fhir_resource for row in rows]
