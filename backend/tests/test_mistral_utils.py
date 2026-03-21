import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.agents.mistral_utils import (
    AgentError,
    AgentTimeoutError,
    safe_chat_complete,
    safe_json_parse,
)
from tests.conftest import mock_mistral_chat_response


@pytest.mark.asyncio
async def test_safe_chat_complete_success() -> None:
    """safe_chat_complete returns content string on success."""
    client = MagicMock()
    response = mock_mistral_chat_response('{"key": "value"}')
    client.chat.complete_async = AsyncMock(return_value=response)

    result = await safe_chat_complete(
        client, model="test", messages=[], agent_name="test_agent"
    )

    assert result == '{"key": "value"}'


@pytest.mark.asyncio
async def test_safe_chat_complete_timeout() -> None:
    """safe_chat_complete raises AgentTimeoutError on timeout."""
    client = MagicMock()

    async def slow_call(**kwargs: object) -> None:
        await asyncio.sleep(10)

    client.chat.complete_async = slow_call

    with pytest.raises(AgentTimeoutError) as exc_info:
        await safe_chat_complete(
            client,
            model="test",
            messages=[],
            agent_name="test_agent",
            timeout_seconds=0.01,
        )

    assert exc_info.value.agent_name == "test_agent"


@pytest.mark.asyncio
async def test_safe_chat_complete_empty_choices() -> None:
    """safe_chat_complete raises AgentError when choices is empty."""
    client = MagicMock()
    response = MagicMock()
    response.choices = []
    client.chat.complete_async = AsyncMock(return_value=response)

    with pytest.raises(AgentError, match="Empty choices"):
        await safe_chat_complete(
            client, model="test", messages=[], agent_name="test_agent"
        )


@pytest.mark.asyncio
async def test_safe_chat_complete_null_content() -> None:
    """safe_chat_complete raises AgentError when content is None."""
    client = MagicMock()
    message = MagicMock()
    message.content = None
    choice = MagicMock()
    choice.message = message
    response = MagicMock()
    response.choices = [choice]
    client.chat.complete_async = AsyncMock(return_value=response)

    with pytest.raises(AgentError, match="Null content"):
        await safe_chat_complete(
            client, model="test", messages=[], agent_name="test_agent"
        )


@pytest.mark.asyncio
async def test_safe_chat_complete_api_error() -> None:
    """safe_chat_complete wraps API exceptions in AgentError."""
    client = MagicMock()
    client.chat.complete_async = AsyncMock(
        side_effect=RuntimeError("Connection failed")
    )

    with pytest.raises(AgentError, match="API call failed"):
        await safe_chat_complete(
            client, model="test", messages=[], agent_name="test_agent"
        )


def test_safe_json_parse_valid() -> None:
    """safe_json_parse returns parsed dict for valid JSON."""
    result = safe_json_parse('{"key": "value"}', agent_name="test")
    assert result == {"key": "value"}


def test_safe_json_parse_invalid() -> None:
    """safe_json_parse raises AgentError for invalid JSON."""
    with pytest.raises(AgentError, match="Invalid JSON"):
        safe_json_parse("not json", agent_name="test")


def test_safe_json_parse_non_object() -> None:
    """safe_json_parse raises AgentError when JSON is not an object."""
    with pytest.raises(AgentError, match="Expected JSON object"):
        safe_json_parse("[1, 2, 3]", agent_name="test")
