#!/usr/bin/env python3
"""
Local release enforcement helpers for the FERPA de-id PoC.

ENFORCEMENT LAYERS (development-tier, on-device):
1) Outbound DLP scan — block cloud-candidate CSVs that still look identifiable.
2) Encrypted local linkage key — cut/keep map at rest; plaintext key file stays local.
3) Mandatory gate checks — refuse export without a prior human APPROVE attestation.

Production campuses should replace the local Fernet key file with a campus
secrets manager or HSM. This module does not claim leak-proof security.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from cryptography.fernet import Fernet

# Patterns that must not appear in a cloud-candidate release CSV.
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
INSTITUTION_RE = re.compile(r"nicholls", re.IGNORECASE)
ALLOWED_TOKENS = {"<PERSON>", "<EMAIL_ADDRESS>", "<US_SSN>"}

DEFAULT_TOKEN_COLUMNS = ("Name", "Email", "SSN")


def load_or_create_fernet(key_path: Path) -> Fernet:
    """
    Load a local Fernet key, or create one if missing.

    LIABILITY NOTE: The key file is local-only (gitignored / cursorignored).
    Losing it means the encrypted linkage map cannot be opened. Production
    should escrow this via campus secrets management — not ad-hoc email.
    """
    key_path = Path(key_path)
    if key_path.exists():
        key = key_path.read_bytes().strip()
    else:
        key = Fernet.generate_key()
        key_path.write_bytes(key + b"\n")
        try:
            key_path.chmod(0o600)
        except OSError:
            pass
    return Fernet(key)


def write_encrypted_json(payload: dict[str, Any], enc_path: Path, key_path: Path) -> Path:
    """Encrypt a JSON payload to disk; never write the plaintext sibling by default."""
    fernet = load_or_create_fernet(key_path)
    blob = json.dumps(payload, sort_keys=True).encode("utf-8")
    enc_path.write_bytes(fernet.encrypt(blob))
    try:
        enc_path.chmod(0o600)
    except OSError:
        pass
    return enc_path


def read_encrypted_json(enc_path: Path, key_path: Path) -> dict[str, Any]:
    """Decrypt a local linkage key for on-device cut/keep only."""
    fernet = load_or_create_fernet(key_path)
    return json.loads(fernet.decrypt(enc_path.read_bytes()).decode("utf-8"))


def scan_dataframe_for_outbound_leaks(
    df: pd.DataFrame,
    token_columns: tuple[str, ...] = DEFAULT_TOKEN_COLUMNS,
) -> dict[str, Any]:
    """
    Lightweight outbound DLP for cloud-candidate tables.

    Fails on: emails, SSN-shaped tokens, institutional brand strings, or
    clear-text values in columns that must remain redaction tokens.
    """
    findings: list[str] = []
    text = df.astype(str)

    # Whole-frame pattern scan (catches brand / emails hiding in any column).
    joined = "\n".join(text.to_numpy().ravel().tolist())
    if EMAIL_RE.search(joined):
        findings.append("EMAIL_PATTERN_DETECTED")
    if SSN_RE.search(joined):
        findings.append("SSN_PATTERN_DETECTED")
    if INSTITUTION_RE.search(joined):
        findings.append("INSTITUTIONAL_BRAND_DETECTED")

    for col in token_columns:
        if col not in df.columns:
            continue
        bad = sorted(
            {
                str(v)
                for v in df[col].dropna().unique().tolist()
                if str(v) not in ALLOWED_TOKENS
            }
        )
        if bad:
            findings.append(f"NON_TOKEN_VALUES_IN_{col}:{bad[:5]}")

    return {
        "event": "outbound_dlp_scan",
        "utc_timestamp": datetime.now(timezone.utc).isoformat(),
        "passed": len(findings) == 0,
        "findings": findings,
        "n_rows": int(len(df)),
        "n_cols": int(df.shape[1]),
    }


def require_human_approve_attestation(attestation_log: Path) -> dict[str, Any]:
    """Refuse export unless the attestation log contains at least one APPROVE."""
    if not attestation_log.exists():
        return {
            "passed": False,
            "reason": f"Missing attestation log: {attestation_log}",
        }
    approved = False
    last_approve: dict[str, Any] | None = None
    for line in attestation_log.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if rec.get("decision") == "APPROVE":
            approved = True
            last_approve = rec
    if not approved:
        return {"passed": False, "reason": "No APPROVE decision in attestation log"}
    return {
        "passed": True,
        "reason": None,
        "last_approve_netid": (last_approve or {}).get("auditor_netid"),
        "last_approve_utc": (last_approve or {}).get("utc_timestamp"),
    }


def refuse_if_plaintext_linkage_key_present(work_dir: Path) -> dict[str, Any]:
    """
    Block release packaging when a plaintext linkage key is sitting in CWD.

    The encrypted key is allowed locally; plaintext JSON next to the cloud CSV
    is treated as a packaging failure (would undo dilution if uploaded together).
    """
    plaintext = work_dir / "local_only_linkage_key.json"
    present = plaintext.exists()
    return {
        "passed": not present,
        "plaintext_path": str(plaintext.resolve()) if present else None,
        "reason": (
            "Plaintext local_only_linkage_key.json present beside release artifacts"
            if present
            else None
        ),
    }


def enforce_release_gates(
    *,
    df: pd.DataFrame,
    attestation_log: Path,
    work_dir: Path,
    report_path: Path,
) -> dict[str, Any]:
    """Run mandatory enforcement checks; exit non-zero on failure."""
    dlp = scan_dataframe_for_outbound_leaks(df)
    attest = require_human_approve_attestation(attestation_log)
    plaintext = refuse_if_plaintext_linkage_key_present(work_dir)
    report = {
        "event": "release_enforcement",
        "utc_timestamp": datetime.now(timezone.utc).isoformat(),
        "dlp": dlp,
        "attestation": attest,
        "plaintext_linkage_key_check": plaintext,
        "passed": bool(dlp["passed"] and attest["passed"] and plaintext["passed"]),
    }
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not report["passed"]:
        print("[ENFORCEMENT] RELEASE BLOCKED. See", report_path.resolve())
        print(json.dumps(report, indent=2, sort_keys=True))
        sys.exit(3)
    print("[ENFORCEMENT] Outbound DLP + attestation + plaintext-key checks PASSED.")
    print(f"[ENFORCEMENT] Report -> {report_path.resolve()}")
    return report


def main_cli(argv: list[str] | None = None) -> int:
    """CLI: python scripts/ferpa_release_enforcement.py scan path/to/file.csv"""
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) < 2 or args[0] != "scan":
        print("Usage: python scripts/ferpa_release_enforcement.py scan <file.csv>")
        return 2
    path = Path(args[1])
    df = pd.read_csv(path)
    result = scan_dataframe_for_outbound_leaks(df)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main_cli())
