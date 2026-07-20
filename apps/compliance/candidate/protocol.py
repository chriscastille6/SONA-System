"""
CANDIDATE linking protocol — Python twin of wave1/js/candidate.js

Adapted from Sandnes, F. E. (2021). CANDIDATE: A tool for generating anonymous
participant-linking IDs in multi-session studies. PLOS ONE, 16(12), e0260569.

Use cases (DEVELOPMENT / offline analysis only unless IRB + campus IT approve):
- Regenerate a Candidate ID from synthetic test answers
- Join Wave 1 and Wave 2 response files on candidate_id
- Never store raw security answers alongside research data
"""

from __future__ import annotations

import hashlib
import json
import re
import zlib
from pathlib import Path
from typing import Any, Iterable, Mapping, MutableMapping, Sequence

DELIMITER = "|"
ID_LENGTH = 16
_NON_ALNUM = re.compile(r"[^a-z0-9]")


def normalize_answer(raw: Any) -> str:
    """Normalize a security-question answer for stable hashing."""
    if raw is None:
        return ""
    text = str(raw).strip().lower()
    text = re.sub(r"\s+", "", text)
    return _NON_ALNUM.sub("", text)


def compose_preimage(
    mother_maiden_initials: str,
    birth_day_of_month: str | int,
    childhood_street_initials: str,
) -> str:
    a = normalize_answer(mother_maiden_initials)
    b = normalize_answer(birth_day_of_month)
    c = normalize_answer(childhood_street_initials)
    if not a or not b or not c:
        raise ValueError("All three CANDIDATE security answers are required.")
    day = int(b)
    if day < 1 or day > 31:
        raise ValueError("Birth day of month must be an integer from 1 to 31.")
    day_norm = f"{day:02d}"
    return DELIMITER.join([a, day_norm, c])


def _djb2(text: str) -> int:
    h = 5381
    for ch in text:
        h = ((h << 5) + h) ^ ord(ch)
        h &= 0xFFFFFFFF
    return h


def generate_candidate_id(
    mother_maiden_initials: str,
    birth_day_of_month: str | int,
    childhood_street_initials: str,
) -> str:
    """
    Return a 16-character lowercase hex CANDIDATE Hash ID.

    Must match templates/projects/longitudinal-candidate/wave1/js/candidate.js
    """
    base = compose_preimage(
        mother_maiden_initials, birth_day_of_month, childhood_street_initials
    )
    reverse = base[::-1]
    enriched = (
        f"{base}{DELIMITER}{_djb2(base):x}"
        f"{DELIMITER}{zlib.crc32(reverse.encode('utf-8')) & 0xFFFFFFFF:x}"
    )
    digest = hashlib.sha256(enriched.encode("utf-8")).hexdigest()
    return digest[:ID_LENGTH]


def is_valid_candidate_id(candidate_id: str) -> bool:
    return bool(re.fullmatch(r"[a-f0-9]{16}", candidate_id or ""))


def merge_waves_by_candidate_id(
    wave1_records: Sequence[Mapping[str, Any]],
    wave2_records: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """
    Outer-join Wave 1 and Wave 2 on candidate_id only.

    Rejects any record that contains email or survey_code keys to enforce the
    privacy firewall during analysis.
    """
    _assert_no_bridge_fields(wave1_records)
    _assert_no_bridge_fields(wave2_records)

    w2_by_id: dict[str, Mapping[str, Any]] = {}
    for row in wave2_records:
        cid = str(row.get("candidate_id", ""))
        if not is_valid_candidate_id(cid):
            raise ValueError(f"Invalid Wave 2 candidate_id: {cid!r}")
        w2_by_id[cid] = row

    seen: set[str] = set()
    merged: list[dict[str, Any]] = []

    for row in wave1_records:
        cid = str(row.get("candidate_id", ""))
        if not is_valid_candidate_id(cid):
            raise ValueError(f"Invalid Wave 1 candidate_id: {cid!r}")
        seen.add(cid)
        out: dict[str, Any] = {
            "candidate_id": cid,
            "wave1": dict(row),
            "wave2": dict(w2_by_id[cid]) if cid in w2_by_id else None,
            "linked": cid in w2_by_id,
        }
        merged.append(out)

    for cid, row in w2_by_id.items():
        if cid not in seen:
            merged.append(
                {
                    "candidate_id": cid,
                    "wave1": None,
                    "wave2": dict(row),
                    "linked": False,
                }
            )
    return merged


_FORBIDDEN_KEYS = frozenset(
    {
        "email",
        "e_mail",
        "survey_code",
        "student_id",
        "name",
        "mother_maiden",
        "security_answers",
    }
)


def _assert_no_bridge_fields(records: Iterable[Mapping[str, Any]]) -> None:
    for row in records:
        keys = {str(k).lower() for k in row.keys()}
        bad = keys & _FORBIDDEN_KEYS
        if bad:
            raise ValueError(
                "Research records must not contain re-identification bridge "
                f"fields: {sorted(bad)}"
            )


def load_json_records(path: str | Path) -> list[MutableMapping[str, Any]]:
    """Load a JSON file containing one object or a list of objects."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return [data]
    raise TypeError("JSON root must be an object or array of objects.")
