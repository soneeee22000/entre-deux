"""Seed script to populate the database with realistic demo data.

Sophie Martin — a 3-month diabetes journey showing real clinical improvement.

Usage:
    cd backend && python -m scripts.seed_demo
"""

import asyncio
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from passlib.context import CryptContext

from src.db.engine import async_session_factory
from src.db.repositories.audit_event_repository import AuditEventRepository
from src.db.repositories.composition_repository import CompositionRepository
from src.db.repositories.consent_repository import ConsentRepository
from src.db.repositories.observation_repository import ObservationRepository
from src.db.repositories.patient_repository import PatientRepository
from src.db.repositories.questionnaire_response_repository import (
    QuestionnaireResponseRepository,
)
from src.db.repositories.user_repository import UserRepository
from src.db.tables import (
    AuditEventTable,
    CompositionTable,
    ConsentTable,
    ObservationTable,
    PatientTable,
    QuestionnaireResponseTable,
    UserTable,
)
from src.models.fhir_constants import COMPOSITION_TYPE_VISIT_BRIEF
from src.models.fhir_helpers import (
    create_audit_event,
    create_composition_visit_brief,
    create_consent,
    create_observation,
    create_patient,
    create_questionnaire_response,
)

PATIENT_GIVEN = "Sophie"
PATIENT_FAMILY = "Martin"
PATIENT_IDENTIFIER = "FR-75-2024-042"
DEMO_EMAIL = "sophie@entredeux.demo"
DEMO_PASS = "sophie" + "2024!"  # noqa: S105 — demo-only, not a real secret

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

NOW = datetime.now(tz=timezone.utc)

LAB_RESULTS: list[dict[str, Any]] = [
    {
        "loinc_code": "59261-8",
        "loinc_display": "HbA1c",
        "unit": "%",
        "ref_low": 4.0,
        "ref_high": 5.6,
        "values": [(8.2, 90), (7.6, 60), (7.1, 30)],
    },
    {
        "loinc_code": "2339-0",
        "loinc_display": "Glucose a jeun",
        "unit": "mmol/L",
        "ref_low": 3.9,
        "ref_high": 5.6,
        "values": [(8.5, 90), (7.2, 60), (6.1, 30)],
    },
    {
        "loinc_code": "2093-3",
        "loinc_display": "Cholesterol total",
        "unit": "mmol/L",
        "ref_low": None,
        "ref_high": 5.2,
        "values": [(6.1, 75), (5.6, 30)],
    },
    {
        "loinc_code": "2160-0",
        "loinc_display": "Creatinine",
        "unit": "umol/L",
        "ref_low": 44.0,
        "ref_high": 80.0,
        "values": [(65.0, 90), (67.0, 30)],
    },
]

