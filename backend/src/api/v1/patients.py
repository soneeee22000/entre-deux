import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.engine import get_session
from src.db.repositories.patient_repository import PatientRepository
from src.db.tables import PatientTable
from src.models.fhir_helpers import create_patient
from src.models.schemas import CreatePatientRequest

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post("", status_code=201)
async def register_patient(
    request: CreatePatientRequest,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> dict[str, Any]:
    """Register a new patient and return a FHIR Patient resource."""
    repo = PatientRepository(session)
    existing = await repo.get_by_identifier(request.identifier)
    if existing:
        raise HTTPException(
            status_code=409, detail="Patient identifier already exists"
        )

    fhir_patient = create_patient(
        request.given_name, request.family_name, request.identifier
    )
    row = PatientTable(
        identifier=request.identifier,
        fhir_resource=fhir_patient.model_dump(mode="json"),
    )
    created = await repo.create(row)
    created.fhir_resource["id"] = str(created.id)
    await session.commit()
    return created.fhir_resource


@router.get("/{patient_id}")
async def get_patient(
    patient_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> dict[str, Any]:
    """Get a patient by ID."""
    repo = PatientRepository(session)
    row = await repo.get_by_id(patient_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return row.fhir_resource


@router.get("/{patient_id}/timeline")
async def get_patient_timeline(
    patient_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> dict[str, Any]:
    """Get a patient's full timeline of resources."""
    from src.db.repositories.composition_repository import (
        CompositionRepository,
    )
    from src.db.repositories.observation_repository import (
        ObservationRepository,
    )
    from src.db.repositories.questionnaire_response_repository import (
        QuestionnaireResponseRepository,
    )

    repo = PatientRepository(session)
    patient = await repo.get_by_id(patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    obs_repo = ObservationRepository(session)
    qr_repo = QuestionnaireResponseRepository(session)
    comp_repo = CompositionRepository(session)

    observations = await obs_repo.list_by_patient(patient_id)
    questionnaire_responses = await qr_repo.list_by_patient(patient_id)
    compositions = await comp_repo.list_by_patient(patient_id)

    return {
        "patient": patient.fhir_resource,
        "observations": [r.fhir_resource for r in observations],
        "questionnaire_responses": [
            r.fhir_resource for r in questionnaire_responses
        ],
        "compositions": [r.fhir_resource for r in compositions],
    }
