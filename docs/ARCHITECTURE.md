# Architecture Decision Record — Entre Deux

## System Architecture

```
┌─────────────────────────────────────────────────┐
│                   Frontend                       │
│          React 19 + TypeScript + Tailwind        │
│                 (Mobile-First)                   │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ Lab Photo │  │  Voice   │  │  Visit Brief  │  │
│  │  Upload   │  │ Recorder │  │   Viewer      │  │
│  └─────┬─────┘  └─────┬────┘  └──────┬────────┘  │
└────────┼──────────────┼──────────────┼───────────┘
         │              │              │
         ▼              ▼              ▼
┌─────────────────────────────────────────────────┐
│                  FastAPI Backend                  │
│                                                  │
│  ┌─────────────────────────────────────────────┐ │
│  │                 API Layer                    │ │
│  │  /lab-results/analyze                       │ │
│  │  /journal/entry                             │ │
│  │  /journal/timeline                          │ │
│  │  /visit-brief/generate                      │ │
│  └──────────────────┬──────────────────────────┘ │
│                     │                            │
│  ┌──────────────────▼──────────────────────────┐ │
│  │              Service Layer                   │ │
│  │  LabResultService                           │ │
│  │  JournalService                             │ │
│  │  VisitBriefService                          │ │
│  └──────────────────┬──────────────────────────┘ │
│                     │                            │
│  ┌──────────────────▼──────────────────────────┐ │
│  │              Agent Layer                     │ │
│  │  ┌────────────┐ ┌──────────┐ ┌───────────┐  │ │
│  │  │  OCR Agent │ │ Journal  │ │   Brief   │  │ │
│  │  │(Mistral    │ │  Agent   │ │  Agent    │  │ │
│  │  │ OCR 3)     │ │(Small 4) │ │(Small 4)  │  │ │
│  │  └────────────┘ └──────────┘ └───────────┘  │ │
│  │  ┌────────────┐                              │ │
│  │  │ Voxtral    │                              │ │
│  │  │ Transcribe │                              │ │
│  │  └────────────┘                              │ │
│  └─────────────────────────────────────────────┘ │
└──────────────────────┬───────────────────────────┘
                       │
                       ▼
              ┌────────────────┐
              │   PostgreSQL   │
              │   (Supabase)   │
              └────────────────┘
```

## Key Architecture Decisions

### ADR-001: Separate Agent Layer for Mistral Calls

**Decision:** All Mistral API calls are isolated in an `agents/` directory, never called directly from routes or services.

**Why:** Clean separation allows swapping models, adding fallbacks, and testing with mocks without touching business logic. Also mirrors the multi-agent pattern from StoryBridge (proven architecture).

### ADR-002: Mistral Small 4 as Primary Reasoning Model

**Decision:** Use Mistral Small 4 (released March 16, 2026) for all text reasoning tasks.

**Why:**

- Just released 4 days before the hackathon event page went live — using it signals technical currency
- 119B params MoE with only 6B active — fast inference
- Unified instruct + reasoning + coding in one model
- Best-in-class French language capabilities
- Open-weight (Apache 2.0) — deployable anywhere

### ADR-003: Voxtral for Voice Input (Not Web Speech API)

**Decision:** Use Voxtral Transcribe for speech-to-text instead of browser Web Speech API.

**Why:**

- Superior French language transcription accuracy
- Consistent behavior across browsers/devices
- Demonstrates use of Mistral's model ecosystem (hackathon bonus)
- Supports speaker diarization for future multi-speaker scenarios

### ADR-004: Mobile-First, Single-Page Application

**Decision:** Build as a mobile-first SPA with React, not a native app or desktop-first design.

**Why:** Patients use this on their phones — in waiting rooms, at home, on the go. Touch targets (44px min), large text (16px min input), and thumb-friendly layout are non-negotiable.

### ADR-005: PostgreSQL with Simple Schema

**Decision:** Use PostgreSQL (via Supabase) with a simple, denormalized schema optimized for the hackathon timeline.

**Why:** 12 hours. No time for complex relational modeling. Store structured JSON in journal entries. Optimize for read speed on timeline queries.

## Database Schema (MVP)

```sql
CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    date_of_birth DATE,
    conditions TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE lab_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id),
    original_image_url TEXT,
    extracted_data JSONB NOT NULL,
    explanation TEXT NOT NULL,
    analyzed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE journal_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id),
    raw_transcript TEXT,
    structured_data JSONB NOT NULL,
    emotional_state TEXT,
    ai_response TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE visit_briefs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id),
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    content JSONB NOT NULL,
    generated_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Mistral Model Usage

| Task                   | Model                              | Why                                                         |
| ---------------------- | ---------------------------------- | ----------------------------------------------------------- |
| Lab result OCR         | Mistral OCR 3                      | Purpose-built document extraction                           |
| Lab result explanation | Mistral Small 4                    | French reasoning, plain-language generation                 |
| Voice transcription    | Voxtral Transcribe                 | French speech recognition                                   |
| Journal structuring    | Mistral Small 4                    | Extract symptoms, emotions, medications from natural speech |
| Empathetic responses   | Mistral Small 4                    | Conversational, context-aware                               |
| Visit brief generation | Mistral Small 4 + function calling | Aggregate data, structure into brief                        |
