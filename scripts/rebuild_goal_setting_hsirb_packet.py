#!/usr/bin/env python3
"""
Rebuild the goal-setting HSIRB full packet with pilot/main consent split and narrative patches.

Patches narrative pages for two-phase design (pilot then main), payment main-only,
repeat-participation disclosure, and replaces the single consent block with
Appendix B (pilot) + Appendix B2 (main) consent PDFs.

Usage:
    python scripts/rebuild_goal_setting_hsirb_packet.py
    python scripts/rebuild_goal_setting_hsirb_packet.py --source tmp/HSIRB_Application_goal_setting_full_packet.pdf
"""
from __future__ import annotations

import argparse
import io
import re
import shutil
from pathlib import Path
from xml.sax.saxutils import escape

import fitz
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.pdfgen import canvas as pdf_canvas

REPO_ROOT = Path(__file__).resolve().parent.parent
MATERIALS = REPO_ROOT / "apps/studies/assets/irb/goal-setting/materials"
PDF_DIR = MATERIALS / "pdf"

DEFAULT_SOURCES = [
    REPO_ROOT / "tmp/HSIRB_Application_goal_setting_full_packet.pdf",
    PDF_DIR / "HSIRB_Application_A_Study_in_Decision_Making_full_packet.pdf",
]

OUTPUT_REPO = PDF_DIR / "HSIRB_Application_A_Study_in_Decision_Making_full_packet.pdf"
OUTPUT_TMP = REPO_ROOT / "tmp/HSIRB_Application_goal_setting_full_packet.pdf"

PILOT_CONSENT = PDF_DIR / "ConsentForm_pilot_20260312.pdf"
MAIN_CONSENT = PDF_DIR / "ConsentForm_main_20260312.pdf"

# 0-based page indices in the legacy packet layout.
PAGE_RESEARCH_PROCEDURES = 2
PAGE_RECRUITMENT = 3
PAGE_BENEFITS_PAYMENT = 4
PAGE_RISK_DATA = 5
PAGE_CONSENT_PROCEDURES = 6
PAGE_APPENDIX_LIST = 7

SECTION_HEADING_RE = re.compile(r"^\d+\.\s")
HYPOTHESIS_RE = re.compile(r"^H\d+[a-z]?\.")

APPENDICES = [
    ("A", "Pilot Recruitment Flyer"),
    ("A2", "Main Study Recruitment Flyer"),
    ("B", "Pilot Informed Consent Statement"),
    ("B2", "Main Study Informed Consent Statement"),
    ("C", "Anagram Task Workbook (Study Instrument)"),
    ("D", "Participant Productivity Report (Main Study)"),
    ("E", "Pilot Study Appreciation Letter"),
    ("E2", "Main Study Debriefing & Appreciation Letter"),
    ("F", "Approved UWaterloo Master Protocol"),
    ("G", "Psychological Science Registered Report Manuscript"),
    ("H", "Psychological Science Stage 1 In-Principle Acceptance Letter"),
]

APPENDIX_PDF_FILES = {
    "A": PDF_DIR / "Recruitment_pilot_20260312.pdf",
    "A2": PDF_DIR / "Recruitment_main_study_20260312.pdf",
    "B": PILOT_CONSENT,
    "B2": MAIN_CONSENT,
    "C": PDF_DIR / "Workbook_version2_20260312.pdf",  # HSIRB sample (~17 pp); print master: materials/admin/workbooks_cash_no_computers_v2.docx
    "D": PDF_DIR / "ProductivityReport_version2_20260312.pdf",
    "E": PDF_DIR / "Feedback_pilot_20260312.pdf",
    "E2": PDF_DIR / "Feedback_main_20260312.pdf",
    "F": PDF_DIR / "UWaterloo protocol March 2026.pdf",
    "G": PDF_DIR / "PsychScience manuscript RR2 - final.pdf",
    "H": PDF_DIR / "PsychScience_ScholarOne_acceptance_letter.pdf",
}

REPEAT_PARTICIPATION = (
    "Students who participated in the pilot may also participate in the main study. Because all data "
    "are anonymous, the research team cannot monitor repeat participation without compromising anonymity."
)

