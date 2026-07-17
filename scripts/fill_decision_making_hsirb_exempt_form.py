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
    c.drawString(175, 669, "A-M. Castille; S. Falgout; A. Maught (see Att. A)")
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
    c.drawString(3.6 * inch, 508, "July 17, 2026")
    c.setFont(FONT, SIZE)
    c.drawString(0.95 * inch, 422, "N/A — PI is faculty")
    c.save()
    buf.seek(0)
    return buf.read()


# Readable study narrative borrowed from the branded Nicholls HSIRB packet.
# Kept under Attachment A so the official rev9 form boxes stay short.
ATTACHMENT_A_BLOCKS = [
    (
        "Description of Project",
        "This study is a local replication of the foundational Schweitzer, Ordóñez, and Douma "
        "(2004) experiment examining whether performance goals drive unethical behavior. "
        "Participants complete anagram puzzles under one of four conditions: do-your-best, "
        "mere goal, reward goal, or personal goal. This design directly addresses several "
        "methodological limitations of the original 2004 study, tests key boundary "
        "conditions—specifically trait loss aversion and goal proximity—and contributes to a "
        "multi-site global replication project. Data collection occurs in two phases: a pilot "
        "session to calibrate materials and administration procedures, followed by a main study "
        "session for hypothesis testing. Both pilot and main materials are supplied for HSIRB "
        "review.",
    ),
    (
        "4a. Population of Human Subjects",
        "Participation is VOLUNTARY. Undergraduate students enrolled in Business Administration "
        "courses (specifically BSAD 101, meeting in Powell 140) at Nicholls State University, as "
        "well as working professionals. All participants must be 18 years of age or older.",
    ),
    (
        "4b. Research Procedures and Data Collection",
        "Pilot session: (1) Consent using Appendix B pilot form; (2) two 1-minute practice "
        "rounds; (3) timed anagram performance rounds under do-your-best instructions; "
        "(4) anonymous productivity report (no cash self-payment; participants may use a phone "
        "to access an online Scrabble dictionary via a QR code on the report); (5) brief "
        "questionnaires; (6) pilot appreciation letter.\n\n"
        "Main study: (1) Consent using Appendix B2 main study form; (2) two 1-minute practice "
        "rounds; (3) random assignment to do-your-best, mere goal, personal goal, or reward "
        "goal; (4) seven 1-minute performance rounds; (5) eighth-round unique anagram for "
        "anonymous linking (participants are told this round does not count toward payment); "
        "(6) demographics and trait measures while the researcher is present; (7) while the "
        "researcher is out of the room, participants privately check their work using a phone "
        "to access an online Scrabble dictionary via a QR code on the productivity report, "
        "complete an anonymous productivity report for rounds 1–7, perform private self-payment "
        "from a $14 cash envelope per the report instructions, seal the productivity report and "
        "cash envelope in a large envelope, and deposit materials in designated boxes (workbook "
        "folder and sealed large envelope separately); (8) main study debriefing sheet.\n\n"
        "Students who participated in the pilot may also participate in the main study. Because "
        "all data are anonymous, the research team cannot monitor repeat participation without "
        "compromising anonymity.\n\n"
        "Instruments: Appendix C (anagram workbook) and Appendix D (productivity report).",
    ),
    (
        "4c. Research Objectives",
        "Our primary objective is to conduct a constructive replication of the foundational "
        "Schweitzer et al. (2004) study, correcting its methodological limitations while "
        "maintaining its core strengths. Second, we aim to investigate when and for whom "
        "performance goals lead to unethical behavior. By testing how trait loss aversion and "
        "goal proximity influence overstatement, we provide a direct empirical test of the loss "
        "aversion mechanism theorized by Ordóñez and Wu (2013). These findings will help "
        "strengthen the empirical basis of the goal-setting literature and offer new theoretical "
        "insights for behavioral ethics.",
    ),
    (
        "4c. Research Questions or Hypotheses",
        "H1. People with specific challenging goals (i.e., personal, mere, or reward goals) are "
        "more likely to overstate their performance than people without specific challenging "
        "goals (i.e., do-your-best condition).\n\n"
        "H2. Challenging goal type is related to overstating performance. People with reward "
        "goals are more likely to overstate their performance than those with mere goals, who "
        "in turn are more likely to overstate their performance than those with personal goals.\n\n"
        "H3a. People who fail to reach their goal by a smaller margin are more likely to "
        "overstate their performance than if they were to fail to reach their goal by a larger "
        "margin.\n\n"
        "H3b. People who reach their goal are less likely to overstate their performance than if "
        "they failed to reach the goal.\n\n"
        "H4. People with greater trait loss aversion are more likely to overstate their "
        "performance.\n\n"
        "H5. The relationship between trait loss aversion and overstating behavior is amplified "
        "in trials where people failed their goal by a smaller margin than when they failed by "
        "a larger margin.",
    ),
    (
        "Educational Justification",
        "This project is part of a global multi-site initiative designed to train student "
        "researchers and junior faculty in rigorous, open-science replication methodologies. By "
        "engaging with a conditionally accepted Registered Report, local co-investigators and "
        "research assistants gain firsthand experience in pre-registration, double-blind "
        "administration, and collaborative behavioral science research.",
    ),
    (
        "5a. Recruitment Method & Script",
        "Recruitment occurs via classroom visits using approved informational flyers. Two flyer "
        "versions are included (Appendix A for pilot sessions, Appendix A2 for main study); only "
        "the version matching the session is shown. Both pilot and main recruitment materials "
        "are supplied for HSIRB review. Instructors may offer course credit or bonus points. The "
        "main-study flyer mentions a small cash reward of at least $7.00 with opportunity for up "
        "to $14.00; the pilot flyer does not mention cash compensation.\n\n"
        "Pilot script: You are invited to participate in a pilot session for a research study "
        "examining decision-making during cognitive tasks. This session takes approximately one "
        "hour, has received IRB ethics clearance, and helps refine procedures before main data "
        "collection. There is no cash compensation. Participation is voluntary and anonymous.\n\n"
        "Main study script: You are invited to participate in a research study examining "
        "decision-making during cognitive tasks. This study takes approximately one hour and has "
        "received IRB ethics clearance. Depending on your instructor's policy, you may receive "
        "course credit, bonus points, or a small cash reward of at least $7.00 with opportunity "
        "for up to $14.00 total. Participation is voluntary and anonymous.",
    ),
    (
        "5b–c. Inclusion & Exclusion Criteria",
        "Inclusion: undergraduate students or working professionals; 18 years of age or older. "
        "Exclusion: individuals under 18 years of age.",
    ),
    (
        "6. Subject Benefits, Payment, and Costs",
        "Benefits to subjects: Pilot session participants receive no cash compensation. They "
        "may receive course credit or bonus points at their instructor's discretion and receive "
        "a written appreciation letter explaining how pilot data support calibration for the "
        "main study. Main study participants receive direct financial compensation through the "
        "self-payment procedure, keeping at least $7.00 and up to $14.00 depending on their "
        "assigned instructions and performance (averaging about $10.00). They also receive a "
        "detailed debriefing sheet explaining the logic and value of open-science replication "
        "research.\n\n"
        "Benefits to others/society: Strengthening the empirical foundation of the dark-side of "
        "goal setting literature, generating a shared understanding between goal setting and "
        "behavioral ethics scholars, and developing novel theoretical insights to guide "
        "organizational practices.\n\n"
        "Payment/compensation: Pilot session — no cash compensation is provided. Main study "
        "only — all main-study participants receive an envelope containing $14.00 at the start "
        "of the session. Payment amounts are stated on each participant's productivity report "
        "during the private self-payment step. Those in the 'do your best', 'mere goal', and "
        "'personal goal' conditions are instructed to keep $10.00. Those in the 'reward goal' "
        "condition are instructed to keep $7.00 plus an additional $1.00 for each scored round "
        "(rounds 1–7) in which they met the site-calibrated goal (on average, approximately "
        "$10.00). Unearned cash is returned in the cash envelope, which is sealed with the "
        "productivity report in a large envelope while the researcher is out of the room. "
        "Participant-facing materials describe a small cash reward of at least $7.00 with "
        "opportunity for up to $14.00 total.\n\n"
        "Costs: Participation requires approximately one hour of time. There are no financial "
        "costs to the subjects.",
    ),
    (
        "7. Basis of Exemption / Justification",
        "On this official Request for HSIRB Exemption form, the study is submitted under "
        "Category D, techniques 1 (educational tests) and 3 (survey procedures). This aligns "
        "with Common Rule Category 2 (45 CFR 46.104(d)(2)): data are collected via behavioral "
        "tests (an anagram task) and survey procedures. No participant names, IDs, or other "
        "identifying information are recorded on any data collection sheets, ensuring "
        "participants cannot be identified, directly or through linked identifiers. While we "
        "correlate task performance with self-reported productivity reports using a unique "
        "eighth-round anagram, this linking mechanism is entirely anonymous and never "
        "associated with any student identity.",
    ),
    (
        "9. Statement of Risk & Mitigation",
        "Risk statement: The study presents minimal risk. The anagram task may cause mild "
        "frustration or performance anxiety, but no more than everyday schoolwork or standard "
        "puzzles. While participants have an opportunity to over-report performance or keep "
        "unearned money, all data are completely anonymous and cannot be linked to individual "
        "identities.\n\n"
        "Mitigation: To protect participants, the design is double-blind, and no names or "
        "student IDs are ever written on the study workbooks or productivity reports. Signed "
        "consent forms are collected and stored separately. The researcher leaves the room "
        "during grading, self-payment, and report submission. A unique eighth-round anagram is "
        "used for anonymous data linking. Finally, participants receive a detailed debriefing, "
        "and contact information for the Nicholls Counseling Center is provided.",
    ),
    (
        "Data Collection, Storage, & Access",
        "Collection methods: Data collection uses paper-and-pencil materials, including a task "
        "workbook (practice and performance anagram rounds, goal commitment, trait loss "
        "aversion, and demographics), a separate productivity report for self-reported "
        "performance, and a follow-up survey for manipulation and data quality checks. Hard "
        "copies are collected in a secure box.\n\n"
        "Storage: Hard-copy workbooks and productivity reports are stored in a locked office in "
        "the Department of Management and Marketing at Nicholls State University. De-identified, "
        "anonymized electronic datasets are maintained on secure, password-protected computers "
        "and shared publicly on the Open Science Framework (OSF) to facilitate open-science "
        "collaboration.\n\n"
        "Confidentiality procedures: Participants remain completely anonymous. No names, email "
        "addresses, or student IDs are written on the workbooks, productivity reports, or survey "
        "forms. Signed consent forms are stored in a separate locked cabinet from the raw data "
        "sheets. Anonymized data are linked via a unique eighth-round anagram rather than any "
        "personal identifier, and the de-identified spreadsheet is shared publicly on the OSF.\n\n"
        "Access: The principal investigator and local co-investigators have access to the raw "
        "paper materials. De-identified, anonymous data are shared with our research "
        "collaborators across the multi-site initiative and made publicly available on the Open "
        "Science Framework (OSF).\n\n"
        "Retention: Paper materials will be retained in a locked office for five to seven years "
        "in accordance with APA guidelines, after which they will be shredded. The anonymized "
        "electronic dataset will be preserved indefinitely on the OSF for replication and "
        "meta-analysis.",
    ),
    (
        "Consent Procedures",
        "Two written informed consent forms are included for HSIRB review: Appendix B (pilot "
        "session) and Appendix B2 (main study). Only the form matching the session is shown to "
        "participants. Each form details the study's purpose, procedures, risks, and benefits, "
        "emphasizing that participation is entirely voluntary and that participants may withdraw "
        "at any time without penalty. The main-study form describes cash compensation; the pilot "
        "form states that no cash compensation is provided. Students who choose not to "
        "participate are offered an equivalent alternative assignment for equal course credit.",
    ),
    (
        "8. CITI Training Certification",
        "All investigators have completed CITI Program training. Dr. Christopher Castille "
        "(Faculty Researchers), Dr. Ann-Marie R. Castille (Faculty Researchers), Dr. Samantha "
        "Falgout (Faculty Researchers), Dr. Adrien Maught (Social/Behavioral RCR). PI "
        "certificate is attached; co-investigator certificates are on file / to be submitted "
        "upon request.",
    ),
    (
        "Appendices (attached as-is below from the polished packet)",
        "A Pilot Recruitment Flyer; A2 Main Study Recruitment Flyer; B Pilot Informed Consent; "
        "B2 Main Study Informed Consent; C Anagram Task Workbook; D Participant Productivity "
        "Report; E Pilot Appreciation Letter; E2 Main Study Debriefing & Appreciation Letter; "
        "F Approved UWaterloo Master Protocol; G Psychological Science Registered Report "
        "Manuscript; H Psychological Science Stage 1 In-Principle Acceptance Letter.",
    ),
]


