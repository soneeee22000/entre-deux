from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agents.mistral_utils import AgentError, AgentTimeoutError
from src.agents.transcribe_agent import TranscribeAgent


@pytest.fixture
def mock_session() -> AsyncMock:
    """Provide a mock AsyncSession."""
    session = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def agent(mock_session: AsyncMock) -> TranscribeAgent:
    """Provide a TranscribeAgent with mocked session."""
    return TranscribeAgent("test-key", mock_session)


@pytest.mark.asyncio
async def test_transcribe_returns_text(agent: TranscribeAgent) -> None:
    """Successful transcription returns text."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"text": "Bonjour, je me sens bien."}

    with patch("src.agents.transcribe_agent.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__ = AsyncMock(
            return_value=mock_client.return_value
        )
        mock_client.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_client.return_value.post = AsyncMock(return_value=mock_response)

        result = await agent.transcribe(
            b"fake-audio", "test.webm", "Patient/123"
        )

    assert result == "Bonjour, je me sens bien."


@pytest.mark.asyncio
async def test_transcribe_api_error_raises_agent_error(
    agent: TranscribeAgent,
) -> None:
    """Non-200 API response raises AgentError."""
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad request"

    with patch("src.agents.transcribe_agent.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__ = AsyncMock(
            return_value=mock_client.return_value
        )
        mock_client.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_client.return_value.post = AsyncMock(return_value=mock_response)

        with pytest.raises(AgentError, match="API returned 400"):
            await agent.transcribe(b"fake-audio", "test.webm")


@pytest.mark.asyncio
async def test_transcribe_empty_result_raises_agent_error(
    agent: TranscribeAgent,
) -> None:
    """Empty transcription text raises AgentError."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"text": ""}

    with patch("src.agents.transcribe_agent.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__ = AsyncMock(
            return_value=mock_client.return_value
        )
        mock_client.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_client.return_value.post = AsyncMock(return_value=mock_response)

        with pytest.raises(AgentError, match="Empty transcription"):
            await agent.transcribe(b"fake-audio", "test.webm")


@pytest.mark.asyncio
async def test_transcribe_timeout_raises_timeout_error(
    agent: TranscribeAgent,
) -> None:
    """Timeout during transcription raises AgentTimeoutError."""
    with patch("src.agents.transcribe_agent.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__ = AsyncMock(
            return_value=mock_client.return_value
        )
        mock_client.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_client.return_value.post = AsyncMock(
            side_effect=TimeoutError("timeout")
        )

        with pytest.raises(AgentTimeoutError):
            await agent.transcribe(b"fake-audio", "test.webm")
