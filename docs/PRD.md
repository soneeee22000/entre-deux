# Product Requirements Document — Entre Deux

## Product Vision

Entre Deux is a FHIR-native AI companion for chronic condition patients, filling the gap between doctor appointments. Starting with diabetes, it helps patients understand their lab results, track their health journey through voice, and walk into every appointment prepared. Built for the French B2B2C healthcare market.

## Target User

**Primary:** Patients with chronic conditions (diabetes first, then cardiovascular, autoimmune) who see specialists every 3-6 months and struggle with:

- Understanding lab results and medical documents
- Remembering symptoms and changes to report
- Preparing for appointments
- The emotional burden of managing their condition alone

**Secondary:** Caregivers managing a family member's health.

**Context:** France-based, French-speaking. Navigating the French healthcare system (parcours de soins, medecin traitant, ALD classifications).

## Core Features

### Feature 1: Lab Result Analyzer (FHIR Observations + DiagnosticReport)

**User story:** As a patient, I want to photograph my lab results and get a plain-French explanation so I understand what the numbers mean.

**Flow:**

1. User uploads a photo of lab results (ordonnance, bilan sanguin)
2. Mistral OCR 3 extracts structured data (LOINC-coded test names, values, reference ranges)
3. Each value is stored as a FHIR Observation resource
4. A FHIR DiagnosticReport wraps all Observations
5. Mistral Small 4 generates a plain-French explanation with context
6. All AI calls are audit-logged as FHIR AuditEvents

**API:** `POST /api/v1/observations/analyze-image`

### Feature 2: Voice Health Journal (FHIR QuestionnaireResponse)

**User story:** As a patient, I want to speak naturally about how I'm feeling and have it structured into a health timeline.

**Flow:**

1. User records a voice message or types text
2. AI structures the entry: symptoms, emotional state, medications mentioned, severity
3. Stored as a FHIR QuestionnaireResponse with structured items
4. AI generates an empathetic response acknowledging the patient's experience

**API:** `POST /api/v1/questionnaire-responses`

### Feature 3: Visit Brief Generator (FHIR Composition)

**User story:** As a patient, I want a one-page summary before my next appointment so I remember everything important.

**Flow:**

1. AI aggregates all Observations and QuestionnaireResponses
2. Generates a structured brief with sections: key changes, symptom timeline, lab trends, suggested questions
3. Stored as a FHIR Composition resource

**API:** `POST /api/v1/compositions/visit-brief`

### Feature 4: Consent Management (FHIR Consent)

**User story:** As a patient, I want to control what data processing is performed on my health data.

**Flow:**

1. Patient grants consent for specific scopes (e.g., "ai-processing")
2. All AI-powered endpoints verify active consent before processing
3. Patients can revoke consent at any time

**API:** `POST /api/v1/consents`, `PUT /api/v1/consents/{id}/revoke`

## Regulatory Compliance

- All clinical data stored as FHIR R5 resources (JSONB in PostgreSQL)
- Every AI agent call audit-logged as FHIR AuditEvent
- Consent-first architecture: no AI processing without explicit patient consent
- LOINC coding for all lab observations
- Designed for CE marking pathway

## Business Model

- **B2B2C:** Sold to healthcare insurers (mutuelles), hospital groups, and diabetes care networks
- **Diabetes-first:** Focused vertical with HbA1c, glucose, creatinine as initial LOINC codes
- **Revenue:** Per-patient licensing to enterprise buyers

## Non-Functional Requirements

- Mobile-first responsive design (patients use phones)
- French-language UI and AI responses
- Sub-3s response time for AI operations
- GDPR-compliant data handling
- Audit trail for all AI interactions
