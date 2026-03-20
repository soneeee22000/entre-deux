from typing import Any

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_audit_service
from src.services.audit_service import AuditService

router = APIRouter(prefix="/audit-events", tags=["audit-events"])


@router.get("")
async def list_audit_events(
    patient_ref: str = Query(description="FHIR patient reference"),  # noqa: B008
    limit: int = Query(default=100, le=1000),  # noqa: B008
    service: AuditService = Depends(get_audit_service),  # noqa: B008
) -> list[dict[str, Any]]:
    """List audit events for a patient."""
    rows = await service.get_audit_trail(patient_ref, limit)
    return [row.fhir_resource for row in rows]
