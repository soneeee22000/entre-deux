import json
from typing import Any

from mistralai import Mistral
from mistralai.models import ResponseFormat
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.audit_service import AuditService

STRUCTURE_SYSTEM_PROMPT = (
    "Tu es un assistant medical qui structure les entrees "
    "de journal de sante des patients.\n\n"
    "A partir du texte du patient, extrais:\n"
    "- symptoms: liste de symptomes mentionnes\n"
    "- emotional_state: etat emotionnel (ex: fatigue, "
    "anxieux, motive, triste)\n"
    "- medications_mentioned: medicaments mentionnes\n"
    "- severity: gravite globale (low, medium, high)\n\n"
    "Reponds en JSON:\n"
    '{"symptoms": [...], "emotional_state": "...", '
    '"medications_mentioned": [...], "severity": "..."}'
)

RESPONSE_SYSTEM_PROMPT = (
    "Tu es un compagnon bienveillant pour les patients "
    "atteints de maladies chroniques.\n\n"
    "Le patient vient de partager comment il se sent. "
    "Reponds avec empathie en francais.\n\n"
    "Regles:\n"
    "- Reconnais ses emotions et son experience\n"
    "- Ne minimise JAMAIS ce qu'il ressent\n"
    "- Ne fais pas de diagnostic medical\n"
    "- Si les symptomes semblent graves, suggere "
    "doucement de contacter son medecin\n"
    "- Sois chaleureux mais concis (3-5 phrases)\n"
    "- Tutoie le patient\n\n"
    "Reponds en JSON:\n"
    '{"response": "texte de la reponse empathique"}'
)


class JournalAgent:
    """Structures journal entries and generates empathetic responses."""

    MODEL = "mistral-small-latest"

    def __init__(self, api_key: str, session: AsyncSession) -> None:
        self._client = Mistral(api_key=api_key)
        self._audit = AuditService(session)

    async def structure_entry(
        self, transcript: str, patient_ref: str | None = None
    ) -> dict[str, Any]:
        """Extract structured data from a journal transcript."""
        response = await self._client.chat.complete_async(
            model=self.MODEL,
            messages=[
                {"role": "system", "content": STRUCTURE_SYSTEM_PROMPT},
                {"role": "user", "content": transcript},
            ],
            response_format=ResponseFormat(type="json_object"),
            temperature=0.1,
        )

        raw = response.choices[0].message.content  # type: ignore[union-attr]
        structured = json.loads(raw)  # type: ignore[arg-type]

        await self._audit.log_ai_call(
            agent_name="journal_agent.structure",
            model_version=self.MODEL,
            patient_ref=patient_ref,
            input_text=transcript,
            output_text=raw,
        )
        return structured  # type: ignore[no-any-return]

    async def generate_response(
        self,
        transcript: str,
        structured_data: dict[str, Any],
        patient_ref: str | None = None,
    ) -> str:
        """Generate an empathetic AI response to a journal entry."""
        context = (
            f"Le patient a dit: {transcript}\n\n"
            f"Donnees structurees: {json.dumps(structured_data, ensure_ascii=False)}"
        )
        response = await self._client.chat.complete_async(
            model=self.MODEL,
            messages=[
                {"role": "system", "content": RESPONSE_SYSTEM_PROMPT},
                {"role": "user", "content": context},
            ],
            response_format=ResponseFormat(type="json_object"),
            temperature=0.5,
        )

        raw = response.choices[0].message.content  # type: ignore[union-attr]
        parsed = json.loads(raw)  # type: ignore[arg-type]
        empathetic_response = parsed.get("response", raw)

        await self._audit.log_ai_call(
            agent_name="journal_agent.response",
            model_version=self.MODEL,
            patient_ref=patient_ref,
            input_text=transcript,
            output_text=str(empathetic_response),
        )
        return str(empathetic_response)
