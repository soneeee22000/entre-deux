# Entre Deux — Project CLAUDE.md

## Project Overview

Entre Deux is an AI-powered companion for chronic condition patients, filling the gap between doctor appointments. Built for the Alan x Mistral Health Hack (April 11, 2026).

## Tech Stack

- **Backend:** Python 3.12, FastAPI, Mistral AI SDK
- **Frontend:** React 19, TypeScript (strict), Tailwind CSS, shadcn/ui
- **Database:** PostgreSQL via Supabase
- **AI Models:** Mistral Small 4, Mistral OCR 3, Voxtral Transcribe
- **Deployment:** Docker, Google Cloud Run
- **Testing:** pytest (backend), vitest (frontend), Playwright (E2E)

## Build & Run Commands

```bash
# Backend
cd backend && pip install -r requirements.txt
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
- All Mistral API calls go through agents/ — never call Mistral directly from routes
- Frontend components are mobile-first (this is a patient tool, used on phones)
- All API responses include structured error handling
- Voice input handled client-side (Web Speech API or Voxtral direct)
- Lab result photos processed server-side (OCR → explanation pipeline)

## Hackathon Constraints

- 12-hour build window — prioritize demo flow over feature completeness
- One polished user journey beats five half-working features
- Demo script: photo upload → explanation → voice journal → visit brief
- No medical claims — position as organizational/comprehension tool
- Must use Mistral models (hackathon requirement)

## Design System

- Warm, approachable aesthetic (not clinical)
- Earth tones palette — no cold blues or sterile whites
- Mobile-first: 44px touch targets, 16px minimum input font
- Max 3 colors: primary warm, neutral, accent
- Typography: one serif for headings (warmth), one sans-serif for body (readability)
- No emojis as icons — use Lucide icons
- No gradients on buttons

## API Design

- RESTful endpoints under /api/v1/
- POST /api/v1/lab-results/analyze — upload and explain lab results
- POST /api/v1/journal/entry — create voice/text journal entry
- GET /api/v1/journal/timeline — get structured timeline
- POST /api/v1/visit-brief/generate — generate pre-appointment brief
- All endpoints return JSON with consistent error format

## Quality Gates

- No TODO comments — implement or don't
- Type hints on all Python functions
- TypeScript strict mode
- Tests before implementation (TDD)
- No magic numbers
- Max 30 lines per function