REVIEW_TYPE = "exempt"
EXEMPTION_CATEGORY = "Exempt Category 2 (45 CFR 46.104(d)(2))"

PROJECT_INFO = {
    "study_title": "A Study in Decision Making",
    "pi_name": "Dr. Christopher Castille",
    "pi_title": "Associate Professor of Management",
    "pi_department": "Management and Marketing",
    "pi_email": "christopher.castille@nicholls.edu",
    "pi_phone": "985-449-7015",
    "co_investigators": (
        "Dr. Ann-Marie R. Castille (Associate Professor of Management), "
        "ann-marie.castille@nicholls.edu, 985-448-4738\n"
        "Dr. Samantha Falgout (Assistant Professor of Accounting), "
        "samantha.falgout@nicholls.edu, 985-448-4193\n"
        "Dr. Adrien Maught (Assistant Professor of Marketing), "
        "adrien.maught@nicholls.edu, 985-448-4194"
    ),
    "funding_source": "Nicholls State University Research Council",
    "continuation_of_previous": False,
    "previous_protocol_number": "",
}

PAGE3_TEXT = """1. Description of Project or Proposal
This study is a local replication of the foundational Schweitzer, Ordóñez, and Douma (2004) experiment examining whether performance goals drive unethical behavior. Participants complete anagram puzzles under one of four conditions: do-your-best, mere goal, reward goal, or personal goal. This design directly addresses several methodological limitations of the original 2004 study, tests key boundary conditions—specifically trait loss aversion and goal proximity—and contributes to a multi-site global replication project. Data collection occurs in two phases: a pilot session to calibrate materials and administration procedures, followed by a main study session for hypothesis testing. Both pilot and main materials are supplied for HSIRB review.

2. Population of Human Subjects
Undergraduate students enrolled in Business Administration courses (specifically BSAD 101, meeting in Powell 140) at Nicholls State University, as well as working professionals. All participants must be 18 years of age or older.

3. Research Procedures and Data Collection
Pilot session: (1) Consent using Appendix B pilot form; (2) two 1-minute practice rounds; (3) timed anagram performance rounds under do-your-best instructions; (4) anonymous productivity report (no cash self-payment; participants may use a phone to access an online Scrabble dictionary via a QR code on the report); (5) brief questionnaires; (6) pilot appreciation letter.

Main study: (1) Consent using Appendix B2 main study form; (2) two 1-minute practice rounds; (3) random assignment to do-your-best, mere goal, personal goal, or reward goal; (4) seven 1-minute performance rounds; (5) eighth-round unique anagram for anonymous linking (participants are told this round does not count toward payment); (6) demographics and trait measures while the researcher is present; (7) while the researcher is out of the room, participants privately check their work using a phone to access an online Scrabble dictionary via a QR code on the productivity report, complete an anonymous productivity report for rounds 1–7, perform private self-payment from a $14 cash envelope per the report instructions, seal the productivity report and cash envelope in a large envelope, and deposit materials in designated boxes (workbook folder and sealed large envelope separately); (8) main study debriefing sheet.

""" + REPEAT_PARTICIPATION

