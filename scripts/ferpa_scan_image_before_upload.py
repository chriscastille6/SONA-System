#!/usr/bin/env python3
"""
ON-DEVICE image PII pre-scan — run BEFORE attaching a screenshot to Cursor.

This is the control that can actually execute before image bytes touch a
Cursor/cloud server. Cursor rules/hooks cannot OCR pasted vision attachments
prior to upload; this script is the pre-flight gate.

Usage:
  python scripts/ferpa_scan_image_before_upload.py path/to/screenshot.png
  python scripts/ferpa_scan_image_before_upload.py path/to/screenshot.png --json

Exit codes:
  0 = PASS (no high-confidence PII patterns in OCR/text layer)
  1 = FAIL (PII-like content detected, or OCR unavailable without attestation)
  2 = usage / file error

Optional OCR: install tesseract + pytesseract for text extraction.
Without OCR, the scan FAIL-CLOSED unless --i-attest-no-education-record-pii
is supplied (for clearly synthetic/dummy images only).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
PHONE_RE = re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b")
INSTITUTION_RE = re.compile(r"nicholls|students\.nicholls\.edu|banner\s*id|\bstudent\s*id\b", re.I)
NAME_LABEL_RE = re.compile(
    r"\b(name|student|email|ssn|dob|date of birth|grade|gpa)\b\s*[:#]", re.I
)


def extract_text(path: Path) -> tuple[str, str]:
    """Return (text, engine_name). engine_name is 'none' if unavailable."""
    try:
        from PIL import Image  # type: ignore
    except ImportError:
        return "", "none"

    try:
        import pytesseract  # type: ignore

        img = Image.open(path)
        text = pytesseract.image_to_string(img) or ""
        return text, "pytesseract"
    except Exception:
        return "", "none"


def scan_text(text: str) -> list[str]:
    findings: list[str] = []
    if EMAIL_RE.search(text):
        findings.append("EMAIL_PATTERN")
    if SSN_RE.search(text):
        findings.append("SSN_PATTERN")
    if PHONE_RE.search(text):
        findings.append("PHONE_PATTERN")
    if INSTITUTION_RE.search(text):
        findings.append("INSTITUTION_OR_STUDENT_ID_PATTERN")
    if NAME_LABEL_RE.search(text):
        findings.append("PII_FIELD_LABEL")
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pre-upload image PII scan (local only)")
    parser.add_argument("image", type=Path, help="Path to image file")
    parser.add_argument("--json", action="store_true", help="Machine-readable output")
    parser.add_argument(
        "--i-attest-no-education-record-pii",
        action="store_true",
        help=(
            "Required to PASS when OCR is unavailable. Affirms the image contains "
            "no education-record PII (synthetic/dummy UI only)."
        ),
    )
    args = parser.parse_args(argv)

    path: Path = args.image
    if not path.is_file():
        msg = {"passed": False, "error": f"File not found: {path}"}
        print(json.dumps(msg) if args.json else msg["error"])
        return 2

    text, engine = extract_text(path)
    findings = scan_text(text) if text.strip() else []

    if engine == "none" and not args.i_attest_no_education_record_pii:
        result = {
            "passed": False,
            "engine": engine,
            "findings": ["OCR_UNAVAILABLE_FAIL_CLOSED"],
            "path": str(path.resolve()),
            "advice": (
                "Install tesseract + pytesseract for OCR, or re-run with "
                "--i-attest-no-education-record-pii only for synthetic/dummy images."
            ),
        }
        print(json.dumps(result, indent=2) if args.json else (
            "FAIL: OCR unavailable. Install tesseract/pytesseract, or attest "
            "synthetic-only with --i-attest-no-education-record-pii."
        ))
        return 1

    passed = len(findings) == 0
    result = {
        "passed": passed,
        "engine": engine,
        "findings": findings,
        "path": str(path.resolve()),
        "attested_no_pii": bool(args.i_attest_no_education_record_pii),
        "advice": (
            None
            if passed
            else "Redact locally and re-scan. Do not attach this image to Cursor."
        ),
    }

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        status = "PASS" if passed else "FAIL"
        print(f"{status}: {path}")
        print(f"  OCR engine: {engine}")
        if findings:
            print("  Findings:", ", ".join(findings))
        if result["advice"]:
            print(" ", result["advice"])
        if passed:
            print("  Safe to consider attaching only if you also trust visual non-text PII.")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
