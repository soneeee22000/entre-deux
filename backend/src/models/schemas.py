from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str
    code: str


class CreatePatientRequest(BaseModel):
    """Request to register a new patient."""

    given_name: str = Field(min_length=1)
    family_name: str = Field(min_length=1)
    identifier: str = Field(min_length=1, description="External patient identifier")


class AnalyzeLabImageRequest(BaseModel):
    """Request to analyze a lab result image."""

    patient_id: UUID
    image_base64: str = Field(description="Base64-encoded lab result image")


class CreateObservationRequest(BaseModel):
    """Request to manually create an observation."""

    patient_id: UUID
    loinc_code: str = Field(min_length=1)
    loinc_display: str = Field(min_length=1)
    value: float
    unit: str = Field(min_length=1)
    reference_range_low: float | None = None
    reference_range_high: float | None = None


class CreateJournalEntryRequest(BaseModel):
    """Request to create a journal entry."""

    patient_id: UUID
    transcript: str = Field(min_length=1, description="Voice transcript or typed text")


class GenerateVisitBriefRequest(BaseModel):
    """Request to generate a visit brief."""

    patient_id: UUID
    period_start: datetime
    period_end: datetime


class CreateConsentRequest(BaseModel):
    """Request to record patient consent."""

    patient_id: UUID
    scope: str = Field(min_length=1, description="Consent scope (e.g. 'ai-processing')")


class RegisterRequest(BaseModel):
    """Request to register a new user account."""

    email: str = Field(min_length=5)
    password: str = Field(min_length=8)
    given_name: str = Field(min_length=1)
    family_name: str = Field(min_length=1)
    identifier: str = Field(min_length=1, description="External patient identifier")


class LoginRequest(BaseModel):
    """Request to authenticate."""

    email: str = Field(min_length=1)
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    """JWT token pair response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    patient_id: str


class RefreshRequest(BaseModel):
    """Request to refresh an access token."""

    refresh_token: str