PAGE4_TEXT = """4. Research Objectives
Our primary objective is to conduct a constructive replication of the foundational Schweitzer et al. (2004) study, correcting its methodological limitations while maintaining its core strengths. Second, we aim to investigate when and for whom performance goals lead to unethical behavior. By testing how trait loss aversion and goal proximity influence overstatement, we provide a direct empirical test of the loss aversion mechanism theorized by Ordóñez and Wu (2013). These findings will help strengthen the empirical basis of the goal-setting literature and offer new theoretical insights for behavioral ethics.

5. Research Questions or Hypotheses
H1. People with specific challenging goals (i.e., personal, mere, or reward goals) are more likely to overstate their performance than people without specific challenging goals (i.e., do-your-best condition).
H2. Challenging goal type is related to overstating performance. People with reward goals are more likely to overstate their performance than those with mere goals, who in turn are more likely to overstate their performance than those with personal goals.
H3a. People who fail to reach their goal by a smaller margin are more likely to overstate their performance than if they were to fail to reach their goal by a larger margin.
H3b. People who reach their goal are less likely to overstate their performance than if they failed to reach the goal.
H4. People with greater trait loss aversion are more likely to overstate their performance.
H5. The relationship between trait loss aversion and overstating behavior is amplified in trials where people failed their goal by a smaller margin than when they failed by a larger margin.

6. Educational Justification
This project is part of a global multi-site initiative designed to train student researchers and junior faculty in rigorous, open-science replication methodologies. By engaging with a conditionally accepted Registered Report, local co-investigators and research assistants gain firsthand experience in pre-registration, double-blind administration, and collaborative behavioral science research.

7. Recruitment Method & Script
Recruitment occurs via classroom visits using approved informational flyers. Two flyer versions are included (Appendix A for pilot sessions, Appendix A2 for main study); only the version matching the session is shown. Both pilot and main recruitment materials are supplied for HSIRB review. Instructors may offer course credit or bonus points. The main-study flyer mentions a small cash reward of at least $7.00 with opportunity for up to $14.00; the pilot flyer does not mention cash compensation.

Pilot script: You are invited to participate in a pilot session for a research study examining decision-making during cognitive tasks. This session takes approximately one hour, has received IRB ethics clearance, and helps refine procedures before main data collection. There is no cash compensation. Participation is voluntary and anonymous.

Main study script: You are invited to participate in a research study examining decision-making during cognitive tasks. This study takes approximately one hour and has received IRB ethics clearance. Depending on your instructor's policy, you may receive course credit, bonus points, or a small cash reward of at least $7.00 with opportunity for up to $14.00 total. Participation is voluntary and anonymous."""

PAGE5_TEXT = """8. Subject Inclusion & Exclusion Criteria
Inclusion:
- Undergraduate students or working professionals
- 18 years of age or older
Exclusion:
- Individuals under 18 years of age

9. Subject Benefits & Costs
Benefits to Subjects:
Pilot session participants receive no cash compensation. They may receive course credit or bonus points at their instructor's discretion and receive a written appreciation letter explaining how pilot data support calibration for the main study.

Main study participants receive direct financial compensation through the self-payment procedure, keeping at least $7.00 and up to $14.00 depending on their assigned instructions and performance (averaging about $10.00). They also receive a detailed debriefing sheet explaining the logic and value of open-science replication research.

Benefits to Others/Society:
Strengthening the empirical foundation of the dark-side of goal setting literature, generating a shared understanding between goal setting and behavioral ethics scholars, and developing novel theoretical insights to guide organizational practices.

Payment/Compensation:
Pilot session: No cash compensation is provided.

Main study only: All main-study participants receive an envelope containing $14.00 at the start of the session. Payment amounts are stated on each participant's productivity report during the private self-payment step. Those in the 'do your best', 'mere goal', and 'personal goal' conditions are instructed to keep $10.00. Those in the 'reward goal' condition are instructed to keep $7.00 plus an additional $1.00 for each scored round (rounds 1–7) in which they met the site-calibrated goal (on average, approximately $10.00). Unearned cash is returned in the cash envelope, which is sealed with the productivity report in a large envelope while the researcher is out of the room. Participant-facing materials describe a small cash reward of at least $7.00 with opportunity for up to $14.00 total.

Costs:
Participation requires approximately one hour of time. There are no financial costs to the subjects.

10. Basis of Exemption / Justification
The study qualifies for exempt review under Category 2 of the revised Common Rule (45 CFR 46.104(d)(2)). Data are collected via behavioral tests (an anagram task) and survey procedures. No participant names, IDs, or other identifying information are recorded on any data collection sheets, ensuring participants cannot be identified, directly or through linked identifiers. While we correlate task performance with self-reported productivity reports using a unique eighth-round anagram, this linking mechanism is entirely anonymous and never associated with any student identity."""

