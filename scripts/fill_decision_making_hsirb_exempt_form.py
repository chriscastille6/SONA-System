#!/usr/bin/env python3
"""Map *A Study in Decision Making* (goal-setting) onto HSIRB Exempt Review Request (rev9 2019).

Official blank (4 pages, no AcroForm fields):
  apps/studies/assets/irb/goal-setting/HSIRB-exempt_review_request.rev9_2019.v2_BLANK.pdf

Source: branded packet narrative + populate_goal_setting_protocol_details.py

Outputs:
  apps/studies/assets/irb/goal-setting/HSIRB_EXEMPT_REVIEW_REQUEST.pdf
  apps/studies/assets/irb/goal-setting/HSIRB_EXEMPT_REVIEW_REQUEST.md
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
GS = ROOT / "apps" / "studies" / "assets" / "irb" / "goal-setting"
BLANK = GS / "HSIRB-exempt_review_request.rev9_2019.v2_BLANK.pdf"
OUT_PDF = GS / "HSIRB_EXEMPT_REVIEW_REQUEST.pdf"
OUT_MD = GS / "HSIRB_EXEMPT_REVIEW_REQUEST.md"
CITI = ROOT / "docs" / "citiCompletionCertificate_4689946_59381539.pdf"
FULL_PACKET = (
    GS / "materials" / "pdf" / "HSIRB_Application_A_Study_in_Decision_Making_full_packet.pdf"
)

TITLE = "A Study in Decision Making"
PI_NAME = "Dr. Christopher Castille"
PI_PHONE = "985-449-7015"
PI_EMAIL = "christopher.castille@nicholls.edu"
COLLEGE = "CBA (Al Danos)"
DEPT = "Management and Marketing"
COLLEGE_PHONE = "985-449-7015"

OTHER_INVESTIGATORS_SHORT = (
    "A-M. Castille; S. Falgout; K. Gravois; A. Maught (full list Att. A)"
)

POPULATION = (
    "VOLUNTARY participation. Adults 18+: (1) Undergraduates in Business Administration "
    "courses at Nicholls (esp. BSAD 101, Powell 140); (2) working professionals. Multi-site "
    "replication context (Nicholls local site). Under-18 excluded (required for HSIRB exemption). "
    "See Attachment A."
)

PROCEDURES = (
    "Pilot then main (paper-and-pencil anagram task). Consent → practice rounds → random "
    "assignment to do-your-best / mere / personal / reward goal → timed performance rounds → "
    "anonymous productivity report; main study adds private self-payment from cash envelope "
    "while researcher is out of room → questionnaires → debrief. ~1 hour. Instruments in "
    "full HSIRB packet. See Attachment A for full procedure."
)

OBJECTIVES = (
    "Constructive replication of Schweitzer, Ordóñez & Douma (2004): whether specific "
    "performance goals increase overstatement of performance (unethical reporting). Also tests "
    "boundary conditions (trait loss aversion; goal proximity) and contributes to a multi-site "
    "open-science Registered Report. Hypotheses H1–H5 in Attachment A."
)

RECRUITMENT = (
    "Classroom visits with approved informational flyers (pilot flyer + main-study flyer in "
    "full packet Appendices A/A2). Instructors may offer course credit/bonus; main flyer notes "
    "cash of at least $7 with opportunity up to $14. Verbatim scripts in Attachment A. "
    "Participation voluntary and anonymous."
)

INCLUSION = (
    "Undergraduate students or working professionals; age 18 or older. See Attachment A."
)

EXCLUSION = "Under 18 years of age. See Attachment A."

BENEFIT_SUBJECTS = (
    "Pilot: possible course credit/bonus + appreciation letter (no cash). Main: cash via "
    "self-payment (≥$7, up to $14, ~$10 typical) + debriefing on open-science replication."
)
BENEFIT_OTHERS = (
    "Managers/employees and scholars: evidence on when goal setting may increase unethical "
    "reporting; shared goal-setting / behavioral-ethics understanding."
)
BENEFIT_SOCIETY = (
    "Stronger empirical basis for the “dark side” of goal setting; insights to preserve "
    "performance benefits while mitigating unethical behavior."
)
PAYMENT = (
    "Pilot: no cash. Main: $14 envelope at start; do-your-best/mere/personal keep $10; "
    "reward goal keep $7 + $1 per scored round meeting calibrated goal (avg ~$10). Unearned "
    "cash returned privately. Course credit/bonus per instructor policy."
)
COST_TIME = "Approximately one hour per session (pilot and/or main)."
COST_MONEY = "None (participants receive compensation in main study)."
REPEATED = (
    "Pilot calibrates materials; separate main session for hypothesis tests. Pilot "
    "participants may also do the main study (all data anonymous)."
)


def wrap(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    max_w: float,
    size: float = 8,
    leading: float = 9.5,
    min_y: float | None = None,
) -> float:
    c.setFont("Helvetica", size)
    words = text.split()
    line = ""
    for w in words:
        trial = f"{line} {w}".strip()
        if c.stringWidth(trial, "Helvetica", size) <= max_w:
            line = trial
        else:
            if min_y is not None and y < min_y:
                return y
            c.drawString(x, y, line)
            y -= leading
            line = w
    if line:
        if min_y is not None and y < min_y:
            return y
        c.drawString(x, y, line)
        y -= leading
    return y


def check(c: canvas.Canvas, x: float, y: float) -> None:
    c.setFont("Helvetica-Bold", 12)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(x, y, "X")


def overlay_page1() -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    mid = 1.5 * inch
    max_w = 7.2 * inch

    c.setFont("Helvetica", 9)
    c.drawString(268, 697, PI_NAME)
    c.drawString(512, 697, PI_PHONE)

    c.setFont("Helvetica", 7)
    c.drawString(175, 669, OTHER_INVESTIGATORS_SHORT)

    c.setFont("Helvetica", 8)
    c.drawString(290, 640, "N/A (faculty PI)")

    c.setFont("Helvetica", 8)
    c.drawString(115, 612, COLLEGE)
    c.drawString(268, 612, DEPT)
    c.drawString(500, 612, COLLEGE_PHONE)

    c.setFont("Helvetica", 9)
    c.drawString(210, 583, TITLE)

    wrap(c, POPULATION, mid, 488, max_w - 0.5 * inch, size=7, leading=8.5, min_y=438)
    wrap(c, PROCEDURES, mid, 368, max_w - 0.5 * inch, size=7, leading=8.5, min_y=322)
    wrap(c, OBJECTIVES, mid, 298, max_w - 0.5 * inch, size=7, leading=8.5, min_y=238)
    wrap(c, RECRUITMENT, mid, 158, max_w - 0.5 * inch, size=7, leading=8.5, min_y=122)
    wrap(c, INCLUSION, mid, 100, max_w - 0.5 * inch, size=7, leading=8.5, min_y=55)
    wrap(c, EXCLUSION, mid, 32, max_w - 0.5 * inch, size=6.5, leading=7.5, min_y=12)

    c.save()
    buf.seek(0)
    return buf.read()


def overlay_page2() -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    body_x = 1.5 * inch
    max_w = 6.5 * inch

    wrap(c, BENEFIT_SUBJECTS, body_x, 618, max_w, size=7.5, leading=9, min_y=590)
    wrap(c, BENEFIT_OTHERS, body_x, 575, max_w, size=7.5, leading=9, min_y=548)
    wrap(c, BENEFIT_SOCIETY, body_x, 532, max_w, size=7.5, leading=9, min_y=505)
    wrap(c, PAYMENT, body_x, 475, max_w, size=7.5, leading=9, min_y=448)
    wrap(c, COST_TIME, body_x, 405, max_w, size=7.5, leading=9, min_y=378)
    c.setFont("Helvetica", 8)
    c.drawString(body_x, 362, COST_MONEY)
    wrap(c, REPEATED, body_x, 318, max_w, size=7.5, leading=9, min_y=295)

    c.setFont("Helvetica", 7)
    c.setFillColorRGB(0.25, 0.25, 0.25)
    c.drawString(
        0.5 * inch,
        78,
        "Primary exemption basis: Category D (see next page). A/B/C not claimed as primary basis.",
    )

    c.save()
    buf.seek(0)
    return buf.read()


def overlay_page3() -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)

    check(c, 38, 742)  # D
    check(c, 110, 657)  # 1 educational tests
    check(c, 110, 586)  # 3 survey

    wrap(
        c,
        "CITI attached (PI): Christopher Castille — Human Subjects Research / Faculty Researchers "
        "and Research Sponsors (Basic). Completion 10-May-2024; Expiration 10-May-2026; Record ID "
        "59381539. Co-investigators maintain current CITI per HSIRB policy (certificates on file / "
        "available upon request).",
        0.9 * inch,
        55,
        7.0 * inch,
        size=7.5,
        leading=9,
        min_y=20,
    )

    c.save()
    buf.seek(0)
    return buf.read()


def overlay_page4() -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)

    c.setFont("Helvetica", 9)
    c.drawString(0.95 * inch, 508, PI_NAME)
    c.setFont("Helvetica", 7)
    c.setFillColorRGB(0.25, 0.25, 0.25)
    c.drawString(3.6 * inch, 508, "(Sign/date upon submission)")

    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 9)
    c.drawString(0.95 * inch, 422, "N/A — Principal Investigator is faculty")

    c.save()
    buf.seek(0)
    return buf.read()


def attachment_a_pages() -> list[bytes]:
    """Full narrative so reviewers can understand the study from this form packet alone."""
    sections = [
        (
            "ATTACHMENT A — HSIRB Exempt Review Request (rev9 2019)\n"
            f"Project: {TITLE}\n"
            f"PI: {PI_NAME} | {PI_PHONE} | {PI_EMAIL}\n"
            "College: Al Danos College of Business Administration | Dept: Management and Marketing\n"
            "Funding: Nicholls State University Research Council; multi-site ARIM replication context\n"
            "Companion branded packet: materials/pdf/HSIRB_Application_A_Study_in_Decision_Making_full_packet.pdf",
            None,
        ),
        (
            "1. Investigators",
            "Principal Investigator: Dr. Christopher Castille, Associate Professor of Management, "
            "Management and Marketing; christopher.castille@nicholls.edu; 985-449-7015. "
            "Other investigators: Dr. Ann-Marie R. Castille (Associate Professor of Management; "
            "ann-marie.castille@nicholls.edu; 985-448-4738); Dr. Samantha Falgout (Assistant "
            "Professor of Accounting; samantha.falgout@nicholls.edu; 985-448-4193); Dr. Kaitlin "
            "Gravois (Assistant Professor of Marketing; kaitlin.gravois@nicholls.edu; 985-448-4187); "
            "Dr. Adrien Maught (Assistant Professor of Marketing; adrien.maught@nicholls.edu; "
            "985-448-4194). Faculty sponsor: N/A (faculty PI).",
        ),
        (
            "4a. Population of human subjects (VOLUNTARY)",
            "Participation is VOLUNTARY. Subjects are adults 18 years of age or older: (1) "
            "undergraduate students enrolled in Business Administration courses at Nicholls State "
            "University (specifically including BSAD 101 meeting in Powell 140); and (2) working "
            "professionals. This Nicholls protocol is the local site of a multi-site constructive "
            "replication / Registered Report effort. Individuals under 18 are excluded (required "
            "for HSIRB exemption).",
        ),
        (
            "4b. Research procedures and techniques of data collection",
            "Design overview: Local constructive replication of Schweitzer, Ordóñez, and Douma "
            "(2004) examining whether performance goals increase unethical overstatement of "
            "performance on an anagram (word-creation) task. Four between-subjects conditions: "
            "(i) do-your-best; (ii) mere goal (site-calibrated challenging goal, typically ~90th "
            "percentile from pilot); (iii) personal goal (same numeric goal without “prior "
            "students” framing); (iv) reward goal (same goal plus cash contingent on meeting the "
            "goal each scored round). Participants have an opportunity to over-report performance "
            "on an anonymous productivity report; in the main study they also privately "
            "self-pay from a cash envelope.\n\n"
            "Pilot session (calibration): (1) Consent (pilot form); (2) two 1-minute practice "
            "rounds; (3) timed anagram rounds under do-your-best instructions; (4) anonymous "
            "productivity report (no cash self-payment; participants may use a phone to access an "
            "online Scrabble dictionary via QR on the report); (5) brief questionnaires; "
            "(6) pilot appreciation letter. No cash compensation in pilot.\n\n"
            "Main study: (1) Consent (main form); (2) two 1-minute practice rounds; (3) random "
            "assignment to one of the four conditions (double-blind materials); (4) seven 1-minute "
            "performance rounds; (5) eighth-round unique anagram for anonymous linking of workbook "
            "to productivity report (participants told this round does not count toward payment); "
            "(6) demographics and trait measures (e.g., trait loss aversion) while researcher is "
            "present; (7) while researcher is out of the room, participants privately check work "
            "(phone/QR dictionary), complete anonymous productivity report for rounds 1–7, "
            "perform private self-payment from a $14 cash envelope per report instructions, seal "
            "productivity report and cash envelope in a large envelope, and deposit materials in "
            "designated boxes; (8) main-study debriefing sheet. Approximate duration: one hour.\n\n"
            "Data collection instruments (paper): task workbook, productivity report, follow-up "
            "survey / manipulation checks. Active materials and flyers/consents are in the full "
            "branded HSIRB application packet "
            "(HSIRB_Application_A_Study_in_Decision_Making_full_packet.pdf), including Appendices "
            "for pilot/main flyers, consents, workbook sample, productivity report, debrief, "
            "UWaterloo master protocol, and Registered Report manuscript.",
        ),
        (
            "4c. Objectives / hypotheses",
            "Primary objective: constructive replication of Schweitzer et al. (2004), correcting "
            "methodological limitations while retaining core strengths. Secondary: test when and "
            "for whom performance goals lead to unethical overstatement, focusing on trait loss "
            "aversion and goal proximity (Ordóñez & Wu, 2013). The project also trains local "
            "co-investigators/assistants in open-science replication methods.\n\n"
            "H1. People with specific challenging goals (personal, mere, or reward) are more likely "
            "to overstate performance than people without specific challenging goals (do-your-best).\n"
            "H2. Challenging goal type relates to overstating: reward > mere > personal (ordered "
            "prediction as in the Registered Report).\n"
            "H3a. People who fail to reach their goal by a smaller margin are more likely to "
            "overstate than those who fail by a larger margin.\n"
            "H3b. People who reach their goal are less likely to overstate than those who failed.\n"
            "H4. Greater trait loss aversion is associated with more overstatement.\n"
            "H5. The loss-aversion–overstatement relationship is amplified when failure margin is "
            "small (near miss) versus large.",
        ),
        (
            "5a. Recruitment (verbatim materials; flyers attached in full packet)",
            "Method: Classroom visits using approved informational flyers. Two flyer versions: "
            "pilot (Appendix A) and main study (Appendix A2); only the version matching the "
            "session is shown. Instructors may offer course credit or bonus points. Main-study "
            "materials describe a small cash reward of at least $7.00 with opportunity for up to "
            "$14.00. Participation is voluntary and anonymous.\n\n"
            "Pilot script (verbatim): You are invited to participate in a research study examining "
            "decision-making during cognitive tasks. This study takes approximately one hour and "
            "has received IRB ethics clearance. There is no cash compensation. Participation is "
            "voluntary and anonymous. (Course credit/bonus may apply per instructor policy.)\n\n"
            "Main study script (verbatim): You are invited to participate in a research study "
            "examining decision-making during cognitive tasks. This study takes approximately one "
            "hour and has received IRB ethics clearance. Depending on your instructor's policy, "
            "you may receive course credit, bonus points, or a small cash reward of at least $7.00 "
            "with opportunity for up to $14.00 total. Participation is voluntary and anonymous.",
        ),
        (
            "5b. Inclusion criteria",
            "Undergraduate students or working professionals; 18 years of age or older.",
        ),
        (
            "5c. Exclusion criteria",
            "Individuals under 18 years of age.",
        ),
        (
            "6a–c. Benefits, payment, and costs",
            f"Benefits to subjects: {BENEFIT_SUBJECTS} Benefits to others: {BENEFIT_OTHERS} "
            f"Society: {BENEFIT_SOCIETY} Payment: {PAYMENT} Time: {COST_TIME} Money cost: "
            f"{COST_MONEY} Repeated testing: {REPEATED}",
        ),
        (
            "7. Basis of exemption — Category D (techniques 1 and 3)",
            "Exempt Category D / Common Rule Category 2 (45 CFR 46.104(d)(2)): research limited "
            "to educational tests (cognitive anagram task) and survey procedures, with data "
            "recorded so subjects cannot be identified directly or through identifiers linked to "
            "subjects. No names, student IDs, or emails appear on workbooks or productivity "
            "reports. Signed consents are stored separately from anonymous data sheets. Workbook "
            "and productivity report are linked only via a unique eighth-round anagram (anonymous "
            "linking). Mild cover story (“decision making”) is disclosed in debriefing. Minimal "
            "risk. Techniques checked: (1) educational tests; (3) survey procedures.",
        ),
        (
            "8. CITI training",
            "PI Christopher Castille — Human Subjects Research / Faculty Researchers and Research "
            "Sponsors (Basic). Completion 10-May-2024; Expiration 10-May-2026; Record ID 59381539. "
            "Certificate appended. Co-investigators complete/maintain appropriate CITI learner "
            "groups per Nicholls HSIRB policy.",
        ),
        (
            "9. Statement of risk (supporting narrative)",
            "Minimal risk. The anagram task may cause mild frustration or performance anxiety, "
            "comparable to ordinary schoolwork or puzzles. Participants have an opportunity to "
            "over-report performance or (main study) keep unearned money, but all performance data "
            "are anonymous and cannot be linked to individual identities. Mitigation: double-blind "
            "condition assignment; no names/IDs on data sheets; researcher leaves room during "
            "grading/self-payment; anonymous eighth-round linking; detailed debrief; Nicholls "
            "Counseling Center contact provided as appropriate.",
        ),
        (
            "Data handling (supporting)",
            "Hard-copy workbooks and productivity reports stored in a locked Management & Marketing "
            "office. De-identified electronic datasets on password-protected systems and shared on "
            "OSF for open science. Paper retained ~5–7 years per APA norms, then shredded. Access: "
            "PI and local co-investigators for raw materials; anonymized data shared with multi-site "
            "collaborators and publicly on OSF.",
        ),
        (
            "Attachments checklist",
            "Submit with this form: filled rev9 pages 1–4; this Attachment A; PI CITI certificate; "
            "and (recommended) the full branded HSIRB packet with pilot/main flyers, consents, "
            "workbook/productivity report samples, debrief, UWaterloo protocol, and RR manuscript.",
        ),
    ]

    pages: list[bytes] = []
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    y = 10.4 * inch
    page_no = 1

    def new_page() -> None:
        nonlocal buf, c, y, page_no
        c.setFont("Helvetica", 8)
        c.drawString(0.75 * inch, 0.5 * inch, f"Attachment A — page {page_no}")
        c.save()
        pages.append(buf.getvalue())
        page_no += 1
        buf = BytesIO()
        c = canvas.Canvas(buf, pagesize=letter)
        y = 10.4 * inch

    for title, body in sections:
        if y < 1.8 * inch:
            new_page()
        if body is None:
            for i, line in enumerate(title.split("\n")):
                if y < 1.0 * inch:
                    new_page()
                c.setFont("Helvetica-Bold" if i == 0 else "Helvetica", 9 if i == 0 else 8)
                c.drawString(0.75 * inch, y, line[:105])
                y -= 11
            y -= 6
            continue
        c.setFont("Helvetica-Bold", 9)
        c.drawString(0.75 * inch, y, title)
        y -= 12
        # Allow multi-paragraph bodies
        for para in body.split("\n"):
            if not para.strip():
                y -= 4
                continue
            if y < 1.0 * inch:
                new_page()
                c.setFont("Helvetica-Bold", 9)
                c.drawString(0.75 * inch, y, f"{title} (continued)")
                y -= 12
            y = wrap(c, para.strip(), 0.75 * inch, y, 7.0 * inch, size=8, leading=10)
        y -= 8

    c.setFont("Helvetica", 8)
    c.drawString(0.75 * inch, 0.5 * inch, f"Attachment A — page {page_no}")
    c.save()
    pages.append(buf.getvalue())
    return pages


def write_field_map_md() -> None:
    md = f"""# NICHOLLS STATE UNIVERSITY — Request for HSIRB Exemption

