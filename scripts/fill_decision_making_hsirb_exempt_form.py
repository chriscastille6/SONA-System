#!/usr/bin/env python3
"""Fill HSIRB Exempt Review Request (rev9 2019) for A Study in Decision Making.

Short answers at Times-Roman 10. Original polished appendices (A–H) appended as-is
from the branded packet (from the List of Appendices page onward).
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
# 0-based index of "LIST OF APPENDICES" in the polished packet
APPENDIX_START_PAGE = 9  # page 10 in the packet

TITLE = "A Study in Decision Making"
PI_NAME = "Dr. Christopher Castille"
PI_PHONE = "985-449-7015"
FONT = "Times-Roman"
SIZE = 12
LEADING = 14


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
    c.setFont(FONT, 9)
    c.drawString(175, 669, "A-M. Castille; S. Falgout; K. Gravois; A. Maught (see Att. A)")
    c.setFont(FONT, SIZE)
    c.drawString(290, 640, "N/A (faculty PI)")
    c.drawString(115, 612, "CBA")
    c.drawString(268, 612, "Management and Marketing")
    c.drawString(500, 612, PI_PHONE)
    c.drawString(210, 583, TITLE)

    wrap(c, "VOLUNTARY. Ages 18+: Business students (esp. BSAD 101) and working professionals. See Attachment A.", mid, 488, w, min_y=445)
    wrap(c, "Pilot then main: anagram task under do-your-best / mere / personal / reward goals; anonymous productivity report; main study private self-payment. ~1 hour. Instruments: Appendices C–D.", mid, 368, w, min_y=330)
    wrap(c, "Replication of Schweitzer et al. (2004): do performance goals increase overstatement? Also tests loss aversion and goal proximity. Hypotheses in Attachment A.", mid, 298, w, min_y=250)
    wrap(c, "Classroom visits with approved flyers (Appendices A / A2). Credit/bonus and (main) cash $7–$14. Scripts in Attachment A.", mid, 158, w, min_y=128)
    wrap(c, "Undergraduate students or working professionals; age 18+.", mid, 100, w, min_y=60)
    wrap(c, "Under 18.", mid, 32, w, min_y=14)

    c.save()
    buf.seek(0)
    return buf.read()


def overlay_page2():
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    x = 1.5 * inch
    w = 6.5 * inch

    wrap(c, "Pilot: credit/bonus possible (no cash). Main: cash self-payment ($7–$14) + debrief.", x, 618, w, min_y=595)
    wrap(c, "Evidence on when goals may increase unethical reporting.", x, 575, w, min_y=552)
    wrap(c, "Stronger goal-setting / behavioral-ethics evidence base.", x, 532, w, min_y=510)
    wrap(c, "Pilot: no cash. Main: $14 envelope; keep $10 or $7+$1/round (reward). Credit per instructor.", x, 475, w, min_y=452)
    wrap(c, "About one hour per session.", x, 405, w, min_y=385)
    c.setFont(FONT, SIZE)
    c.drawString(x, 362, "None.")
    wrap(c, "Pilot then separate main session (optional for pilot participants).", x, 318, w, min_y=295)

    c.setFont(FONT, 9)
    c.drawString(0.5 * inch, 78, "Primary basis: Category D (next page).")

    c.save()
    buf.seek(0)
    return buf.read()


def overlay_page3():
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    check(c, 38, 742)
    check(c, 110, 657)
    check(c, 110, 586)
    wrap(
        c,
        "CITI attached: Christopher Castille — Faculty Researchers (Basic). Completed 10-May-2024; expires 10-May-2026; Record ID 59381539. Co-I CITI on file.",
        0.9 * inch,
        55,
        7.0 * inch,
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
    """Short Attachment A — references original Appendices A–H (attached as-is)."""
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    y = 10.4 * inch
    c.setFont("Times-Bold", 12)
    c.drawString(0.75 * inch, y, "ATTACHMENT A")
    y -= 16
    c.setFont(FONT, SIZE)
    c.drawString(0.75 * inch, y, f"{TITLE}  |  PI: {PI_NAME}, {PI_PHONE}")
    y -= 14
    c.drawString(0.75 * inch, y, "Co-Is: Ann-Marie Castille; Samantha Falgout; Kaitlin Gravois; Adrien Maught")
    y -= 20

    blocks = [
        ("4a. Population", "VOLUNTARY. Adults 18+: Nicholls business students (esp. BSAD 101, Powell 140) and working professionals. Multi-site replication (Nicholls local site)."),
        ("4b. Procedures", "Pilot (calibration) then main study. Consent → practice → random assignment to do-your-best / mere / personal / reward goal → timed anagram rounds → anonymous productivity report; main study adds private self-payment from a $14 envelope while researcher is out of the room → questionnaires → debrief. ~1 hour. Instruments: Appendices C (workbook) and D (productivity report)."),
        ("4c. Objectives / hypotheses", "Constructive replication of Schweitzer, Ordóñez & Douma (2004). H1: specific goals increase overstatement vs do-your-best. H2: reward > mere > personal. H3a/b: near-miss / goal attainment effects. H4–H5: trait loss aversion and proximity."),
        ("5a. Recruitment", "Classroom flyers: Appendix A (pilot), Appendix A2 (main). Verbatim scripts and materials are in those appendices (attached as-is)."),
        ("5b–c", "Include: students or working professionals, 18+. Exclude: under 18."),
        ("6. Benefits / payment", "Pilot: credit/bonus possible; no cash. Main: self-payment $7–$14 (typical ~$10) + debrief. Time ~1 hour. Money cost: none."),
        ("7. Exemption", "Category D — educational tests (1) and survey procedures (3); anonymous recording (no names on data sheets; eighth-round anagram links workbook to report)."),
        ("8. CITI", "PI certificate attached. Co-investigator CITI on file."),
        ("9. Risk", "Minimal. Anonymous design; researcher leaves during self-payment; debrief provided."),
        (
            "Appendices (original polished packet — attached as-is below)",
            "A Pilot flyer; A2 Main flyer; B Pilot consent; B2 Main consent; C Workbook; D Productivity report; E Pilot appreciation; E2 Main debrief; F UWaterloo protocol; G RR manuscript; H Stage 1 IPA letter.",
        ),
    ]
    for title, body in blocks:
        c.setFont("Times-Bold", SIZE)
        c.drawString(0.75 * inch, y, title)
        y -= LEADING
        y = wrap(c, body, 0.75 * inch, y, 7.0 * inch)
        y -= 8
        if y < 1.2 * inch:
            c.showPage()
            y = 10.4 * inch
    c.save()
    buf.seek(0)
    return buf.read()


def write_md():
    OUT_MD.write_text(
        f"""# HSIRB Exempt Review Request — Decision Making (rev9)