PAGE6_TEXT = """11. Statement of Risk & Mitigation
Risk Statement:
The study presents minimal risk. The anagram task may cause mild frustration or performance anxiety, but no more than everyday schoolwork or standard puzzles. While participants have an opportunity to over-report performance or keep unearned money, all data are completely anonymous and cannot be linked to individual identities.

Mitigation:
To protect participants, the design is double-blind, and no names or student IDs are ever written on the study workbooks or productivity reports. Signed consent forms are collected and stored separately. The researcher leaves the room during grading, self-payment, and report submission. A unique eighth-round anagram is used for anonymous data linking. Finally, participants receive a detailed debriefing, and contact information for the Nicholls Counseling Center is provided.

12. Data Collection, Storage, & Access
Collection Methods:
Data collection uses paper-and-pencil materials, including a task workbook (practice and performance anagram rounds, goal commitment, trait loss aversion, and demographics), a separate productivity report for self-reported performance, and a follow-up survey for manipulation and data quality checks. Hard copies are collected in a secure box.

Storage:
Hard-copy workbooks and productivity reports are stored in a locked office in the Department of Management and Marketing at Nicholls State University. De-identified, anonymized electronic datasets are maintained on secure, password-protected computers and shared publicly on the Open Science Framework (OSF) to facilitate open-science collaboration.

Confidentiality Procedures:
Participants remain completely anonymous. No names, email addresses, or student IDs are written on the workbooks, productivity reports, or survey forms. Signed consent forms are stored in a separate locked cabinet from the raw data sheets. Anonymized data are linked via a unique eighth-round anagram rather than any personal identifier, and the de-identified spreadsheet is shared publicly on the OSF.

Access:
The principal investigator and local co-investigators have access to the raw paper materials. De-identified, anonymous data are shared with our research collaborators across the multi-site initiative and made publicly available on the Open Science Framework (OSF).

Retention:
Paper materials will be retained in a locked office for five to seven years in accordance with APA guidelines, after which they will be shredded. The anonymized electronic dataset will be preserved indefinitely on the OSF for replication and meta-analysis."""

PAGE7_TEXT = """13. Consent Procedures
Two written informed consent forms are included for HSIRB review: Appendix B (pilot session) and Appendix B2 (main study). Only the form matching the session is shown to participants. Each form details the study's purpose, procedures, risks, and benefits, emphasizing that participation is entirely voluntary and that participants may withdraw at any time without penalty. The main-study form describes cash compensation; the pilot form states that no cash compensation is provided. Students who choose not to participate are offered an equivalent alternative assignment for equal course credit.

""" + REPEAT_PARTICIPATION + """

14. CITI Training Certification
All investigators have completed CITI Program training. Dr. Christopher Castille (Faculty Researchers), Dr. Ann-Marie R. Castille (Faculty Researchers), Dr. Samantha Falgout (Faculty Researchers), Dr. Adrien Maught (Social/Behavioral RCR). Certificates are pending / to be submitted upon request.

Statement of Compliance & Ethical Assurances:
By signing below, the Primary Investigator certifies that the described project will be conducted in accordance with university guidelines, the Belmont Report, and 45 CFR 46. Any protocol modifications or adverse events must be reported immediately to the board.

____________________________________________________
Primary Investigator Signature
_________________
Date
____________________________________________________
College HSIRB Representative Signature
_________________
Date
____________________________________________________
HSIRB Chairperson Signature (Approval)
_________________
Date"""


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


def _legacy_front_matter_styles() -> dict[str, ParagraphStyle]:
    return {
        "title_univ": ParagraphStyle(
            name="LegacyUniv",
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=18,
            textColor=colors.HexColor("#A6192E"),
            alignment=TA_CENTER,
            spaceAfter=3,
        ),
        "title_board": ParagraphStyle(
            name="LegacyBoard",
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=14,
            textColor=colors.HexColor("#1f2937"),
            alignment=TA_CENTER,
            spaceAfter=12,
        ),
        "title_form": ParagraphStyle(
            name="LegacyForm",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=13,
            textColor=colors.HexColor("#1f2937"),
            alignment=TA_CENTER,
            spaceAfter=18,
        ),
        "section_head": ParagraphStyle(
            name="LegacySecHead",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=13,
            textColor=colors.HexColor("#A6192E"),
            alignment=TA_LEFT,
            spaceBefore=12,
            spaceAfter=8,
            keepWithNext=True,
        ),
        "field_label": ParagraphStyle(
            name="LegacyLabel",
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=11,
            textColor=colors.HexColor("#1f2937"),
            alignment=TA_LEFT,
        ),
        "field_value": ParagraphStyle(
            name="LegacyValue",
            fontName="Helvetica",
            fontSize=9.5,
            leading=12.5,
            textColor=colors.HexColor("#374151"),
            alignment=TA_LEFT,
        ),
        "body_text": ParagraphStyle(
            name="LegacyBody",
            fontName="Helvetica",
            fontSize=9.5,
            leading=13.5,
            textColor=colors.HexColor("#374151"),
            alignment=TA_JUSTIFY,
            spaceAfter=10,
        ),
        "preamble_style": ParagraphStyle(
            name="LegacyPreamble",
            fontName="Helvetica-Oblique",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#4b5563"),
            alignment=TA_JUSTIFY,
            spaceAfter=14,
        ),
    }


