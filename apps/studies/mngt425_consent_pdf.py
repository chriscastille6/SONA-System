"""
PDF copies of the MNGT 425 Exhibits A–C consent (information sheet + signed record).
ReportLab layout tuned for a professional, academic document appearance.
"""
from __future__ import annotations

import html as html_stdlib
import re
from io import BytesIO

from django.utils.html import strip_tags

try:
    from reportlab.lib import colors
    from reportlab.lib.colors import HexColor
    from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
    from reportlab.pdfgen import canvas as pdf_canvas
except ImportError:  # pragma: no cover
    SimpleDocTemplate = None

# Nicholls-adjacent palette (formal, not official marketing lockup)
_ACCENT = HexColor("#0e4c99")
_MUTED = HexColor("#4b5563")
_TABLE_HEADER = HexColor("#e8eef5")
_RULE = HexColor("#cbd5e1")

_PAGE_WIDTH, PAGE_HEIGHT = letter


def _html_to_plain_chunks(consent_html: str, max_chunk: int = 4200) -> list[str]:
    """Strip HTML to plain text; split into paragraphs for readability."""
    plain_full = strip_tags(consent_html)
    plain_full = html_stdlib.unescape(plain_full)
    plain_full = re.sub(r"\s+", " ", plain_full).strip()
    if not plain_full:
        return ["(No text.)"]

    sections = _split_numbered_sections(plain_full)
    chunks: list[str] = []
    for sec in sections:
        if len(sec) <= max_chunk:
            chunks.append(sec)
            continue
        start = 0
        while start < len(sec):
            end = min(start + max_chunk, len(sec))
            if end < len(sec):
                back = sec.rfind(". ", start + 1600, end)
                if back != -1:
                    end = back + 1
            piece = sec[start:end].strip()
            if piece:
                chunks.append(piece)
            start = end if end > start else end + 1
    return chunks


def _split_numbered_sections(plain: str) -> list[str]:
    """Break consent text at numbered sections (1. 2. …) when present."""
    parts = re.split(r"(?=\s\d+\.\s)", plain)
    parts = [p.strip() for p in parts if p.strip()]
    if len(parts) >= 2:
        merged = []
        buf = ""
        for p in parts:
            if re.match(r"^\d+\.\s", p):
                if buf:
                    merged.append(buf.strip())
                buf = p
            else:
                buf = (buf + " " + p).strip() if buf else p
        if buf:
            merged.append(buf.strip())
        return merged if merged else [plain]
    return [plain]


