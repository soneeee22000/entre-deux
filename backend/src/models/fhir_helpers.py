from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fhir.resources.auditevent import AuditEvent
from fhir.resources.composition import Composition
from fhir.resources.consent import Consent
from fhir.resources.diagnosticreport import DiagnosticReport
from fhir.resources.observation import Observation
from fhir.resources.patient import Patient
from fhir.resources.questionnaireresponse import QuestionnaireResponse

from src.models.fhir_constants import (
    AUDIT_CODE_AI_QUERY,
    AUDIT_CODE_AI_QUERY_DISPLAY,
    AUDIT_SYSTEM_DCM,
    COMPOSITION_LOINC,
    COMPOSITION_LOINC_DISPLAY,
    CONSENT_CATEGORY_CODE,
    LOINC_DIAGNOSTIC_REPORT,
    LOINC_DIAGNOSTIC_REPORT_DISPLAY,
    SYSTEM_ENTRE_DEUX,
    SYSTEM_LOINC,
)


def create_patient(
    given_name: str, family_name: str, identifier: str
) -> Patient:
    """Create a FHIR Patient resource."""
    return Patient(
        id=str(uuid4()),
        identifier=[
            {
                "system": SYSTEM_ENTRE_DEUX,
                "value": identifier,
            }
        ],
        name=[{"given": [given_name], "family": family_name}],
    )


def create_observation(
    patient_ref: str,
    loinc_code: str,
    loinc_display: str,
    value: float,
    unit: str,
    reference_range_low: float | None = None,
    reference_range_high: float | None = None,
) -> Observation:
    """Create a FHIR Observation for a lab value."""
    obs_data: dict[str, Any] = {
        "id": str(uuid4()),
        "status": "final",
        "code": {
            "coding": [
                {
                    "system": SYSTEM_LOINC,
                    "code": loinc_code,
                    "display": loinc_display,
                }
            ]
        },
        "subject": {"reference": patient_ref},
        "effectiveDateTime": datetime.now(tz=timezone.utc).isoformat(),
        "valueQuantity": {"value": value, "unit": unit},
    }
    if reference_range_low is not None or reference_range_high is not None:
        range_item: dict[str, Any] = {}
        if reference_range_low is not None:
            range_item["low"] = {"value": reference_range_low, "unit": unit}
        if reference_range_high is not None:
            range_item["high"] = {"value": reference_range_high, "unit": unit}
        obs_data["referenceRange"] = [range_item]
    return Observation(**obs_data)


def create_diagnostic_report(
    patient_ref: str, observation_refs: list[str]
) -> DiagnosticReport:
    """Create a FHIR DiagnosticReport wrapping Observations."""
    return DiagnosticReport(
        id=str(uuid4()),
        status="final",
        code={
            "coding": [
                {
                    "system": SYSTEM_LOINC,
                    "code": LOINC_DIAGNOSTIC_REPORT,
                    "display": LOINC_DIAGNOSTIC_REPORT_DISPLAY,
                }
            ]
        },
        subject={"reference": patient_ref},
        result=[{"reference": ref} for ref in observation_refs],
        issued=datetime.now(tz=timezone.utc).isoformat(),
    )


def create_questionnaire_response(
    patient_ref: str,
    items: list[dict[str, Any]],
) -> QuestionnaireResponse:
    """Create a FHIR QuestionnaireResponse for journal PROs."""
    return QuestionnaireResponse(
        id=str(uuid4()),
        questionnaire=f"{SYSTEM_ENTRE_DEUX}/Questionnaire/patient-journal",
        status="completed",
        subject={"reference": patient_ref},
        authored=datetime.now(tz=timezone.utc).isoformat(),
        item=items,
    )


def create_composition_visit_brief(
    patient_ref: str,
    author_ref: str,
    sections: list[dict[str, Any]],
) -> Composition:
    """Create a FHIR Composition for a visit brief."""
    return Composition(
        id=str(uuid4()),
        status="final",
        type={
            "coding": [
                {
                    "system": SYSTEM_LOINC,
                    "code": COMPOSITION_LOINC,
                    "display": COMPOSITION_LOINC_DISPLAY,
                }
            ]
        },
        subject=[{"reference": patient_ref}],
        author=[{"reference": author_ref}],
        date=datetime.now(tz=timezone.utc).isoformat(),
        title="Visit Brief",
        section=sections,
    )


def create_consent(
    patient_ref: str, scope: str
) -> Consent:
    """Create a FHIR Consent resource."""
    return Consent(
        id=str(uuid4()),
        status="active",
        category=[
            {
                "coding": [
                    {
                        "system": SYSTEM_ENTRE_DEUX,
                        "code": CONSENT_CATEGORY_CODE,
                    }
                ]
            }
        ],
        subject={"reference": patient_ref},
        date=datetime.now(tz=timezone.utc).strftime("%Y-%m-%d"),
        provision=[
            {
                "purpose": [
                    {
                        "system": SYSTEM_ENTRE_DEUX,
                        "code": scope,
                        "display": f"Consent for {scope}",
                    }
                ],
            }
        ],
    )


def create_audit_event(
    agent_name: str,
    patient_ref: str | None = None,
) -> AuditEvent:
    """Create a FHIR AuditEvent for tracking AI agent calls."""
    entity_list = []
    if patient_ref:
        entity_list.append({"what": {"reference": patient_ref}})
    return AuditEvent(
        id=str(uuid4()),
        code={
            "coding": [
                {
                    "system": AUDIT_SYSTEM_DCM,
                    "code": AUDIT_CODE_AI_QUERY,
                    "display": AUDIT_CODE_AI_QUERY_DISPLAY,
                }
            ]
        },
        agent=[
            {
                "who": {"display": agent_name},
                "requestor": False,
            }
        ],
        source={"observer": {"display": "entre-deux-api"}},
        recorded=datetime.now(tz=timezone.utc).isoformat(),
        entity=entity_list if entity_list else None,
    )
