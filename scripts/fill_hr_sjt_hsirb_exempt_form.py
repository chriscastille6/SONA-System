#!/usr/bin/env python3
"""Map HR SJT protocol content onto HSIRB Exempt Review Request (rev9 2019).

Official blank (4 pages, no AcroForm fields):
  apps/studies/assets/irb/hr-sjt/HSIRB-exempt_review_request.rev9_2019.v2_BLANK.pdf

Source content: protocol.json + study_config.json (aligned with HSIRB_EXEMPT_REVIEW_REQUEST.md)

Outputs:
  apps/studies/assets/irb/hr-sjt/HSIRB_EXEMPT_REVIEW_REQUEST.pdf
  apps/studies/assets/irb/hr-sjt/HSIRB_EXEMPT_REVIEW_REQUEST.md
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
STUDY = HR / "study_config.json"
CITI = ROOT / "docs" / "citiCompletionCertificate_4689946_59381539.pdf"

# Canonical answers (form section order)
TITLE = "HR Situational Judgment Test: Evidence-Based HR Decision-Making"
PI_NAME = "Dr. Christopher Castille"
PI_PHONE = "985-449-7015"
COLLEGE = "CBA (Al Danos)"
DEPT = "Management and Marketing"
COLLEGE_PHONE = "985-449-7015"

POPULATION = (
    "VOLUNTARY; ages 18+. Adults interested in management topics: (1) Business students "
    "(primarily MNGT 425 & MNGT 502) completing this as an in-class assignment (Option A), "
    "with qualitative Option B for equivalent credit (grading only; not analyzed as research); "
    "(2) working employees (professionals/managers/executives welcome). No flyer. See Attachment A."
)

PROCEDURES = (
    "e-consent → opaque session ID (no PRAMS ID) → optional role category → online SJT "
    "(27 scenarios; optional 1–5 ratings; Skip; optional decision notes) → optional feedback "
    "report. No deception; no formal debriefing. Emails for updates only on a separate lab form "
    "(not formal data). ~45–60 min. IRB instrument: "
    "https://bayoupal.nicholls.edu/hsirb/studies/hr-sjt/run/ . See Attachment A."
)

OBJECTIVES = (
    "Exploratory: describe tactic-effectiveness ratings; explore (without assuming) differences "
    "across role groups (students, professionals, executives, etc.); support MNGT 425/502 "
    "teaching; share aggregate findings for community learning/networking. See Attachment A."
)

RECRUITMENT = (
    "No flyer. MNGT 425/502: classroom/LMS assignment Options A (research) / B (qualitative "
    "alt; grading only). Community: outreach to working employees interested in management. "
    "Separate lab page lists HSIRB-approved studies + optional stay-informed email. See Att. A."
)

INCLUSION = (
    "Age 18+; interested in management topics (preferred); MNGT 425/502 students choosing "
    "Option A, or working employees / community adults; internet-capable device. See Attachment A."
)

EXCLUSION = (
    "Under 18; unable to complete online assessment; prior participation; Option B choosers "
    "(alt not research / not analyzed)."
)

BENEFIT_SUBJECTS = (
    "Course assignment credit (425/502); optional feedback report; contribute to exploratory "
    "research; optional aggregate findings via separate email form (not formal data)."
)
BENEFIT_OTHERS = (
    "Students/community may learn from aggregate insights supporting networking around management topics."
)
BENEFIT_SOCIETY = (
    "Exploratory evidence on management/HR tactic ratings; university–community engagement."
)
PAYMENT = (
    "No monetary payment. MNGT 425/502: Option A or B earn equivalent assignment credit; "
    "Option B not analyzed as research. Community volunteers unpaid."
)
COST_TIME = "Approx. 45–60 minutes for SJT; Option B is written alt for instructor only."
COST_MONEY = "None."
REPEATED = "Not required."


def load_protocol() -> dict:
    return json.loads(PROTOCOL.read_text(encoding="utf-8"))


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
    """Bold X over a _____ checkbox."""
    c.setFont("Helvetica-Bold", 12)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(x, y, "X")


def overlay_page1() -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    left = 0.55 * inch
    mid = 1.5 * inch
    max_w = 7.2 * inch

    # 1. PI name + phone (line y≈695; phone blanks near right)
    c.setFont("Helvetica", 9)
    c.drawString(268, 697, PI_NAME)
    c.drawString(512, 697, PI_PHONE)

    # Other investigators
    c.drawString(175, 669, "None")

    # Faculty sponsor
    c.setFont("Helvetica", 8)
    c.drawString(290, 640, "N/A (faculty PI)")

    # 2. College / Department / Phone
    c.setFont("Helvetica", 8)
    c.drawString(115, 612, COLLEGE)
    c.drawString(268, 612, DEPT)
    c.drawString(500, 612, COLLEGE_PHONE)

    # 3. Title
    c.setFont("Helvetica", 8)
    c.drawString(210, 583, TITLE)

    # 4a Population — blank under prompt (~495–440)
    wrap(c, POPULATION, mid, 488, max_w - 0.5 * inch, size=7, leading=8.5, min_y=438)

    # 4b Procedures (~375–325)
    wrap(c, PROCEDURES, mid, 368, max_w - 0.5 * inch, size=7, leading=8.5, min_y=322)

    # 4c Objectives (~298–240)
    wrap(c, OBJECTIVES, mid, 298, max_w - 0.5 * inch, size=7, leading=8.5, min_y=238)

    # 5a Recruitment (~160–125)
    wrap(c, RECRUITMENT, mid, 158, max_w - 0.5 * inch, size=7, leading=8.5, min_y=122)

    # 5b Inclusion (~100–55)
    wrap(c, INCLUSION, mid, 100, max_w - 0.5 * inch, size=7, leading=8.5, min_y=55)

    # 5c Exclusion (~32–18)
    wrap(c, EXCLUSION, mid, 32, max_w - 0.5 * inch, size=6.5, leading=7.5, min_y=12)

    c.save()
    buf.seek(0)
    return buf.read()


def overlay_page2() -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    body_x = 1.5 * inch
    max_w = 6.5 * inch

    # 6a-1 benefits to subjects (~615–590)
    wrap(c, BENEFIT_SUBJECTS, body_x, 618, max_w, size=7.5, leading=9, min_y=590)

    # 6a-2 others (~575–550)
    wrap(c, BENEFIT_OTHERS, body_x, 575, max_w, size=7.5, leading=9, min_y=548)

    # 6a-3 society (~532–508)
    wrap(c, BENEFIT_SOCIETY, body_x, 532, max_w, size=7.5, leading=9, min_y=505)

    # 6b payment (~475–450)
    wrap(c, PAYMENT, body_x, 475, max_w, size=7.5, leading=9, min_y=448)

    # 6c-1 time (~405–380)
    wrap(c, COST_TIME, body_x, 405, max_w, size=7.5, leading=9, min_y=378)

    # 6c-2 money (~362)
    c.setFont("Helvetica", 8)
    c.drawString(body_x, 362, COST_MONEY)

    # 6c-3 repeated (~320)
    wrap(c, REPEATED, body_x, 318, max_w, size=7.5, leading=9, min_y=295)

    # 7. Categories A–C on this page — leave unchecked (primary claim is D on p.3)
    c.setFont("Helvetica", 7)
    c.setFillColorRGB(0.25, 0.25, 0.25)
    c.drawString(0.5 * inch, 78, "Primary exemption basis: Category D (see next page). A/B/C not claimed as primary basis.")

    c.save()
    buf.seek(0)
    return buf.read()


def overlay_page3() -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)

    # Category D checkbox (_____ D. at x≈36, y≈742)
    check(c, 38, 742)

    # Techniques: 1 educational tests; 3 survey/interview (_____ at x≈108)
    check(c, 110, 657)  # 1
    check(c, 110, 586)  # 3

    # Section 8 CITI note in whitespace near learner-group text
    c.setFont("Helvetica", 8)
    c.setFillColorRGB(0, 0, 0)
    wrap(
        c,
        "CITI attached: Christopher Castille — Human Subjects Research / Faculty Researchers and "
        "Research Sponsors (Basic). Completion 10-May-2024; Expiration 10-May-2026; Record ID "
        "59381539. Certificate appended to this PDF.",
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

    # 9. PI signature blank (underscores ~y=493–519) — sit just above the label
    c.setFont("Helvetica", 9)
    c.drawString(0.95 * inch, 508, f"{PI_NAME}")
    c.setFont("Helvetica", 7)
    c.setFillColorRGB(0.25, 0.25, 0.25)
    c.drawString(3.6 * inch, 508, "(Sign/date upon submission)")

    # 10. Faculty sponsor — N/A just above the sponsor label
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 9)
    c.drawString(0.95 * inch, 422, "N/A — Principal Investigator is faculty")

    # 11. Leave chair signature + protocol number blank for HSIRB assignment

    c.save()
    buf.seek(0)
    return buf.read()


def attachment_a_pages() -> list[bytes]:
    """Full narrative keyed to form section numbers (form allows attachments)."""
    protocol = load_protocol()
    pages: list[bytes] = []

    sections = [
        (
            "ATTACHMENT A — HSIRB Exempt Review Request (rev9 2019)\n"
            f"Project: {TITLE}\n"
            f"PI: {PI_NAME} | Phone: {PI_PHONE} | Email: {protocol['study_contact_email']}\n"
            "College: Al Danos College of Business Administration | Dept: Management and Marketing",
            None,
        ),
        ("4a. Population of human subjects", POPULATION),
        ("4b. Research procedures and data collection", PROCEDURES),
        ("4c. Objectives of the research", OBJECTIVES),
        ("5a. Recruitment (verbatim script)", protocol.get("recruitment_script", RECRUITMENT)),
        ("5b. Inclusion criteria", protocol.get("inclusion_criteria", INCLUSION).replace("\n", " ")),
        ("5c. Exclusion criteria", protocol.get("exclusion_criteria", EXCLUSION).replace("\n", " ")),
        ("6a–c. Benefits, payment, and costs", f"{BENEFIT_SUBJECTS} | Others: {BENEFIT_OTHERS} | Society: {BENEFIT_SOCIETY} | Payment: {PAYMENT} | Time: {COST_TIME} | Money: {COST_MONEY} | Repeated testing: {REPEATED}"),
        (
            "7. Basis of exemption — Category D (techniques 1 and 3)",
            protocol.get(
                "review_type_justification",
                "Category D: educational tests (SJT) and survey procedures; data recorded so subjects "
                "cannot be identified through linked identifiers (PRAMS/session IDs only).",
            ).replace("\n", " "),
        ),
        (
            "8. CITI training",
            "Christopher Castille — Human Subjects Research / Faculty Researchers and Research "
            "Sponsors (Basic Course). Completion 10-May-2024; Expiration 10-May-2026; Record ID "
            "59381539. Certificate attached.",
        ),
        (
            "9. Statement of risk (supporting narrative)",
            protocol.get("risk_statement", "").replace("\n", " ")
            + " Mitigation: "
            + protocol.get("risk_mitigation", "").replace("\n", " "),
        ),
        (
            "Active links for IRB review",
            "Interactive instrument (skip/optional ratings): "
            "https://bayoupal.nicholls.edu/hsirb/studies/hr-sjt/run/ | "
            "Professional consent: https://bayoupal.nicholls.edu/hsirb/studies/hr-sjt/professional-consent/ | "
            "Class/student consent: https://bayoupal.nicholls.edu/hsirb/studies/hr-sjt/student-data-consent/ | "
            "Full branded packet: materials/pdf/HSIRB_Application_HR_SJT_Rating_Effectiveness_full_packet.pdf",
        ),
    ]

    # Paginate
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
        if y < 1.5 * inch:
            new_page()
        if body is None:
            for i, line in enumerate(title.split("\n")):
                c.setFont("Helvetica-Bold" if i == 0 else "Helvetica", 9 if i == 0 else 8)
                c.drawString(0.75 * inch, y, line[:110])
                y -= 12
            y -= 6
            continue
        c.setFont("Helvetica-Bold", 9)
        c.drawString(0.75 * inch, y, title)
        y -= 12
        y = wrap(c, body, 0.75 * inch, y, 7.0 * inch, size=8, leading=10)
        y -= 10

    c.setFont("Helvetica", 8)
    c.drawString(0.75 * inch, 0.5 * inch, f"Attachment A — page {page_no}")
    c.save()
    pages.append(buf.getvalue())
    return pages


def write_field_map_md() -> None:
    protocol = load_protocol()
    md = f"""# NICHOLLS STATE UNIVERSITY — Request for HSIRB Exemption

