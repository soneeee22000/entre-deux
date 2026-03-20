import json
from typing import Any

from mistralai import Mistral
from mistralai.models import ResponseFormat
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.audit_service import AuditService

BRIEF_SYSTEM_PROMPT = (
    "Tu es un assistant medical qui prepare des resumes "
    "de visite pour les patients chroniques.\n\n"
    "A partir des observations (resultats de labo) et des "
    "entrees de journal du patient, genere un resume "
    "structure pour son prochain rendez-vous medical.\n\n"
    "Le resume doit contenir ces sections:\n"
    "1. 'Changements cles' — ce qui a change depuis "
    "la derniere visite\n"
    "2. 'Evolution des symptomes' — tendances des "
    "symptomes rapportes\n"
    "3. 'Tendances biologiques' — evolution des "
    "valeurs de labo\n"
    "4. 'Questions suggerees' — questions pertinentes "
    "a poser au medecin\n\n"
    "Reponds en JSON:\n"
    '{"sections": [{"title": "...", "text": "..."}]}\n\n'
    "Ecris en francais, de maniere claire et concise. "
    "Le patient va montrer ce resume a son medecin."
)


class BriefAgent:
    """Generates visit briefs from patient data."""

    MODEL = "mistral-small-latest"

    def __init__(self, api_key: str, session: AsyncSession) -> None:
        self._client = Mistral(api_key=api_key)
        self._audit = AuditService(session)

    async def generate_brief(
        self,
        observations: list[dict[str, Any]],
        questionnaire_responses: list[dict[str, Any]],
        patient_ref: str | None = None,
    ) -> dict[str, Any]:
        """Generate a structured visit brief."""
        context = self._build_context(
            observations, questionnaire_responses
        )

        response = await self._client.chat.complete_async(
            model=self.MODEL,
            messages=[
                {"role": "system", "content": BRIEF_SYSTEM_PROMPT},
                {"role": "user", "content": context},
            ],
            response_format=ResponseFormat(type="json_object"),
            temperature=0.3,
        )

        raw = response.choices[0].message.content  # type: ignore[union-attr]
        parsed = json.loads(raw)  # type: ignore[arg-type]

        await self._audit.log_ai_call(
            agent_name="brief_agent",
            model_version=self.MODEL,
            patient_ref=patient_ref,
            input_text=context[:500],
            output_text=raw,
        )
        return parsed  # type: ignore[no-any-return]

    def _build_context(
        self,
        observations: list[dict[str, Any]],
        questionnaire_responses: list[dict[str, Any]],
    ) -> str:
        """Build context string from patient data."""
        parts: list[str] = ["RESULTATS DE LABORATOIRE:"]
        for obs in observations:
            code = obs.get("code", {})
            codings = code.get("coding", [{}])
            display = codings[0].get("display", "Test") if codings else "Test"
            vq = obs.get("valueQuantity", {})
            val = vq.get("value", "?")
            unit = vq.get("unit", "")
            parts.append(f"- {display}: {val} {unit}")

        parts.append("\nENTREES DE JOURNAL:")
        for qr in questionnaire_responses:
            items = qr.get("item", [])
            for item in items:
                if item.get("linkId") == "transcript":
                    answers = item.get("answer", [])
                    if answers:
                        text = answers[0].get("valueString", "")
                        parts.append(f"- {text}")

        return "\n".join(parts)
