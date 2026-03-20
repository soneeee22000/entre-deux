# Entre Deux

**The AI companion for the space between doctor appointments.**

Patients with chronic conditions see their specialist every 3-6 months, but between visits they're alone: they can't interpret their lab results, forget what symptoms to report, and carry the emotional weight of managing their condition in silence. When they finally see their doctor, they blank out.

**Entre Deux** fills that gap with a voice-first, AI-powered companion that helps patients understand, remember, and prepare.

## What It Does

### 1. Lab Result Translator

Patient photographs their lab results or ordonnance. AI extracts and explains in plain French:

> "Your HbA1c dropped from 7.2 to 6.8 — that's great, your 3-month average blood sugar improved."

### 2. Voice Health Journal

Between appointments, patients speak naturally about how they're feeling — symptoms, side effects, good days, bad days. AI structures this into a searchable health timeline.

### 3. Visit Brief Generator

Before the next appointment, AI generates a one-page brief: what changed since last visit, trends over time, and suggested questions to ask the doctor.

### 4. Emotional Companion

"I'm tired of being sick" gets a real, empathetic response — not a dashboard. The emotional burden of chronic illness is acknowledged, not ignored.

## Why This Matters

- **60%** of patients forget what to tell their doctor during appointments
- **3-6 months** between specialist visits — patients are the sole integration layer
- **11 million** informal caregivers in France managing someone else's health
- Lab results, medication leaflets, and specialist letters are incomprehensible to most patients

## Tech Stack

| Layer          | Technology                                                                                             |
| -------------- | ------------------------------------------------------------------------------------------------------ |
| **AI Models**  | Mistral Small 4 (reasoning/French), Mistral OCR 3 (document extraction), Voxtral (voice transcription) |
| **Backend**    | Python, FastAPI                                                                                        |
| **Frontend**   | React 19, TypeScript, Tailwind CSS                                                                     |
| **Database**   | PostgreSQL (via Supabase)                                                                              |
| **Deployment** | Docker, Google Cloud Run                                                                               |

## Architecture

```
User → React Frontend (mobile-first)
  ├── Lab photo upload → Mistral OCR 3 → Mistral Small 4 (explain in plain French)
  ├── Voice journal → Voxtral Transcribe → Mistral Small 4 (structure + empathize)
  └── Visit brief request → Small 4 + function calling (aggregate timeline → generate brief)
Backend: FastAPI → PostgreSQL
```

## Hackathon Context

Built for the **Alan x Mistral: AI Health Hack** (April 11, 2026, Paris).

- **Theme:** Reimagining how the world stays healthy
- **Challenge areas:** Preventive care adherence, 24/7 mental health support, chronic condition daily support
- **Format:** 30 curated builders, 12 hours, one track

## Demo Flow (3 minutes)

1. **"Meet Sophie, she has Type 2 diabetes."** → She photographs her lab results → instant plain-French explanation with trend comparison
2. **"Two weeks later, she's exhausted."** → Voice message in French → AI structures it, asks a follow-up question, acknowledges the emotional weight
3. **"Appointment day."** → AI generates a visit brief with trends, changes, and suggested questions for her endocrinologist
4. **Impact:** "60% of patients forget what to tell their doctor. Entre Deux remembers for them."

## Project Structure

```
entre-deux/
├── README.md
├── CLAUDE.md
├── docs/
│   ├── STRATEGY.md          # Hackathon strategy & research
│   ├── PRD.md                # Product Requirements Document
│   └── ARCHITECTURE.md       # Technical architecture decisions
├── backend/                  # FastAPI + Mistral integration
│   ├── src/
│   │   ├── agents/           # Mistral-powered AI agents
│   │   ├── api/              # API routes
│   │   ├── models/           # Database models
│   │   └── services/         # Business logic
│   └── tests/
├── frontend/                 # React 19 + TypeScript
│   ├── src/
│   │   ├── components/       # UI components
│   │   ├── pages/            # Page components
│   │   └── hooks/            # Custom hooks
│   └── tests/
└── docker/                   # Docker configuration
```

## License

MIT
