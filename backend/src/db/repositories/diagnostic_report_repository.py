from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repositories.base_repository import BaseRepository
from src.db.tables import DiagnosticReportTable


class DiagnosticReportRepository(BaseRepository[DiagnosticReportTable]):
    """Repository for DiagnosticReport records."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(DiagnosticReportTable, session)