**Filled draft for:** {TITLE}  
**Form:** HSIRB-exempt_review_request.rev9_2019.v2 (official blank overlay)  
**Blank source:** `HSIRB-exempt_review_request.rev9_2019.v2_BLANK.pdf`  
**Filled PDF:** `HSIRB_EXEMPT_REVIEW_REQUEST.pdf`  
**Status:** Draft for PI signature / college rep recommendation  
**Companion branded packet:** `materials/pdf/HSIRB_Application_A_Study_in_Decision_Making_full_packet.pdf`

The official form has **no fillable AcroForm fields**. Answers are overlaid on pages 1–4; **Attachment A** carries the full narrative keyed to form section numbers so reviewers can understand the study from this packet.

---

## 1. Investigators

| Field | Response |
|-------|----------|
| **Name(s) of Principal Investigator(s)** | {PI_NAME} |
| **Phone** | {PI_PHONE} |
| **Other Investigators** | Dr. Ann-Marie R. Castille; Dr. Samantha Falgout; Dr. Kaitlin Gravois; Dr. Adrien Maught (details in Attachment A) |
| **Faculty Sponsor** | N/A (faculty PI) |

## 2. Unit

| Field | Response |
|-------|----------|
| **College** | Al Danos College of Business Administration |
| **Department** | Management and Marketing |
| **Phone** | {COLLEGE_PHONE} |

