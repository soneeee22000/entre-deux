# Hackathon Strategy — Alan x Mistral Health Hack

## Event Details

- **Event:** Alan x Mistral: AI Health Hack
- **Date:** Saturday, April 11, 2026
- **Location:** Paris (exact address on registration)
- **Format:** 30 curated builders, 12 hours, one track
- **Prizes:** Up to 2,500 EUR for top team
- **Perks:** Mistral Vibe credits, meals, mentoring from Alan's engineering/product/medical teams
- **Pipeline:** Direct path to full-time roles at Alan

## Intelligence Summary

### About Alan

- Vertically integrated health partner (not just insurance) — covers 1M+ members, 700M+ EUR ARR
- Product combines insurance + care access (teleconsultation, AI medical chat) + prevention
- Their AI "Mo" is an LLM-based health companion that can prescribe, triage, and follow up
- Tech stack: Python/Flask, React, React Native, PostgreSQL
- Hiring 27 engineering roles across 5 AI-focused teams
- Mission: "Help people live in good health to 100"
- Values: distributed ownership, radical transparency, fight for simplicity

### About Mistral

- Mistral Small 4 launched March 16, 2026 — unified instruct/reasoning/coding, 119B params MoE
- Voxtral for real-time audio transcription
- Mistral OCR 3 for document processing
- Best-in-class French language capabilities (Paris-based company)
- Open-weight models, EU data sovereignty
- Function calling with parallel tool support

### What Judges Score On

| Criteria                     | Weight |
| ---------------------------- | ------ |
| Problem-Solution Fit         | ~32%   |
| Innovation / Differentiation | ~25%   |
| Technical Depth              | ~20%   |
| Execution Quality            | ~15%   |
| Presentation / Storytelling  | ~14%   |

### Overdone Ideas (AVOID)

- Generic symptom checker chatbots
- Mental health chatbots (generic CBT/mood trackers)
- Medication reminder apps
- Generic fitness/diet trackers
- "AI doctor" assistants with no domain focus
- Flashy dashboards without real users
- Generic EHR summarizers

### Winning Patterns from Past Health Hackathons

- Narrow scope: one clearly defined use case, not a platform
- AI as the engine, but the problem is the star
- Multi-modal or multi-agent approaches stand out
- Real data or realistic simulation in the demo
- Problem clarity + differentiation > technical flashiness
- Practice pitch multiple times — top teams start pitch prep at T-6 hours

## Why "Entre Deux"

### The Gap We're Filling

Nobody owns the between-appointment space. Alan's "Mo" handles triage and acute care. Doctolib handles scheduling. But the 3-6 months between specialist visits — where patients are alone with incomprehensible lab results, accumulating symptoms they'll forget, and emotional weight they carry silently — is completely unaddressed.

### Strategic Alignment

- **Adjacent to Alan, not competitive:** Complements Mo (triage) rather than replacing it
- **Directly supports Alan's prevention mission:** Helps patients stay engaged with their health between visits
- **Uses 3 Mistral capabilities:** OCR 3, Voxtral, Small 4 — demonstrates technical depth with their newest models
- **France-specific value:** Plain French explanations, French healthcare system context
- **No regulatory risk:** Organizational/comprehension tool, not diagnostic

### Differentiation from Other Teams

In a room of 30 builders, the likely distribution:

- 5-8 will build generic health chatbots
- 3-5 will build symptom trackers
- 3-5 will build mental health tools
- 2-3 will build medication management
- The remaining will try something creative

"Entre Deux" is in the creative category — a specific, relatable problem that nobody else will think of because it's not about a medical condition, it's about the patient experience of managing one.

## 12-Hour Build Plan

### Hour 0-1: Setup & Validation

- Project scaffold (FastAPI + React)
- Mistral API credentials and model testing
- Validate OCR on a real French lab result
- Talk to Alan mentors — validate the problem

### Hour 1-3: Core Backend

- Lab result photo → OCR → explanation pipeline
- Voice transcription → structured journal entry
- PostgreSQL schema: patients, journal_entries, lab_results, visit_briefs

### Hour 3-6: Frontend + Integration

- Mobile-first UI: photo upload, voice recorder, timeline view
- Connect to backend APIs
- Visit brief generation endpoint

### Hour 6-9: Polish & Edge Cases

- Visit brief template and generation logic
- Emotional response handling in journal entries
- Error handling and loading states
- Demo data seeding

### Hour 9-11: Demo Prep

- Record backup demo video
- Practice pitch 3x minimum
- Polish UI for demo resolution
- Prepare impact statistics

### Hour 11-12: Final Polish

- Bug fixes only — no new features
- Final pitch rehearsal
- Deploy to Cloud Run

## Demo Script (3 Minutes)

### Act 1: The Problem (30 sec)

"Meet Sophie. She has Type 2 diabetes. She sees her endocrinologist every 4 months. Between visits, she gets lab results she can't understand, experiences symptoms she forgets to mention, and carries the weight of managing her condition alone."

### Act 2: Lab Results (45 sec)

Sophie photographs her lab results. Entre Deux instantly explains them in plain French — not medical jargon. "Your HbA1c dropped from 7.2 to 6.8 — your 3-month blood sugar average improved. Your doctor will be pleased."

### Act 3: Voice Journal (45 sec)

Two weeks later, Sophie is exhausted. She opens Entre Deux and speaks: "I've been really tired this week, my feet are tingling, and I'm stressed about my next appointment." The AI structures this, asks a follow-up, and acknowledges the emotional weight: "That sounds difficult. The tingling is worth mentioning to your doctor — I'll add it to your visit brief."

### Act 4: Visit Brief (30 sec)

Appointment day. Sophie opens her visit brief: a one-page summary of what changed since her last visit, trends in her symptoms, and three suggested questions for her endocrinologist. She walks in prepared.

### Act 5: Impact (30 sec)

"60% of patients forget what to tell their doctor. 281 million people worldwide manage chronic conditions between appointments alone. Entre Deux gives them a memory, a voice, and a companion for the space between."
