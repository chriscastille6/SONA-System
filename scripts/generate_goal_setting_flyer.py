#!/usr/bin/env python3
"""
Script to generate the Nicholls Goal-Setting recruitment flyer.
Generates a clean, single-page, professional PDF with Nicholls branding,
completely removing the "How to Sign Up" section.
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
    KeepTogether
)

def build_nicholls_flyer():
    # Setup output path
    base_dir = Path(__file__).resolve().parent.parent
    output_dir = base_dir / "apps" / "studies" / "assets" / "irb" / "goal-setting" / "materials" / "pdf"
    output_dir.mkdir(exist_ok=True, parents=True)
    pdf_path = output_dir / "Recruitment_version2_20260312.pdf"
    
    # Setup Document (letter size: 8.5 x 11 inches)
    # Margins tuned for a balanced, professional single-page layout
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch
    )

    styles = getSampleStyleSheet()

    # Core styles matching Nicholls branding
    style_univ = ParagraphStyle(
        name="FlyerUniv",
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#A6192E"),  # Nicholls Red
        alignment=TA_CENTER,
        spaceAfter=2
    )
    style_sub = ParagraphStyle(
        name="FlyerSub",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#1f2937"),
        alignment=TA_CENTER,
        spaceAfter=12
    )
    style_title = ParagraphStyle(
        name="FlyerTitle",
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#111827"),
        alignment=TA_CENTER,
        spaceAfter=15
    )
    style_body = ParagraphStyle(
        name="FlyerBody",
        fontName="Helvetica",
        fontSize=10.5,
        leading=15.5,
        textColor=colors.HexColor("#374151"),
        alignment=TA_JUSTIFY,
        spaceAfter=15
    )
    style_bullet_head = ParagraphStyle(
        name="FlyerBulletHead",
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#A6192E"),
        alignment=TA_LEFT,
        spaceAfter=6,
        keepWithNext=True
    )
    style_bullet_text = ParagraphStyle(
        name="FlyerBulletText",
        fontName="Helvetica",
        fontSize=10.5,
        leading=15,
        textColor=colors.HexColor("#374151"),
        alignment=TA_LEFT,
        spaceAfter=12
    )
    style_footer = ParagraphStyle(
        name="FlyerFooter",
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#6b7280"),
        alignment=TA_CENTER,
        spaceBefore=25
    )

    story = []

    # 1. Nicholls Header Lockup
    story.append(Paragraph("NICHOLLS STATE UNIVERSITY", style_univ))
    story.append(Paragraph("COLLEGE OF BUSINESS ADMINISTRATION  ·  RESEARCH PARTICIPATION", style_sub))
    story.append(Spacer(1, 0.05 * inch))
    
    # Draw a bold crimson line below the header
    header_line = Table([[""]], colWidths=[7.0 * inch])
    header_line.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,-1), 3.0, colors.HexColor("#A6192E")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(header_line)
    story.append(Spacer(1, 0.25 * inch))

    # 2. Catching Title
    story.append(Paragraph("A Study in Decision Making", style_title))
    story.append(Spacer(1, 0.1 * inch))

    # 3. Invitation Body Text (verbatim Waterloo content localized to Nicholls)
    invitation_text = (
        "You are invited to participate in an exciting, multi-site global research study on organizational "
        "decision-making. This study is part of a larger collaborative initiative (ARIM) and has received "
        "formal ethics clearance from the Human Subjects Institutional Review Board (HSIRB) at Nicholls State University. "
        "The project is being conducted locally by <b>Dr. Christopher Castille</b> (Associate Professor of Management), "
        "<b>Dr. Samantha Falgout</b> (Assistant Professor of Accounting), and our student research team."
    )
    story.append(Paragraph(invitation_text, style_body))
    story.append(Spacer(1, 0.15 * inch))

    # 4. Details Blocks arranged in a neat grid table (Bullet heads + text)
    details_data = [
        [
            Paragraph("What will I do?", style_bullet_head),
            Paragraph("What are the requirements?", style_bullet_head)
        ],
        [
            Paragraph(
                "You will be asked to complete a decision-making task involving word puzzles (anagrams) "
                "in a classroom or computer lab on the Nicholls State University campus. You will also "
                "complete a brief personality scale, task commitment measures, and standard demographics. "
                "Participation takes <b>no more than 1 hour</b> of your time.", 
                style_bullet_text
            ),
            Paragraph(
                "• Must be currently enrolled as a student at Nicholls State University.<br/>"
                "• Must be 18 years of age or older.<br/>"
                "• Fluent in English and comfortable working on basic word problems.",
                style_bullet_text
            )
        ],
        [
            Paragraph("What will I receive?", style_bullet_head),
            Paragraph("Is participation confidential?", style_bullet_head)
        ],
        [
            Paragraph(
                "In appreciation of your time, you will receive a base payment of <b>$10.00 cash</b>, with "
                "the opportunity to receive up to <b>$14.00 cash</b> depending on your performance during "
                "the task rounds. Instructors may also offer course bonus points or research credit.",
                style_bullet_text
            ),
            Paragraph(
                "<b>Yes, completely.</b> All data collected in this study are anonymous. Your name and "
                "email are never associated with your answers, workbooks, or self-reported scores. "
                "Data are stored securely using de-identified code IDs.",
                style_bullet_text
            )
        ]
    ]

    t_details = Table(details_data, colWidths=[3.4 * inch, 3.4 * inch])
    t_details.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (0,-1), 12),
        ('LEFTPADDING', (1,0), (1,-1), 12),
    ]))
    story.append(t_details)
    story.append(Spacer(1, 0.3 * inch))

    # 5. Formal University Disclaimer Footer
    footer_text = (
        "Nicholls State University  ·  College of Business Administration  ·  HSIRB Approved Protocol: IRB 2024-07-30-001 CBA<br/>"
        "For questions about your rights as a participant, contact the Nicholls HSIRB Chair (Dr. Alaina Daigle, 985-448-4697)."
    )
    story.append(Paragraph(footer_text, style_footer))

    # Build PDF
    doc.build(story)
    print(f"Successfully generated Nicholls branded flyer at: {pdf_path}")

if __name__ == "__main__":
    build_nicholls_flyer()