## 3. Title of Project or Proposal

{TITLE}

## 4. Description

### 4a. Population
{POPULATION}

### 4b. Procedures
{PROCEDURES}

### 4c. Objectives
{OBJECTIVES}

## 5. Recruitment

### 5a.
{RECRUITMENT}

### 5b. Inclusion
{INCLUSION}

### 5c. Exclusion
{EXCLUSION}

## 6. Benefits and costs

1. **Subjects:** {BENEFIT_SUBJECTS}
2. **Others:** {BENEFIT_OTHERS}
3. **Society:** {BENEFIT_SOCIETY}

**Payment:** {PAYMENT}  
**Time:** {COST_TIME}  
**Money:** {COST_MONEY}  
**Repeated testing:** {REPEATED}

## 7. Basis of exemption

**☑ D** — educational tests + survey procedures; anonymous recording  
**☑ D-1** educational tests (anagram cognitive task)  
**☑ D-3** survey procedures (questionnaires / productivity report)  
**☐ A, ☐ B, ☐ C, ☐ E** — not primary claimed basis

## 8. CITI

PI Christopher Castille — Faculty Researchers / Research Sponsors (Basic); completion 10-May-2024; expiration 10-May-2026; Record ID 59381539. Certificate appended.

## 9–11. Signatures

