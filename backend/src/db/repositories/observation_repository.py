import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repositories.base_repository import BaseRepository
from src.db.tables import ObservationTable


class ObservationRepository(BaseRepository[ObservationTable]):
    """Repository for Observation records."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(ObservationTable, session)

    async def list_by_patient_and_code(
        self, patient_id: uuid.UUID, loinc_code: str, limit: int = 100
    ) -> list[ObservationTable]:
        """List observations for a patient filtered by LOINC code."""
        stmt = (
            select(ObservationTable)
            .where(
                ObservationTable.patient_id == patient_id,
                ObservationTable.loinc_code == loinc_code,
            )
            .order_by(ObservationTable.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
