# Entre Deux — Project CLAUDE.md

## Project Overview

Entre Deux is a FHIR-native AI companion for chronic condition patients, filling the gap between doctor appointments. Diabetes-first B2B2C healthcare SaaS for the French market. Consent-first, audit-logged, CE-marking ready.

## Tech Stack

- **Backend:** Python 3.12, FastAPI, SQLAlchemy async, Alembic, Mistral AI SDK
- **Frontend:** React 19, TypeScript (strict), Tailwind CSS, shadcn/ui, PWA (vite-plugin-pwa)
- **Database:** PostgreSQL 16 (FHIR R5 JSONB via asyncpg)
- **FHIR:** fhir.resources 8.x (R5) for data model validation
- **AI Models:** Mistral Small 4, Mistral OCR 3, Voxtral Transcribe
- **Auth:** JWT (python-jose) + bcrypt (passlib), per-user rate limiting (slowapi)
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
cd backend && pytest -v --cov=src --cov-fail-under=80   # 93 tests
cd frontend && npm test                                   # 73 unit tests
cd frontend && npm run test:e2e                           # 19 Playwright E2E tests

# Demo seed data
cd backend && python -m scripts.seed_demo

# Docker
docker compose up --build
```

## Architecture Rules

- Clean Architecture: agents/ (AI logic) → services/ (business logic) → api/ (routes)
- All clinical data stored as FHIR R5 resources in PostgreSQL JSONB
- All Mistral API calls go through agents/ via `mistral_utils.safe_chat_complete` — never call Mistral directly
- `mistral_utils` provides `AgentError` / `AgentTimeoutError` exceptions, `safe_chat_complete` with timeout, `safe_json_parse`
- Every AI agent call is audit-logged as a FHIR AuditEvent
- All AI-powered endpoints require active FHIR Consent (middleware enforcement)
- JWT auth with patient data isolation: `users` table (1:1 with patients), `middleware/auth.py` extracts user from JWT
- When `jwt_secret_key` is set: full JWT auth with patient isolation (403 for cross-patient access)
- When `jwt_secret_key` is empty: falls back to `demo_api_token` bearer auth (backward compatible)
- AI endpoints rate-limited at 5/min per user, auth endpoints at 10/min (slowapi)
- Services wrap multi-step agent operations in try/except with `session.rollback()` on failure
- Database access goes through repositories (db/repositories/) — never raw queries in services
- Frontend uses React Error Boundaries at app + route level for crash resilience
- Frontend is a PWA: offline banner, service worker caching app shell, standalone display
- Frontend components are mobile-first (this is a patient tool, used on phones)
- Frontend uses `useAsyncData` hook for all data fetching — never raw `useEffect + .catch(() => {})`
- All API responses include structured error handling; frontend surfaces French contextual error messages

## Design System

- Warm, approachable aesthetic (not clinical)
- Earth tones palette — no cold blues or sterile whites
- Mobile-first: 44px touch targets, 16px minimum input font
- Max 3 colors: primary warm, neutral, accent
- Typography: Lora (headings), Inter (body)
- No emojis as icons — use Lucide icons
- No gradients on buttons
- No `dangerouslySetInnerHTML` — use `stripHtmlTags()` from `utils.ts`

## API Design

RESTful endpoints under /api/v1/:

### Public (no auth required)

- GET /health — health check with DB + Mistral status
- POST /auth/register — create account (returns JWT + patient_id)
- POST /auth/login — authenticate (returns JWT + patient_id)
- POST /auth/refresh — refresh token pair

### Protected (require bearer token, patient-isolated when JWT enabled)

- POST /patients — register a new patient
- GET /patients/{id} — get patient by ID
- GET /patients/{id}/timeline — full patient timeline
- POST /observations/analyze-image — OCR lab photo → Observations + DiagnosticReport (rate limited)
- POST /observations — create a single observation
- GET /observations/patients/{id} — list patient observations
- POST /questionnaire-responses — create journal entry (rate limited)
- GET /questionnaire-responses/patients/{id} — list patient journal entries
- POST /compositions/visit-brief — generate visit brief (rate limited)
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
- `ruff check` clean before commit
- `mypy src/ --ignore-missing-imports --strict` clean (CI enforced)
- `pytest --cov=src --cov-fail-under=80` (CI enforced)
- All 3 test suites pass (pytest, vitest, playwright)
- CI runs: backend (ruff + mypy strict + pytest-cov), frontend (lint + test + build), E2E (playwright), docker (compose build)