def wrap_paragraphs(c, text, x, y, max_w, size=SIZE, leading=LEADING, min_y=1.0 * inch):
    """Wrap text that may contain blank-line paragraph breaks; paginate as needed."""
    paragraphs = text.split("\n\n")
    for pi, para in enumerate(paragraphs):
        words = para.replace("\n", " ").split()
        line = ""
        for w in words:
            trial = f"{line} {w}".strip()
            if c.stringWidth(trial, FONT, size) <= max_w:
                line = trial
            else:
                if y < min_y:
                    c.showPage()
                    y = 10.4 * inch
                    c.setFont(FONT, size)
                c.setFont(FONT, size)
                c.drawString(x, y, line)
                y -= leading
                line = w
        if line:
            if y < min_y:
                c.showPage()
                y = 10.4 * inch
            c.setFont(FONT, size)
            c.drawString(x, y, line)
            y -= leading
        if pi < len(paragraphs) - 1:
            y -= 6
    return y


def attachment_a():
    """Attachment A — readable study details borrowed from the branded Nicholls packet."""
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    y = 10.4 * inch
    left = 0.75 * inch
    width = 7.0 * inch

    c.setFont("Times-Bold", 12)
    c.drawString(left, y, "ATTACHMENT A — Study Details")
    y -= 16
    c.setFont(FONT, SIZE)
    c.drawString(left, y, f"{TITLE}")
    y -= LEADING
    c.drawString(left, y, f"PI: {PI_NAME}, {PI_PHONE}")
    y -= LEADING
    c.drawString(
        left,
        y,
        "Co-Investigators: Dr. Ann-Marie R. Castille; Dr. Samantha Falgout; Dr. Adrien Maught",
    )
    y -= 18
    y = wrap_paragraphs(
        c,
        "The short answers on the Request for HSIRB Exemption form are summarized above. "
        "Fuller study details below are taken from the Nicholls-formatted exempt application "
        "narrative so reviewers can read the design in ordinary prose. Original Appendices A–H "
        "follow this Attachment as-is.",
        left,
        y,
        width,
    )
    y -= 10

    for title, body in ATTACHMENT_A_BLOCKS:
        if y < 1.4 * inch:
            c.showPage()
            y = 10.4 * inch
        c.setFont("Times-Bold", SIZE)
        c.drawString(left, y, title)
        y -= LEADING + 2
        y = wrap_paragraphs(c, body, left, y, width)
        y -= 10

    c.save()
    buf.seek(0)
    return buf.read()


def write_md():
    OUT_MD.write_text(
        f"""# HSIRB Exempt Review Request — Decision Making (rev9)

**PDF:** `HSIRB_EXEMPT_REVIEW_REQUEST.pdf`  
**Rebuild:** `python3 scripts/fill_decision_making_hsirb_exempt_form.py`

Form page answers stay short (Times-Roman 12). **Attachment A** uses the readable study
narrative from the branded Nicholls packet. Original Appendices A–H are appended as-is.

| § | Answer |
|---|--------|
| 1–3 | {PI_NAME}; CBA / M&M; {TITLE} |
| 4a–c / 5–9 | Short on form; full prose in Attachment A |
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

    for page in PdfReader(BytesIO(attachment_a())).pages:
        writer.add_page(page)

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
