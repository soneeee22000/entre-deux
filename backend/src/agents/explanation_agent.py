from typing import Any

from mistralai import Mistral
from mistralai.models import ResponseFormat
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.mistral_utils import safe_chat_complete, safe_json_parse
from src.services.audit_service import AuditService

AGENT_NAME = "explanation_agent"

EXPLANATION_SYSTEM_PROMPT = (
    "Tu es un assistant medical bienveillant qui explique "
    "les resultats de laboratoire en francais simple.\n\n"
    "Le patient n'est PAS medecin. Utilise un langage "
    "accessible, chaleureux et rassurant.\n\n"
    "Pour chaque resultat:\n"
    "- Explique ce que le test mesure\n"
    "- Dis si la valeur est normale, haute ou basse\n"
    "- Explique ce que ca signifie concretement\n"
    "- Si pertinent, mentionne les tendances\n\n"
    "Ne fais JAMAIS de diagnostic. Dis toujours au patient "
    "d'en parler avec son medecin pour les valeurs anormales.\n\n"
    "Reponds en JSON:\n"
    '{"explanation": "texte complet en francais"}'
)


class ExplanationAgent:
    """Plain-French explanations of lab results via Mistral Small."""

    MODEL = "mistral-small-latest"

    def __init__(self, api_key: str, session: AsyncSession) -> None:
        self._client = Mistral(api_key=api_key)
        self._audit = AuditService(session)

    async def explain_results(
        self,
        observations: list[dict[str, Any]],
        patient_ref: str | None = None,
    ) -> str:
        """Generate a plain-French explanation of lab observations."""
        summary = self._format_observations(observations)

        raw = await safe_chat_complete(
            self._client,
            model=self.MODEL,
            messages=[
                {"role": "system", "content": EXPLANATION_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        "Voici mes resultats de labo:\n\n"
                        f"{summary}"
                    ),
                },
            ],
            response_format=ResponseFormat(type="json_object"),
            temperature=0.3,
            agent_name=AGENT_NAME,
        )
        parsed = safe_json_parse(raw, agent_name=AGENT_NAME)
        explanation = parsed.get("explanation", raw)

        await self._audit.log_ai_call(
            agent_name=AGENT_NAME,
            model_version=self.MODEL,
            patient_ref=patient_ref,
            input_text=summary,
            output_text=str(explanation),
        )
        return str(explanation)

    def _format_observations(
        self, observations: list[dict[str, Any]]
    ) -> str:
        """Format observations into a readable summary for the LLM."""
        lines: list[str] = []
        for obs in observations:
            line = (
                f"- {obs.get('loinc_display', 'Test')}: "
                f"{obs.get('value', '?')} {obs.get('unit', '')}"
            )
            low = obs.get("reference_range_low")
            high = obs.get("reference_range_high")
            if low is not None or high is not None:
                line += f" (ref: {low or '?'}-{high or '?'})"
            lines.append(line)
        return "\n".join(lines)
