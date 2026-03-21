import asyncio
import logging

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.mistral_utils import AgentError, AgentTimeoutError
from src.services.audit_service import AuditService

logger = logging.getLogger(__name__)

AGENT_NAME = "transcribe_agent"
TRANSCRIBE_MODEL = "mistral-audio-latest"
TRANSCRIBE_URL = "https://api.mistral.ai/v1/audio/transcriptions"
TRANSCRIBE_TIMEOUT_SECONDS = 60.0


class TranscribeAgent:
    """Transcribes audio files using Mistral Voxtral."""

    def __init__(self, api_key: str, session: AsyncSession) -> None:
        self._api_key = api_key
        self._audit = AuditService(session)

    async def transcribe(
        self,
        audio_bytes: bytes,
        filename: str,
        patient_ref: str | None = None,
    ) -> str:
        """Transcribe audio bytes to text via Mistral REST API."""
        try:
            transcript = await asyncio.wait_for(
                self._call_transcribe_api(audio_bytes, filename),
                timeout=TRANSCRIBE_TIMEOUT_SECONDS,
            )
        except (TimeoutError, asyncio.TimeoutError) as exc:
            raise AgentTimeoutError(AGENT_NAME) from exc
        except AgentError:
            raise
        except Exception as exc:
            raise AgentError(
                AGENT_NAME, f"Transcription failed: {exc}"
            ) from exc

        await self._audit.log_ai_call(
            agent_name=AGENT_NAME,
            model_version=TRANSCRIBE_MODEL,
            patient_ref=patient_ref,
            input_text=f"[audio:{filename}]",
            output_text=transcript,
        )
        return transcript

    async def _call_transcribe_api(
        self, audio_bytes: bytes, filename: str
    ) -> str:
        """Send audio to Mistral transcription endpoint."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                TRANSCRIBE_URL,
                headers={"Authorization": f"Bearer {self._api_key}"},
                files={"file": (filename, audio_bytes)},
                data={"model": TRANSCRIBE_MODEL},
                timeout=TRANSCRIBE_TIMEOUT_SECONDS,
            )

        if response.status_code != 200:
            detail = response.text[:200]
            raise AgentError(
                AGENT_NAME,
                f"API returned {response.status_code}: {detail}",
            )

        data = response.json()
        text = data.get("text", "")
        if not text:
            raise AgentError(AGENT_NAME, "Empty transcription result")
        return str(text)
