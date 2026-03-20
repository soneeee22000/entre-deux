from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import settings
from src.db.repositories.audit_event_repository import AuditEventRepository
from src.db.tables import AuditEventTable
from src.models.fhir_helpers import create_audit_event


class AuditService:
    """Service for logging AI agent calls as FHIR AuditEvents."""

    def __init__(self, session: AsyncSession) -> None:
        self._repo = AuditEventRepository(session)
        self._session = session

    async def log_ai_call(
        self,
        agent_name: str,
        model_version: str,
        patient_ref: str | None = None,
        input_text: str | None = None,
        output_text: str | None = None,
    ) -> AuditEventTable | None:
        """Log an AI agent invocation as an audit event."""
        if not settings.audit_enabled:
            return None
        fhir_event = create_audit_event(agent_name, patient_ref)
        row = AuditEventTable(
            patient_ref=patient_ref,
            agent_name=agent_name,
            model_version=model_version,
            input_text=input_text,
            output_text=output_text,
            fhir_resource=fhir_event.model_dump(mode="json"),
        )
        created = await self._repo.create(row)
        await self._session.flush()
        return created

    async def get_audit_trail(
        self, patient_ref: str, limit: int = 100
    ) -> list[AuditEventTable]:
        """Retrieve the audit trail for a patient."""
        return await self._repo.get_by_patient_ref(patient_ref, limit)
