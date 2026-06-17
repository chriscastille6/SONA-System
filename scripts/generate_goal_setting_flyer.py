#!/usr/bin/env python3
"""
Nicholls Goal-Setting IRB materials build helpers.

Recruitment flyers (Appendices A and A2):
    python scripts/generate_goal_setting_flyer.py

Generates:
    Recruitment_pilot_20260312.pdf       — pilot sessions; no cash compensation language
    Recruitment_main_study_20260312.pdf  — main study; Waterloo-style cash compensation

Informed consent (Appendix B) — edit Word, not .txt:
    1. Edit apps/studies/assets/irb/goal-setting/materials/consent_form.docx
    2. ./scripts/build_consent_from_docx.sh

Debriefing / appreciation letter (Appendix E):
    1. Edit apps/studies/assets/irb/goal-setting/materials/debriefing_protocol.txt
    2. python scripts/build_goal_setting_debriefing_docx.py   # optional .docx
    3. python scripts/generate_goal_setting_flyer.py --debriefing

Workbook and Productivity Report (Appendices C–D):
    High-fidelity PDFs in materials/pdf/ — copy from Desktop source; do not regenerate from .txt.

Legacy build_pdf_from_text() remains for one-off .txt conversions but is not the consent workflow.
"""

import os
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)

FLYER_VARIANTS = {
    "pilot": {
        "filename": "Recruitment_pilot_20260312.pdf",
        "include_payment": False,
        "include_signup": True,
        "invitation_lead": (
            "You are invited to participate in a pilot session for a multi-site research study"
        ),
    },
    "main": {
        "filename": "Recruitment_main_study_20260312.pdf",
        "include_payment": True,
        "include_signup": True,
        "invitation_lead": "You are invited to participate in a multi-site research study",
    },
}

SIGNUP_URL = "https://bayoupal.nicholls.edu/hsirb/studies/signup/decision-making/"
CONTENT_WIDTH = 7.0 * inch


def _flyer_styles():
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            name="FlyerTitle",
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=23,
            textColor=colors.HexColor("#111827"),
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            name="FlyerBody",
            fontName="Helvetica",
            fontSize=9.5,
            leading=12.5,
            textColor=colors.HexColor("#374151"),
            alignment=TA_JUSTIFY,
            spaceAfter=6,
        ),
        "bullet_head": ParagraphStyle(
            name="FlyerBulletHead",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=13,
            textColor=colors.HexColor("#A6192E"),
            alignment=TA_LEFT,
            spaceAfter=3,
            keepWithNext=True,
        ),
        "bullet_text": ParagraphStyle(
            name="FlyerBulletText",
            fontName="Helvetica",
            fontSize=9.5,
            leading=12,
            textColor=colors.HexColor("#374151"),
            alignment=TA_LEFT,
            spaceAfter=3,
        ),
        "center_small": ParagraphStyle(
            name="FlyerCenterSmall",
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#374151"),
            alignment=TA_CENTER,
            spaceAfter=0,
        ),
    }


def _append_header(story, base_dir):
    """Logo and crimson rule only — no university/college text lines."""
    logo_path = base_dir / "apps/studies/assets/irb/goal-setting/materials/nicholls_state_university_logo.png"
    if logo_path.exists():
        img = Image(str(logo_path), width=1.1 * inch, height=0.72 * inch)
        img.hAlign = "CENTER"
        story.append(img)
        story.append(Spacer(1, 0.04 * inch))

    header_line = Table([[""]], colWidths=[CONTENT_WIDTH])
    header_line.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, -1), 2.5, colors.HexColor("#A6192E")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(header_line)
    story.append(Spacer(1, 0.08 * inch))