**PDF:** `HSIRB_EXEMPT_REVIEW_REQUEST.pdf`  
**Rebuild:** `python3 scripts/fill_decision_making_hsirb_exempt_form.py`

Form answers: Times-Roman 10. Original Appendices A–H from the polished packet are appended **as-is** (not redesigned).

| § | Answer |
|---|--------|
| 1–3 | {PI_NAME}; CBA / M&M; {TITLE} |
| 4a | VOLUNTARY; BSAD 101 students + working professionals |
| 4b | Pilot/main anagram SJT; self-payment in main |
| 4c | Schweitzer et al. (2004) replication |
| 5 | Classroom flyers (App. A / A2) |
| 7 | **D** — techniques **1** and **3** |
| Appendices | A–H from polished packet (unchanged) |
""",
        encoding="utf-8",
    )


def main():
    if not BLANK.exists():
        raise SystemExit(f"Missing blank: {BLANK}")
    if not FULL_PACKET.exists():
        raise SystemExit(f"Missing polished packet: {FULL_PACKET}")

    blank = PdfReader(str(BLANK))
    writer = PdfWriter()
    for i, raw in enumerate([overlay_page1(), overlay_page2(), overlay_page3(), overlay_page4()]):
        page = blank.pages[i]
        page.merge_page(PdfReader(BytesIO(raw)).pages[0])
        writer.add_page(page)

    writer.add_page(PdfReader(BytesIO(attachment_a())).pages[0])

    # Original appendices as-is (List of Appendices → end)
    polished = PdfReader(str(FULL_PACKET))
    for i in range(APPENDIX_START_PAGE, len(polished.pages)):
        writer.add_page(polished.pages[i])

    if CITI.exists():
        for page in PdfReader(str(CITI)).pages:
            writer.add_page(page)

    with OUT_PDF.open("wb") as f:
        writer.write(f)
    write_md()
    print(f"Wrote {OUT_PDF} ({len(writer.pages)} pages; appendices from polished p.{APPENDIX_START_PAGE + 1}+)")


if __name__ == "__main__":
    main()
