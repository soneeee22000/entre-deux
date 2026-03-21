import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repositories.base_repository import BaseRepository
from src.db.tables import UserTable


class UserRepository(BaseRepository[UserTable]):
    """Repository for User records."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(UserTable, session)

    async def get_by_email(self, email: str) -> UserTable | None:
        """Find a user by email address."""
        stmt = select(UserTable).where(UserTable.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_patient_id(self, patient_id: uuid.UUID) -> UserTable | None:
        """Find a user by linked patient ID."""
        stmt = select(UserTable).where(UserTable.patient_id == patient_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
