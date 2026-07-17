#!/usr/bin/env python3
"""
Build the HR SJT (Rating Effectiveness) HSIRB full packet in the familiar
Nicholls-branded format (same style as A Study in Decision Making).

Usage:
    python3 scripts/build_hr_sjt_hsirb_packet.py
"""
from __future__ import annotations

import io
import json
from pathlib import Path
from xml.sax.saxutils import escape

import fitz
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
HR_SJT = REPO_ROOT / "apps/studies/assets/irb/hr-sjt"
MATERIALS = HR_SJT / "materials"
PDF_DIR = MATERIALS / "pdf"
PROTOCOL_JSON = HR_SJT / "protocol.json"
OUTPUT = PDF_DIR / "HSIRB_Application_HR_SJT_Rating_Effectiveness_full_packet.pdf"

REVIEW_TYPE = "exempt"
EXEMPTION_CATEGORY = (
    "Exempt Category 2 (45 CFR 46.104(d)(2)) / Nicholls Category D "
    "(educational tests and survey procedures; anonymized identifiers)"
)

APPENDICES = [
    ("A", "Professional Informed Consent"),
    ("B", "Class / Student Informed Consent"),
    ("C", "HR SJT Instrument (All 27 Situations)"),
    ("D", "Recruitment Script (Verbatim)"),
    ("E", "CITI Training Certificate (PI)"),
]

APPENDIX_PDF_FILES = {
    "A": PDF_DIR / "Appendix_A_Professional_Consent.pdf",
    "B": PDF_DIR / "Appendix_B_Student_Consent.pdf",
    "C": PDF_DIR / "Appendix_C_Instrument_27_Situations.pdf",
    "D": PDF_DIR / "Appendix_D_Recruitment_Script.pdf",
    "E": PDF_DIR / "Appendix_E_CITI_Certificate.pdf",
}