**Filled draft for:** {TITLE}  
**Form:** HSIRB-exempt_review_request.rev9_2019.v2 (official blank overlay)  
**Blank source:** `HSIRB-exempt_review_request.rev9_2019.v2_BLANK.pdf`  
**Filled PDF:** `HSIRB_EXEMPT_REVIEW_REQUEST.pdf`  
**Status:** Ready for PI signature / college rep recommendation  
**Attachments:** Attachment A (narrative); CITI certificate (`docs/citiCompletionCertificate_4689946_59381539.pdf`); instrument / consents in full packet

The official form has **no fillable AcroForm fields**. Answers are overlaid on pages 1–4; Attachment A carries the full narrative keyed to form section numbers.

---

## 1. Investigators

| Field | Response |
|-------|----------|
| **Name(s) of Principal Investigator(s)** | {PI_NAME} |
| **Phone** | {PI_PHONE} |
| **Other Investigators** | None |
| **Faculty Sponsor (If Student Research)** | N/A (faculty PI) |
| **Faculty Sponsor Phone** | N/A |

## 2. Unit

| Field | Response |
|-------|----------|
| **College** | Al Danos College of Business Administration |
| **Department** | Management and Marketing |
| **Phone** | {COLLEGE_PHONE} |

## 3. Title of Project or Proposal

