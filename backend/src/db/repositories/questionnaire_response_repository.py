from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repositories.base_repository import BaseRepository
from src.db.tables import QuestionnaireResponseTable


class QuestionnaireResponseRepository(BaseRepository[QuestionnaireResponseTable]):
    """Repository for QuestionnaireResponse records."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(QuestionnaireResponseTable, session)