class NumberedCanvas(pdf_canvas.Canvas):
    def __init__(self, *args, start_page: int = 1, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages: list[dict] = []
        self.start_page = start_page

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        for page in self.pages:
            self.__dict__.update(page)
            self._draw_footer()
            super().showPage()
        super().save()

    def _draw_footer(self):
        self.saveState()
        self.setStrokeColor(colors.HexColor("#94a3b8"))
        self.setLineWidth(0.5)
        self.line(0.75 * inch, 0.75 * inch, letter[0] - 0.75 * inch, 0.75 * inch)
        page_num = self.start_page + self._pageNumber - 1
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#4b5563"))
        self.drawString(0.75 * inch, 0.55 * inch, "NICHOLLS STATE UNIVERSITY  ·  HSIRB")
        self.drawRightString(letter[0] - 0.75 * inch, 0.55 * inch, f"HSIRB {page_num}")
        self.restoreState()


def _styles() -> dict[str, ParagraphStyle]:
    return {
        "title_univ": ParagraphStyle(
            name="Univ", fontName="Helvetica-Bold", fontSize=15, leading=18,
            textColor=colors.HexColor("#A6192E"), alignment=TA_CENTER, spaceAfter=3,
        ),
        "title_board": ParagraphStyle(
            name="Board", fontName="Helvetica-Bold", fontSize=12, leading=14,
            textColor=colors.HexColor("#1f2937"), alignment=TA_CENTER, spaceAfter=12,
        ),
        "title_form": ParagraphStyle(
            name="Form", fontName="Helvetica-Bold", fontSize=11, leading=13,
            textColor=colors.HexColor("#1f2937"), alignment=TA_CENTER, spaceAfter=18,
        ),
        "section_head": ParagraphStyle(
            name="SecHead", fontName="Helvetica-Bold", fontSize=11, leading=13,
            textColor=colors.HexColor("#A6192E"), alignment=TA_LEFT,
            spaceBefore=12, spaceAfter=8, keepWithNext=True,
        ),
        "field_label": ParagraphStyle(
            name="Label", fontName="Helvetica-Bold", fontSize=9.5, leading=11,
            textColor=colors.HexColor("#1f2937"), alignment=TA_LEFT,
        ),
        "field_value": ParagraphStyle(
            name="Value", fontName="Helvetica", fontSize=9.5, leading=12.5,
            textColor=colors.HexColor("#374151"), alignment=TA_LEFT,
        ),
        "body": ParagraphStyle(
            name="Body", fontName="Helvetica", fontSize=9.5, leading=13.5,
            textColor=colors.HexColor("#374151"), alignment=TA_JUSTIFY, spaceAfter=8,
        ),
        "heading": ParagraphStyle(
            name="Heading", fontName="Helvetica-Bold", fontSize=11, leading=14,
            textColor=colors.HexColor("#1f2937"), alignment=TA_LEFT,
            spaceBefore=10, spaceAfter=6, keepWithNext=True,
        ),
        "preamble": ParagraphStyle(
            name="Preamble", fontName="Helvetica-Oblique", fontSize=9, leading=12,
            textColor=colors.HexColor("#4b5563"), alignment=TA_JUSTIFY, spaceAfter=14,
        ),
    }


def _logo_path() -> Path | None:
    logo = MATERIALS / "nicholls_state_university_logo.png"
    return logo if logo.is_file() else None


def _append_logo(story: list, logo: Path | None) -> None:
    if logo:
        img = Image(str(logo), width=1.8 * inch, height=1.2 * inch)
        img.hAlign = "CENTER"
        story.extend([img, Spacer(1, 4)])


def _load_protocol() -> dict:
    return json.loads(PROTOCOL_JSON.read_text(encoding="utf-8"))


def _project_info(proto: dict) -> dict:
    return {
        "study_title": "HR Situational Judgment Test: Evidence-Based HR Decision-Making",
        "pi_name": proto.get("study_contact_name") or "Dr. Christopher Castille",
        "pi_title": proto.get("pi_title") or "Associate Professor",
        "pi_department": proto.get("pi_department") or "Management and Marketing",
        "pi_email": proto.get("study_contact_email") or "christopher.castille@nicholls.edu",
        "pi_phone": proto.get("pi_phone") or proto.get("study_contact_phone") or "985-449-7015",
        "co_investigators": proto.get("co_investigators") or "None",
        "funding_source": proto.get("funding_source") or "No external funding. Internal research project.",
        "continuation_of_previous": bool(proto.get("continuation_of_previous")),
        "previous_protocol_number": "",
    }


def _build_front_matter(info: dict) -> bytes:
    styles = _styles()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=letter,
        rightMargin=0.75 * inch, leftMargin=0.75 * inch,
        topMargin=0.85 * inch, bottomMargin=0.95 * inch,
    )
    logo = _logo_path()
    story: list = []
    _append_logo(story, logo)
    story.extend([
        Paragraph("NICHOLLS STATE UNIVERSITY", styles["title_univ"]),
        Paragraph("HUMAN SUBJECTS INSTITUTIONAL REVIEW BOARD", styles["title_board"]),
        Paragraph(
            f"REQUEST FOR {REVIEW_TYPE.upper()} REVIEW BY HUMAN SUBJECTS INSTITUTIONAL BOARD",
            styles["title_form"],
        ),
    ])
    story.append(Paragraph(
        "Nicholls State University has established standards and guidelines to ensure adequate protection "
        "is provided to individuals participating in a research activity. The Human Subjects Institutional "
        "Review Board (HSIRB) is charged with the responsibility of screening all research which employs human "
        "participants conducted by faculty, administrators, or students affiliated with Nicholls State University. "
        "The guidelines employed for screening are those set forth by university policy. Please fill in all "
        "requested information and keep a copy of this form and any supporting documentation on file.",
        styles["preamble"],
    ))
    story.append(Paragraph("General Guidelines:", styles["section_head"]))
    story.extend([
        Paragraph(
            "<b>1. Primary Investigator:</b> The primary investigator planning a research activity involving human "
            "subjects should obtain a Request for HSIRB application form and complete all requested fields fully "
            "with authentic, descriptive details. Research originating from other institutions should be approved "
            "by the host institution prior to applying for approval at Nicholls State University.",
            styles["body"],
        ),
        Paragraph(
            "<b>2. Review Workflow:</b> The completed application is submitted through the PRAMS platform. "
            "An initial review of the application will be made by the college HSIRB representative to determine if the "
            "project is considered Category I, EXEMPT, Category II, EXPEDITED REVIEW, or Category III, FULL COMMITTEE REVIEW.",
            styles["body"],
        ),
        Paragraph(
            "<b>3. Timing:</b> Investigators must receive formal approved status from the board BEFORE any recruitment "
            "actions or data collection commence. Retroactive approvals are strictly prohibited.",
            styles["body"],
        ),
    ])
    story.append(PageBreak())

    _append_logo(story, logo)
    story.extend([
        Paragraph("NICHOLLS STATE UNIVERSITY", styles["title_univ"]),
        Paragraph("HUMAN SUBJECTS INSTITUTIONAL REVIEW BOARD", styles["title_board"]),
        Paragraph("PROJECT INFORMATION FORM", styles["title_form"]),
    ])
    continuation = "No"
    info_data = [
        [Paragraph("Title of Investigation:", styles["field_label"]),
         Paragraph(escape(info["study_title"]), styles["field_value"])],
        [Paragraph("Name of Primary Investigator:", styles["field_label"]),
         Paragraph(escape(info["pi_name"]), styles["field_value"])],
        [Paragraph("PI Title / Academic Rank:", styles["field_label"]),
         Paragraph(escape(info["pi_title"]), styles["field_value"])],
        [Paragraph("PI Department / School:", styles["field_label"]),
         Paragraph(escape(info["pi_department"]), styles["field_value"])],
        [Paragraph("PI Email Address:", styles["field_label"]),
         Paragraph(escape(info["pi_email"]), styles["field_value"])],
        [Paragraph("PI Phone Number:", styles["field_label"]),
         Paragraph(escape(info["pi_phone"]), styles["field_value"])],
        [Paragraph("Other Investigators Involved:", styles["field_label"]),
         Paragraph(escape(info["co_investigators"]).replace("\n", "<br/>"), styles["field_value"])],
        [Paragraph("Source of Project Funds:", styles["field_label"]),
         Paragraph(escape(info["funding_source"]), styles["field_value"])],
        [Paragraph("Is this a Continuation of research?", styles["field_label"]),
         Paragraph(continuation, styles["field_value"])],
        [Paragraph("Federal Exemption Category:", styles["field_label"]),
         Paragraph(escape(EXEMPTION_CATEGORY), styles["field_value"])],
    ]
    table = Table(info_data, colWidths=[2.2 * inch, 4.8 * inch])
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
    ]))
    story.append(table)
    doc.build(story, canvasmaker=lambda *a, **k: NumberedCanvas(*a, start_page=1, **k))
    return buf.getvalue()


