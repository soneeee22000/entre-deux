from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repositories.base_repository import BaseRepository
from src.db.tables import AuditEventTable


class AuditEventRepository(BaseRepository[AuditEventTable]):
    """Repository for AuditEvent records."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(AuditEventTable, session)

    async def get_by_patient_ref(
        self, patient_ref: str, limit: int = 100
    ) -> list[AuditEventTable]:
        """List audit events for a patient reference."""
        stmt = (
            select(AuditEventTable)
            .where(AuditEventTable.patient_ref == patient_ref)
            .order_by(AuditEventTable.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
