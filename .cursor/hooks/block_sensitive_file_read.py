#!/usr/bin/env python3
"""
Cursor beforeReadFile hook — deny agent reads of identifiable local drops.

failClosed is set in hooks.json so crashes block the read.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BLOCK_PATH_PARTS = (
    "/data/raw/",
    "/data/identifiable/",
    "/data/local_only/",
    "/exports/identifiable/",
    "local_only_linkage_key",
    "step2_human_audit_sample.csv",
    "final_safe_synthetic_data.csv",
)

BLOCK_SUFFIX_IN_SENSITIVE_DIR = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".csv", ".xlsx"}
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        json.dump({"permission": "deny", "user_message": "Invalid hook payload."}, sys.stdout)
        return 0

    # Schema may use file_path or path depending on Cursor version.
    file_path = str(payload.get("file_path") or payload.get("path") or "")
    normalized = file_path.replace("\\", "/")
    lower = normalized.lower()

    for part in BLOCK_PATH_PARTS:
        if part.lower() in lower:
            json.dump(
                {
                    "permission": "deny",
                    "user_message": (
                        f"Blocked read of sensitive local artifact: {Path(file_path).name}. "
                        "Keep identifiable files out of AI context."
                    ),
                },
                sys.stdout,
            )
            return 0

    # Extra: any image under a path containing 'identifiable' or 'raw_student'
    if any(token in lower for token in ("/identifiable/", "raw_student", "ferpa_raw")):
        suffix = Path(normalized).suffix.lower()
        if suffix in BLOCK_SUFFIX_IN_SENSITIVE_DIR or suffix == "":
            json.dump(
                {
                    "permission": "deny",
                    "user_message": "Blocked read under identifiable/raw student path.",
                },
                sys.stdout,
            )
            return 0

    content = str(payload.get("content") or "")
    # Only scan small text-like contents (avoid huge binary dumps).
    if content and len(content) < 2_000_000 and "\x00" not in content[:1000]:
        if EMAIL_RE.search(content) or SSN_RE.search(content):
            json.dump(
                {
                    "permission": "deny",
                    "user_message": (
                        "Blocked file read: content looks like it contains email/SSN PII."
                    ),
                },
                sys.stdout,
            )
            return 0

    json.dump({"permission": "allow"}, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
