import uuid
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from tests.conftest import make_table_row


@pytest.fixture(autouse=True)
def _override_db(override_session: AsyncMock) -> None:
    """Auto-apply session override for all tests in this module."""


@pytest.mark.asyncio
async def test_list_audit_events(
    async_client: ASGITransport,
    override_session: AsyncMock,
    patient_id: uuid.UUID,
) -> None:
    """GET /audit-events returns audit trail for a patient."""
    audit_fhir: dict[str, Any] = {
        "resourceType": "AuditEvent",
        "id": str(uuid.uuid4()),
        "code": {"coding": [{"code": "110112"}]},
        "agent": [{"who": {"display": "ocr_agent"}, "requestor": False}],
        "source": {"observer": {"display": "entre-deux-api"}},
        "recorded": "2025-03-01T00:00:00Z",
    }
    row = make_table_row(audit_fhir)

    with patch(
        "src.api.dependencies.AuditService"
    ) as mock_svc_cls:
        mock_svc_cls.return_value.get_audit_trail = AsyncMock(
            return_value=[row]
        )

        async with AsyncClient(
            transport=async_client, base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/v1/audit-events",
                params={
                    "patient_ref": f"Patient/{patient_id}",
                    "limit": 50,
                },
            )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["resourceType"] == "AuditEvent"


@pytest.mark.asyncio
async def test_list_audit_events_requires_patient_ref(
    async_client: ASGITransport,
    override_session: AsyncMock,
) -> None:
    """GET /audit-events without patient_ref returns 422."""
    async with AsyncClient(
        transport=async_client, base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/audit-events")
    assert response.status_code == 422
