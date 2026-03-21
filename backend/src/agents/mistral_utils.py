import asyncio
import json
import logging
from typing import Any

from mistralai import Mistral
from mistralai.models import ResponseFormat

logger = logging.getLogger(__name__)


class AgentError(Exception):
    """Raised when an AI agent call fails."""

    def __init__(self, agent_name: str, detail: str) -> None:
        self.agent_name = agent_name
        self.detail = detail
        super().__init__(f"[{agent_name}] {detail}")


class AgentTimeoutError(AgentError):
    """Raised when an AI agent call times out."""

    def __init__(self, agent_name: str) -> None:
        super().__init__(agent_name, "Request timed out")


async def safe_chat_complete(
    client: Mistral,
    *,
    model: str,
    messages: list[dict[str, str]],
    response_format: ResponseFormat | None = None,
    temperature: float = 0.3,
    timeout_seconds: float = 30.0,
    agent_name: str = "unknown",
) -> str:
    """Call Mistral chat API with timeout and error handling."""
    try:
        response = await asyncio.wait_for(
            client.chat.complete_async(
                model=model,
                messages=messages,
                response_format=response_format,
                temperature=temperature,
            ),
            timeout=timeout_seconds,
        )
    except (TimeoutError, asyncio.TimeoutError) as exc:
        logger.error(
            "[%s] Mistral API timed out after %ss", agent_name, timeout_seconds
        )
        raise AgentTimeoutError(agent_name) from exc
    except Exception as exc:
        logger.error("[%s] Mistral API error: %s", agent_name, exc)
        raise AgentError(agent_name, f"API call failed: {exc}") from exc

    if not response.choices:
        raise AgentError(agent_name, "Empty choices in Mistral response")

    content = response.choices[0].message.content
    if content is None:
        raise AgentError(agent_name, "Null content in Mistral response")

    return str(content)


def safe_json_parse(raw: str, *, agent_name: str) -> dict[str, Any]:
    """Parse a JSON string with a clear error on failure."""
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.error("[%s] Invalid JSON from Mistral: %s", agent_name, raw[:200])
        raise AgentError(agent_name, f"Invalid JSON response: {exc}") from exc

    if not isinstance(parsed, dict):
        kind = type(parsed).__name__
        raise AgentError(agent_name, f"Expected JSON object, got {kind}")

    return parsed
