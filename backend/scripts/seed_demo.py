"""Seed script to populate the database with realistic demo data.

Usage:
    cd backend && python -m scripts.seed_demo
"""

import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.db.engine import async_session_factory
from src.db.repositories.composition_repository import CompositionRepository
from src.db.repositories.consent_repository import ConsentRepository
from src.db.repositories.observation_repository import ObservationRepository
from src.db.repositories.patient_repository import PatientRepository
from src.db.repositories.questionnaire_response_repository import (
    QuestionnaireResponseRepository,
)
from src.db.tables import (
    CompositionTable,
    ConsentTable,
    ObservationTable,
    PatientTable,
    QuestionnaireResponseTable,
)
from src.models.fhir_constants import COMPOSITION_TYPE_VISIT_BRIEF
from src.models.fhir_helpers import (
    create_composition_visit_brief,
    create_consent,
    create_observation,
    create_patient,
    create_questionnaire_response,
)

PATIENT_GIVEN = "Marie"
PATIENT_FAMILY = "Laurent"
PATIENT_IDENTIFIER = "FR-75-2024-001"

LAB_RESULTS = [
    {"loinc_code": "59261-8", "loinc_display": "HbA1c", "unit": "%", "ref_low": 4.0, "ref_high": 5.6,
     "values": [(7.2, 90), (6.9, 60), (6.5, 30)]},
    {"loinc_code": "2339-0", "loinc_display": "Glucose a jeun", "unit": "mmol/L", "ref_low": 3.9, "ref_high": 5.6,
     "values": [(6.8, 90), (6.2, 60), (5.9, 30)]},
    {"loinc_code": "2093-3", "loinc_display": "Cholesterol total", "unit": "mmol/L", "ref_low": None, "ref_high": 5.2,
     "values": [(5.8, 80), (5.4, 40)]},
    {"loinc_code": "2160-0", "loinc_display": "Creatinine", "unit": "umol/L", "ref_low": 44.0, "ref_high": 80.0,
     "values": [(62.0, 90), (58.0, 60), (60.0, 30)]},
]

JOURNAL_ENTRIES = [
    {"transcript": "Aujourd'hui je me sens fatiguee, j'ai mal dormi. Mon taux de sucre etait un peu haut ce matin.",
     "symptoms": ["fatigue", "insomnie"], "emotional_state": "fatiguee", "days_ago": 85},
    {"transcript": "J'ai mange equilibre toute la semaine. Je me sens motivee et energique.",
     "symptoms": [], "emotional_state": "motivee", "days_ago": 72},
    {"transcript": "Maux de tete depuis hier. J'ai pris mon metformine comme d'habitude.",
     "symptoms": ["maux de tete"], "emotional_state": "inquiete", "days_ago": 58},
    {"transcript": "Bonne journee, j'ai marche 30 minutes. Mon moral est au beau fixe.",
     "symptoms": [], "emotional_state": "positive", "days_ago": 45},
    {"transcript": "Un peu anxieuse avant mon rendez-vous chez le medecin la semaine prochaine.",
     "symptoms": ["anxiete"], "emotional_state": "anxieuse", "days_ago": 35},
    {"transcript": "Tres contente, mon HbA1c a baisse ! Le medecin est satisfait de mes progres.",
     "symptoms": [], "emotional_state": "contente", "days_ago": 25},
    {"transcript": "Fatigue inhabituelle aujourd'hui, peut-etre le changement de saison.",
     "symptoms": ["fatigue"], "emotional_state": "fatiguee", "days_ago": 12},
    {"transcript": "Je me sens bien, j'ai commence le yoga. Ca m'aide a gerer le stress.",
     "symptoms": [], "emotional_state": "sereine", "days_ago": 3},
]

BRIEF_SECTIONS = [
    {"title": "Changements cles", "text": "HbA1c en amelioration (7.2% -> 6.5%), glucose a jeun se normalise."},
    {"title": "Evolution des symptomes", "text": "Episodes de fatigue intermittents, anxiete pre-rdv resolue. Debut du yoga."},
    {"title": "Tendances biologiques", "text": "Toutes les valeurs en tendance favorable. Cholesterol en legere baisse."},
    {"title": "Questions suggerees", "text": "Discuter de l'ajustement du metformine vu les bons resultats."},
]


