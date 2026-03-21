
from src.services.pdf_service import generate_visit_brief_pdf

SAMPLE_COMPOSITION: dict = {
    "resourceType": "Composition",
    "id": "test-id",
    "status": "final",
    "title": "Bilan de visite",
    "date": "2026-03-15T10:00:00+00:00",
    "subject": [{"reference": "Patient/123", "display": "Sophie Martin"}],
    "section": [
        {
            "title": "Resume clinique",
            "text": {
                "status": "generated",
                "div": "<div>Patiente de 45 ans suivie pour diabete.</div>",
            },
        },
        {
            "title": "Evolution biologique",
            "text": {
                "status": "generated",
                "div": "<div>HbA1c en amelioration : 8.2% -> 7.1%</div>",
            },
        },
    ],
}


def test_generates_valid_pdf_bytes() -> None:
    """PDF service returns bytes starting with PDF header."""
    pdf_bytes = generate_visit_brief_pdf(SAMPLE_COMPOSITION, "Sophie Martin")
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 100
    assert pdf_bytes[:5] == b"%PDF-"


def test_handles_empty_sections() -> None:
    """PDF generation works with no sections."""
    composition = {
        "resourceType": "Composition",
        "id": "empty",
        "status": "final",
        "title": "Bilan vide",
        "section": [],
    }
    pdf_bytes = generate_visit_brief_pdf(composition, "Test Patient")
    assert pdf_bytes[:5] == b"%PDF-"


def test_handles_french_accents() -> None:
    """PDF generation handles French accented characters."""
    composition = {
        "resourceType": "Composition",
        "id": "accents",
        "status": "final",
        "title": "Bilan de visite",
        "section": [
            {
                "title": "Resume",
                "text": {
                    "status": "generated",
                    "div": (
                        "<div>Amelioration, cree, repondre, "
                        "francais, medecin, therapeutique</div>"
                    ),
                },
            },
        ],
    }
    pdf_bytes = generate_visit_brief_pdf(composition, "Sophie Martin")
    assert pdf_bytes[:5] == b"%PDF-"
    assert len(pdf_bytes) > 100


def test_handles_missing_date() -> None:
    """PDF generation handles missing date gracefully."""
    composition = {
        "resourceType": "Composition",
        "id": "no-date",
        "status": "final",
        "title": "Bilan",
        "section": [
            {
                "title": "Section",
                "text": {"status": "generated", "div": "<div>Content</div>"},
            },
        ],
    }
    pdf_bytes = generate_visit_brief_pdf(composition, "Patient")
    assert pdf_bytes[:5] == b"%PDF-"
