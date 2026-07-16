#!/usr/bin/env python3
"""
Cursor beforeSubmitPrompt hook — TEXT + on-disk image-path attachments only.

IMPORTANT LIMITATION:
  Pasted/attached images that Cursor sends directly as vision attachments are
  NOT included in this hook payload (attachments are typed file|rule only).
  Those bytes can reach the server before any hook runs. Use
  scripts/ferpa_scan_image_before_upload.py on-device BEFORE attaching images.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
STUDENT_ID_RE = re.compile(r"\b(student\s*id|banner\s*id|n#)\b[:\s]*[A-Za-z0-9\-]+", re.I)
INSTITUTION_RE = re.compile(r"nicholls|students\.nicholls\.edu", re.I)
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".tif", ".tiff", ".bmp"}

# Repo-relative scanner used when an attachment path points at an image file.
SCANNER = Path(__file__).resolve().parents[2] / "scripts" / "ferpa_scan_image_before_upload.py"


def _block(message: str) -> dict:
    return {"continue": False, "user_message": message}


def _scan_text(prompt: str) -> str | None:
    if EMAIL_RE.search(prompt):
        return "Blocked: prompt appears to contain an email address (possible PII)."
    if SSN_RE.search(prompt):
        return "Blocked: prompt appears to contain an SSN-shaped value."
    if STUDENT_ID_RE.search(prompt):
        return "Blocked: prompt appears to reference a student/Banner ID."
    if INSTITUTION_RE.search(prompt) and re.search(
        r"\b(roster|grade|gpa|ssn|student)\b", prompt, re.I
    ):
        return (
            "Blocked: prompt appears to discuss institutional student data. "
            "Use synthetic/dummy examples only."
        )
    return None


def _scan_image_attachment(path: Path) -> str | None:
    if not path.exists() or path.suffix.lower() not in IMAGE_SUFFIXES:
        return None
    if not SCANNER.exists():
        return (
            f"Blocked: image attachment {path.name} requires local pre-scan, but "
            f"scanner missing at {SCANNER}."
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
        # Fail open on malformed hook input so we don't brick the IDE; text/image
        # policy still applies on well-formed prompts.
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

    # Soft warning in allow path: pasted vision images are invisible to this hook.
    if re.search(r"\b(screenshot|roster|gradebook|canvas)\b", prompt, re.I):
        # Still allow text-only discussion; do not claim image bytes were scanned.
        pass

    json.dump({"continue": True}, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
