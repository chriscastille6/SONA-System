#!/usr/bin/env python3
"""
Cursor beforeSubmitPrompt hook — block prompts that risk FERPA / La. R.S. 17:3914 /
Nicholls PPM §5.3.5 / JML 25-109 violations.

Scans prompt TEXT and on-disk image-path attachments only.

IMPORTANT LIMITATION:
  Pasted/attached images sent directly as vision attachments are NOT always in this
  payload. Those bytes can reach the server before any hook runs. Use
  scripts/ferpa_scan_image_before_upload.py on-device BEFORE attaching images.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
STUDENT_ID_RE = re.compile(
    r"\b(student\s*id|banner\s*id|n#)\b[:\s]*[A-Za-z0-9\-]+", re.I
)
INSTITUTION_RE = re.compile(r"nicholls|students\.nicholls\.edu", re.I)
STUDENT_DATA_RE = re.compile(
    r"\b(roster|grade(?:book)?|gpa|ssn|transcript|ferpa|education\s*record|"
    r"participant\s*(?:email|name|id)|student\s*(?:email|name|list))\b",
    re.I,
)
PUBLIC_AI_RE = re.compile(
    r"\b(chatgpt|openai|claude\.ai|gemini\.google|upload(?:ed|ing)?\s+to\s+"
    r"(?:gpt|chatgpt|claude|gemini))\b",
    re.I,
)
DEEPSEEK_RE = re.compile(r"\bdeep\s*seek\b", re.I)
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".tif", ".tiff", ".bmp"}

SCANNER = Path(__file__).resolve().parents[2] / "scripts" / "ferpa_scan_image_before_upload.py"

AUTHORITY = (
    "Authority: FERPA; La. R.S. 17:3914; Nicholls PPM §5.3.5 / IT Policies; "
    "Louisiana EO JML 25-109 §6; CITI data privacy."
)


def _block(message: str) -> dict:
    return {"continue": False, "user_message": f"{message} {AUTHORITY}"}


def _scan_text(prompt: str) -> str | None:
    if DEEPSEEK_RE.search(prompt):
        return (
            "Blocked: prompt references DeepSeek / prohibited foreign AI "
            "(JML 25-109 — not for Louisiana universities)."
        )
    if EMAIL_RE.search(prompt):
        return "Blocked: prompt appears to contain an email address (possible PII)."
    if SSN_RE.search(prompt):
        return "Blocked: prompt appears to contain an SSN-shaped value."
    if STUDENT_ID_RE.search(prompt):
        return "Blocked: prompt appears to reference a student/Banner ID."
    if INSTITUTION_RE.search(prompt) and STUDENT_DATA_RE.search(prompt):
        return (
            "Blocked: prompt appears to discuss institutional student data. "
            "Use synthetic/dummy examples only."
        )
    if PUBLIC_AI_RE.search(prompt) and STUDENT_DATA_RE.search(prompt):
        return (
            "Blocked: prompt appears to combine public/consumer AI with student/"
            "education-record data (JML 25-109 §6; La. R.S. 17:3914)."
        )
    return None


def _scan_image_attachment(path: Path) -> str | None:
    if not path.exists() or path.suffix.lower() not in IMAGE_SUFFIXES:
        return None
    if not SCANNER.exists():
        return (
            f"Blocked: image attachment {path.name} requires local pre-scan "
            f"(scripts/ferpa_scan_image_before_upload.py missing). "
            "Do not attach education-record screenshots; use synthetic text instead."
        )
    import subprocess

    proc = subprocess.run(
        [sys.executable, str(SCANNER), str(path), "--json"],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        detail = (proc.stdout or proc.stderr or "").strip()
        return (
            f"Blocked: image attachment failed local PII pre-scan ({path.name}). "
            f"{detail[:500]}"
        )
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        # Fail open on malformed hook input so we don't brick the IDE.
        json.dump({"continue": True}, sys.stdout)
        return 0

    prompt = str(payload.get("prompt") or "")
    reason = _scan_text(prompt)
    if reason:
        json.dump(_block(reason), sys.stdout)
        return 0

    for att in payload.get("attachments") or []:
        if not isinstance(att, dict):
            continue
        file_path = att.get("file_path")
        if not file_path:
            continue
        reason = _scan_image_attachment(Path(file_path))
        if reason:
            json.dump(_block(reason), sys.stdout)
            return 0

    json.dump({"continue": True}, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
