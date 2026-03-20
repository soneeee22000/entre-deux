import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repositories.base_repository import BaseRepository
from src.db.tables import ConsentTable


class ConsentRepository(BaseRepository[ConsentTable]):
    """Repository for Consent records."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(ConsentTable, session)

    async def get_active_consent(
        self, patient_id: uuid.UUID, scope: str
    ) -> ConsentTable | None:
        """Find an active consent for a patient and scope."""
        stmt = select(ConsentTable).where(
            ConsentTable.patient_id == patient_id,
            ConsentTable.scope == scope,
            ConsentTable.active.is_(True),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