{TITLE}

## 4. Description of Project or Proposal

### 4a. Population of human subjects

{POPULATION}

### 4b. Research procedures and data collection

{PROCEDURES}

### 4c. Objectives of the research

{OBJECTIVES}

## 5. Recruitment

### 5a. How will you recruit subjects? (verbatim materials)

{RECRUITMENT}

**Recruitment script (verbatim):**

> {protocol.get("recruitment_script", "").replace(chr(10), "  ")}

### 5b. Inclusion criteria

{protocol.get("inclusion_criteria", INCLUSION)}

### 5c. Exclusion criteria

{protocol.get("exclusion_criteria", EXCLUSION)}

## 6. Subject benefits and costs

### 6a. Benefits

1. **Human subjects:** {BENEFIT_SUBJECTS}
2. **Others with similar problems / roles:** {BENEFIT_OTHERS}
3. **Society:** {BENEFIT_SOCIETY}

### 6b. Payment

{PAYMENT}

### 6c. Estimated costs to each subject

1. **Time:** {COST_TIME}
2. **Money:** {COST_MONEY}
3. **Repeated testing:** {REPEATED}

## 7. Basis of request for exemption

**☑ D.** Limited to collection/study of data obtained using the techniques below **AND** recorded so subjects cannot be identified, directly or indirectly, through identifiers linked with the subjects.

