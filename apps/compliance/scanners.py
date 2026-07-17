"""
Lightweight IPI / mosaic-risk pattern scanners.

These are heuristic pre-checks for warning systems. They do not claim
perfect detection. False positives are acceptable; false negatives are
mitigated by mandatory human-in-the-loop review before external share.

Never log matched raw student values — only pattern category counts.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List

# Pattern detectors (match presence only; do not retain matched substrings in logs)
EMAIL_RE = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
SSN_RE = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
PHONE_RE = re.compile(r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
# Common student-ID shaped tokens (digit runs 6–10); heuristic only
STUDENT_ID_RE = re.compile(r'\b\d{6,10}\b')
# Institutional brand / campus identifiers that increase mosaic / branding risk in exports
INSTITUTION_RE = re.compile(r'\bnicholls\b', re.IGNORECASE)

# Phrases suggesting cloud / public AI / third-party processing of participant data
CLOUD_AI_PHRASES = re.compile(
    r'\b('
    r'chatgpt|openai|claude\.ai|gemini\.google|bard|'
    r'public\s+llm|consumer[- ]grade\s+ai|'
    r'upload(?:ed|ing)?\s+to\s+(?:gpt|chatgpt|claude|gemini)|'
    r'google\s+colab|dropbox|google\s+drive\s+share'
    r')\b',
    re.IGNORECASE,
)

THIRD_PARTY_SHARE_PHRASES = re.compile(
    r'\b('
    r'third[- ]party\s+(?:vendor|cloud|processor)|'
    r'share(?:d|s|ing)?\s+with\s+(?:vendor|outside|external)|'
    r'external\s+data\s+(?:share|transfer|processor)'
    r')\b',
    re.IGNORECASE,
)

# Small-cell / mosaic risk cues in protocol text
MOSAIC_CUES = re.compile(
    r'\b('
    r'small\s+n|cell\s+size\s*[<=]\s*5|n\s*[<=]\s*5|'
    r'individual[- ]level\s+export|raw\s+identif|'
    r'cross[- ]link(?:ed|ing)?'
    r')\b',
    re.IGNORECASE,
)


def _count_matches(pattern: re.Pattern, text: str) -> int:
    return len(pattern.findall(text or ''))


def scan_text_for_ipi_signals(text: str) -> Dict[str, Any]:
    """
    Scan free text for IPI-like signals.

    Returns counts by category only (no raw matches) for FERPA-safe logging.
    """
    text = text or ''
    counts = {
        'email': _count_matches(EMAIL_RE, text),
        'ssn_shaped': _count_matches(SSN_RE, text),
        'phone': _count_matches(PHONE_RE, text),
        'student_id_shaped': _count_matches(STUDENT_ID_RE, text),
        'institutional_brand': _count_matches(INSTITUTION_RE, text),
        'cloud_ai_phrase': _count_matches(CLOUD_AI_PHRASES, text),
        'third_party_share_phrase': _count_matches(THIRD_PARTY_SHARE_PHRASES, text),
        'mosaic_cue': _count_matches(MOSAIC_CUES, text),
    }
    signal_categories = [k for k, v in counts.items() if v > 0]
    return {
        'has_ipi_like_signals': any(
            counts[k] > 0 for k in ('email', 'ssn_shaped', 'phone', 'student_id_shaped')
        ),
        'has_cloud_ai_risk': counts['cloud_ai_phrase'] > 0,
        'has_third_party_share_risk': counts['third_party_share_phrase'] > 0,
        'has_mosaic_cue': counts['mosaic_cue'] > 0,
        'counts': counts,
        'signal_categories': signal_categories,
    }


def join_fields(fields: Iterable[str]) -> str:
    """Join multiple protocol/export text fields for scanning."""
    parts: List[str] = []
    for f in fields:
        if f:
            parts.append(str(f))
    return '\n'.join(parts)
