import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.consent_service import ConsentService


@pytest.fixture
def mock_session() -> AsyncMock:
    session = AsyncMock()
    session.commit = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()
    return session


class TestConsentServiceRecordConsent:
    @pytest.mark.asyncio
    async def test_creates_consent_row(
        self, mock_session: AsyncMock
    ) -> None:
        patient_id = uuid.uuid4()
        service = ConsentService(mock_session)

        with patch.object(
            service._repo, "create", new_callable=AsyncMock
        ) as mock_create:
            mock_row = MagicMock()
            mock_row.fhir_resource = {"resourceType": "Consent"}
            mock_create.return_value = mock_row

            result = await service.record_consent(patient_id, "ai-processing")

            mock_create.assert_called_once()
            mock_session.commit.assert_called_once()
            assert result == mock_row


class TestConsentServiceVerifyConsent:
    @pytest.mark.asyncio
    async def test_returns_true_when_active_consent_exists(
        self, mock_session: AsyncMock
    ) -> None:
        patient_id = uuid.uuid4()
        service = ConsentService(mock_session)

        with patch.object(
            service._repo,
            "get_active_consent",
            new_callable=AsyncMock,
            return_value=MagicMock(),
        ):
            result = await service.verify_consent(patient_id, "ai-processing")
            assert result is True

    @pytest.mark.asyncio
    async def test_returns_false_when_no_consent(
        self, mock_session: AsyncMock
    ) -> None:
        patient_id = uuid.uuid4()
        service = ConsentService(mock_session)

        with patch.object(
            service._repo,
            "get_active_consent",
            new_callable=AsyncMock,
            return_value=None,
        ):
            result = await service.verify_consent(patient_id, "ai-processing")
            assert result is False


class TestConsentServiceRevokeConsent:
    @pytest.mark.asyncio
    async def test_revokes_existing_consent(
        self, mock_session: AsyncMock
    ) -> None:
        consent_id = uuid.uuid4()
        service = ConsentService(mock_session)

        mock_row = MagicMock()
        mock_row.active = True
        mock_row.fhir_resource = {"status": "active"}

        with patch.object(
            service._repo,
            "get_by_id",
            new_callable=AsyncMock,
            return_value=mock_row,
        ):
            result = await service.revoke_consent(consent_id)

            assert result is not None
            assert mock_row.active is False
            assert mock_row.fhir_resource["status"] == "inactive"
            mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_none_for_nonexistent(
        self, mock_session: AsyncMock
    ) -> None:
        consent_id = uuid.uuid4()
        service = ConsentService(mock_session)

        with patch.object(
            service._repo,
            "get_by_id",
            new_callable=AsyncMock,
            return_value=None,
        ):
            result = await service.revoke_consent(consent_id)
            assert result is None
