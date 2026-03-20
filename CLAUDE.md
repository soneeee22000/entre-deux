# Entre Deux — Project CLAUDE.md

## Project Overview

Entre Deux is a FHIR-native AI companion for chronic condition patients, filling the gap between doctor appointments. Diabetes-first B2B2C healthcare SaaS for the French market. Consent-first, audit-logged, CE-marking ready.

## Tech Stack

- **Backend:** Python 3.12, FastAPI, SQLAlchemy async, Alembic, Mistral AI SDK
- **Frontend:** React 19, TypeScript (strict), Tailwind CSS, shadcn/ui
- **Database:** PostgreSQL 16 (FHIR R5 JSONB via asyncpg)
- **FHIR:** fhir.resources 8.x (R5) for data model validation
- **AI Models:** Mistral Small 4, Mistral OCR 3, Voxtral Transcribe
- **Deployment:** Docker, Google Cloud Run
- **Testing:** pytest (backend), vitest (frontend), Playwright (E2E)

## Build & Run Commands

```bash
# Backend
cd backend && pip install -r requirements.txt
alembic upgrade head
uvicorn src.main:app --reload --port 8000

# Frontend
cd frontend && npm install
npm run dev

# Tests
cd backend && pytest
cd frontend && npm test

# Docker
docker compose up --build
```

## Architecture Rules

- Clean Architecture: agents/ (AI logic) → services/ (business logic) → api/ (routes)
- All clinical data stored as FHIR R5 resources in PostgreSQL JSONB
- All Mistral API calls go through agents/ — never call Mistral directly from routes
- Every AI agent call is audit-logged as a FHIR AuditEvent
- All AI-powered endpoints require active FHIR Consent (middleware enforcement)
- Database access goes through repositories (db/repositories/) — never raw queries in services
- Frontend components are mobile-first (this is a patient tool, used on phones)
- All API responses include structured error handling

## Design System

- Warm, approachable aesthetic (not clinical)
- Earth tones palette — no cold blues or sterile whites
- Mobile-first: 44px touch targets, 16px minimum input font
- Max 3 colors: primary warm, neutral, accent
- Typography: Lora (headings), Inter (body)
- No emojis as icons — use Lucide icons
- No gradients on buttons

## API Design

RESTful endpoints under /api/v1/:

- POST /patients — register a new patient
- GET /patients/{id} — get patient by ID
- GET /patients/{id}/timeline — full patient timeline
- POST /observations/analyze-image — OCR lab photo → Observations + DiagnosticReport
- POST /observations — create a single observation
- GET /observations/patients/{id} — list patient observations
- POST /questionnaire-responses — create journal entry (QuestionnaireResponse)
- GET /questionnaire-responses/patients/{id} — list patient journal entries
- POST /compositions/visit-brief — generate visit brief (Composition)
- GET /compositions/patients/{id} — list patient compositions
- POST /consents — record patient consent
- PUT /consents/{id}/revoke — revoke consent
- GET /consents/patients/{id} — list patient consents
- GET /audit-events — list audit events by patient_ref

## Quality Gates

- No TODO comments — implement or don't
- Type hints on all Python functions
- TypeScript strict mode
- Tests before implementation (TDD)
- No magic numbers
- Max 30 lines per function
