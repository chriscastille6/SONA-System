"""
Shared Microsoft Presidio helpers for PII detection and anonymization.

Use from Django views/tasks, Celery jobs, management commands, and scripts:

    from config.presidio_utils import analyze_text, anonymize_text, deep_scan

Engines are lazy-loaded on first use so Django startup stays fast.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from functools import lru_cache
from typing import Any, Iterable, Mapping, Sequence

DEFAULT_LANGUAGE = "en"
DEFAULT_SCORE_THRESHOLD = 0.35


@dataclass(frozen=True)
class PIIHit:
    entity_type: str
    start: int
    end: int
    score: float
    text: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _settings_value(name: str, default: Any) -> Any:
    try:
        from django.conf import settings

        return getattr(settings, name, default)
    except Exception:
        return default


@lru_cache(maxsize=1)
def get_analyzer():
    from presidio_analyzer import AnalyzerEngine

    return AnalyzerEngine()


@lru_cache(maxsize=1)
def get_anonymizer():
    from presidio_anonymizer import AnonymizerEngine

    return AnonymizerEngine()


def is_presidio_available() -> bool:
    try:
        get_analyzer()
        get_anonymizer()
        return True
    except Exception:
        return False


def analyze_text(
    text: str,
    *,
    language: str | None = None,
    entities: Sequence[str] | None = None,
    score_threshold: float | None = None,
) -> list[PIIHit]:
    if not text or not str(text).strip():
        return []

    language = language or _settings_value("PRESIDIO_LANGUAGE", DEFAULT_LANGUAGE)
    if score_threshold is None:
        score_threshold = _settings_value("PRESIDIO_SCORE_THRESHOLD", DEFAULT_SCORE_THRESHOLD)

    analyzer = get_analyzer()
    results = analyzer.analyze(
        text=str(text),
        language=language,
        entities=list(entities) if entities else None,
        score_threshold=score_threshold,
    )
    return [
        PIIHit(
            entity_type=r.entity_type,
            start=r.start,
            end=r.end,
            score=r.score,
            text=str(text)[r.start : r.end],
        )
        for r in results
    ]


def anonymize_text(
    text: str,
    *,
    language: str | None = None,
    entities: Sequence[str] | None = None,
    score_threshold: float | None = None,
) -> str:
    if text is None:
        return ""
    if not str(text).strip():
        return str(text)

    language = language or _settings_value("PRESIDIO_LANGUAGE", DEFAULT_LANGUAGE)
    if score_threshold is None:
        score_threshold = _settings_value("PRESIDIO_SCORE_THRESHOLD", DEFAULT_SCORE_THRESHOLD)

    analyzer = get_analyzer()
    anonymizer = get_anonymizer()
    results = analyzer.analyze(
        text=str(text),
        language=language,
        entities=list(entities) if entities else None,
        score_threshold=score_threshold,
    )
    if not results:
        return str(text)
    return anonymizer.anonymize(text=str(text), analyzer_results=results).text


def scan_text(
    text: str,
    *,
    language: str | None = None,
    entities: Sequence[str] | None = None,
    score_threshold: float | None = None,
) -> dict[str, Any]:
    hits = analyze_text(
        text,
        language=language,
        entities=entities,
        score_threshold=score_threshold,
    )
    return {
        "has_pii": bool(hits),
        "hit_count": len(hits),
        "entity_types": sorted({h.entity_type for h in hits}),
        "hits": [h.to_dict() for h in hits],
    }


def _walk_strings(value: Any, path: str = "") -> Iterable[tuple[str, str]]:
    if isinstance(value, str):
        yield path or "$", value
    elif isinstance(value, Mapping):
        for key, nested in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            yield from _walk_strings(nested, child_path)
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            child_path = f"{path}[{index}]"
            yield from _walk_strings(nested, child_path)


def deep_scan(
    data: Any,
    *,
    language: str | None = None,
    entities: Sequence[str] | None = None,
    score_threshold: float | None = None,
) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    for path, text in _walk_strings(data):
        scan = scan_text(
            text,
            language=language,
            entities=entities,
            score_threshold=score_threshold,
        )
        if scan["has_pii"]:
            findings.append({"path": path, **scan})

    return {
        "has_pii": bool(findings),
        "field_count": len(findings),
        "findings": findings,
    }


def deep_anonymize(
    data: Any,
    *,
    language: str | None = None,
    entities: Sequence[str] | None = None,
    score_threshold: float | None = None,
) -> Any:
    if isinstance(data, str):
        return anonymize_text(
            data,
            language=language,
            entities=entities,
            score_threshold=score_threshold,
        )
    if isinstance(data, Mapping):
        return {
            key: deep_anonymize(
                value,
                language=language,
                entities=entities,
                score_threshold=score_threshold,
            )
            for key, value in data.items()
        }
    if isinstance(data, list):
        return [
            deep_anonymize(
                item,
                language=language,
                entities=entities,
                score_threshold=score_threshold,
            )
            for item in data
        ]
    return data


def scan_json_text(
    raw: str,
    *,
    language: str | None = None,
    entities: Sequence[str] | None = None,
    score_threshold: float | None = None,
) -> dict[str, Any]:
    parsed = json.loads(raw)
    return deep_scan(
        parsed,
        language=language,
        entities=entities,
        score_threshold=score_threshold,
    )