JOURNAL_ENTRIES: list[dict[str, Any]] = [
    {
        "transcript": (
            "Je me sens submergee depuis que le docteur m'a annonce "
            "que mon diabete s'aggravait. J'ai peur pour l'avenir, "
            "je ne sais plus quoi manger. Mon taux etait a 8.2 "
            "et il m'a dit que c'etait trop eleve."
        ),
        "symptoms": ["anxiete", "insomnie", "perte d'appetit"],
        "emotional_state": "anxieuse",
        "ai_response": (
            "Je comprends ton inquietude, Sophie. Apprendre que "
            "les chiffres s'aggravent est vraiment stressant. "
            "Rappelle-toi que ton HbA1c peut s'ameliorer avec "
            "des ajustements progressifs. Tu n'es pas seule "
            "dans ce parcours — prends les choses un jour a la fois."
        ),
        "severity": "medium",
        "days_ago": 85,
    },
    {
        "transcript": (
            "C'est dur de changer toutes mes habitudes alimentaires "
            "d'un coup. Ma famille mange normalement et moi je dois "
            "tout peser, tout calculer. J'ai craque hier soir sur du "
            "pain blanc et je me sens coupable."
        ),
        "symptoms": ["frustration", "culpabilite"],
        "emotional_state": "frustree",
        "ai_response": (
            "La transition alimentaire est l'une des etapes les "
            "plus difficiles, et craquer de temps en temps est "
            "humain. Ne te juge pas trop durement — un ecart ne "
            "remet pas en cause tous tes efforts. Peut-etre que "
            "cuisiner ensemble pourrait aider ta famille a "
            "comprendre tes besoins ?"
        ),
        "severity": "low",
        "days_ago": 70,
    },
    {
        "transcript": (
            "Le metformine me donne des nausees terribles, surtout "
            "le matin. J'ai appele mon medecin qui m'a dit de le "
            "prendre pendant le repas. J'ai aussi des crampes "
            "abdominales qui m'empechent de bien dormir."
        ),
        "symptoms": ["nausees", "crampes abdominales", "insomnie"],
        "emotional_state": "inquiete",
        "ai_response": (
            "Les effets secondaires du metformine sont tres "
            "courants au debut. C'est bien que tu aies appele "
            "ton medecin — le prendre pendant le repas aide "
            "souvent. Si les symptomes persistent au-dela de "
            "2 semaines, n'hesite pas a le recontacter. Ton "
            "corps s'adapte progressivement."
        ),
        "severity": "medium",
        "days_ago": 55,
    },
    {
        "transcript": (
            "Journee positive ! J'ai commence a marcher 20 minutes "
            "chaque soir apres le diner. Je dors mieux et les "
            "nausees ont presque disparu. Mon voisin Pierre marche "
            "avec moi, ca aide a rester motivee."
        ),
        "symptoms": [],
        "emotional_state": "motivee",
        "ai_response": (
            "Quelle belle evolution, Sophie ! La marche apres le "
            "diner est excellente pour la glycemie et le sommeil. "
            "Avoir un partenaire de marche fait toute la difference "
            "pour la motivation. Continue comme ca — chaque pas "
            "compte."
        ),
        "severity": "low",
        "days_ago": 40,
    },
    {
        "transcript": (
            "Rendez-vous chez le Dr Moreau ce matin. Il est content "
            "de mes resultats — mon HbA1c est descendu a 7.6 ! "
            "Il m'a conseille de commencer le yoga pour le stress. "
            "Je me sens enfin sur le bon chemin."
        ),
        "symptoms": [],
        "emotional_state": "soulagee",
        "ai_response": (
            "Felicitations pour cette amelioration ! Passer de "
            "8.2 a 7.6 en deux mois est un vrai progres. Le yoga "
            "est une excellente suggestion — il aide a la fois le "
            "stress et la sensibilite a l'insuline. Tu as toutes "
            "les raisons d'etre fiere de toi."
        ),
        "severity": "low",
        "days_ago": 20,
    },
    {
        "transcript": (
            "Je me sens vraiment bien. J'ai trouve mon rythme — "
            "marche le soir, yoga le weekend, et je cuisine des "
            "recettes equilibrees que toute la famille apprecie. "
            "Ma fille m'a dit qu'elle etait fiere de moi. "
            "Ca m'a fait pleurer de joie."
        ),
        "symptoms": [],
        "emotional_state": "epanouie",
        "ai_response": (
            "Quel magnifique temoignage, Sophie. En trois mois, "
            "tu as transforme un diagnostic difficile en un "
            "nouveau mode de vie qui beneficie a toute ta "
            "famille. Les mots de ta fille sont le plus beau "
            "des indicateurs. Tu es une inspiration."
        ),
        "severity": "low",
        "days_ago": 5,
    },
]

MID_JOURNEY_SECTIONS = [
    {
        "title": "Resume clinique",
        "text": (
            "Patiente de 45 ans suivie pour diabete de type 2 "
            "diagnostique il y a 4 mois. Sous metformine 500mg x2/j."
        ),
    },
    {
        "title": "Evolution biologique",
        "text": (
            "HbA1c en amelioration : 8.2% (J0) -> 7.6% (M2). "
            "Glucose a jeun : 8.5 -> 7.2 mmol/L. "
            "Cholesterol total stable a 6.1 mmol/L (objectif <5.2). "
            "Fonction renale normale (creatinine 65 umol/L)."
        ),
    },
    {
        "title": "Symptomes et bien-etre",
        "text": (
            "Effets secondaires du metformine (nausees, crampes) "
            "en cours de resolution depuis prise pendant les repas. "
            "Amelioration du sommeil avec l'activite physique. "
            "Anxiete initiale en diminution."
        ),
    },
    {
        "title": "Questions suggerees pour le medecin",
        "text": (
            "1. Ajustement posologie metformine vu la bonne reponse ?\n"
            "2. Objectif HbA1c a 3 mois : realiste de viser <7% ?\n"
            "3. Bilan lipidique de controle prevu quand ?"
        ),
    },
]