Applicable techniques under D:

- **☑ D-1.** Educational tests (cognitive, diagnostic, aptitude, achievement, etc.) — situational judgment assessment
- **☑ D-3.** Survey or interview procedures — online rating interface / consent questionnaire

**☐ A, ☐ B, ☐ C, ☐ E** — not the primary claimed basis.

## 8. CITI training

Attach current CITI certificate(s) for all investigators.

- **PI:** Christopher Castille — Human Subjects Research / Faculty Researchers and Research Sponsors (Basic)
- **Completion:** 10-May-2024
- **Expiration:** 10-May-2026
- **Record ID:** 59381539
- **File:** `docs/citiCompletionCertificate_4689946_59381539.pdf`

## 9. Statement of risk

The undersigned certify that they believe that the conduct of the above described research creates no risk of physical or emotional harm, or social or legal embarrassment to any participating human subject.

**Signature of Principal Investigator:** {PI_NAME} (sign upon submission) **Date:** ________

## 10. Faculty sponsor

N/A — Principal investigator is a faculty member.

## 11. Recommendation of HSIRB representative or HSIRB chair

I recommend that the above described research project be exempt from review.

**Signature of Chairperson / Representative:** ___________________________ **Date:** ________  
**HSIRB PROTOCOL NUMBER:** ______________

---

## Appendix checklist (submit with this form)

- [x] Filled exemption request (official rev9 PDF)  
- [x] Attachment A (section-keyed narrative)  
- [x] CITI certificate (PI)  
- [x] Professional consent form  
- [x] Class/student consent form  
- [x] Data collection instrument (27 situations — interactive packet + `incidents.json`)  
- [x] Classroom assignment announcement (verbatim, Section 5a; no flyer)  
- [x] Protocol narrative (`HR_SJT_PROTOCOL_PRAMS.md` / `protocol.json`)  
- [x] Full branded packet (`materials/pdf/HSIRB_Application_HR_SJT_Rating_Effectiveness_full_packet.pdf`)

**Suggested college representative / reviewers:** Jon Murphy (CBA), Juliann Allen

**Rebuild:** `python3 scripts/fill_hr_sjt_hsirb_exempt_form.py`
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
    print(f"Wrote {OUT_PDF}")
    print(f"Wrote {OUT_MD}")
    print(f"Pages: {len(writer.pages)}")


if __name__ == "__main__":
    main()
