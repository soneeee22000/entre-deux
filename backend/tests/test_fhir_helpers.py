from fhir.resources.auditevent import AuditEvent
from fhir.resources.composition import Composition
from fhir.resources.consent import Consent
from fhir.resources.diagnosticreport import DiagnosticReport
from fhir.resources.observation import Observation
from fhir.resources.patient import Patient
from fhir.resources.questionnaireresponse import QuestionnaireResponse

from src.models.fhir_constants import (
    LOINC_CREATININE,
    LOINC_CREATININE_DISPLAY,
    LOINC_GLUCOSE,
    LOINC_GLUCOSE_DISPLAY,
    LOINC_HBA1C,
    LOINC_HBA1C_DISPLAY,
    SYSTEM_LOINC,
)
from src.models.fhir_helpers import (
    create_audit_event,
    create_composition_visit_brief,
    create_consent,
    create_diagnostic_report,
    create_observation,
    create_patient,
    create_questionnaire_response,
)


class TestCreatePatient:
    def test_returns_valid_fhir_patient(self) -> None:
        patient = create_patient("Jean", "Dupont", "PAT-001")
        assert isinstance(patient, Patient)
        assert patient.name[0].family == "Dupont"  # type: ignore[index]
        assert patient.name[0].given == ["Jean"]  # type: ignore[index]

    def test_identifier_is_set(self) -> None:
        patient = create_patient("Marie", "Martin", "PAT-002")
        assert patient.identifier[0].value == "PAT-002"  # type: ignore[index]


class TestCreateObservation:
    def test_hba1c_observation(self) -> None:
        obs = create_observation(
            patient_ref="Patient/123",
            loinc_code=LOINC_HBA1C,
            loinc_display=LOINC_HBA1C_DISPLAY,
            value=6.5,
            unit="%",
            reference_range_low=4.0,
            reference_range_high=5.6,
        )
        assert isinstance(obs, Observation)
        assert obs.status == "final"
        coding = obs.code.coding[0]  # type: ignore[union-attr]
        assert coding.system == SYSTEM_LOINC
        assert coding.code == LOINC_HBA1C
        assert obs.valueQuantity.value == 6.5  # type: ignore[union-attr]

    def test_glucose_observation(self) -> None:
        obs = create_observation(
            patient_ref="Patient/456",
            loinc_code=LOINC_GLUCOSE,
            loinc_display=LOINC_GLUCOSE_DISPLAY,
            value=95.0,
            unit="mg/dL",
        )
        assert isinstance(obs, Observation)
        assert obs.referenceRange is None

    def test_creatinine_with_range(self) -> None:
        obs = create_observation(
            patient_ref="Patient/789",
            loinc_code=LOINC_CREATININE,
            loinc_display=LOINC_CREATININE_DISPLAY,
            value=1.2,
            unit="mg/dL",
            reference_range_low=0.7,
            reference_range_high=1.3,
        )
        assert obs.referenceRange is not None
        assert len(obs.referenceRange) == 1


class TestCreateDiagnosticReport:
    def test_wraps_observations(self) -> None:
        dr = create_diagnostic_report(
            patient_ref="Patient/123",
            observation_refs=["Observation/a", "Observation/b"],
        )
        assert isinstance(dr, DiagnosticReport)
        assert dr.status == "final"
        assert len(dr.result) == 2  # type: ignore[arg-type]


class TestCreateQuestionnaireResponse:
    def test_valid_questionnaire_response(self) -> None:
        items = [
            {
                "linkId": "q1",
                "text": "How are you feeling?",
                "answer": [{"valueString": "Tired but okay"}],
            }
        ]
        qr = create_questionnaire_response("Patient/123", items)
        assert isinstance(qr, QuestionnaireResponse)
        assert qr.status == "completed"
        assert len(qr.item) == 1  # type: ignore[arg-type]


class TestCreateComposition:
    def test_visit_brief_composition(self) -> None:
        sections = [
            {
                "title": "Key Changes",
                "text": {
                    "status": "generated",
                    "div": "<div>HbA1c improved</div>",
                },
            }
        ]
        comp = create_composition_visit_brief(
            "Patient/123", "Device/entre-deux", sections
        )
        assert isinstance(comp, Composition)
        assert comp.status == "final"
        assert comp.title == "Bilan de visite"
        assert len(comp.section) == 1  # type: ignore[arg-type]


class TestCreateConsent:
    def test_active_consent(self) -> None:
        consent = create_consent("Patient/123", "ai-processing")
        assert isinstance(consent, Consent)
        assert consent.status == "active"

    def test_consent_serializable(self) -> None:
        consent = create_consent("Patient/456", "data-sharing")
        data = consent.model_dump(mode="json")
        assert data["resourceType"] == "Consent"


class TestCreateAuditEvent:
    def test_with_patient_ref(self) -> None:
        ae = create_audit_event("ocr_agent", "Patient/123")
        assert isinstance(ae, AuditEvent)
        assert ae.entity is not None
        assert len(ae.entity) == 1

    def test_without_patient_ref(self) -> None:
        ae = create_audit_event("system_check")
        assert isinstance(ae, AuditEvent)
        assert ae.entity is None
