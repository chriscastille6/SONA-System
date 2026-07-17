"""
FERPA prompt screening for IRB AI review.

Scans prompts for patterns that suggest identifiable student education records
before transmission to external AI providers.
"""
import re
from dataclasses import dataclass, field
from typing import List


STUDENT_ID_PATTERN = re.compile(
    r'\b(?:student\s*(?:id|#|number)|sid|banner\s*id)\s*[:#]?\s*[\w-]{4,}\b',
    re.IGNORECASE,
)

GRADE_CONTEXT_PATTERN = re.compile(
    r'\b(?:grade|gpa|credit(?:s)?\s*(?:earned|required|allocated)|'
    r'(?:score|mark)\s*(?:of|is|:)?\s*\d|enrolled\s+in|attendance\s+record|'
    r'no[- ]show|disciplinary|advising\s+note|assessment\s+result)\b',
    re.IGNORECASE,
)

NAME_LIKE_PATTERN = re.compile(
    r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',
)

ACADEMIC_CONTEXT_PATTERN = re.compile(
    r'\b(?:course|enrollment|transcript|ferpa|education\s+record|'
    r'participant\s+roster|prescreen(?:ing)?|signup|timeslot)\b',
    re.IGNORECASE,
)


@dataclass
class ScreeningResult:
    """Outcome of FERPA prompt screening."""

    allowed: bool
    risk_level: str  # none | low | medium | high
    flags: List[str] = field(default_factory=list)
    redacted_prompt: str = ''
    message: str = ''

    def to_metadata(self) -> dict:
        return {
            'allowed': self.allowed,
            'risk_level': self.risk_level,
            'flags': self.flags,
            'message': self.message,
        }


class FERPAPromptScreener:
    """Scan and optionally block/redact prompts containing FERPA-sensitive content."""

    def screen(self, prompt: str, provider: str) -> ScreeningResult:
        """
        Screen a prompt before AI API transmission.

        External providers (openai, anthropic, gemini) are blocked on high-risk
        patterns. Ollama (institutional) receives warnings but is allowed.
        """
        flags: List[str] = []
        institutional = provider == 'ollama'

        if STUDENT_ID_PATTERN.search(prompt):
            flags.append('student_id_pattern')

        has_grade_context = bool(GRADE_CONTEXT_PATTERN.search(prompt))
        has_name_like = bool(NAME_LIKE_PATTERN.search(prompt))
        has_academic_context = bool(ACADEMIC_CONTEXT_PATTERN.search(prompt))

        if has_grade_context:
            flags.append('academic_performance_context')

        if has_name_like and (has_grade_context or has_academic_context):
            flags.append('name_plus_academic_context')

        if has_academic_context and re.search(
            r'\b(?:ssn|social\s+security|date\s+of\s+birth|dob)\b', prompt, re.IGNORECASE
        ):
            flags.append('sensitive_demographic_in_academic_context')

        if not flags:
            return ScreeningResult(
                allowed=True,
                risk_level='none',
                redacted_prompt=prompt,
                message='No FERPA risk patterns detected.',
            )

        high_risk = (
            'student_id_pattern' in flags
            or 'name_plus_academic_context' in flags
            or 'sensitive_demographic_in_academic_context' in flags
        )
        medium_risk = 'academic_performance_context' in flags

        if high_risk:
            risk_level = 'high'
        elif medium_risk:
            risk_level = 'medium'
        else:
            risk_level = 'low'

        if high_risk and not institutional:
            return ScreeningResult(
                allowed=False,
                risk_level=risk_level,
                flags=flags,
                redacted_prompt=prompt,
                message=(
                    'Prompt blocked: potential FERPA-protected student data detected. '
                    'Use Ollama (institutional) or remove identifiable student information.'
                ),
            )

        redacted = self._redact(prompt)
        message = (
            'Prompt allowed with FERPA risk flags; prefer institutional Ollama provider.'
            if institutional
            else 'Prompt allowed after redaction; review for residual FERPA risk.'
        )
        return ScreeningResult(
            allowed=True,
            risk_level=risk_level,
            flags=flags,
            redacted_prompt=redacted,
            message=message,
        )

    def _redact(self, prompt: str) -> str:
        """Redact high-sensitivity patterns before external transmission."""
        redacted = STUDENT_ID_PATTERN.sub('[REDACTED_STUDENT_ID]', prompt)
        redacted = re.sub(
            r'\b(?:ssn|social\s+security)\s*[:#]?\s*[\d-]+\b',
            '[REDACTED_SSN]',
            redacted,
            flags=re.IGNORECASE,
        )
        return redacted