def _details_grid(styles, include_payment):
    requirements_text = (
        "• Must be currently enrolled as a student at Nicholls State University.<br/>"
        "• Must be 18 years of age or older.<br/>"
        "• Fluent in English and comfortable working on basic word problems."
    )
    task_text = (
        "You will be asked to complete a decision-making task involving anagram puzzles (word puzzles) "
        "in a classroom or computer lab on the Nicholls State University campus. You will also "
        "complete brief questionnaires about the task, a brief personality scale, and standard demographics. "
        "Participation takes <b>no more than 1 hour</b> of your time."
    )
    confidentiality_text = (
        "<b>Yes, completely.</b> All data collected in this study are anonymous. Your name and "
        "email are never associated with your answers, workbooks, or self-reported scores. "
        "Data are stored securely using de-identified code IDs."
    )

    if include_payment:
        return [
            [
                Paragraph("What will I do?", styles["bullet_head"]),
                Paragraph("What are the requirements?", styles["bullet_head"]),
            ],
            [
                Paragraph(task_text, styles["bullet_text"]),
                Paragraph(requirements_text, styles["bullet_text"]),
            ],
            [
                Paragraph("What will I receive?", styles["bullet_head"]),
                Paragraph("Is participation confidential?", styles["bullet_head"]),
            ],
            [
                Paragraph(
                    "In appreciation of your time, you will receive at least <b>$7.00 cash</b>.",
                    styles["bullet_text"],
                ),
                Paragraph(confidentiality_text, styles["bullet_text"]),
            ],
        ]

    return [
        [
            Paragraph("What will I do?", styles["bullet_head"]),
            Paragraph("What are the requirements?", styles["bullet_head"]),
        ],
        [
            Paragraph(task_text, styles["bullet_text"]),
            Paragraph(requirements_text, styles["bullet_text"]),
        ],
        [
            Paragraph("Is participation confidential?", styles["bullet_head"]),
            Paragraph("", styles["bullet_text"]),
        ],
        [
            Paragraph(confidentiality_text, styles["bullet_text"]),
            Paragraph("", styles["bullet_text"]),
        ],
    ]


def _qr_image_path(base_dir: Path) -> Path:
    qr_path = base_dir / "apps/studies/assets/irb/goal-setting/materials/goal_setting_signup_qr.png"
    import qrcode

    qr = qrcode.QRCode(version=None, error_correction=qrcode.ERROR_CORRECT_M, box_size=10, border=2)
    qr.add_data(SIGNUP_URL)
    qr.make(fit=True)
    qr.make_image(fill_color="black", back_color="white").save(str(qr_path))
    return qr_path


def _append_signup_block(story, styles, qr_path: Path) -> None:
    """Compact sign-up row: copy left, QR right, URL centered below."""
    signup_copy = (
        "<b>Sign up for a session</b><br/><br/>"
        "Scan the QR code to choose an open time slot. <b>No account or login required.</b> "
        "You will receive a booking reference and PIN only — no name or email is collected."
    )
    qr_img = Image(str(qr_path), width=0.82 * inch, height=0.82 * inch)
    qr_row = Table(
        [[Paragraph(signup_copy, styles["bullet_text"]), qr_img]],
        colWidths=[5.35 * inch, 1.15 * inch],
    )
    qr_row.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(qr_row)


def _assert_single_page(pdf_path: Path, variant: str) -> int:
    import fitz

    doc = fitz.open(str(pdf_path))
    page_count = doc.page_count
    doc.close()
    if page_count != 1:
        raise RuntimeError(f"{variant} flyer must be exactly 1 page; got {page_count} ({pdf_path.name})")
    return page_count


