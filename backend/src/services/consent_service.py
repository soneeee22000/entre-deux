import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from src.db.repositories.consent_repository import ConsentRepository
from src.db.tables import ConsentTable
from src.models.fhir_helpers import create_consent


class ConsentService:
    """Service for managing patient consent records."""

    def __init__(self, session: AsyncSession) -> None:
        self._repo = ConsentRepository(session)
        self._session = session

    async def record_consent(
        self, patient_id: uuid.UUID, scope: str
    ) -> ConsentTable:
        """Record a new consent for a patient."""
        patient_ref = f"Patient/{patient_id}"
        fhir_consent = create_consent(patient_ref, scope)
        row = ConsentTable(
            patient_id=patient_id,
            scope=scope,
            active=True,
            fhir_resource=fhir_consent.model_dump(mode="json"),
        )
        created = await self._repo.create(row)
        created.fhir_resource["id"] = str(created.id)
        flag_modified(created, "fhir_resource")
        await self._session.commit()
        return created

    async def verify_consent(
        self, patient_id: uuid.UUID, scope: str
    ) -> bool:
        """Check whether an active consent exists for the given scope."""
        consent = await self._repo.get_active_consent(patient_id, scope)
        return consent is not None

    async def revoke_consent(
        self, consent_id: uuid.UUID
    ) -> ConsentTable | None:
        """Revoke an existing consent by setting active=False."""
        row = await self._repo.get_by_id(consent_id)
        if row is None:
            return None
        row.active = False
        row.fhir_resource["status"] = "inactive"
        flag_modified(row, "fhir_resource")
        await self._session.commit()
        await self._session.refresh(row)
        return row