PI name typed for draft; wet signature/date upon submission. Faculty sponsor N/A. HSIRB protocol number blank for assignment.

---

**Rebuild:** `python3 scripts/fill_decision_making_hsirb_exempt_form.py`
"""
    OUT_MD.write_text(md, encoding="utf-8")


def main() -> None:
    if not BLANK.exists():
        raise SystemExit(f"Missing official blank: {BLANK}")

    blank = PdfReader(str(BLANK))
    if len(blank.pages) != 4:
        raise SystemExit(f"Expected 4-page blank, found {len(blank.pages)}")

    overlays = [overlay_page1(), overlay_page2(), overlay_page3(), overlay_page4()]
    writer = PdfWriter()

    for i, raw in enumerate(overlays):
        page = blank.pages[i]
        page.merge_page(PdfReader(BytesIO(raw)).pages[0])
        writer.add_page(page)

    for raw in attachment_a_pages():
        writer.add_page(PdfReader(BytesIO(raw)).pages[0])

    if CITI.exists():
        for page in PdfReader(str(CITI)).pages:
            writer.add_page(page)

    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PDF.open("wb") as f:
        writer.write(f)

    write_field_map_md()
    print(f"Wrote {OUT_PDF} ({OUT_PDF.stat().st_size} bytes)")
    print(f"Wrote {OUT_MD}")
    print(f"Pages: {len(writer.pages)}")
    if FULL_PACKET.exists():
        print(f"Companion packet present: {FULL_PACKET.name}")


if __name__ == "__main__":
    main()
