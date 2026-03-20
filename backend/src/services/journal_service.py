import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.journal_agent import JournalAgent
from src.db.repositories.questionnaire_response_repository import (
    QuestionnaireResponseRepository,
)
from src.db.tables import QuestionnaireResponseTable
from src.models.fhir_helpers import create_questionnaire_response


class JournalService:
    """Service for managing journal entries as FHIR QuestionnaireResponses."""

    def __init__(self, journal_agent: JournalAgent, session: AsyncSession) -> None:
        self._agent = journal_agent
        self._repo = QuestionnaireResponseRepository(session)
        self._session = session

    async def create_entry(
        self, patient_id: uuid.UUID, transcript: str
    ) -> dict[str, Any]:
        """Structure transcript, generate response, persist as QR."""
        patient_ref = f"Patient/{patient_id}"

        structured = await self._agent.structure_entry(transcript, patient_ref)
        ai_response = await self._agent.generate_response(
            transcript, structured, patient_ref
        )

        items = [
            {
                "linkId": "transcript",
                "text": "Raw transcript",
                "answer": [{"valueString": transcript}],
            },
            {
                "linkId": "symptoms",
                "text": "Symptoms",
                "answer": [
                    {"valueString": s} for s in structured.get("symptoms", [])
                ],
            },
            {
                "linkId": "emotional_state",
                "text": "Emotional state",
                "answer": [
                    {"valueString": structured.get("emotional_state", "")}
                ],
            },
            {
                "linkId": "ai_response",
                "text": "AI empathetic response",
                "answer": [{"valueString": ai_response}],
            },
        ]

        fhir_qr = create_questionnaire_response(patient_ref, items)
        row = QuestionnaireResponseTable(
            patient_id=patient_id,
            fhir_resource=fhir_qr.model_dump(mode="json"),
        )
        await self._repo.create(row)
        await self._session.commit()

        return fhir_qr.model_dump(mode="json")

    async def list_entries(
        self, patient_id: uuid.UUID
    ) -> list[dict[str, Any]]:
        """List all journal entries for a patient."""
        rows = await self._repo.list_by_patient(patient_id)
        return [row.fhir_resource for row in rows]
