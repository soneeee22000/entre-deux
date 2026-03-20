from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repositories.base_repository import BaseRepository
from src.db.tables import CompositionTable


class CompositionRepository(BaseRepository[CompositionTable]):
    """Repository for Composition records."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(CompositionTable, session)
