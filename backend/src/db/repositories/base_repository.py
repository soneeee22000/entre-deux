import uuid
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Generic async repository with CRUD operations."""

    def __init__(self, model: type[T], session: AsyncSession) -> None:
        self._model = model
        self._session = session

    async def create(self, entity: T) -> T:
        """Persist a new entity and return it."""
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def get_by_id(self, entity_id: uuid.UUID) -> T | None:
        """Fetch an entity by primary key."""
        return await self._session.get(self._model, entity_id)

    async def list_by_patient(
        self, patient_id: uuid.UUID, limit: int = 100
    ) -> list[T]:
        """List entities filtered by patient_id column."""
        stmt = (
            select(self._model)
            .where(self._model.patient_id == patient_id)
            .order_by(self._model.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