def _px(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _draw_page_frame(canv: pdf_canvas.Canvas, doc, *, doc_title: str) -> None:
    """Header rule + institution line + footer with page number."""
    canv.saveState()
    m_l = doc.leftMargin
    m_r = doc.pagesize[0] - doc.rightMargin
    top_y = doc.pagesize[1] - doc.topMargin + 0.15 * inch

    canv.setStrokeColor(_ACCENT)
    canv.setLineWidth(3)
    canv.line(m_l, top_y + 0.08 * inch, m_r, top_y + 0.08 * inch)

    canv.setFillColor(_MUTED)
    canv.setFont("Helvetica", 8.5)
    canv.drawString(m_l, top_y + 0.02 * inch, "Nicholls State University")
    canv.setFont("Helvetica-Oblique", 8)
    right_txt = "Management & Marketing  ·  MNGT 425 HR Analytics"
    tw = canv.stringWidth(right_txt, "Helvetica-Oblique", 8)
    canv.drawRightString(m_r, top_y + 0.02 * inch, right_txt)

    canv.setStrokeColor(_RULE)
    canv.setLineWidth(0.5)
    canv.line(m_l, top_y - 0.06 * inch, m_r, top_y - 0.06 * inch)

    footer_y = 0.52 * inch
    canv.setFillColor(colors.HexColor("#6b7280"))
    canv.setFont("Helvetica", 7.5)
    canv.drawCentredString(
        doc.pagesize[0] / 2,
        footer_y,
        f"Page {canv.getPageNumber()}    ·    {doc_title[:72]}{'…' if len(doc_title) > 72 else ''}    ·    PRAMS / HSIRB",
    )
    canv.restoreState()


def build_exhibits_consent_pdf(
    *,
    consent_html: str,
    signer_first: str | None = None,
    signer_last: str | None = None,
    signer_email: str | None = None,
    consent_given: bool | None = None,
    submitted_at_display: str | None = None,
    document_title: str = "MNGT 425 — Exhibits A–C consent",
) -> bytes:
    """
    Build PDF bytes. If signer fields are provided, page 1 includes an attestation block.
    """
    if SimpleDocTemplate is None:
        raise RuntimeError("reportlab is required for PDF generation (pip install reportlab)")

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        rightMargin=0.85 * inch,
        leftMargin=0.85 * inch,
        topMargin=1.05 * inch,
        bottomMargin=0.85 * inch,
        title=document_title,
    )

    styles = getSampleStyleSheet()

    title_main = ParagraphStyle(
        name="M425Title",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=21,
        textColor=colors.HexColor("#111827"),
        spaceAfter=4,
        alignment=TA_LEFT,
    )
    title_sub = ParagraphStyle(
        name="M425Sub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=14,
        textColor=_MUTED,
        spaceAfter=16,
        alignment=TA_LEFT,
    )
    body = ParagraphStyle(
        name="M425Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=13.5,
        textColor=colors.HexColor("#1f2937"),
        spaceAfter=10,
        alignment=TA_JUSTIFY,
        firstLineIndent=0,
    )
    body_first = ParagraphStyle(
        name="M425BodyFirst",
        parent=body,
        spaceBefore=0,
    )
    section_head = ParagraphStyle(
        name="M425Section",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=_ACCENT,
        spaceBefore=14,
        spaceAfter=8,
        alignment=TA_LEFT,
    )
    callout = ParagraphStyle(
        name="M425Callout",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        leftIndent=10,
        rightIndent=10,
        borderPadding=10,
        borderColor=_RULE,
        borderWidth=0.5,
        backColor=HexColor("#f8fafc"),
        spaceAfter=14,
        alignment=TA_LEFT,
    )
    footnote = ParagraphStyle(
        name="M425Foot",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#6b7280"),
        spaceBefore=16,
        alignment=TA_LEFT,
    )

    story: list = []

    story.append(Paragraph(_px("Participant consent document"), title_sub))
    story.append(Spacer(1, 0.05 * inch))
    story.append(Paragraph(_px(document_title), title_main))
    story.append(
        Paragraph(
            _px("Exhibits A–C — Technical supplement & de-identified course data (teaching portfolio / research)"),
            title_sub,
        )
    )

    signed = (
        signer_email
        and signer_first is not None
        and signer_last is not None
        and consent_given is not None
    )

    if signed:
        story.append(
            Paragraph(
                "<b>Participant attestation</b> — retain this page for your records or Canvas upload.",
                section_head,
            )
        )
        decision = "I consent" if consent_given else "I do not consent"
        decision_color = colors.HexColor("#065f46") if consent_given else colors.HexColor("#92400e")
        data = [
            ["Legal name (typed signature)", f"{signer_first} {signer_last}"],
            ["Nicholls email", signer_email],
            ["Decision", decision],
            ["Recorded (server time)", submitted_at_display or "—"],
        ]
        att = Table(
            [[_px(a), _px(b)] for a, b in data],
            colWidths=[2.05 * inch, 4.25 * inch],
        )
        att.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("TEXTCOLOR", (0, 0), (0, -1), _MUTED),
                    ("TEXTCOLOR", (1, 2), (1, 2), decision_color),
                    ("FONTNAME", (1, 2), (1, 2), "Helvetica-Bold"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                    ("LEFTPADDING", (0, 0), (-1, -1), 12),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                    ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.75, _RULE),
                    ("LINEABOVE", (0, 0), (-1, 0), 2, _ACCENT),
                ]
            )
        )
        story.append(att)
        story.append(Spacer(1, 0.12 * inch))
        story.append(
            Paragraph(
                _px(
                    "You submitted this decision through the authorized PRAMS web form. "
                    "Your printed name above constitutes your electronic signature under this record. "
                    "If your instructor assigned a Canvas upload, attach this file there as a backup copy."
                ),
                callout,
            )
        )
        story.append(PageBreak())
        story.append(
            Paragraph("<b>Consent language in effect at submission</b>", section_head),
        )
        story.append(Spacer(1, 0.06 * inch))
    else:
        story.append(
            Paragraph(
                _px(
                    "This PDF is an information copy only. Your choice is not recorded until you complete "
                    "and submit the official web form on PRAMS/HSIRB."
                ),
                callout,
            )
        )
        story.append(Spacer(1, 0.08 * inch))
        story.append(Paragraph("<b>Consent text</b>", section_head))

    first_para = True
    for chunk in _html_to_plain_chunks(consent_html):
        style = body_first if first_para else body
        first_para = False
        story.append(Paragraph(_px(chunk), style))

    story.append(
        Paragraph(
            _px(
                "Document generated from the Participant Recruitment & Management System (PRAMS / HSIRB). "
                "Questions: contact your course instructor."
            ),
            footnote,
        )
    )

    short_title = "Exhibits A–C consent"

    def _on_page(canv, d):
        _draw_page_frame(canv, d, doc_title=short_title)

    doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)
    return buf.getvalue()


def safe_pdf_filename(last: str, first: str) -> str:
    safe_l = re.sub(r"[^\w\-]+", "_", last)[:40] or "student"
    safe_f = re.sub(r"[^\w\-]+", "_", first)[:40] or "name"
    return f"MNGT425_Exhibits_ABC_Consent_{safe_l}_{safe_f}.pdf"