def _para_blocks(text: str) -> list[str]:
    text = (text or "").strip()
    if not text:
        return []
    # Split on blank lines; keep numbered lines readable
    parts = [p.strip() for p in text.replace("\r\n", "\n").split("\n\n") if p.strip()]
    if len(parts) == 1 and "\n" in parts[0]:
        # bullet-ish single block: keep as one paragraph with <br/>
        return [parts[0]]
    return parts


def _build_narrative(proto: dict, start_page: int) -> bytes:
    styles = _styles()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=letter,
        rightMargin=0.75 * inch, leftMargin=0.75 * inch,
        topMargin=0.85 * inch, bottomMargin=0.95 * inch,
    )
    story: list = []

    sections = [
        ("1. Description of Project or Proposal", proto.get("protocol_description")),
        ("2. Population of Human Subjects", proto.get("population_description")),
        ("3. Research Procedures and Data Collection", proto.get("research_procedures")),
        ("4. Research Objectives", proto.get("research_objectives")),
        ("5. Research Questions", proto.get("research_questions")),
        ("6. Recruitment", proto.get("recruitment_method")),
        ("7. Subject Inclusion Criteria", proto.get("inclusion_criteria")),
        ("8. Subject Exclusion Criteria", proto.get("exclusion_criteria")),
        ("9. Subject Benefits & Costs", None),  # composed below
        ("10. Basis of Exemption / Justification", proto.get("review_type_justification")),
        ("11. Statement of Risk & Mitigation", None),
        ("12. Data Collection, Storage, & Access", None),
        ("13. Consent Procedures", proto.get("consent_procedures")),
        ("14. Active Links for IRB Review", None),
    ]

    benefits = (
        f"<b>Benefits to Subjects:</b><br/>{escape(proto.get('benefits_to_subjects') or '')}<br/><br/>"
        f"<b>Benefits to Others:</b><br/>{escape(proto.get('benefits_to_others') or '')}<br/><br/>"
        f"<b>Benefits to Society:</b><br/>{escape(proto.get('benefits_to_society') or '')}<br/><br/>"
        f"<b>Payment/Compensation:</b><br/>{escape(proto.get('payment_compensation') or '')}<br/><br/>"
        f"<b>Costs to Subjects:</b><br/>{escape(proto.get('costs_to_subjects') or '')}"
    )
    risk = (
        f"<b>Risk Statement:</b><br/>{escape(proto.get('risk_statement') or '').replace(chr(10), '<br/>')}<br/><br/>"
        f"<b>Mitigation:</b><br/>{escape(proto.get('risk_mitigation') or '').replace(chr(10), '<br/>')}"
    )
    data = (
        f"<b>Collection Methods:</b><br/>{escape(proto.get('data_collection_methods') or '').replace(chr(10), '<br/>')}<br/><br/>"
        f"<b>Storage:</b><br/>{escape(proto.get('data_storage') or '').replace(chr(10), '<br/>')}<br/><br/>"
        f"<b>Confidentiality:</b><br/>{escape(proto.get('confidentiality_procedures') or '').replace(chr(10), '<br/>')}<br/><br/>"
        f"<b>Retention / Access:</b><br/>{escape(proto.get('data_retention') or '')}<br/><br/>"
        f"{escape(proto.get('data_access') or '')}"
    )
    links = (
        "<b>Interactive instrument review (skip / optional ratings; no Begin Assessment API required):</b><br/>"
        "https://bayoupal.nicholls.edu/hsirb/studies/hr-sjt/run/<br/><br/>"
        "<b>Professional consent:</b><br/>"
        "https://bayoupal.nicholls.edu/hsirb/studies/hr-sjt/professional-consent/<br/><br/>"
        "<b>Class / student consent:</b><br/>"
        "https://bayoupal.nicholls.edu/hsirb/studies/hr-sjt/student-data-consent/<br/><br/>"
        "<b>Live assessment host:</b><br/>"
        "https://bayoupal.nicholls.edu/hr-sjt-assessment/"
    )

    composed = {
        "9. Subject Benefits & Costs": benefits,
        "11. Statement of Risk & Mitigation": risk,
        "12. Data Collection, Storage, & Access": data,
        "14. Active Links for IRB Review": links,
    }

    for title, raw in sections:
        story.append(Paragraph(title, styles["heading"]))
        if title in composed:
            story.append(Paragraph(composed[title], styles["body"]))
            continue
        for block in _para_blocks(raw or ""):
            esc = escape(block).replace("\n", "<br/>")
            story.append(Paragraph(esc, styles["body"]))

    story.append(Paragraph("15. List of Appendices", styles["heading"]))
    for label, name in APPENDICES:
        story.append(Paragraph(f"<b>Appendix {label}.</b> {escape(name)}", styles["body"]))

    story.append(Spacer(1, 16))
    story.append(Paragraph("16. Statement of Risk (Signature)", styles["heading"]))
    story.append(Paragraph(
        "The undersigned certify that they believe that the conduct of the above described research creates "
        "no risk of physical or emotional harm, or social or legal embarrassment to any participating human subject.",
        styles["body"],
    ))
    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "_________________________________<br/>Signature of Principal Investigator &nbsp;&nbsp;&nbsp;&nbsp; Date",
        styles["body"],
    ))
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        f"PI: {escape(proto.get('study_contact_name') or 'Dr. Christopher Castille')} &nbsp;|&nbsp; "
        f"{escape(proto.get('study_contact_email') or '')} &nbsp;|&nbsp; "
        f"{escape(proto.get('study_contact_phone') or '')}",
        styles["body"],
    ))
    story.append(Paragraph(
        f"Suggested reviewers: {escape(proto.get('suggested_reviewers') or 'Jon Murphy (CBA), Juliann Allen')}",
        styles["body"],
    ))

    doc.build(story, canvasmaker=lambda *a, **k: NumberedCanvas(*a, start_page=start_page, **k))
    return buf.getvalue()


