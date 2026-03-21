import asyncio
import json
import logging
from typing import Any

from mistralai import Mistral
from mistralai.models import ImageURLChunk
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.mistral_utils import (
    AgentError,
    AgentTimeoutError,
    safe_chat_complete,
    safe_json_parse,
)
from src.services.audit_service import AuditService

logger = logging.getLogger(__name__)

AGENT_NAME = "ocr_agent"

# fmt: off
EXTRACTION_SYSTEM_PROMPT = (
    "Tu es un assistant medical specialise dans "
    "l'extraction de resultats de laboratoire.\n\n"
    "A partir du texte OCR d'un bilan sanguin, "
    "extrais TOUS les resultats sous forme JSON.\n\n"
    "Reponds UNIQUEMENT avec un JSON valide:\n"
    '{"results": [{"test_name": "...", '
    '"loinc_code": "code LOINC ou unknown", '
    '"loinc_display": "nom LOINC standard", '
    '"value": 6.5, "unit": "...", '
    '"reference_range_low": 4.0, '
    '"reference_range_high": 5.6}]}\n\n'
    "Codes LOINC courants pour le diabete:\n"
    "- HbA1c: 59261-8\n"
    "- Glucose a jeun: 2339-0\n"
    "- Creatinine: 2160-0\n"
    "- Cholesterol total: 2093-3\n"
    "- HDL: 2085-9\n"
    "- LDL: 13457-7\n"
    "- Triglycerides: 2571-8\n\n"
    "Si tu ne reconnais pas le code LOINC, utilise 'unknown'.\n"
    "Si les valeurs de reference ne sont pas visibles, mets null.\n"
    "La valeur doit etre un nombre (float), pas une chaine."
)
# fmt: on

OCR_TIMEOUT_SECONDS = 60.0


class OCRAgent:
    """Extracts structured data from lab result images."""

    OCR_MODEL = "mistral-ocr-latest"
    CHAT_MODEL = "mistral-small-latest"

    def __init__(self, api_key: str, session: AsyncSession) -> None:
        self._client = Mistral(api_key=api_key)
        self._audit = AuditService(session)

    async def extract_lab_results(
        self, image_base64: str, patient_ref: str | None = None
    ) -> list[dict[str, Any]]:
        """Extract structured lab results from a base64 image."""
        ocr_text = await self._run_ocr(image_base64)
        results = await self._parse_ocr_to_structured(ocr_text)

        await self._audit.log_ai_call(
            agent_name=AGENT_NAME,
            model_version=f"{self.OCR_MODEL}+{self.CHAT_MODEL}",
            patient_ref=patient_ref,
            input_text="[image]",
            output_text=json.dumps(results, ensure_ascii=False),
        )
        return results

    async def _run_ocr(self, image_base64: str) -> str:
        """Run Mistral OCR on a base64 image."""
        data_url = f"data:image/jpeg;base64,{image_base64}"
        try:
            response = await asyncio.wait_for(
                self._client.ocr.process_async(
                    model=self.OCR_MODEL,
                    document=ImageURLChunk(image_url=data_url),
                ),
                timeout=OCR_TIMEOUT_SECONDS,
            )
        except TimeoutError as exc:
            raise AgentTimeoutError(AGENT_NAME) from exc
        except Exception as exc:
            raise AgentError(AGENT_NAME, f"OCR processing failed: {exc}") from exc

        pages = response.pages or []
        return "\n\n".join(page.markdown for page in pages)

    async def _parse_ocr_to_structured(
        self, ocr_text: str
    ) -> list[dict[str, Any]]:
        """Parse OCR text into structured lab values via LLM."""
        from mistralai.models import ResponseFormat

        raw = await safe_chat_complete(
            self._client,
            model=self.CHAT_MODEL,
            messages=[
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        "Voici le texte OCR du bilan:\n\n"
                        f"{ocr_text}"
                    ),
                },
            ],
            response_format=ResponseFormat(type="json_object"),
            temperature=0.0,
            agent_name=AGENT_NAME,
        )
        parsed = safe_json_parse(raw, agent_name=AGENT_NAME)
        return _normalize_results(parsed.get("results", []))


def _normalize_results(
    raw_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Normalize and validate parsed lab results."""
    normalized: list[dict[str, Any]] = []
    for item in raw_results:
        try:
            value = float(item["value"])
        except (ValueError, TypeError, KeyError):
            logger.warning("Skipping invalid result: %s", item)
            continue

        display = item.get("loinc_display") or item.get("test_name", "Unknown")
        normalized.append({
            "loinc_code": str(item.get("loinc_code", "unknown")),
            "loinc_display": str(display),
            "value": value,
            "unit": str(item.get("unit", "")),
            "reference_range_low": _to_float(
                item.get("reference_range_low")
            ),
            "reference_range_high": _to_float(
                item.get("reference_range_high")
            ),
        })
    return normalized


def _to_float(val: Any) -> float | None:
    """Safely convert a value to float or None."""
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None
