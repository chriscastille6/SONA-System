import io
from pathlib import Path
from django.conf import settings

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    KeepTogether
)
from reportlab.pdfgen import canvas as pdf_canvas


class NumberedCanvas(pdf_canvas.Canvas):
    """Custom canvas to compute total page count and draw standard running footers with legacy HSIRB page numbering."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_footer(num_pages)
            super().showPage()
        super().save()

    def draw_footer(self, page_count):
        self.saveState()
        # Draw a thin running rule above the footer
        self.setStrokeColor(colors.HexColor("#94a3b8")) # cool grey
        self.setLineWidth(0.5)
        self.line(0.75 * inch, 0.75 * inch, letter[0] - 0.75 * inch, 0.75 * inch)

        # Draw legacy page indicator: "HSIRB X"
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#4b5563")) # slate gray
        self.drawString(0.75 * inch, 0.55 * inch, "NICHOLLS STATE UNIVERSITY  ·  HSIRB")
        self.drawRightString(letter[0] - 0.75 * inch, 0.55 * inch, f"HSIRB {self._pageNumber}")
        self.restoreState()


def build_legacy_irb_pdf(submission) -> bytes:
    """
    Build a multi-page PDF document representing the legacy Nicholls HSIRB Request for Review form
    populated dynamically from the fields of a ProtocolSubmission model.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.85 * inch,
        bottomMargin=0.95 * inch,
        title=f"HSIRB Application — {submission.safe_study_title}"
    )

    styles = getSampleStyleSheet()

    # Define custom styles matching formal legacy templates
    title_univ = ParagraphStyle(
        name="LegacyUniv",
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#A6192E"), # Nicholls Red
        alignment=TA_CENTER,
        spaceAfter=3
    )
    title_board = ParagraphStyle(
        name="LegacyBoard",
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=14,
        textColor=colors.HexColor("#1f2937"),
        alignment=TA_CENTER,
        spaceAfter=12
    )
    title_form = ParagraphStyle(
        name="LegacyForm",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=13,
        textColor=colors.HexColor("#1f2937"),
        alignment=TA_CENTER,
        spaceAfter=18
    )
    section_head = ParagraphStyle(
        name="LegacySecHead",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=13,
        textColor=colors.HexColor("#A6192E"),
        alignment=TA_LEFT,
        spaceBefore=12,
        spaceAfter=8,
        keepWithNext=True
    )
    field_label = ParagraphStyle(
        name="LegacyLabel",
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=11,
        textColor=colors.HexColor("#1f2937"),
        alignment=TA_LEFT
    )
    field_value = ParagraphStyle(
        name="LegacyValue",
        fontName="Helvetica",
        fontSize=9.5,
        leading=12.5,
        textColor=colors.HexColor("#374151"),
        alignment=TA_LEFT
    )
    body_text = ParagraphStyle(
        name="LegacyBody",
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#374151"),
        alignment=TA_JUSTIFY,
        spaceAfter=10
    )
    preamble_style = ParagraphStyle(
        name="LegacyPreamble",
        fontName="Helvetica-Oblique",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#4b5563"),
        alignment=TA_JUSTIFY,
        spaceAfter=14
    )

    story = []

    # =========================================================================
    # PAGE 1: COVER PREAMBLE & PROCEDURES
    # =========================================================================
    story.append(Paragraph("NICHOLLS STATE UNIVERSITY", title_univ))
    story.append(Paragraph("HUMAN SUBJECTS INSTITUTIONAL REVIEW BOARD", title_board))
    
    review_type_label = submission.get_review_type_display() if submission.review_type else "EXEMPT"
    story.append(Paragraph(f"REQUEST FOR {review_type_label.upper()} REVIEW BY HUMAN SUBJECTS INSTITUTIONAL BOARD", title_form))

    preamble_text = (
        "Nicholls State University has established standards and guidelines to ensure adequate protection "
        "is provided to individuals participating in a research activity. The Human Subjects Institutional "
        "Review Board (HSIRB) is charged with the responsibility of screening all research which employs human "
        "participants conducted by faculty, administrators, or students affiliated with Nicholls State University. "
        "The guidelines employed for screening are those set forth by university policy. Please fill in all "
        "requested information and keep a copy of this form and any supporting documentation on file."
    )
    story.append(Paragraph(preamble_text, preamble_style))

    story.append(Paragraph("General Guidelines:", section_head))
    
    guideline_1 = (
        "<b>1. Primary Investigator:</b> The primary investigator planning a research activity involving human "
        "subjects should obtain a Request for HSIRB application form and complete all requested fields fully "
        "with authentic, descriptive details. Research originating from other institutions should be approved "
        "by the host institution prior to applying for approval at Nicholls State University."
    )
    guideline_2 = (
        "<b>2. Review Workflow:</b> The completed application is submitted through the PRAMS platform. "
        "An initial review of the application will be made by the college HSIRB representative to determine if the "
        "project is considered Category I, EXEMPT, Category II, EXPEDITED REVIEW, or Category III, FULL COMMITTEE REVIEW."
    )
    guideline_3 = (
        "<b>3. Timing:</b> Investigators must receive formal approved status from the board BEFORE any recruitment "
        "actions or data collection commence. Retroactive approvals are strictly prohibited."
    )
    story.append(Paragraph(guideline_1, body_text))
    story.append(Paragraph(guideline_2, body_text))
    story.append(Paragraph(guideline_3, body_text))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: BASIC PROJECT INFORMATION
    # =========================================================================
    story.append(Paragraph("NICHOLLS STATE UNIVERSITY", title_univ))
    story.append(Paragraph("HUMAN SUBJECTS INSTITUTIONAL REVIEW BOARD", title_board))
    story.append(Paragraph("PROJECT INFORMATION FORM", title_form))

    # Construct formal key-value table for basic info
    info_data = [
        [Paragraph("Title of Investigation:", field_label), Paragraph(submission.safe_study_title, field_value)],
        [Paragraph("Name of Primary Investigator:", field_label), Paragraph(submission.pi_name or "—", field_value)],
        [Paragraph("PI Title / Academic Rank:", field_label), Paragraph(submission.pi_title or "—", field_value)],
        [Paragraph("PI Department / School:", field_label), Paragraph(submission.pi_department or "—", field_value)],
        [Paragraph("PI Email Address:", field_label), Paragraph(submission.pi_email or "—", field_value)],
        [Paragraph("PI Phone Number:", field_label), Paragraph(submission.pi_phone or "—", field_value)],
        [Paragraph("Other Investigators Involved:", field_label), Paragraph((submission.co_investigators or "None").replace("\n", "<br/>"), field_value)],
        [Paragraph("Source of Project Funds:", field_label), Paragraph(submission.funding_source or "None (Internal / Faculty Research)", field_value)],
        [Paragraph("Is this a Continuation of research?", field_label), Paragraph("Yes (Protocol #: %s)" % submission.previous_protocol_number if submission.continuation_of_previous and submission.previous_protocol_number else "No", field_value)],
        [Paragraph("Federal Exemption Category:", field_label), Paragraph(submission.exemption_category or "Exempt Category 2 (45 CFR 46.104(d)(2))" if submission.review_type == 'exempt' else "N/A", field_value)],
    ]

    t = Table(info_data, colWidths=[2.2 * inch, 4.8 * inch])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
    ]))
    story.append(t)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: DETAILED DESCRIPTION & QUESTIONS
    # =========================================================================
    def clean_text_with_linebreaks(text_val: str) -> str:
        if not text_val:
            return "—"
        return text_val.replace("\n", "<br/>")

    sections_mapping = [
        ("1. Description of Project or Proposal", submission.protocol_description),
        ("2. Population of Human Subjects", submission.population_description),
        ("3. Research Procedures and Data Collection", submission.research_procedures),
        ("4. Research Objectives", submission.research_objectives),
        ("5. Research Questions or Hypotheses", submission.research_questions),
        ("6. Educational Justification", submission.educational_justification),
        ("7. Recruitment Method & Script", (submission.recruitment_method or "") + "\n\n<b>Script:</b>\n" + (submission.recruitment_script or "")),
        ("8. Subject Inclusion & Exclusion Criteria", "<b>Inclusion:</b>\n" + (submission.inclusion_criteria or "") + "\n\n<b>Exclusion:</b>\n" + (submission.exclusion_criteria or "")),
        ("9. Subject Benefits & Costs", "<b>Benefits to Subjects:</b>\n" + (submission.benefits_to_subjects or "") + "\n\n<b>Benefits to Others/Society:</b>\n" + (submission.benefits_to_society or "") + "\n\n<b>Payment/Compensation:</b>\n" + (submission.payment_compensation or "") + "\n\n<b>Costs:</b>\n" + (submission.costs_to_subjects or "")),
        ("10. Basis of Exemption / Justification", submission.review_type_justification),
        ("11. Statement of Risk & Mitigation", "<b>Risk Statement:</b>\n" + (submission.risk_statement or "") + "\n\n<b>Mitigation:</b>\n" + (submission.risk_mitigation or "")),
        ("12. Data Collection, Storage, & Access", "<b>Collection Methods:</b>\n" + (submission.data_collection_methods or "") + "\n\n<b>Storage:</b>\n" + (submission.data_storage or "") + "\n\n<b>Confidentiality Procedures:</b>\n" + (submission.confidentiality_procedures or "") + "\n\n<b>Access:</b>\n" + (submission.data_access or "") + "\n\n<b>Retention:</b>\n" + (submission.data_retention or "")),
        ("13. Consent Procedures", submission.consent_procedures),
        ("14. CITI Training Certification", submission.citi_training_completion),
    ]

    for head, val in sections_mapping:
        elements = [
            Paragraph(head, section_head),
            Paragraph(clean_text_with_linebreaks(val), body_text),
            Spacer(1, 0.15 * inch)
        ]
        story.append(KeepTogether(elements))

    story.append(Spacer(1, 0.2 * inch))

    # =========================================================================
    # SIGNATURE BLOCK (PAGE END / KEEP TOGETHER)
    # =========================================================================
    sig_text = (
        "<b>Statement of Compliance & Ethical Assurances:</b><br/>"
        "By signing below, the Primary Investigator certifies that the described project "
        "will be conducted in accordance with university guidelines, the Belmont Report, "
        "and 45 CFR 46. Any protocol modifications or adverse events must be reported "
        "immediately to the board."
    )
    
    sig_lines = [
        Paragraph(sig_text, body_text),
        Spacer(1, 0.3 * inch),
        Table([
            [Paragraph("____________________________________________________<br/>Primary Investigator Signature", field_label), 
             Paragraph("_________________<br/>Date", field_label)],
            [Paragraph("____________________________________________________<br/>College HSIRB Representative Signature", field_label), 
             Paragraph("_________________<br/>Date", field_label)],
            [Paragraph("____________________________________________________<br/>HSIRB Chairperson Signature (Approval)", field_label), 
             Paragraph("_________________<br/>Date", field_label)]
        ], colWidths=[4.5 * inch, 2.5 * inch], style=TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 18),
        ]))
    ]
    story.append(KeepTogether(sig_lines))

    doc.build(story, canvasmaker=NumberedCanvas)
    buf.seek(0)
    return buf.getvalue()