def _append_logo(story: list, logo: Path | None) -> None:
    if logo:
        img = Image(str(logo), width=1.8 * inch, height=1.2 * inch)
        img.hAlign = "CENTER"
        story.extend([img, Spacer(1, 4)])


def _build_front_matter_pages() -> bytes:
    """Cover (page 1) and project information form (page 2), mirroring irb_legacy_pdf.py."""
    styles = _legacy_front_matter_styles()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.85 * inch,
        bottomMargin=0.95 * inch,
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
    preamble_text = (
        "Nicholls State University has established standards and guidelines to ensure adequate protection "
        "is provided to individuals participating in a research activity. The Human Subjects Institutional "
        "Review Board (HSIRB) is charged with the responsibility of screening all research which employs human "
        "participants conducted by faculty, administrators, or students affiliated with Nicholls State University. "
        "The guidelines employed for screening are those set forth by university policy. Please fill in all "
        "requested information and keep a copy of this form and any supporting documentation on file."
    )
    story.append(Paragraph(preamble_text, styles["preamble_style"]))
    story.append(Paragraph("General Guidelines:", styles["section_head"]))
    story.extend([
        Paragraph(
            "<b>1. Primary Investigator:</b> The primary investigator planning a research activity involving human "
            "subjects should obtain a Request for HSIRB application form and complete all requested fields fully "
            "with authentic, descriptive details. Research originating from other institutions should be approved "
            "by the host institution prior to applying for approval at Nicholls State University.",
            styles["body_text"],
        ),
        Paragraph(
            "<b>2. Review Workflow:</b> The completed application is submitted through the PRAMS platform. "
            "An initial review of the application will be made by the college HSIRB representative to determine if the "
            "project is considered Category I, EXEMPT, Category II, EXPEDITED REVIEW, or Category III, FULL COMMITTEE REVIEW.",
            styles["body_text"],
        ),
        Paragraph(
            "<b>3. Timing:</b> Investigators must receive formal approved status from the board BEFORE any recruitment "
            "actions or data collection commence. Retroactive approvals are strictly prohibited.",
            styles["body_text"],
        ),
    ])
    story.append(PageBreak())

    _append_logo(story, logo)
    story.extend([
        Paragraph("NICHOLLS STATE UNIVERSITY", styles["title_univ"]),
        Paragraph("HUMAN SUBJECTS INSTITUTIONAL REVIEW BOARD", styles["title_board"]),
        Paragraph("PROJECT INFORMATION FORM", styles["title_form"]),
    ])

    continuation = (
        f"Yes (Protocol #: {PROJECT_INFO['previous_protocol_number']})"
        if PROJECT_INFO["continuation_of_previous"] and PROJECT_INFO["previous_protocol_number"]
        else "No"
    )
    exemption_value = (
        EXEMPTION_CATEGORY
        if REVIEW_TYPE == "exempt"
        else "N/A"
    )
    info_data = [
        [Paragraph("Title of Investigation:", styles["field_label"]),
         Paragraph(PROJECT_INFO["study_title"], styles["field_value"])],
        [Paragraph("Name of Primary Investigator:", styles["field_label"]),
         Paragraph(PROJECT_INFO["pi_name"], styles["field_value"])],
        [Paragraph("PI Title / Academic Rank:", styles["field_label"]),
         Paragraph(PROJECT_INFO["pi_title"], styles["field_value"])],
        [Paragraph("PI Department / School:", styles["field_label"]),
         Paragraph(PROJECT_INFO["pi_department"], styles["field_value"])],
        [Paragraph("PI Email Address:", styles["field_label"]),
         Paragraph(PROJECT_INFO["pi_email"], styles["field_value"])],
        [Paragraph("PI Phone Number:", styles["field_label"]),
         Paragraph(PROJECT_INFO["pi_phone"], styles["field_value"])],
        [Paragraph("Other Investigators Involved:", styles["field_label"]),
         Paragraph(PROJECT_INFO["co_investigators"].replace("\n", "<br/>"), styles["field_value"])],
        [Paragraph("Source of Project Funds:", styles["field_label"]),
         Paragraph(PROJECT_INFO["funding_source"], styles["field_value"])],
        [Paragraph("Is this a Continuation of research?", styles["field_label"]),
         Paragraph(continuation, styles["field_value"])],
        [Paragraph("Federal Exemption Category:", styles["field_label"]),
         Paragraph(exemption_value, styles["field_value"])],
    ]
    table = Table(info_data, colWidths=[2.2 * inch, 4.8 * inch])
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
    ]))
    story.append(table)

    doc.build(
        story,
        canvasmaker=lambda *args, **kwargs: NumberedCanvas(*args, start_page=1, **kwargs),
    )
    return buf.getvalue()


