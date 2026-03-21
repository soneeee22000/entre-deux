import io
import re
from datetime import datetime
from typing import Any

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


def generate_visit_brief_pdf(
    composition_fhir: dict[str, Any], patient_name: str
) -> bytes:
    """Generate a PDF visit brief from a FHIR Composition."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )
    styles = _build_styles()
    story: list[Any] = []

    _build_header(story, styles, composition_fhir, patient_name)
    _build_sections(story, styles, composition_fhir)
    _build_footer(story, styles)

    doc.build(story)
    return buffer.getvalue()


def _build_styles() -> dict[str, ParagraphStyle]:
    """Create PDF paragraph styles."""
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "PDFTitle",
            parent=base["Heading1"],
            fontSize=16,
            spaceAfter=6 * mm,
        ),
        "subtitle": ParagraphStyle(
            "PDFSubtitle",
            parent=base["Normal"],
            fontSize=10,
            textColor=HexColor("#666666"),
            spaceAfter=4 * mm,
        ),
        "section_title": ParagraphStyle(
            "PDFSectionTitle",
            parent=base["Heading2"],
            fontSize=13,
            spaceBefore=4 * mm,
            spaceAfter=2 * mm,
        ),
        "body": ParagraphStyle(
            "PDFBody",
            parent=base["Normal"],
            fontSize=11,
            leading=15,
            spaceAfter=2 * mm,
        ),
        "footer": ParagraphStyle(
            "PDFFooter",
            parent=base["Normal"],
            fontSize=8,
            textColor=HexColor("#999999"),
            spaceBefore=8 * mm,
        ),
    }


def _build_header(
    story: list[Any],
    styles: dict[str, ParagraphStyle],
    composition: dict[str, Any],
    patient_name: str,
) -> None:
    """Add title, patient info, and date to the PDF."""
    title = composition.get("title", "Bilan de visite")
    story.append(Paragraph(f"Entre Deux &mdash; {title}", styles["title"]))

    comp_date = composition.get("date", "")
    date_str = _format_date(comp_date) if comp_date else "Date non disponible"
    info = f"Patient : {patient_name} &bull; Date : {date_str}"
    story.append(Paragraph(info, styles["subtitle"]))
    story.append(Spacer(1, 4 * mm))


def _build_sections(
    story: list[Any],
    styles: dict[str, ParagraphStyle],
    composition: dict[str, Any],
) -> None:
    """Add composition sections to the PDF."""
    sections = composition.get("section", [])
    for section in sections:
        section_title = section.get("title", "")
        if section_title:
            story.append(Paragraph(section_title, styles["section_title"]))

        text_div = section.get("text", {}).get("div", "")
        clean_text = _strip_html(text_div)
        if clean_text:
            paragraphs = clean_text.split("\n")
            for para in paragraphs:
                stripped = para.strip()
                if stripped:
                    story.append(Paragraph(stripped, styles["body"]))


def _build_footer(
    story: list[Any], styles: dict[str, ParagraphStyle]
) -> None:
    """Add disclaimer footer to the PDF."""
    story.append(Spacer(1, 10 * mm))
    disclaimer = (
        "Ce document est genere automatiquement par Entre Deux a titre "
        "informatif. Il ne constitue pas un avis medical. Consultez "
        "votre medecin pour toute decision therapeutique."
    )
    story.append(Paragraph(disclaimer, styles["footer"]))


def _strip_html(html: str) -> str:
    """Remove HTML tags from a string."""
    return re.sub(r"<[^>]+>", "", html).strip()


def _format_date(iso_date: str) -> str:
    """Format an ISO date string to French date format."""
    try:
        parsed = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
        return parsed.strftime("%d/%m/%Y")
    except (ValueError, AttributeError):
        return iso_date
