"""
FERPA in-flight screening before data leaves institutional control.

Combines Presidio PII detection, Nicholls-specific student signals, and an
allowlist for faculty/staff identifiers that are not FERPA concerns in this
workspace (e.g. Christopher Castille).

Use before:
  - Cursor prompts (via .cursor/hooks)
  - External AI API calls (OpenAI, Anthropic, Gemini)
  - Optional export / payload validation in Django views
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal, Sequence

import yaml

from config.presidio_utils import analyze_text, anonymize_text, is_presidio_available

Action = Literal["allow", "block"]

EXTERNAL_AI_PROVIDERS = frozenset({"openai", "anthropic", "gemini"})

# Strong student / education-record signals for Nicholls + this platform.
STUDENT_EMAIL_RE = re.compile(r"\b[\w.+-]+@my\.nicholls\.edu\b", re.IGNORECASE)
STUDENT_ID_RE = re.compile(r"\bN\d{7,9}\b", re.IGNORECASE)
ACADEMIC_CONTEXT_RE = re.compile(
    r"\b("
    r"student|students|enrollment|enrolled|grade|grades|gpa|transcript|"
    r"credit|credits|course|courses|section|roster|attendance|no[- ]show|"
    r"participant|participants|signup|signups|prescreen|ferpa|education record|"
    r"my\.nicholls\.edu|student_id|participant_id|prams id|secure participant"
    r")\b",
    re.IGNORECASE,
)
PII_ENTITY_TYPES = frozenset(
    {"PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "US_SSN", "US_DRIVER_LICENSE", "US_PASSPORT"}
)


class FerpaBlockedError(Exception):
    """Raised when content must not be sent to an external provider."""

    def __init__(self, verdict: "FerpaVerdict"):
        self.verdict = verdict
        super().__init__(verdict.summary())


@dataclass
class FerpaFinding:
    kind: str
    detail: str
    snippet: str = ""

    def to_dict(self) -> dict[str, str]:
        return {"kind": self.kind, "detail": self.detail, "snippet": self.snippet}


@dataclass
class FerpaVerdict:
    action: Action
    summary: str
    findings: list[FerpaFinding] = field(default_factory=list)
    content_hash: str = ""

    @property
    def blocked(self) -> bool:
        return self.action == "block"

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "summary": self.summary,
            "findings": [f.to_dict() for f in self.findings],
            "content_hash": self.content_hash,
        }


def _settings_value(name: str, default: Any) -> Any:
    try:
        from django.conf import settings

        return getattr(settings, name, default)
    except Exception:
        return default


def _default_allowlist_path() -> Path:
    return Path(__file__).resolve().parent / "ferpa_allowlist.yaml"


@lru_cache(maxsize=1)
def load_allowlist() -> dict[str, Any]:
    path = Path(_settings_value("FERPA_ALLOWLIST_PATH", str(_default_allowlist_path())))
    if not path.exists():
        return {"people": [], "ignore_patterns": []}
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return {
        "people": data.get("people") or [],
        "ignore_patterns": data.get("ignore_patterns") or [],
    }


def _collect_allowlist_literals() -> tuple[list[str], list[re.Pattern[str]]]:
    literals: list[str] = []
    patterns: list[re.Pattern[str]] = []

    for person in load_allowlist().get("people", []):
        for key in ("names", "emails", "phones", "tokens"):
            for value in person.get(key) or []:
                if value:
                    literals.append(str(value))
        label = person.get("label")
        if label:
            literals.append(str(label))

    for raw in load_allowlist().get("ignore_patterns") or []:
        if raw:
            patterns.append(re.compile(str(raw), re.IGNORECASE))

    # Longest first so multi-word names mask correctly.
    literals.sort(key=len, reverse=True)
    return literals, patterns


def mask_allowlisted_content(text: str) -> str:
    if not text:
        return text

    masked = text
    literals, ignore_patterns = _collect_allowlist_literals()

    for literal in literals:
        if not literal.strip():
            continue
        masked = re.sub(re.escape(literal), " ", masked, flags=re.IGNORECASE)

    for pattern in ignore_patterns:
        masked = pattern.sub(" ", masked)

    return masked


def _hash_content(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _snippet(text: str, start: int, end: int, radius: int = 40) -> str:
    left = max(0, start - radius)
    right = min(len(text), end + radius)
    return text[left:right].replace("\n", " ")


def _context_window(text: str, start: int, end: int, radius: int = 120) -> str:
    left = max(0, start - radius)
    right = min(len(text), end + radius)
    return text[left:right]


def _is_allowlisted_literal(value: str) -> bool:
    value_l = value.strip().lower()
    if not value_l:
        return False
    literals, _ = _collect_allowlist_literals()
    return any(value_l == lit.strip().lower() for lit in literals)


def screen_text(
    text: str,
    *,
    destination: Literal["internal", "external"] = "external",
    require_presidio: bool | None = None,
) -> FerpaVerdict:
    """
    Screen free text for FERPA-sensitive content.

    destination=external applies stricter blocking (default for outbound AI).
    """
    if not text or not str(text).strip():
        return FerpaVerdict(action="allow", summary="Empty content.", content_hash=_hash_content(text or ""))

    if not _settings_value("FERPA_GUARD_ENABLED", True):
        return FerpaVerdict(action="allow", summary="FERPA guard disabled.", content_hash=_hash_content(text))

    raw = str(text)
    masked = mask_allowlisted_content(raw)
    findings: list[FerpaFinding] = []

    for match in STUDENT_EMAIL_RE.finditer(raw):
        email = match.group(0)
        if _is_allowlisted_literal(email):
            continue
        findings.append(
            FerpaFinding(
                kind="student_email",
                detail="Nicholls student email address (@my.nicholls.edu)",
                snippet=email,
            )
        )

    for match in STUDENT_ID_RE.finditer(masked):
        findings.append(
            FerpaFinding(
                kind="student_id",
                detail="Possible Nicholls student ID (N-number)",
                snippet=match.group(0),
            )
        )

    if require_presidio is None:
        require_presidio = destination == "external"

    if is_presidio_available():
        hits = analyze_text(masked)
        for hit in hits:
            if hit.entity_type not in PII_ENTITY_TYPES:
                continue
            if _is_allowlisted_literal(hit.text):
                continue
            window = _context_window(masked, hit.start, hit.end)
            if hit.entity_type == "PERSON" and not ACADEMIC_CONTEXT_RE.search(window):
                continue
            findings.append(
                FerpaFinding(
                    kind=f"pii:{hit.entity_type.lower()}",
                    detail=f"Detected {hit.entity_type} near academic/participant context",
                    snippet=hit.text,
                )
            )
    elif require_presidio and ACADEMIC_CONTEXT_RE.search(masked):
        findings.append(
            FerpaFinding(
                kind="presidio_unavailable",
                detail="Presidio unavailable; academic context detected in outbound content",
                snippet=masked[:120],
            )
        )

    if ACADEMIC_CONTEXT_RE.search(masked) and re.search(
        r"\b(first|last|full)[-_ ]name\b|\bemail\b|\bphone\b|\baddress\b",
        masked,
        re.IGNORECASE,
    ):
        findings.append(
            FerpaFinding(
                kind="structured_pii_fields",
                detail="Academic context combined with direct identifier field names",
                snippet=masked[:160],
            )
        )

    # De-duplicate findings by kind+snippet
    deduped: list[FerpaFinding] = []
    seen: set[tuple[str, str]] = set()
    for item in findings:
        key = (item.kind, item.snippet.lower())
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)

    if deduped and destination == "external":
        return FerpaVerdict(
            action="block",
            summary=(
                f"Blocked: {len(deduped)} potential FERPA issue(s) detected before external transfer."
            ),
            findings=deduped,
            content_hash=_hash_content(raw),
        )

    if deduped:
        return FerpaVerdict(
            action="allow",
            summary=f"Internal-only review flagged {len(deduped)} item(s).",
            findings=deduped,
            content_hash=_hash_content(raw),
        )

    return FerpaVerdict(
        action="allow",
        summary="No FERPA issues detected.",
        content_hash=_hash_content(raw),
    )


def screen_payload(data: Any, **kwargs: Any) -> FerpaVerdict:
    return screen_text(json.dumps(data, default=str), **kwargs)


SYNTHETIC_OPT_IN_PREFIXES = (
    "USE_SYNTHETIC:",
    "[use-synthetic]",
    "[allow-synthetic]",
)


def strip_synthetic_opt_in(text: str) -> tuple[str, bool]:
    raw = str(text or "")
    stripped = raw.lstrip()
    for prefix in SYNTHETIC_OPT_IN_PREFIXES:
        if stripped.lower().startswith(prefix.lower()):
            remainder = stripped[len(prefix) :].lstrip()
            return remainder, True
    return raw, False


def synthesize_text(text: str) -> str:
    """
    Build a redacted/synthetic version safe to paste into external AI prompts.

    Uses Presidio token replacement plus Nicholls-specific substitutions.
    """
    if not text or not str(text).strip():
        return str(text or "")

    body, _ = strip_synthetic_opt_in(str(text))
    masked = mask_allowlisted_content(body)
    synthetic = anonymize_text(masked)
    synthetic = STUDENT_EMAIL_RE.sub("student@example.edu", synthetic)
    synthetic = STUDENT_ID_RE.sub("N00000000", synthetic)
    return synthetic.strip()


def synthesize_if_needed(text: str) -> tuple[str, FerpaVerdict]:
    """Return a synthetic version plus the post-synthesis screening verdict."""
    synthetic = synthesize_text(text)
    return synthetic, screen_text(synthetic, destination="external")


def assert_safe_for_external_transfer(text: str, *, context: str = "") -> FerpaVerdict:
    verdict = screen_text(text, destination="external")
    if verdict.blocked:
        prefix = f"{context}: " if context else ""
        verdict.summary = prefix + verdict.summary
        raise FerpaBlockedError(verdict)
    return verdict


def is_external_ai_provider(provider: str | None) -> bool:
    return (provider or "").lower() in EXTERNAL_AI_PROVIDERS


def provider_destination(provider: str | None) -> Literal["internal", "external"]:
    return "external" if is_external_ai_provider(provider) else "internal"
