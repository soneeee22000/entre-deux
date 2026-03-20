# Architecture — Entre Deux

## System Architecture

```
┌─────────────────────────────────────────────────┐
│                   Frontend                       │
│          React 19 + TypeScript + Tailwind        │
│                 (Mobile-First)                   │
└────────────────────┬────────────────────────────┘
                     │ REST API
                     ▼
┌─────────────────────────────────────────────────┐
│                FastAPI Backend                    │
│                                                  │
│  ┌─────────────────────────────────────────────┐ │
│  │              API Layer (v1)                  │ │
│  │  /patients                                  │ │
│  │  /observations/analyze-image                │ │
│  │  /questionnaire-responses                   │ │
│  │  /compositions/visit-brief                  │ │
│  │  /consents                                  │ │
│  │  /audit-events                              │ │
│  └──────────────────┬──────────────────────────┘ │
│                     │                            │
│  ┌──────────────────▼──────────────────────────┐ │
│  │         Middleware (Consent Check)           │ │
│  └──────────────────┬──────────────────────────┘ │
│                     │                            │
│  ┌──────────────────▼──────────────────────────┐ │
│  │             Service Layer                    │ │
│  │  LabResultService, JournalService,          │ │
│  │  VisitBriefService, ConsentService,         │ │
│  │  AuditService                               │ │
│  └──────────┬───────────────┬──────────────────┘ │
│             │               │                    │
│  ┌──────────▼─────┐  ┌─────▼──────────────────┐ │
│  │  Agent Layer    │  │  Repository Layer       │ │
│  │  OCR, Explain,  │  │  PatientRepo,          │ │
│  │  Journal, Brief │  │  ObservationRepo,      │ │
│  │  (Mistral AI)   │  │  ConsentRepo, etc.     │ │
│  └──────────┬──────┘  └─────┬──────────────────┘ │
│             │               │                    │
└─────────────┼───────────────┼────────────────────┘
              │               │
              ▼               ▼
     ┌──────────────┐  ┌──────────────┐
     │  Mistral AI   │  │ PostgreSQL   │
     │  Small 4      │  │ (FHIR JSONB) │
     │  OCR 3        │  │              │
     │  Voxtral      │  │              │
     └──────────────┘  └──────────────┘
```

## Key Architecture Decisions

### ADR-001: FHIR R5 as Data Model

**Decision:** Store all clinical data as FHIR R5 resources in PostgreSQL JSONB columns.

**Context:** Healthcare interoperability, CE marking requirements, and enterprise sales all require standard clinical data formats.

**Consequences:**

- All data is portable and interoperable from day one
- FHIR validation via `fhir.resources` library catches data quality issues early
- Enterprise integrations (EHR, insurance systems) become straightforward
- Slightly more complex than custom schemas, but pays dividends at scale

### ADR-002: Consent-First Architecture

**Decision:** All AI-powered endpoints require active FHIR Consent before processing. Consent is verified via FastAPI middleware.

**Context:** GDPR, French health data regulations (HDS), and enterprise buyers all require explicit consent management.

**Consequences:**

- Every AI endpoint checks consent before any processing
- Consent is a first-class FHIR resource, not an afterthought
- Consent can be revoked, immediately blocking further processing
- Enterprise buyers see a compliant system from the first demo

### ADR-003: Audit Logging via FHIR AuditEvent

**Decision:** Every AI agent call is logged as a FHIR AuditEvent with agent name, model version, and patient reference.

**Context:** Regulatory requirements for AI in healthcare demand full traceability of all automated decisions.

**Consequences:**

- Complete audit trail for every AI interaction
- AuditEvents are queryable per patient
- Enables compliance reporting and incident investigation

### ADR-004: Direct PostgreSQL (asyncpg) over Supabase

**Decision:** Use SQLAlchemy async with asyncpg directly instead of Supabase client.

**Context:** Production healthcare SaaS needs full control over database schema, migrations, and connection pooling. Alembic provides version-controlled migrations.

**Consequences:**

- Full control over schema evolution via Alembic migrations
- No vendor lock-in to Supabase
- Async support for high-concurrency workloads
- Standard PostgreSQL deployment (Docker, Cloud SQL, RDS)

## Database Schema

7 tables, each storing a `fhir_resource JSONB` column alongside indexed metadata:

| Table                     | Key Columns                        | Indexes                  |
| ------------------------- | ---------------------------------- | ------------------------ |
| `patients`                | identifier (unique)                | identifier               |
| `observations`            | patient_id, loinc_code             | (patient_id, loinc_code) |
| `diagnostic_reports`      | patient_id                         | patient_id               |
| `questionnaire_responses` | patient_id                         | patient_id               |
| `compositions`            | patient_id, composition_type       | patient_id               |
| `consents`                | patient_id, scope, active          | (patient_id, scope)      |
| `audit_events`            | patient_ref, agent_name, model_ver | patient_ref              |

## AI Agent Architecture

All AI agents follow a consistent pattern: Mistral SDK async call → JSON response parsing → audit logging.

| Agent                    | Model                                     | Input                        | Output                             | Temperature |
| ------------------------ | ----------------------------------------- | ---------------------------- | ---------------------------------- | ----------- |
| `OCRAgent`               | mistral-ocr-latest + mistral-small-latest | Base64 image                 | LOINC-coded lab values             | 0.0         |
| `ExplanationAgent`       | mistral-small-latest                      | Observation list             | Plain-French explanation           | 0.3         |
| `JournalAgent.structure` | mistral-small-latest                      | Patient transcript           | Symptoms, emotions, meds, severity | 0.1         |
| `JournalAgent.response`  | mistral-small-latest                      | Transcript + structured data | Empathetic French response         | 0.5         |
| `BriefAgent`             | mistral-small-latest                      | Observations + QRs           | Visit brief sections               | 0.3         |

**Key design decisions:**

- All agents use `response_format=json_object` for reliable parsing
- OCR is a two-step pipeline: Mistral OCR (image → markdown) then Mistral Small (markdown → structured JSON)
- Every agent call is audit-logged as a FHIR AuditEvent via `AuditService`
- French-language system prompts tuned for patient comprehension

## Technology Stack

| Layer          | Technology                              |
| -------------- | --------------------------------------- |
| **AI Models**  | Mistral Small 4, Mistral OCR 3, Voxtral |
| **Backend**    | Python 3.12, FastAPI, SQLAlchemy async  |
| **Frontend**   | React 19, TypeScript, Tailwind CSS      |
| **Database**   | PostgreSQL 16 (FHIR JSONB)              |
| **Migrations** | Alembic                                 |
| **FHIR**       | fhir.resources 8.x (R5)                 |
| **Deployment** | Docker, Google Cloud Run                |
| **Testing**    | pytest, vitest, Playwright              |