def _logo_path() -> Path | None:
    logo = MATERIALS / "nicholls_state_university_logo.png"
    return logo if logo.is_file() else None


def _build_appendix_list_page(start_page: int) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.85 * inch,
        bottomMargin=0.95 * inch,
    )
    title_univ = ParagraphStyle(
        name="ListUniv",
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#A6192E"),
        alignment=TA_CENTER,
        spaceAfter=3,
    )
    title_board = ParagraphStyle(
        name="ListBoard",
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=14,
        textColor=colors.HexColor("#1f2937"),
        alignment=TA_CENTER,
        spaceAfter=12,
    )
    title_form = ParagraphStyle(
        name="ListForm",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=13,
        textColor=colors.HexColor("#1f2937"),
        alignment=TA_CENTER,
        spaceAfter=18,
    )
    list_label_style = ParagraphStyle(
        name="ListLabel",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        textColor=colors.HexColor("#A6192E"),
        alignment=TA_LEFT,
    )
    list_title_style = ParagraphStyle(
        name="ListTitle",
        fontName="Helvetica",
        fontSize=10,
        leading=12,
        textColor=colors.HexColor("#374151"),
        alignment=TA_LEFT,
    )
    story = []
    logo = _logo_path()
    if logo:
        img = Image(str(logo), width=1.8 * inch, height=1.2 * inch)
        img.hAlign = "CENTER"
        story.extend([img, Spacer(1, 4)])
    story.extend([
        Paragraph("NICHOLLS STATE UNIVERSITY", title_univ),
        Paragraph("HUMAN SUBJECTS INSTITUTIONAL REVIEW BOARD", title_board),
        Paragraph("LIST OF APPENDICES", title_form),
    ])
    rows = [
        [Paragraph(f"Appendix {label}", list_label_style), Paragraph(title, list_title_style)]
        for label, title in APPENDICES
    ]
    table = Table(rows, colWidths=[1.35 * inch, 5.65 * inch])
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
    ]))
    story.append(table)
    doc.build(
        story,
        canvasmaker=lambda *args, **kwargs: NumberedCanvas(*args, start_page=start_page, **kwargs),
    )
    return buf.getvalue()


def _build_appendix_title_page(start_page: int, label: str, short_title: str) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.85 * inch,
        bottomMargin=0.95 * inch,
    )
    label_style = ParagraphStyle(
        name="TitleAppendixLabel",
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#A6192E"),
        alignment=TA_CENTER,
        spaceAfter=10,
    )
    title_style = ParagraphStyle(
        name="TitleAppendixTitle",
        fontName="Helvetica",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#1f2937"),
        alignment=TA_CENTER,
        spaceAfter=6,
    )
    story = [
        Spacer(1, 2.75 * inch),
        Paragraph(f"Appendix {label}", label_style),
        Paragraph(short_title, title_style),
    ]
    doc.build(
        story,
        canvasmaker=lambda *args, **kwargs: NumberedCanvas(*args, start_page=start_page, **kwargs),
    )
    return buf.getvalue()