def build_nicholls_flyer(variant="main", output_dir=None):
    if variant not in FLYER_VARIANTS:
        raise ValueError(f"Unknown flyer variant: {variant!r}. Choose from {list(FLYER_VARIANTS)}")

    config = FLYER_VARIANTS[variant]
    base_dir = Path(__file__).resolve().parent.parent
    if output_dir is None:
        output_dir = base_dir / "apps" / "studies" / "assets" / "irb" / "goal-setting" / "materials" / "pdf"
    output_dir.mkdir(exist_ok=True, parents=True)
    pdf_path = output_dir / config["filename"]

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.85 * inch,
    )

    styles = _flyer_styles()
    story = []

    _append_header(story, base_dir)
    story.append(Paragraph("A Study in Decision Making", styles["title"]))
    story.append(Spacer(1, 0.03 * inch))

    invitation_text = (
        f"{config['invitation_lead']} aimed at understanding decision-making in work settings. "
        "This study is part of a larger collaborative initiative (ARIM) and has received "
        "formal ethics clearance from the Human Subjects Institutional Review Board (HSIRB) at Nicholls State University "
        "(Protocol: IRB 2024-07-30-001 CBA). Investigators: "
        "<b>Dr. Christopher Castille</b> (Primary Investigator), "
        "<b>Dr. Ann-Marie R. Castille</b>, <b>Dr. Samantha Falgout</b>, "
        "<b>Dr. Kaitlin Gravois</b>, and <b>Dr. Adrien Maught</b> (Co-Investigators), Nicholls State University."
    )
    story.append(Paragraph(invitation_text, styles["body"]))
    story.append(Spacer(1, 0.05 * inch))

    col_width = CONTENT_WIDTH / 2.0
    t_details = Table(_details_grid(styles, config["include_payment"]), colWidths=[col_width, col_width])
    t_details.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (0, -1), 8),
        ("LEFTPADDING", (1, 0), (1, -1), 8),
    ]))
    story.append(t_details)
    story.append(Spacer(1, 0.04 * inch))

    if config.get("include_signup", False):
        _append_signup_block(story, styles, _qr_image_path(base_dir))

    def draw_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(colors.HexColor("#6b7280"))
        text1 = "Nicholls State University  ·  Al Danos College of Business Administration  ·  HSIRB Approved Protocol: IRB 2024-07-30-001 CBA"
        text2 = "For questions about your rights as a participant, contact the Nicholls HSIRB Chair (Dr. Alaina Daigle, 985-448-4697)."
        canvas.drawCentredString(8.5 * inch / 2.0, 0.58 * inch, text1)
        canvas.drawCentredString(8.5 * inch / 2.0, 0.46 * inch, text2)
        canvas.restoreState()

    doc.build(story, onFirstPage=draw_footer, onLaterPages=draw_footer)
    page_count = _assert_single_page(pdf_path, variant)
    print(f"Successfully generated {config['filename']} ({page_count} page) at: {pdf_path}")
    return pdf_path


def build_all_flyers():
    paths = []
    for variant in FLYER_VARIANTS:
        paths.append(build_nicholls_flyer(variant=variant))
    return paths


DEBRIEFING_TXT = "debriefing_protocol.txt"
DEBRIEFING_PDF = "Feedback_version2_20260312.pdf"

PILOT_DEBRIEFING_TXT = "debriefing_protocol_pilot.txt"
PILOT_DEBRIEFING_PDF = "Feedback_pilot_20260312.pdf"

MAIN_DEBRIEFING_TXT = "debriefing_protocol_main.txt"
MAIN_DEBRIEFING_PDF = "Feedback_main_20260312.pdf"


def build_debriefing_pdf():
    """Build Appendix E debriefing/appreciation PDFs (both pilot and main)."""
    build_pdf_from_text(PILOT_DEBRIEFING_TXT, PILOT_DEBRIEFING_PDF)
    build_pdf_from_text(MAIN_DEBRIEFING_TXT, MAIN_DEBRIEFING_PDF)
    build_pdf_from_text(DEBRIEFING_TXT, DEBRIEFING_PDF)


