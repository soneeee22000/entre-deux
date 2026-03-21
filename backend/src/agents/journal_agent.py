import json
from typing import Any

from mistralai import Mistral
from mistralai.models import ResponseFormat
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.mistral_utils import safe_chat_complete, safe_json_parse
from src.services.audit_service import AuditService

AGENT_NAME = "journal_agent"

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
        raw = await safe_chat_complete(
            self._client,
            model=self.MODEL,
            messages=[
                {"role": "system", "content": STRUCTURE_SYSTEM_PROMPT},
                {"role": "user", "content": transcript},
            ],
            response_format=ResponseFormat(type="json_object"),
            temperature=0.1,
            agent_name=f"{AGENT_NAME}.structure",
        )
        structured = safe_json_parse(raw, agent_name=f"{AGENT_NAME}.structure")

        await self._audit.log_ai_call(
            agent_name=f"{AGENT_NAME}.structure",
            model_version=self.MODEL,
            patient_ref=patient_ref,
            input_text=transcript,
            output_text=raw,
        )
        return structured

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
        raw = await safe_chat_complete(
            self._client,
            model=self.MODEL,
            messages=[
                {"role": "system", "content": RESPONSE_SYSTEM_PROMPT},
                {"role": "user", "content": context},
            ],
            response_format=ResponseFormat(type="json_object"),
            temperature=0.5,
            agent_name=f"{AGENT_NAME}.response",
        )
        parsed = safe_json_parse(raw, agent_name=f"{AGENT_NAME}.response")
        empathetic_response = parsed.get("response", raw)

        await self._audit.log_ai_call(
            agent_name=f"{AGENT_NAME}.response",
            model_version=self.MODEL,
            patient_ref=patient_ref,
            input_text=transcript,
            output_text=str(empathetic_response),
        )
        return str(empathetic_response)