def _escape_html(text: str) -> str:
    return escape(text).replace("\n", "<br/>")


def _narrative_styles() -> tuple[ParagraphStyle, ParagraphStyle, ParagraphStyle, ParagraphStyle]:
    section_head = ParagraphStyle(
        name="NarrSecHead",
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#1f2937"),
        alignment=TA_LEFT,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True,
    )
    sub_head = ParagraphStyle(
        name="NarrSubHead",
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#1f2937"),
        alignment=TA_LEFT,
        spaceBefore=6,
        spaceAfter=4,
        keepWithNext=True,
    )
    body = ParagraphStyle(
        name="NarrBody",
        fontName="Helvetica",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#374151"),
        alignment=TA_LEFT,
        spaceAfter=6,
    )
    bullet = ParagraphStyle(
        name="NarrBullet",
        parent=body,
        leftIndent=18,
        bulletIndent=6,
        spaceAfter=3,
    )
    return section_head, sub_head, body, bullet


def _is_subheading(line: str) -> bool:
    return (
        line.endswith(":")
        and len(line) < 80
        and not line.startswith("-")
        and not line.startswith("_")
        and not SECTION_HEADING_RE.match(line)
    )


def _text_to_story(text: str) -> list:
    section_head, sub_head, body, bullet = _narrative_styles()
    story: list = []
    body_lines: list[str] = []

    def flush_body() -> None:
        if not body_lines:
            return
        joined = "\n".join(body_lines).strip()
        body_lines.clear()
        if joined:
            story.append(Paragraph(_escape_html(joined), body))

    for raw_line in text.strip().split("\n"):
        line = raw_line.strip()
        if not line:
            flush_body()
            continue
        if SECTION_HEADING_RE.match(line):
            flush_body()
            story.append(Paragraph(_escape_html(line), section_head))
        elif _is_subheading(line):
            flush_body()
            story.append(Paragraph(_escape_html(line), sub_head))
        elif line.startswith("- "):
            flush_body()
            story.append(Paragraph(_escape_html(line[2:]), bullet, bulletText="•"))
        elif HYPOTHESIS_RE.match(line):
            flush_body()
            match = re.match(r"^(H\d+[a-z]?\.)\s*(.*)$", line)
            if match:
                story.append(
                    Paragraph(f"<b>{escape(match.group(1))}</b> {escape(match.group(2))}", body)
                )
            else:
                story.append(Paragraph(_escape_html(line), body))
        else:
            body_lines.append(line)

    flush_body()
    return story


def _build_narrative_section(text_blocks: list[str], start_page: int) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.95 * inch,
    )
    story: list = []
    for index, block in enumerate(text_blocks):
        if index > 0:
            story.append(PageBreak())
        story.extend(_text_to_story(block))
    doc.build(
        story,
        canvasmaker=lambda *args, **kwargs: NumberedCanvas(*args, start_page=start_page, **kwargs),
    )
    return buf.getvalue()


def _replace_narrative_pages(
    target_doc: fitz.Document,
    first_page_index: int,
    last_page_index: int,
    text_blocks: list[str],
    *,
    start_page: int,
) -> None:
    replacement_pdf = _build_narrative_section(text_blocks, start_page)
    page_count = last_page_index - first_page_index + 1
    for _ in range(page_count):
        target_doc.delete_page(first_page_index)
    _insert_pdf_bytes(target_doc, first_page_index, replacement_pdf)


def _replace_page_with_pdf(target_doc: fitz.Document, page_index: int, replacement_pdf: bytes) -> None:
    replacement = fitz.open(stream=replacement_pdf, filetype="pdf")
    target_doc.delete_page(page_index)
    target_doc.insert_pdf(replacement, start_at=page_index)
    replacement.close()


