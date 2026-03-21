import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.explanation_agent import ExplanationAgent
from src.agents.ocr_agent import OCRAgent
from src.db.repositories.diagnostic_report_repository import (
    DiagnosticReportRepository,
)
from src.db.repositories.observation_repository import ObservationRepository
from src.db.tables import DiagnosticReportTable, ObservationTable
from src.models.fhir_helpers import create_diagnostic_report, create_observation

logger = logging.getLogger(__name__)


class LabResultService:
    """Service for orchestrating lab result analysis pipeline."""

    def __init__(
        self,
        ocr_agent: OCRAgent,
        explanation_agent: ExplanationAgent,
        session: AsyncSession,
    ) -> None:
        self._ocr = ocr_agent
        self._explanation = explanation_agent
        self._obs_repo = ObservationRepository(session)
        self._dr_repo = DiagnosticReportRepository(session)
        self._session = session

    async def analyze_image(
        self, patient_id: uuid.UUID, image_base64: str
    ) -> dict[str, Any]:
        """OCR an image, create Observations + DiagnosticReport, explain, persist."""
        patient_ref = f"Patient/{patient_id}"

        try:
            extracted = await self._ocr.extract_lab_results(image_base64, patient_ref)

            obs_rows: list[ObservationTable] = []
            obs_refs: list[str] = []
            for item in extracted:
                fhir_obs = create_observation(
                    patient_ref=patient_ref,
                    loinc_code=item["loinc_code"],
                    loinc_display=item["loinc_display"],
                    value=item["value"],
                    unit=item["unit"],
                    reference_range_low=item.get("reference_range_low"),
                    reference_range_high=item.get("reference_range_high"),
                )
                row = ObservationTable(
                    patient_id=patient_id,
                    loinc_code=item["loinc_code"],
                    fhir_resource=fhir_obs.model_dump(mode="json"),
                )
                created = await self._obs_repo.create(row)
                created.fhir_resource["id"] = str(created.id)
                obs_rows.append(created)
                obs_refs.append(f"Observation/{created.id}")

            fhir_dr = create_diagnostic_report(patient_ref, obs_refs)
            dr_row = DiagnosticReportTable(
                patient_id=patient_id,
                fhir_resource=fhir_dr.model_dump(mode="json"),
            )
            await self._dr_repo.create(dr_row)

            explanation = await self._explanation.explain_results(
                extracted, patient_ref
            )
            await self._session.commit()
        except Exception:
            await self._session.rollback()
            raise

        return {
            "diagnostic_report": fhir_dr.model_dump(mode="json"),
            "observations": [r.fhir_resource for r in obs_rows],
            "explanation": explanation,
        }

    async def create_observation(
        self, patient_id: uuid.UUID, **kwargs: Any
    ) -> ObservationTable:
        """Create a single observation manually."""
        patient_ref = f"Patient/{patient_id}"
        fhir_obs = create_observation(patient_ref=patient_ref, **kwargs)
        row = ObservationTable(
            patient_id=patient_id,
            loinc_code=kwargs["loinc_code"],
            fhir_resource=fhir_obs.model_dump(mode="json"),
        )
        created = await self._obs_repo.create(row)
        created.fhir_resource["id"] = str(created.id)
        await self._session.commit()
        return created

    async def list_observations(
        self, patient_id: uuid.UUID
    ) -> list[dict[str, Any]]:
        """List all observations for a patient."""
        rows = await self._obs_repo.list_by_patient(patient_id)
        return [row.fhir_resource for row in rows]
