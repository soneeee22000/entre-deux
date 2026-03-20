from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.audit_service import AuditService


@pytest.mark.asyncio
async def test_log_ai_call_creates_audit_event(
    mock_session: AsyncMock,
) -> None:
    """log_ai_call persists an AuditEvent row."""
    service = AuditService(mock_session)

    mock_row = MagicMock()

    with (
        patch.object(
            service._repo,
            "create",
            new_callable=AsyncMock,
            return_value=mock_row,
        ),
        patch(
            "src.services.audit_service.settings"
        ) as mock_settings,
    ):
        mock_settings.audit_enabled = True
        result = await service.log_ai_call(
            agent_name="test_agent",
            model_version="mistral-small-latest",
            patient_ref="Patient/123",
            input_text="input",
            output_text="output",
        )

    assert result == mock_row
    mock_session.flush.assert_called_once()


@pytest.mark.asyncio
async def test_log_ai_call_skips_when_disabled(
    mock_session: AsyncMock,
) -> None:
    """log_ai_call returns None when audit_enabled is False."""
    service = AuditService(mock_session)

    with patch(
        "src.services.audit_service.settings"
    ) as mock_settings:
        mock_settings.audit_enabled = False
        result = await service.log_ai_call(
            agent_name="test_agent",
            model_version="mistral-small-latest",
        )

    assert result is None


@pytest.mark.asyncio
async def test_get_audit_trail(
    mock_session: AsyncMock,
) -> None:
    """get_audit_trail delegates to repository."""
    service = AuditService(mock_session)

    mock_row = MagicMock()

    with patch.object(
        service._repo,
        "get_by_patient_ref",
        new_callable=AsyncMock,
        return_value=[mock_row],
    ):
        result = await service.get_audit_trail("Patient/123", limit=50)

    assert len(result) == 1
    assert result[0] == mock_row