def _insert_pdf_bytes(target_doc: fitz.Document, at_index: int, pdf_bytes: bytes) -> int:
    src = fitz.open(stream=pdf_bytes, filetype="pdf")
    target_doc.insert_pdf(src, start_at=at_index)
    count = len(src)
    src.close()
    return count


def _insert_pdf_file(target_doc: fitz.Document, at_index: int, pdf_path: Path) -> int:
    src = fitz.open(pdf_path)
    target_doc.insert_pdf(src, start_at=at_index)
    count = len(src)
    src.close()
    return count


def resolve_source(explicit: Path | None) -> Path:
    if explicit:
        path = explicit.expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"Source packet not found: {path}")
        return path
    for candidate in DEFAULT_SOURCES:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        "No source HSIRB packet found. Provide --source or place packet at "
        f"{DEFAULT_SOURCES[0]}"
    )


def _insert_appendix_materials(target_doc: fitz.Document, start_page: int) -> None:
    insert_at = len(target_doc)
    next_page = start_page
    for label, short_title in APPENDICES:
        pdf_path = APPENDIX_PDF_FILES.get(label)
        if pdf_path is None or not pdf_path.is_file():
            raise FileNotFoundError(f"Appendix PDF missing for {label}: {pdf_path}")

        pages_added = _insert_pdf_bytes(
            target_doc,
            insert_at,
            _build_appendix_title_page(next_page, label, short_title),
        )
        next_page += pages_added
        insert_at += pages_added

        pages_added = _insert_pdf_file(target_doc, insert_at, pdf_path)
        next_page += pages_added
        insert_at += pages_added


def rebuild_packet(source: Path, output: Path) -> None:
    missing = [
        str(path)
        for path in APPENDIX_PDF_FILES.values()
        if not path.is_file()
    ]
    if missing:
        raise FileNotFoundError("Missing appendix PDF(s):\n" + "\n".join(missing))

    src = fitz.open(source)
    if src.page_count <= PAGE_APPENDIX_LIST:
        raise ValueError(
            f"Source packet has only {src.page_count} pages; expected > {PAGE_APPENDIX_LIST}"
        )

    out = fitz.open()
    _insert_pdf_bytes(out, 0, _build_front_matter_pages())
    out.insert_pdf(src, from_page=PAGE_RESEARCH_PROCEDURES, to_page=PAGE_APPENDIX_LIST - 1)

    narrative_pages = [
        (PAGE_RESEARCH_PROCEDURES, PAGE3_TEXT),
        (PAGE_RECRUITMENT, PAGE4_TEXT),
        (PAGE_BENEFITS_PAYMENT, PAGE5_TEXT),
        (PAGE_RISK_DATA, PAGE6_TEXT),
        (PAGE_CONSENT_PROCEDURES, PAGE7_TEXT),
    ]
    _replace_narrative_pages(
        out,
        PAGE_RESEARCH_PROCEDURES,
        PAGE_CONSENT_PROCEDURES,
        [text for _, text in narrative_pages],
        start_page=PAGE_RESEARCH_PROCEDURES + 1,
    )

    list_page_num = len(out) + 1
    _insert_pdf_bytes(out, len(out), _build_appendix_list_page(list_page_num))
    _insert_appendix_materials(out, list_page_num + 1)

    output.parent.mkdir(parents=True, exist_ok=True)
    out.save(output)
    out.close()
    src.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Rebuild goal-setting HSIRB packet with pilot/main consents")
    parser.add_argument("--source", type=Path, help="Source HSIRB packet PDF")
    parser.add_argument("--output", type=Path, default=OUTPUT_REPO, help="Primary output path")
    parser.add_argument("--no-tmp-copy", action="store_true", help="Skip updating tmp/ copy")
    args = parser.parse_args()

    source = resolve_source(args.source)
    rebuild_packet(source, args.output)
    print(f"Source: {source}")
    print(f"Wrote: {args.output}")

    if not args.no_tmp_copy:
        OUTPUT_TMP.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(args.output, OUTPUT_TMP)
        print(f"Updated: {OUTPUT_TMP}")


if __name__ == "__main__":
    main()
