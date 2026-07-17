"""
Machine-readable registry of research-compliance principles.

Each principle has:
  - id: stable code used in warnings and AuditLog metadata
  - authority: legal / ethical source language for explainability
  - summary: short operational rule for researchers and reviewers

Sources layered into this registry:
  CITI (HSR / InfoSec / Data Privacy), FERPA, La. R.S. 17:3914,
  APA CPTA (2026), SIOP CAPE AI Ethics Brief (2025),
  Landers & Nakamoto (2025) + APA Ethical Principles.
"""

from __future__ import annotations

from typing import Dict, TypedDict


class Principle(TypedDict):
    id: str
    title: str
    authority: str
    summary: str
    category: str


PRINCIPLES: Dict[str, Principle] = {
    'IPI_VS_DEID': {
        'id': 'IPI_VS_DEID',
        'title': 'Identifiable Private Information vs De-identified Data',
        'authority': 'CITI Human Subjects Research; FERPA; La. R.S. 17:3914',
        'summary': (
            'Treat any attribute that alone or in combination can identify a '
            'student/participant as IPI. De-identification requires that '
            're-identification is not reasonably possible, including mosaic attack.'
        ),
        'category': 'privacy',
    },
    'MOSAIC_ATTACK': {
        'id': 'MOSAIC_ATTACK',
        'title': 'Mosaic / Re-identification Risk',
        'authority': 'CITI Data Privacy; APA CPTA §3 Privacy and Confidentiality (2026)',
        'summary': (
            'Small-n cells, course + demographics + timestamps, and cross-linked '
            'exports can re-identify individuals. Apply generalization / k-anonymity '
            'before any external share.'
        ),
        'category': 'privacy',
    },
    'HITL_BEFORE_SHARE': {
        'id': 'HITL_BEFORE_SHARE',
        'title': 'Human-in-the-Loop Before External Sharing',
        'authority': 'APA CPTA §6 Human Oversight (2026); SIOP CAPE Human Oversight; CITI',
        'summary': (
            'No automated external disclosure. A qualified human must review and '
            'approve before data leaves university-managed custody.'
        ),
        'category': 'oversight',
    },
    'NO_PUBLIC_LLM_IPI': {
        'id': 'NO_PUBLIC_LLM_IPI',
        'title': 'No IPI in Public / Consumer Generative AI',
        'authority': 'APA CPTA §3; SIOP CAPE Privacy; La. R.S. 17:3914; FERPA',
        'summary': (
            'Client/student data must not be processed on public consumer-grade LLMs. '
            'Prefer local/university-managed models (e.g., Ollama) when AI assists review.'
        ),
        'category': 'ai_privacy',
    },
    'LOCAL_CUSTODY': {
        'id': 'LOCAL_CUSTODY',
        'title': 'University-Managed Local Custody',
        'authority': 'CITI Information Security; La. R.S. 17:3914; FERPA school-official framework',
        'summary': (
            'Keep identifiable education/research records on university-managed systems '
            'with institutional endpoint controls. Avoid creating new external recipients.'
        ),
        'category': 'security',
    },
    'DATA_MINIMIZATION': {
        'id': 'DATA_MINIMIZATION',
        'title': 'Minimum Necessary Data',
        'authority': 'CITI; APA CPTA §3 guiding questions; FERPA',
        'summary': 'Collect and export only data necessary for the stated research/administrative purpose.',
        'category': 'privacy',
    },
    'TRANSPARENCY_ACCOUNTABILITY': {
        'id': 'TRANSPARENCY_ACCOUNTABILITY',
        'title': 'Transparency and Accountability',
        'authority': 'APA CPTA §1; SIOP CAPE; Landers & Nakamoto (2025) Integrity',
        'summary': (
            'Document who decided what, on what basis, and which principles applied. '
            'AI outputs are aids; humans remain accountable.'
        ),
        'category': 'governance',
    },
    'BIAS_FAIRNESS': {
        'id': 'BIAS_FAIRNESS',
        'title': 'Bias and Fairness',
        'authority': 'APA CPTA §2; SIOP CAPE Fairness; APA Principle D (Justice)',
        'summary': 'Identify data, development, and interaction bias before high-stakes AI-assisted decisions.',
        'category': 'ethics',
    },
    'INFORMED_CONSENT_AI': {
        'id': 'INFORMED_CONSENT_AI',
        'title': 'Informed Consent for AI-Assisted Processes',
        'authority': 'APA CPTA §4; Common Rule; APA Ethical Principles',
        'summary': (
            'When AI is used in assessment or review affecting people, disclose purpose, '
            'privacy limits, and alternatives in accessible language.'
        ),
        'category': 'ethics',
    },
    'COMPETENCE': {
        'id': 'COMPETENCE',
        'title': 'Competence Before Deployment',
        'authority': 'APA CPTA §5; Landers & Nakamoto (2025)',
        'summary': 'Do not deploy AI-assisted research tools without understanding operational limits and oversight duties.',
        'category': 'governance',
    },
    'LA_3914_NO_UNAUTHORIZED_DISCLOSURE': {
        'id': 'LA_3914_NO_UNAUTHORIZED_DISCLOSURE',
        'title': 'Louisiana Student Data Non-Disclosure',
        'authority': 'La. R.S. 17:3914; FERPA',
        'summary': (
            'Student personally identifiable information may not be disclosed to unauthorized '
            'third parties. Vendor/cloud transmission without lawful authority creates statutory risk.'
        ),
        'category': 'legal',
    },
    'FERPA_EDUCATION_RECORDS': {
        'id': 'FERPA_EDUCATION_RECORDS',
        'title': 'FERPA Education Records Protection',
        'authority': 'FERPA 20 U.S.C. §1232g; 34 CFR Part 99',
        'summary': (
            'Course credits, student IDs, names, and emails in PRAMS are education records. '
            'Access, export, and retention require legitimate educational interest and auditability.'
        ),
        'category': 'legal',
    },
    'APA_NONMALEFICENCE': {
        'id': 'APA_NONMALEFICENCE',
        'title': 'Beneficence and Nonmaleficence',
        'authority': 'APA Ethical Principle A; Landers & Nakamoto (2025)',
        'summary': 'Expected benefits of AI/research systems must outweigh costs to individual well-being; do no harm.',
        'category': 'ethics',
    },
}


def get_principle(principle_id: str) -> Principle:
    """Return a principle by id; raises KeyError if unknown."""
    return PRINCIPLES[principle_id]


def principle_citation(principle_id: str) -> str:
    """Short authority string for UI / AuditLog."""
    p = PRINCIPLES[principle_id]
    return f"{p['id']}: {p['title']} ({p['authority']})"
