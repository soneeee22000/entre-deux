from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.brief_agent import BriefAgent
from src.agents.explanation_agent import ExplanationAgent
from src.agents.journal_agent import JournalAgent
from src.agents.ocr_agent import OCRAgent
from src.agents.transcribe_agent import TranscribeAgent
from src.config.settings import settings
from src.db.engine import get_session
from src.services.audit_service import AuditService
from src.services.consent_service import ConsentService
from src.services.journal_service import JournalService
from src.services.lab_result_service import LabResultService
from src.services.visit_brief_service import VisitBriefService


def get_consent_service(
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> ConsentService:
    """Provide a ConsentService instance."""
    return ConsentService(session)


def get_audit_service(
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> AuditService:
    """Provide an AuditService instance."""
    return AuditService(session)


def get_lab_result_service(
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> LabResultService:
    """Provide a LabResultService instance."""
    ocr = OCRAgent(settings.mistral_api_key, session)
    explanation = ExplanationAgent(settings.mistral_api_key, session)
    return LabResultService(ocr, explanation, session)


def get_journal_service(
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> JournalService:
    """Provide a JournalService instance."""
    agent = JournalAgent(settings.mistral_api_key, session)
    return JournalService(agent, session)


def get_transcribe_agent(
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> TranscribeAgent:
    """Provide a TranscribeAgent instance."""
    return TranscribeAgent(settings.mistral_api_key, session)


def get_visit_brief_service(
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> VisitBriefService:
    """Provide a VisitBriefService instance."""
    agent = BriefAgent(settings.mistral_api_key, session)
    return VisitBriefService(agent, session)