def build_pdf_from_text(txt_filename, pdf_filename):
    base_dir = Path(__file__).resolve().parent.parent
    materials_dir = base_dir / "apps" / "studies" / "assets" / "irb" / "goal-setting" / "materials"
    txt_path = materials_dir / txt_filename
    pdf_path = materials_dir / "pdf" / pdf_filename

    with open(txt_path, "r", encoding="utf-8") as f:
        content = f.read()

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()

    style_title = ParagraphStyle(
        name="DocTitle_" + txt_filename.split(".")[0],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=colors.HexColor("#A6192E"),
        alignment=TA_CENTER,
        spaceAfter=12,
    )

    style_heading = ParagraphStyle(
        name="DocHeading_" + txt_filename.split(".")[0],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#111827"),
        alignment=TA_LEFT,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True,
    )

    style_body = ParagraphStyle(
        name="DocBody_" + txt_filename.split(".")[0],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#374151"),
        alignment=TA_JUSTIFY,
        spaceAfter=8,
    )

    style_center = ParagraphStyle(
        name="DocCenter_" + txt_filename.split(".")[0],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#374151"),
        alignment=TA_CENTER,
        spaceAfter=8,
    )

    style_likert = ParagraphStyle(
        name="DocLikert_" + txt_filename.split(".")[0],
        fontName="Helvetica",
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#374151"),
        alignment=TA_LEFT,
        spaceAfter=4,
    )

    story = []

    logo_path = "/Users/ccastille/.cursor/projects/Users-ccastille-Documents-GitHub-SONA-System/assets/image-3692823e-13cc-4d71-87c9-875833604dab.png"
    if os.path.exists(logo_path):
        img = Image(logo_path, width=1.5 * inch, height=1.0 * inch)
        img.hAlign = "CENTER"
        story.append(img)
        story.append(Spacer(1, 0.15 * inch))

    paragraphs = content.split("\n\n")
    for p in paragraphs:
        p_text = p.strip()
        if not p_text:
            continue

        p_text = p_text.replace("\n", "<br/>")

        is_title = p_text in [
            "INFORMED CONSENT STATEMENT/INFORMATION LETTER",
            "FEEDBACK/APPRECIATION LETTER",
            "DEBRIEFING PROTOCOL / APPRECIATION LETTER",
            "A Study in Decision Making",
        ]
        is_center_line = p_text in [
            "Nicholls State University",
            "Al Danos College of Business Administration",
        ]
        is_heading = p_text in [
            "Information", "Risks", "Benefits",
            "Confidentiality of Your Information", "Confidentiality",
            "Remuneration", "Contact", "Participation",
            "Feedback and Publication", "CONSENT",
            "Thank You for Your Participation",
            "Study Purpose and Disclosure",
            "Study Purpose and Calibration",
            "How Your Responses Were Used",
            "Conditions in This Study",
            "What We Are Investigating",
            "Questions or Concerns",
            "Summary of Findings",
        ]

        is_likert_option = p_text in [
            "Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree",
            "Not at all", "Slightly", "Moderately", "Quite a bit", "Extremely",
        ]

        is_contact_line = (
            ("@nicholls.edu" in p_text or p_text.startswith("Dr. ") or p_text.startswith("Mrs. ") or p_text.startswith("Mr. "))
            and len(p_text) < 100
        )

        if is_title:
            story.append(Paragraph(p_text, style_title))
        elif is_center_line:
            story.append(Paragraph(p_text, style_center))
        elif is_heading:
            story.append(Paragraph(p_text, style_heading))
        elif is_likert_option:
            story.append(Paragraph(p_text, style_likert))
        elif is_contact_line:
            story.append(Paragraph(p_text, style_center))
        elif "Signature of Participant" in p_text or p_text.startswith("____________________"):
            sig_data = [
                [
                    Paragraph("_____________________________", style_body),
                    Paragraph("_____________________________", style_body),
                    Paragraph("_________________", style_body),
                ],
                [
                    Paragraph("Name of Participant", style_body),
                    Paragraph("Signature of Participant", style_body),
                    Paragraph("Date", style_body),
                ],
            ]
            sig_table = Table(sig_data, colWidths=[2.5 * inch, 3.0 * inch, 1.5 * inch])
            sig_table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ]))
            story.append(Spacer(1, 0.2 * inch))
            story.append(sig_table)
        else:
            story.append(Paragraph(p_text, style_body))

    doc.build(story)
    print(f"Successfully generated {pdf_filename} from {txt_filename}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build Nicholls goal-setting IRB material PDFs.")
    parser.add_argument(
        "--debriefing",
        action="store_true",
        help="Build Appendix E debriefing PDF from debriefing_protocol.txt",
    )
    parser.add_argument(
        "--flyers-only",
        action="store_true",
        help="Build recruitment flyers only (default when no flags are passed)",
    )
    args = parser.parse_args()

    if args.debriefing:
        build_debriefing_pdf()
    elif args.flyers_only or not args.debriefing:
        build_all_flyers()
    # Consent: use scripts/build_consent_from_docx.sh (not build_pdf_from_text).
