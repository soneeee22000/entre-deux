import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.brief_agent import BriefAgent
from src.db.repositories.composition_repository import CompositionRepository
from src.db.repositories.observation_repository import ObservationRepository
from src.db.repositories.questionnaire_response_repository import (
    QuestionnaireResponseRepository,
)
from src.db.tables import CompositionTable
from src.models.fhir_constants import COMPOSITION_TYPE_VISIT_BRIEF
from src.models.fhir_helpers import create_composition_visit_brief

logger = logging.getLogger(__name__)


class VisitBriefService:
    """Service for generating pre-appointment visit briefs."""

    def __init__(self, brief_agent: BriefAgent, session: AsyncSession) -> None:
        self._agent = brief_agent
        self._obs_repo = ObservationRepository(session)
        self._qr_repo = QuestionnaireResponseRepository(session)
        self._comp_repo = CompositionRepository(session)
        self._session = session

    async def generate(self, patient_id: uuid.UUID) -> dict[str, Any]:
        """Gather observations + journal entries, generate a visit brief Composition."""
        patient_ref = f"Patient/{patient_id}"

        try:
            obs_rows = await self._obs_repo.list_by_patient(patient_id)
            qr_rows = await self._qr_repo.list_by_patient(patient_id)

            observations = [r.fhir_resource for r in obs_rows]
            qr_data = [r.fhir_resource for r in qr_rows]

            brief_result = await self._agent.generate_brief(
                observations, qr_data, patient_ref
            )

            sections = []
            for section in brief_result.get("sections", []):
                sections.append({
                    "title": section["title"],
                    "text": {
                        "status": "generated",
                        "div": f"<div>{section['text']}</div>",
                    },
                })

            fhir_comp = create_composition_visit_brief(
                patient_ref, "Device/entre-deux", sections
            )
            row = CompositionTable(
                patient_id=patient_id,
                composition_type=COMPOSITION_TYPE_VISIT_BRIEF,
                fhir_resource=fhir_comp.model_dump(mode="json"),
            )
            await self._comp_repo.create(row)
            await self._session.commit()
        except Exception:
            await self._session.rollback()
            raise

        result = fhir_comp.model_dump(mode="json")
        result["_db_id"] = str(row.id)
        return result

    async def list_compositions(
        self, patient_id: uuid.UUID
    ) -> list[dict[str, Any]]:
        """List all compositions for a patient."""
        rows = await self._comp_repo.list_by_patient(patient_id)
        results = []
        for row in rows:
            resource = dict(row.fhir_resource)
            resource["_db_id"] = str(row.id)
            results.append(resource)
        return results

    async def get_composition_by_id(
        self, composition_id: uuid.UUID
    ) -> tuple[dict[str, Any], uuid.UUID] | None:
        """Get a composition by DB ID, returning (fhir_resource, patient_id)."""
        row = await self._comp_repo.get_by_id(composition_id)
        if row is None:
            return None
        return row.fhir_resource, row.patient_id