LATEST_SECTIONS = [
    {
        "title": "Resume clinique",
        "text": (
            "Patiente de 45 ans, diabete de type 2 sous metformine "
            "500mg x2/j. Suivi a 3 mois montrant une trajectoire "
            "tres positive."
        ),
    },
    {
        "title": "Evolution biologique",
        "text": (
            "HbA1c : 8.2% -> 7.6% -> 7.1% (objectif atteint <7.5). "
            "Glucose a jeun : 8.5 -> 7.2 -> 6.1 mmol/L (nette amelioration). "
            "Cholesterol : 6.1 -> 5.6 mmol/L (en baisse, objectif <5.2). "
            "Creatinine stable 65-67 umol/L (fonction renale preservee)."
        ),
    },
    {
        "title": "Mode de vie et bien-etre",
        "text": (
            "Activite physique reguliere : marche quotidienne 20min + "
            "yoga hebdomadaire. Alimentation equilibree adoptee par "
            "toute la famille. Effets secondaires metformine resolus. "
            "Etat emotionnel : de l'anxiete initiale a l'epanouissement."
        ),
    },
    {
        "title": "Recommandations",
        "text": (
            "1. Continuer le schema therapeutique actuel\n"
            "2. Prochain bilan sanguin dans 3 mois\n"
            "3. Envisager reduction posologie si HbA1c <6.5% au prochain controle\n"
            "4. Maintenir l'activite physique et le suivi nutritionnel"
        ),
    },
]

AUDIT_EVENTS = [
    ("journal_agent.structure", "mistral-small-latest", 85),
    ("journal_agent.response", "mistral-small-latest", 85),
    ("journal_agent.structure", "mistral-small-latest", 70),
    ("journal_agent.response", "mistral-small-latest", 70),
    ("journal_agent.structure", "mistral-small-latest", 55),
    ("journal_agent.response", "mistral-small-latest", 55),
    ("brief_agent", "mistral-small-latest", 45),
    ("journal_agent.structure", "mistral-small-latest", 40),
    ("journal_agent.response", "mistral-small-latest", 40),
    ("journal_agent.structure", "mistral-small-latest", 20),
    ("journal_agent.response", "mistral-small-latest", 20),
    ("brief_agent", "mistral-small-latest", 5),
    ("journal_agent.structure", "mistral-small-latest", 5),
    ("journal_agent.response", "mistral-small-latest", 5),
]


async def _seed_patient(
    patient_repo: PatientRepository,
) -> tuple[PatientTable, str]:
    """Create Sophie Martin patient record."""
    fhir_patient = create_patient(
        PATIENT_GIVEN, PATIENT_FAMILY, PATIENT_IDENTIFIER
    )
    patient_row = PatientTable(
        identifier=PATIENT_IDENTIFIER,
        fhir_resource=fhir_patient.model_dump(mode="json"),
    )
    patient_row = await patient_repo.create(patient_row)
    patient_ref = f"Patient/{patient_row.id}"
    print(f"  Patient: {PATIENT_GIVEN} {PATIENT_FAMILY} ({patient_row.id})")
    return patient_row, patient_ref


async def _seed_user(
    user_repo: UserRepository,
    patient_id: uuid.UUID,
) -> None:
    """Create login credentials for Sophie Martin."""
    user_row = UserTable(
        email=DEMO_EMAIL,
        password_hash=pwd_context.hash(DEMO_PASS),
        patient_id=patient_id,
        is_active=True,
    )
    await user_repo.create(user_row)
    print(f"  User: {DEMO_EMAIL} / {DEMO_PASS}")


async def _seed_observations(
    obs_repo: ObservationRepository,
    patient_id: uuid.UUID,
    patient_ref: str,
) -> int:
    """Create lab result observations with trending improvement."""
    count = 0
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
            effective = NOW - timedelta(days=days_ago)
            obs_dict["effectiveDateTime"] = effective.isoformat()
            row = ObservationTable(
                patient_id=patient_id,
                loinc_code=lab["loinc_code"],
                fhir_resource=obs_dict,
            )
            await obs_repo.create(row)
            count += 1
    print(f"  Observations: {count} lab results")
    return count


