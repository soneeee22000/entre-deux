from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repositories.base_repository import BaseRepository
from src.db.tables import PatientTable


class PatientRepository(BaseRepository[PatientTable]):
    """Repository for Patient records."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(PatientTable, session)

    async def get_by_identifier(self, identifier: str) -> PatientTable | None:
        """Find a patient by external identifier."""
        stmt = select(PatientTable).where(PatientTable.identifier == identifier)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