def _build_appendix_title_page(start_page: int, label: str, short_title: str) -> bytes:
    styles = _styles()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=letter,
        rightMargin=0.75 * inch, leftMargin=0.75 * inch,
        topMargin=1.5 * inch, bottomMargin=0.95 * inch,
    )
    story = [
        Paragraph("NICHOLLS STATE UNIVERSITY  ·  HSIRB", styles["title_univ"]),
        Spacer(1, 24),
        Paragraph(f"Appendix {label}", styles["title_board"]),
        Paragraph(escape(short_title), styles["title_form"]),
    ]
    doc.build(story, canvasmaker=lambda *a, **k: NumberedCanvas(*a, start_page=start_page, **k))
    return buf.getvalue()


def _insert_pdf_bytes(target: fitz.Document, at_index: int, pdf_bytes: bytes) -> int:
    src = fitz.open(stream=pdf_bytes, filetype="pdf")
    target.insert_pdf(src, start_at=at_index)
    n = src.page_count
    src.close()
    return n


def _insert_pdf_file(target: fitz.Document, at_index: int, pdf_path: Path) -> int:
    src = fitz.open(pdf_path)
    target.insert_pdf(src, start_at=at_index)
    n = src.page_count
    src.close()
    return n


def build_packet() -> Path:
    proto = _load_protocol()
    info = _project_info(proto)
    PDF_DIR.mkdir(parents=True, exist_ok=True)

    for label, path in APPENDIX_PDF_FILES.items():
        if not path.exists():
            raise FileNotFoundError(f"Missing appendix {label}: {path}")

    front = _build_front_matter(info)
    narrative = _build_narrative(proto, start_page=3)

    doc = fitz.open()
    page_cursor = 0
    page_cursor += _insert_pdf_bytes(doc, page_cursor, front)
    page_cursor += _insert_pdf_bytes(doc, page_cursor, narrative)

    for label, title in APPENDICES:
        title_pdf = _build_appendix_title_page(page_cursor + 1, label, title)
        page_cursor += _insert_pdf_bytes(doc, page_cursor, title_pdf)
        page_cursor += _insert_pdf_file(doc, page_cursor, APPENDIX_PDF_FILES[label])

    doc.save(OUTPUT)
    doc.close()
    return OUTPUT


def main() -> None:
    out = build_packet()
    print(f"Wrote: {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
