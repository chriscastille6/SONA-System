#!/usr/bin/env python3
"""Fill HSIRB Exempt Review Request (rev9 2019) for HR SJT.

Short answers at normal form font size (Times-Roman 10). Detail on Attachment A.
"""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
HR = ROOT / "apps" / "studies" / "assets" / "irb" / "hr-sjt"
BLANK = HR / "HSIRB-exempt_review_request.rev9_2019.v2_BLANK.pdf"
OUT_PDF = HR / "HSIRB_EXEMPT_REVIEW_REQUEST.pdf"
OUT_MD = HR / "HSIRB_EXEMPT_REVIEW_REQUEST.md"
PROTOCOL = HR / "protocol.json"
CITI = ROOT / "docs" / "citiCompletionCertificate_4689946_59381539.pdf"

TITLE = "HR Situational Judgment Test: Evidence-Based HR Decision-Making"
PI_NAME = "Dr. Christopher Castille"
PI_PHONE = "985-449-7015"
FONT = "Times-Roman"
SIZE = 10
LEADING = 12


def wrap(c, text, x, y, max_w, size=SIZE, leading=LEADING, min_y=None):
    c.setFont(FONT, size)
    words = text.split()
    line = ""
    for w in words:
        trial = f"{line} {w}".strip()
        if c.stringWidth(trial, FONT, size) <= max_w:
            line = trial
        else:
            if min_y is not None and y < min_y:
                return y
            c.drawString(x, y, line)
            y -= leading
            line = w
    if line and (min_y is None or y >= min_y):
        c.drawString(x, y, line)
        y -= leading
    return y


def check(c, x, y):
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x, y, "X")


def overlay_page1():
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    mid = 1.5 * inch
    w = 7.0 * inch

    c.setFont(FONT, SIZE)
    c.drawString(268, 697, PI_NAME)
    c.drawString(512, 697, PI_PHONE)
    c.drawString(175, 669, "None")
    c.drawString(290, 640, "N/A (faculty PI)")
    c.drawString(115, 612, "CBA")
    c.drawString(268, 612, "Management and Marketing")
    c.drawString(500, 612, PI_PHONE)
    c.drawString(210, 583, TITLE)

    # Short answers — same size as form text
    wrap(c, "VOLUNTARY. Ages 18+: MNGT 425 & MNGT 502 students (course assignment) and working employees interested in management. See Attachment A.", mid, 488, w, min_y=445)
    wrap(c, "Consent; online SJT (27 scenarios; optional ratings; Skip; optional notes). ~45–60 min. No deception. Instrument link in Attachment A.", mid, 368, w, min_y=330)
    wrap(c, "Exploratory study of tactic-effectiveness ratings across role groups (e.g., students, professionals, executives). See Attachment A.", mid, 298, w, min_y=250)
    wrap(c, "Classroom/LMS announcement for MNGT 425/502 (no flyer). Community outreach to working employees. See Attachment A.", mid, 158, w, min_y=128)
    wrap(c, "Age 18+; MNGT 425/502 (Option A) or working adult interested in management; internet access.", mid, 100, w, min_y=60)
    wrap(c, "Under 18; prior participation; Option B alternative assignment (not research).", mid, 32, w, min_y=14)

    c.save()
    buf.seek(0)
    return buf.read()


def overlay_page2():
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    x = 1.5 * inch
    w = 6.5 * inch

    wrap(c, "Course credit (425/502); optional feedback; contribute to research.", x, 618, w, min_y=595)
    wrap(c, "Aggregate findings may support student–community learning/networking.", x, 575, w, min_y=552)
    wrap(c, "Exploratory evidence on management/HR tactic ratings.", x, 532, w, min_y=510)
    wrap(c, "No pay. Option A or B earn equivalent assignment credit. Community unpaid.", x, 475, w, min_y=452)
    wrap(c, "About 45–60 minutes (SJT).", x, 405, w, min_y=385)
    c.setFont(FONT, SIZE)
    c.drawString(x, 362, "None.")
    wrap(c, "Not required.", x, 318, w, min_y=300)

    c.setFont(FONT, 9)
    c.drawString(0.5 * inch, 78, "Primary basis: Category D (next page).")

    c.save()
    buf.seek(0)
    return buf.read()


def overlay_page3():
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    check(c, 38, 742)   # D
    check(c, 110, 657)  # 1
    check(c, 110, 586)  # 3
    wrap(
        c,
        "CITI attached: Christopher Castille — Faculty Researchers (Basic). Completed 10-May-2024; expires 10-May-2026; Record ID 59381539.",
        0.9 * inch,
        55,
        7.0 * inch,
        size=SIZE,
        leading=LEADING,
        min_y=20,
    )
    c.save()
    buf.seek(0)
    return buf.read()