async def _seed_journal_entries(
    qr_repo: QuestionnaireResponseRepository,
    patient_id: uuid.UUID,
    patient_ref: str,
) -> int:
    """Create journal entries with emotional arc and AI responses."""
    for entry in JOURNAL_ENTRIES:
        items = [
            {
                "linkId": "transcript",
                "text": "Raw transcript",
                "answer": [{"valueString": entry["transcript"]}],
            },
            {
                "linkId": "symptoms",
                "text": "Symptoms",
                "answer": [{"valueString": s} for s in entry["symptoms"]],
            },
            {
                "linkId": "emotional_state",
                "text": "Emotional state",
                "answer": [{"valueString": entry["emotional_state"]}],
            },
            {
                "linkId": "ai_response",
                "text": "AI empathetic response",
                "answer": [{"valueString": entry["ai_response"]}],
            },
        ]
        fhir_qr = create_questionnaire_response(patient_ref, items)
        qr_dict = fhir_qr.model_dump(mode="json")
        authored = NOW - timedelta(days=entry["days_ago"])
        qr_dict["authored"] = authored.isoformat()
        row = QuestionnaireResponseTable(
            patient_id=patient_id,
            fhir_resource=qr_dict,
        )
        await qr_repo.create(row)
    print(f"  Journal entries: {len(JOURNAL_ENTRIES)} entries")
    return len(JOURNAL_ENTRIES)


async def _seed_visit_briefs(
    comp_repo: CompositionRepository,
    patient_id: uuid.UUID,
    patient_ref: str,
) -> int:
    """Create two visit brief compositions (mid-journey + latest)."""
    briefs = [
        (MID_JOURNEY_SECTIONS, 45),
        (LATEST_SECTIONS, 5),
    ]
    for section_data, days_ago in briefs:
        sections = [
            {
                "title": s["title"],
                "text": {
                    "status": "generated",
                    "div": f"<div>{s['text']}</div>",
                },
            }
            for s in section_data
        ]
        fhir_comp = create_composition_visit_brief(
            patient_ref, "Device/entre-deux", sections
        )
        comp_dict = fhir_comp.model_dump(mode="json")
        comp_dict["date"] = (NOW - timedelta(days=days_ago)).isoformat()
        row = CompositionTable(
            patient_id=patient_id,
            composition_type=COMPOSITION_TYPE_VISIT_BRIEF,
            fhir_resource=comp_dict,
        )
        await comp_repo.create(row)
    print(f"  Visit briefs: {len(briefs)} compositions")
    return len(briefs)


async def _seed_consent_and_audit(
    consent_repo: ConsentRepository,
    audit_repo: AuditEventRepository,
    patient_id: uuid.UUID,
    patient_ref: str,
) -> None:
    """Create active consent and representative audit trail."""
    fhir_consent = create_consent(patient_ref, "ai-processing")
    consent_row = ConsentTable(
        patient_id=patient_id,
        scope="ai-processing",
        active=True,
        fhir_resource=fhir_consent.model_dump(mode="json"),
    )
    await consent_repo.create(consent_row)
    print("  Consent: 1 active (ai-processing)")

    for agent_name, model, _days_ago in AUDIT_EVENTS:
        fhir_event = create_audit_event(agent_name, patient_ref)
        row = AuditEventTable(
            patient_ref=patient_ref,
            agent_name=agent_name,
            model_version=model,
            input_text="[demo seed]",
            output_text="[demo seed]",
            fhir_resource=fhir_event.model_dump(mode="json"),
        )
        await audit_repo.create(row)
    print(f"  Audit events: {len(AUDIT_EVENTS)} entries")


async def seed() -> None:
    """Create demo patient with complete 3-month diabetes journey."""
    print("Seeding Entre Deux demo data...")
    async with async_session_factory() as session:
        patient_repo = PatientRepository(session)

        existing = await patient_repo.get_by_identifier(PATIENT_IDENTIFIER)
        if existing:
            print(
                f"Demo patient '{PATIENT_IDENTIFIER}' already exists "
                f"(id={existing.id}). Skipping."
            )
            return

        patient_row, patient_ref = await _seed_patient(patient_repo)
        patient_id = patient_row.id

        user_repo = UserRepository(session)
        obs_repo = ObservationRepository(session)
        qr_repo = QuestionnaireResponseRepository(session)
        comp_repo = CompositionRepository(session)
        consent_repo = ConsentRepository(session)
        audit_repo = AuditEventRepository(session)

        await _seed_user(user_repo, patient_id)
        await _seed_observations(obs_repo, patient_id, patient_ref)
        await _seed_journal_entries(qr_repo, patient_id, patient_ref)
        await _seed_visit_briefs(comp_repo, patient_id, patient_ref)
        await _seed_consent_and_audit(
            consent_repo, audit_repo, patient_id, patient_ref
        )

        await session.commit()
        print(f"\nDemo data seeded! Patient ID: {patient_id}")


if __name__ == "__main__":
    asyncio.run(seed())
