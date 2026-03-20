import uuid

from sqlalchemy import Boolean, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class PatientTable(Base):
    """Patient demographic record storing a FHIR Patient resource."""

    __tablename__ = "patients"

    fhir_resource: Mapped[dict] = mapped_column(JSONB, nullable=False)  # type: ignore[type-arg]
    identifier: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)


class ObservationTable(Base):
    """Clinical observation (lab values, vitals) as FHIR Observation."""

    __tablename__ = "observations"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False
    )
    loinc_code: Mapped[str] = mapped_column(String(20), nullable=False)
    fhir_resource: Mapped[dict] = mapped_column(JSONB, nullable=False)  # type: ignore[type-arg]

    __table_args__ = (
        Index("ix_observations_patient_loinc", "patient_id", "loinc_code"),
    )


class DiagnosticReportTable(Base):
    """Diagnostic report wrapping a set of Observations."""

    __tablename__ = "diagnostic_reports"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False
    )
    fhir_resource: Mapped[dict] = mapped_column(JSONB, nullable=False)  # type: ignore[type-arg]

    __table_args__ = (Index("ix_diagnostic_reports_patient", "patient_id"),)


class CompositionTable(Base):
    """FHIR Composition (visit briefs, summaries)."""

    __tablename__ = "compositions"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False
    )
    composition_type: Mapped[str] = mapped_column(String(50), nullable=False)
    fhir_resource: Mapped[dict] = mapped_column(JSONB, nullable=False)  # type: ignore[type-arg]

    __table_args__ = (Index("ix_compositions_patient", "patient_id"),)


class QuestionnaireResponseTable(Base):
    """FHIR QuestionnaireResponse (patient journal PROs)."""

    __tablename__ = "questionnaire_responses"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False
    )
    fhir_resource: Mapped[dict] = mapped_column(JSONB, nullable=False)  # type: ignore[type-arg]

    __table_args__ = (Index("ix_questionnaire_responses_patient", "patient_id"),)


class ConsentTable(Base):
    """FHIR Consent record for data processing authorization."""

    __tablename__ = "consents"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False
    )
    scope: Mapped[str] = mapped_column(String(100), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    fhir_resource: Mapped[dict] = mapped_column(JSONB, nullable=False)  # type: ignore[type-arg]

    __table_args__ = (
        Index("ix_consents_patient_scope", "patient_id", "scope"),
    )


class AuditEventTable(Base):
    """FHIR AuditEvent for tracking all AI agent calls."""

    __tablename__ = "audit_events"

    patient_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    input_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    fhir_resource: Mapped[dict] = mapped_column(JSONB, nullable=False)  # type: ignore[type-arg]

    __table_args__ = (Index("ix_audit_events_patient_ref", "patient_ref"),)