def overlay_page4():
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.setFont(FONT, SIZE)
    c.drawString(0.95 * inch, 508, PI_NAME)
    c.setFont(FONT, 9)
    c.drawString(3.5 * inch, 508, "(Sign/date upon submission)")
    c.setFont(FONT, SIZE)
    c.drawString(0.95 * inch, 422, "N/A — PI is faculty")
    c.save()
    buf.seek(0)
    return buf.read()


def attachment_a():
    """Brief Attachment A — short, clear; details only as needed."""
    proto = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    y = 10.4 * inch
    c.setFont("Times-Bold", 12)
    c.drawString(0.75 * inch, y, "ATTACHMENT A")
    y -= 16
    c.setFont(FONT, SIZE)
    c.drawString(0.75 * inch, y, f"{TITLE}  |  PI: {PI_NAME}")
    y -= 20

    blocks = [
        ("4a. Population", "VOLUNTARY. Adults 18+ interested in management: (1) MNGT 425 & MNGT 502 students as an in-class assignment (Option A), with Option B qualitative write-up to the instructor for equal credit (grading only; not analyzed); (2) working employees. No flyer."),
        ("4b. Procedures", "Consent → opaque session ID (no PRAMS ID) → optional role → online SJT (27 scenarios; optional 1–5 ratings; Skip; optional notes) → optional feedback. No deception; no formal debriefing. Emails for updates only on a separate lab form (/studies/lab/), not formal data. ~45–60 min. Instrument: https://bayoupal.nicholls.edu/hsirb/studies/hr-sjt/run/"),
        ("4c. Objectives", "Exploratory description of tactic ratings; explore differences across role groups without assuming them; support 425/502 teaching; share aggregate findings for community learning."),
        ("5a. Recruitment", proto.get("recruitment_script", "")[:900]),
        ("5b–c. Inclusion / exclusion", "Include: 18+; 425/502 Option A or working adult interested in management. Exclude: under 18; duplicates; Option B (not research)."),
        ("6. Benefits / payment / costs", "Credit for 425/502 (A or B). No pay. Community unpaid. Time ~45–60 min. Money: none."),
        ("7. Exemption", "Category D: educational tests (1) and survey procedures (3); anonymous session IDs only."),
        ("8. CITI", "Christopher Castille — Faculty Researchers (Basic); 10-May-2024 to 10-May-2026; Record ID 59381539. Attached."),
        ("9. Risk", "Minimal. Optional ratings/Skip/notes; withdraw anytime. No deception."),
    ]
    for title, body in blocks:
        c.setFont("Times-Bold", SIZE)
        c.drawString(0.75 * inch, y, title)
        y -= LEADING
        y = wrap(c, body.replace("\n", " "), 0.75 * inch, y, 7.0 * inch)
        y -= 8
        if y < 1.2 * inch:
            c.showPage()
            y = 10.4 * inch
    c.save()
    buf.seek(0)
    return [buf.read()]


def write_md():
    OUT_MD.write_text(
        f"""# HSIRB Exempt Review Request — HR SJT (rev9)

**PDF:** `HSIRB_EXEMPT_REVIEW_REQUEST.pdf`  
**Rebuild:** `python3 scripts/fill_hr_sjt_hsirb_exempt_form.py`

Form answers use Times-Roman 10 (normal size). Detail is on Attachment A.

| § | Answer |
|---|--------|
| 1 PI | {PI_NAME}, {PI_PHONE} |
| 2 | CBA / Management and Marketing |
| 3 | {TITLE} |
| 4a | VOLUNTARY; 425/502 students + working employees |
| 4b | Online SJT; optional ratings/Skip/notes; ~45–60 min |
| 4c | Exploratory tactic ratings across role groups |
| 5 | Classroom announcement (no flyer); community outreach |
| 6 | Credit; no pay; ~45–60 min |
| 7 | **D** — techniques **1** and **3** |
| 8 | CITI attached |
""",
        encoding="utf-8",
    )


def main():
    blank = PdfReader(str(BLANK))
    writer = PdfWriter()
    for i, raw in enumerate([overlay_page1(), overlay_page2(), overlay_page3(), overlay_page4()]):
        page = blank.pages[i]
        page.merge_page(PdfReader(BytesIO(raw)).pages[0])
        writer.add_page(page)
    for raw in attachment_a():
        writer.add_page(PdfReader(BytesIO(raw)).pages[0])
    if CITI.exists():
        for page in PdfReader(str(CITI)).pages:
            writer.add_page(page)
    with OUT_PDF.open("wb") as f:
        writer.write(f)
    write_md()
    print(f"Wrote {OUT_PDF} ({len(writer.pages)} pages)")


if __name__ == "__main__":
    main()
