import json
import uuid
from typing import Any

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.engine import get_session
from src.services.consent_service import ConsentService


def require_consent(scope: str) -> Any:
    """FastAPI dependency that enforces active consent for a given scope."""

    async def _verify(
        request: Request,
        session: AsyncSession = Depends(get_session),  # noqa: B008
    ) -> None:
        patient_id_raw = await _extract_patient_id(request)
        if patient_id_raw is None:
            raise HTTPException(
                status_code=400, detail="patient_id is required"
            )
        try:
            patient_id = uuid.UUID(str(patient_id_raw))
        except ValueError as exc:
            raise HTTPException(
                status_code=400, detail="Invalid patient_id format"
            ) from exc

        consent_svc = ConsentService(session)
        has_consent = await consent_svc.verify_consent(patient_id, scope)
        if not has_consent:
            raise HTTPException(
                status_code=403,
                detail=f"No active consent for scope '{scope}'",
            )

    return Depends(_verify)


async def _extract_patient_id(request: Request) -> str | None:
    """Extract patient_id from JSON body or multipart form data."""
    content_type = request.headers.get("content-type", "")

    if "multipart/form-data" in content_type:
        form = await request.form()
        value = form.get("patient_id")
        if value is None:
            return None
        return str(value)

    body_bytes = await request.body()
    if not body_bytes:
        return None
    try:
        body = json.loads(body_bytes)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    value = body.get("patient_id")
    return str(value) if value is not None else None
