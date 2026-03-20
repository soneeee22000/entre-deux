# Product Requirements Document — Entre Deux

## Product Vision

Entre Deux is the AI companion for the space between doctor appointments, helping chronic condition patients understand their lab results, track their health journey through voice, and walk into every appointment prepared.

## Target User

**Primary:** Patients with chronic conditions (diabetes, cardiovascular, autoimmune) who see specialists every 3-6 months and struggle with:

- Understanding lab results and medical documents
- Remembering symptoms and changes to report
- Preparing for appointments
- The emotional burden of managing their condition alone

**Secondary:** Caregivers managing a family member's health.

**Context:** France-based, French-speaking. Navigating the French healthcare system (parcours de soins, medecin traitant, ALD classifications).

## Core Features (MVP — Hackathon Scope)

### Feature 1: Lab Result Analyzer

**User story:** As a patient, I want to photograph my lab results and get a plain-French explanation so I understand what the numbers mean without Googling.

**Flow:**

1. User uploads a photo of lab results (ordonnance, bilan sanguin)
2. Mistral OCR 3 extracts structured data (test names, values, reference ranges)
3. Mistral Small 4 generates a plain-French explanation with context
4. If previous results exist, show trend comparison
5. Flag any values outside reference range with simple explanation

**Acceptance criteria:**

- Handles standard French lab result formats (bilan sanguin, bilan lipidique, HbA1c)
- Explanation is in plain French (no medical jargon without definition)
- Trend comparison when previous results are stored
- Response time under 10 seconds

### Feature 2: Voice Health Journal

**User story:** As a patient, I want to speak about how I'm feeling between appointments so my symptoms and experiences are captured without manual typing.

**Flow:**

1. User taps microphone and speaks naturally in French
2. Voxtral Transcribe converts speech to text
3. Mistral Small 4 structures the input: extracts symptoms, emotional state, medication mentions, severity
4. AI responds with empathy and may ask a clarifying follow-up
5. Entry is stored in chronological timeline

**Acceptance criteria:**

- French speech recognition via Voxtral
- Structured extraction: symptoms, emotions, medications, dates
- Empathetic response (not clinical/robotic)
- Timeline view of all entries
- Follow-up questions when input is vague

### Feature 3: Visit Brief Generator

**User story:** As a patient, I want a summary of everything that happened since my last appointment so I can share it with my doctor and not forget anything.

**Flow:**

1. User taps "Generate Visit Brief" before their appointment
2. AI aggregates: journal entries, lab results, trends, flagged symptoms
3. Generates a structured one-page brief:
   - Key changes since last visit
   - Symptom timeline with frequency/severity
   - Lab result trends
   - 3-5 suggested questions for the doctor
4. Brief can be shared (PDF or shown on phone)

**Acceptance criteria:**

- Aggregates all data since a configurable "last visit" date
- Structured, scannable format (not a wall of text)
- Includes suggested questions based on symptoms/trends
- Exportable or displayable on mobile

### Feature 4: Emotional Companion Layer

**User story:** As a patient, I want to feel heard when I express frustration or exhaustion about my condition, not just get clinical responses.

**Flow:**

- Embedded in the journal feature
- When user expresses emotional distress ("I'm tired of this," "I can't do this anymore"), AI responds with genuine empathy before structuring the clinical data
- If distress signals are severe, gently suggests resources (3114 crisis line, speaking with their medecin traitant)

**Acceptance criteria:**

- Detects emotional content in journal entries
- Responds with empathy before clinical structuring
- Never claims to be a therapist or offers medical advice
- Provides resource suggestions for severe distress

## Non-Functional Requirements

- **Mobile-first:** Primary use case is on a phone
- **Language:** French (primary), English (stretch)
- **Performance:** OCR + explanation pipeline under 10 seconds
- **Privacy:** No data shared with third parties. Patient data stays in their account
- **Accessibility:** WCAG 2.1 AA compliance for core flows
- **Regulatory positioning:** Organizational/comprehension tool — NOT a medical device, NOT diagnostic

## Out of Scope (Post-Hackathon)

- Integration with Mon Espace Sante or Doctolib APIs
- Multi-patient support for caregivers
- Medication interaction checking
- Doctor-facing dashboard
- Real-time appointment booking
- Push notification system
- Offline mode

## Success Metrics (Hackathon)

- Complete demo flow works end-to-end without crashes
- Lab result explanation is accurate and plain-language
- Voice journal captures and structures input correctly
- Visit brief is coherent and useful
- Judges relate to the problem personally
- Pitch is under 3 minutes with clear impact statement
