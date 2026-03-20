<div align="center">

# Entre Deux

**FHIR-native AI companion for chronic condition patients**

_Filling the gap between doctor appointments with consent-first, audit-logged intelligence_

[![CI](https://github.com/soneeee22000/entre-deux/actions/workflows/ci.yml/badge.svg)](https://github.com/soneeee22000/entre-deux/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-strict-3178C6?logo=typescript&logoColor=white)](https://typescriptlang.org)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![FHIR](https://img.shields.io/badge/FHIR-R5-E44D26?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCI+PHRleHQgeT0iMjAiIGZvbnQtc2l6ZT0iMjAiPvCfjKU8L3RleHQ+PC9zdmc+)](https://hl7.org/fhir/R5/)
[![Mistral AI](https://img.shields.io/badge/Mistral_AI-Small_4-FF7000?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCI+PHRleHQgeT0iMjAiIGZvbnQtc2l6ZT0iMjAiPvCflKU8L3RleHQ+PC9zdmc+)](https://mistral.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## The Problem

Patients with chronic conditions see their specialist every **3-6 months**. Between visits, they're alone:

- They can't interpret their lab results
- They forget symptoms to report
- They carry the emotional weight of managing their condition in silence
- When they finally see their doctor, **60% blank out**

**11 million** informal caregivers in France manage someone else's health with no tools to help.

## The Solution

**Entre Deux** is an AI-powered health companion that helps patients **understand**, **remember**, and **prepare** between doctor appointments. Built consent-first on FHIR R5, designed for the French B2B2C healthcare market.

```mermaid
graph LR
    A["Patient photographs<br/>lab results"] --> B["AI extracts &<br/>explains in French"]
    C["Patient journals<br/>how they feel"] --> D["AI structures symptoms<br/>& responds with empathy"]
    B --> E["Visit Brief<br/>for the doctor"]
    D --> E
    E --> F["Prepared<br/>appointment"]

    style A fill:#f5ede3,stroke:#8b6f47,color:#3d2e1f
    style B fill:#f5ede3,stroke:#8b6f47,color:#3d2e1f
    style C fill:#f5ede3,stroke:#8b6f47,color:#3d2e1f
    style D fill:#f5ede3,stroke:#8b6f47,color:#3d2e1f
    style E fill:#8b6f47,stroke:#3d2e1f,color:#fffbf5
    style F fill:#6b8f71,stroke:#3d2e1f,color:#fffbf5
```

## Features

### Lab Result Translator

Patient photographs their blood work. **Mistral OCR** extracts LOINC-coded observations, creates a FHIR DiagnosticReport, and **Mistral Small** explains in plain French:

> _"Votre HbA1c est passee de 7.2 a 6.8 -- c'est bien, votre glycemie moyenne sur 3 mois s'est amelioree."_

### Health Journal

Between appointments, patients describe how they feel. AI structures it into a FHIR QuestionnaireResponse with symptoms, emotional state, severity, and an empathetic response.

### Visit Brief Generator

Before the next appointment, AI generates a FHIR Composition with 4 sections: key changes, symptom evolution, lab trends, and suggested questions for the doctor.

### Consent + Audit Trail

Every AI interaction requires explicit patient consent (FHIR Consent). Every AI call is audit-logged (FHIR AuditEvent). Designed for **GDPR**, **HDS**, and **CE marking** compliance.

---

## Architecture

```mermaid
graph TB
    subgraph Client["Frontend — React 19 + TypeScript"]
        UI["Mobile-First SPA<br/>Tailwind CSS"]
    end

    subgraph API["FastAPI Backend"]
        Routes["API Routes<br/>/api/v1/*"]
        Consent["Consent Middleware<br/>FHIR Consent check"]
        Services["Service Layer<br/>Lab · Journal · Brief · Audit"]
        Agents["AI Agent Layer"]
        Repos["Repository Layer<br/>Generic CRUD + custom queries"]
    end

    subgraph AI["Mistral AI"]
        OCR["Mistral OCR 3<br/>Image → Text"]
        Small["Mistral Small 4<br/>Structured JSON"]
    end

    subgraph DB["PostgreSQL 16"]
        JSONB["FHIR R5 JSONB<br/>7 tables"]
    end

    UI -->|REST JSON| Routes
    Routes --> Consent
    Consent --> Services
    Services --> Agents
    Services --> Repos
    Agents --> OCR
    Agents --> Small
    Repos --> JSONB

    style Client fill:#f5ede3,stroke:#8b6f47,color:#3d2e1f
    style API fill:#fffbf5,stroke:#8b6f47,color:#3d2e1f
    style AI fill:#fff3e0,stroke:#d4a574,color:#3d2e1f
    style DB fill:#e8f5e9,stroke:#6b8f71,color:#3d2e1f
```

### Clean Architecture Layers

```mermaid
graph LR
    subgraph Presentation
        R["API Routes"]
    end
    subgraph Domain
        S["Services"]
        A["Agents"]
    end
    subgraph Data
        RE["Repositories"]
        T["Tables"]
    end

    R --> S
    S --> A
    S --> RE
    RE --> T

    style Presentation fill:#d4a574,stroke:#8b6f47,color:#3d2e1f
    style Domain fill:#8b6f47,stroke:#3d2e1f,color:#fffbf5
    style Data fill:#6b8f71,stroke:#3d2e1f,color:#fffbf5
```

### FHIR Data Model

```mermaid
erDiagram
    Patient ||--o{ Observation : "has lab results"
    Patient ||--o{ QuestionnaireResponse : "writes journal"
    Patient ||--o{ Composition : "receives briefs"
    Patient ||--o{ Consent : "grants consent"
    Patient ||--o{ DiagnosticReport : "gets reports"
    Observation }o--|| DiagnosticReport : "grouped in"
    AuditEvent }o--o| Patient : "tracks AI calls"

    Patient {
        uuid id PK
        string identifier UK
        jsonb fhir_resource
    }
    Observation {
        uuid id PK
        uuid patient_id FK
        string loinc_code
        jsonb fhir_resource
    }
    QuestionnaireResponse {
        uuid id PK
        uuid patient_id FK
        jsonb fhir_resource
    }
    Composition {
        uuid id PK
        uuid patient_id FK
        string composition_type
        jsonb fhir_resource
    }
    Consent {
        uuid id PK
        uuid patient_id FK
        string scope
        boolean active
        jsonb fhir_resource
    }
    AuditEvent {
        uuid id PK
        string patient_ref
        string agent_name
        string model_version
        jsonb fhir_resource
    }
```

### AI Agent Pipeline

```mermaid
sequenceDiagram
    participant P as Patient
    participant API as FastAPI
    participant CM as Consent<br/>Middleware
    participant S as Service
    participant A as AI Agent
    participant M as Mistral AI
    participant DB as PostgreSQL
    participant AU as Audit

    P->>API: POST /observations/analyze-image
    API->>CM: Check active consent
    CM->>DB: Query ConsentTable
    DB-->>CM: Consent active
    CM-->>API: Authorized
    API->>S: LabResultService.analyze_image()
    S->>A: OCRAgent.extract_lab_results()
    A->>M: Mistral OCR 3 (image)
    M-->>A: Raw text
    A->>M: Mistral Small 4 (parse to JSON)
    M-->>A: Structured results
    A->>AU: Log AuditEvent
    A-->>S: LOINC-coded observations
    S->>DB: Save Observations + DiagnosticReport
    S->>A: ExplanationAgent.explain_results()
    A->>M: Mistral Small 4 (explain)
    M-->>A: French explanation
    A->>AU: Log AuditEvent
    S-->>API: {observations, report, explanation}
    API-->>P: 201 Created
```

---

## Tech Stack

| Layer          | Technology                                    | Purpose                                                       |
| -------------- | --------------------------------------------- | ------------------------------------------------------------- |
| **AI**         | Mistral Small 4, Mistral OCR 3                | Structured extraction, empathetic responses, brief generation |
| **Backend**    | Python 3.10+, FastAPI, SQLAlchemy async       | FHIR-native REST API with dependency injection                |
| **FHIR**       | fhir.resources 8.x (R5), LOINC                | Clinical data interoperability standard                       |
| **Frontend**   | React 19, TypeScript (strict), Tailwind CSS 4 | Mobile-first patient interface                                |
| **Database**   | PostgreSQL 16, JSONB, asyncpg                 | FHIR resources stored as validated JSONB                      |
| **Migrations** | Alembic                                       | Schema versioning with auto-run on deploy                     |
| **Testing**    | pytest (61 tests), vitest (56 tests)          | Unit + integration coverage                                   |
| **CI/CD**      | GitHub Actions, Docker, Google Cloud Run      | Automated lint, type-check, test, build                       |

---

## API Endpoints

| Method | Endpoint                                        | Description                     | Auth    |
| ------ | ----------------------------------------------- | ------------------------------- | ------- |
| `POST` | `/api/v1/patients`                              | Register a new patient          | --      |
| `GET`  | `/api/v1/patients/{id}`                         | Get patient by ID               | --      |
| `GET`  | `/api/v1/patients/{id}/timeline`                | Full patient timeline           | --      |
| `POST` | `/api/v1/observations/analyze-image`            | OCR lab photo into Observations | Consent |
| `POST` | `/api/v1/observations`                          | Create manual observation       | --      |
| `GET`  | `/api/v1/observations/patients/{id}`            | List patient observations       | --      |
| `POST` | `/api/v1/questionnaire-responses`               | Create journal entry            | Consent |
| `GET`  | `/api/v1/questionnaire-responses/patients/{id}` | List journal entries            | --      |
| `POST` | `/api/v1/compositions/visit-brief`              | Generate visit brief            | Consent |
| `GET`  | `/api/v1/compositions/patients/{id}`            | List compositions               | --      |
| `POST` | `/api/v1/consents`                              | Record patient consent          | --      |
| `PUT`  | `/api/v1/consents/{id}/revoke`                  | Revoke consent                  | --      |
| `GET`  | `/api/v1/audit-events`                          | List audit trail                | --      |

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 24+
- PostgreSQL 16+ (or Docker)
- [Mistral AI API key](https://console.mistral.ai/)

### Quick Start (Docker)

```bash
git clone https://github.com/soneeee22000/entre-deux.git
cd entre-deux
cp backend/.env.example backend/.env   # add your MISTRAL_API_KEY
docker compose up --build               # backend :8000 | frontend :5173 | postgres :5433
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

### Manual Setup

**Backend:**

```bash
cd backend
cp .env.example .env                    # add your MISTRAL_API_KEY
pip install -r requirements.txt
alembic upgrade head                    # run database migrations
uvicorn src.main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev                             # starts at http://localhost:5173
```

### Testing

```bash
# Backend — 61 tests
cd backend && pytest -v

# Frontend — 56 tests
cd frontend && npm test

# Linting
cd backend && ruff check src/ tests/
cd frontend && npm run lint
```

---

## Project Structure

```
entre-deux/
├── docker-compose.yml
├── .github/workflows/ci.yml       # CI: lint + type-check + test + build
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic/                    # Database migrations
│   └── src/
│       ├── main.py                 # FastAPI app + router wiring
│       ├── config/settings.py      # Pydantic settings from .env
│       ├── agents/                 # 4 Mistral AI agents
│       │   ├── ocr_agent.py        #   Image → LOINC-coded observations
│       │   ├── explanation_agent.py #   Lab values → French explanation
│       │   ├── journal_agent.py    #   Transcript → structured + empathy
│       │   └── brief_agent.py      #   Data → visit brief sections
│       ├── services/               # 5 business logic orchestrators
│       ├── middleware/consent.py    # Consent enforcement dependency
│       ├── models/                 # FHIR helpers, constants, Pydantic schemas
│       ├── db/                     # Engine, base, 7 tables, 8 repositories
│       └── api/v1/                 # 7 versioned route modules
│
├── frontend/
│   ├── Dockerfile + nginx.conf     # Multi-stage build → nginx
│   └── src/
│       ├── App.tsx                 # Router: 6 pages
│       ├── components/             # 9 reusable UI components
│       ├── pages/                  # Onboarding, Dashboard, Journal,
│       │                           #   LabResults, VisitBrief, Settings
│       └── lib/                    # API client, FHIR types, patient context
│
└── docs/
    ├── PRD.md                      # Product Requirements Document
    ├── ARCHITECTURE.md             # Architecture Decision Records
    └── STRATEGY.md                 # Market strategy & positioning
```

---

## Regulatory Design

```mermaid
graph TB
    subgraph Compliance["Compliance Architecture"]
        direction TB
        GDPR["GDPR<br/>Consent-first data processing"]
        HDS["HDS<br/>Health Data Hosting ready"]
        CE["CE Marking<br/>Medical device pathway"]
        FHIR["FHIR R5<br/>Interoperability standard"]
    end

    subgraph Implementation["How It's Built"]
        C["FHIR Consent<br/>Explicit opt-in per scope"]
        A["FHIR AuditEvent<br/>Every AI call logged"]
        L["LOINC Coding<br/>Standardized lab values"]
        J["JSONB Storage<br/>Full FHIR resources preserved"]
    end

    GDPR --> C
    GDPR --> A
    HDS --> J
    CE --> A
    FHIR --> L
    FHIR --> J

    style Compliance fill:#f5ede3,stroke:#8b6f47,color:#3d2e1f
    style Implementation fill:#e8f5e9,stroke:#6b8f71,color:#3d2e1f
```

---

## Business Model

| Dimension   | Detail                                                                     |
| ----------- | -------------------------------------------------------------------------- |
| **Market**  | French B2B2C healthcare (diabetes-first)                                   |
| **Buyers**  | Healthcare insurers (mutuelles), hospital groups, diabetes care networks   |
| **Revenue** | Per-patient SaaS licensing to enterprise buyers                            |
| **TAM**     | 4M+ diabetic patients in France, 11M informal caregivers                   |
| **Moat**    | FHIR-native data model + regulatory compliance + Mistral AI (sovereign AI) |

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

Built with [Mistral AI](https://mistral.ai) | [FHIR R5](https://hl7.org/fhir/R5/) | [FastAPI](https://fastapi.tiangolo.com) | [React](https://react.dev)

</div>