async def seed() -> None:
    """Create demo patient with observations, journal entries, visit brief, and consent."""
    async with async_session_factory() as session:
        patient_repo = PatientRepository(session)
        obs_repo = ObservationRepository(session)
        qr_repo = QuestionnaireResponseRepository(session)
        comp_repo = CompositionRepository(session)
        consent_repo = ConsentRepository(session)

        existing = await patient_repo.get_by_identifier(PATIENT_IDENTIFIER)
        if existing:
            print(f"Demo patient '{PATIENT_IDENTIFIER}' already exists (id={existing.id}). Skipping.")
            return

        fhir_patient = create_patient(PATIENT_GIVEN, PATIENT_FAMILY, PATIENT_IDENTIFIER)
        patient_row = PatientTable(
            identifier=PATIENT_IDENTIFIER,
            fhir_resource=fhir_patient.model_dump(mode="json"),
        )
        patient_row = await patient_repo.create(patient_row)
        patient_id = patient_row.id
        patient_ref = f"Patient/{patient_id}"
        print(f"Created patient: {PATIENT_GIVEN} {PATIENT_FAMILY} ({patient_id})")

        now = datetime.now(tz=timezone.utc)
        obs_count = 0
        for lab in LAB_RESULTS:
            for value, days_ago in lab["values"]:
                fhir_obs = create_observation(
                    patient_ref=patient_ref,
                    loinc_code=lab["loinc_code"],
                    loinc_display=lab["loinc_display"],
                    value=value,
                    unit=lab["unit"],
                    reference_range_low=lab["ref_low"],
                    reference_range_high=lab["ref_high"],
                )
                obs_dict = fhir_obs.model_dump(mode="json")
                obs_dict["effectiveDateTime"] = (now - timedelta(days=days_ago)).isoformat()
                row = ObservationTable(
                    patient_id=patient_id,
                    loinc_code=lab["loinc_code"],
                    fhir_resource=obs_dict,
                )
                await obs_repo.create(row)
                obs_count += 1
        print(f"Created {obs_count} observations")

        for entry in JOURNAL_ENTRIES:
            items = [
                {"linkId": "transcript", "text": "Raw transcript",
                 "answer": [{"valueString": entry["transcript"]}]},
                {"linkId": "symptoms", "text": "Symptoms",
                 "answer": [{"valueString": s} for s in entry["symptoms"]]},
                {"linkId": "emotional_state", "text": "Emotional state",
                 "answer": [{"valueString": entry["emotional_state"]}]},
                {"linkId": "ai_response", "text": "AI empathetic response",
                 "answer": [{"valueString": "Merci de partager. Prenez soin de vous."}]},
            ]
            fhir_qr = create_questionnaire_response(patient_ref, items)
            qr_dict = fhir_qr.model_dump(mode="json")
            qr_dict["authored"] = (now - timedelta(days=entry["days_ago"])).isoformat()
            row = QuestionnaireResponseTable(
                patient_id=patient_id,
                fhir_resource=qr_dict,
            )
            await qr_repo.create(row)
        print(f"Created {len(JOURNAL_ENTRIES)} journal entries")

        sections = [
            {"title": s["title"], "text": {"status": "generated", "div": f"<div>{s['text']}</div>"}}
            for s in BRIEF_SECTIONS
        ]
        fhir_comp = create_composition_visit_brief(patient_ref, "Device/entre-deux", sections)
        comp_row = CompositionTable(
            patient_id=patient_id,
            composition_type=COMPOSITION_TYPE_VISIT_BRIEF,
            fhir_resource=fhir_comp.model_dump(mode="json"),
        )
        await comp_repo.create(comp_row)
        print("Created 1 visit brief composition")

        fhir_consent = create_consent(patient_ref, "ai-processing")
        consent_row = ConsentTable(
            patient_id=patient_id,
            scope="ai-processing",
            active=True,
            fhir_resource=fhir_consent.model_dump(mode="json"),
        )
        await consent_repo.create(consent_row)
        print("Created 1 active consent (ai-processing)")

        await session.commit()
        print(f"\nDemo data seeded successfully! Patient ID: {patient_id}")


if __name__ == "__main__":
    asyncio.run(seed())
