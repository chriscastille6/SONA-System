#!/usr/bin/env python3
"""
=============================================================================
LOCAL FERPA DE-IDENTIFICATION + SYNTHETIC DATA PoC
=============================================================================
Audience: Chief IT Security Administrator / University Privacy Officer

PURPOSE
-------
Demonstrate a 100% local, air-gap-friendly pipeline that:
  1) Ingests sensitive educational records (PoC uses synthetic dummy rows only)
  2) Redacts direct identifiers with Microsoft Presidio (local NLP models)
  3) Strips institutional brand strings (university name)
  4) HARD-STOPS for a human security audit before any synthesis
  5) Generates synthetic data with SDV (local Gaussian Copula)
  6) Removes any exact 1:1 "clone" rows (overfitting / re-identification risk)
  7) Applies a mosaic-attack gate (quasi-identifier k-map + DCR near-match cull)
  8) Dilutes with distractor variables + distractor cases; keeps a LOCAL-ONLY
     linkage key so analysts know what to cut/keep on-device
  9) Exports only the diluted file (never the linkage key) for cloud candidacy

LEGAL / FERPA LIABILITY NOTES (for reviewers)
---------------------------------------------
- This PoC NEVER ships real student education records. Step 0 creates fake data
  solely so IT can exercise the controls without touching FERPA-covered PII.
- Automated redaction is necessary but NOT sufficient under FERPA / institutional
  policy. The mandatory human audit gate (Step 2) creates an explicit approval
  artifact before synthesis proceeds — documenting that a named official
  (full name + NetID) attested to legal de-identification, with UTC time
  and a SHA-256 hash of the scrubbed audit CSV bound to that decision.
- Synthetic data derived from scrubbed records is still treated as sensitive
  until clone-checked. Exact row matches can leak training examples (membership
  inference / overfitting), so Step 4 deletes clones before export.
- Mosaic / linkage risk remains after direct-identifier removal: an attacker can
  join quasi-identifiers (e.g., GPA + Personality_Score) to auxiliary files.
  Step 5 therefore (a) measures scrubbed QID equivalence-class sizes (k-map),
  (b) drops synthetic rows whose QID bin matches a singleton scrubbed class,
  and (c) drops synthetic rows whose Distance to Closest Record (DCR) is below
  a configured floor. Export is blocked if too few rows survive.
- IMPORTANT: DCR distance == 0 would mean a clone (BAD). Step 6 drives DCR
  *violations* to zero on analytic rows, then dilutes the release with
  distractor variables AND distractor cases. A true linking key is retained
  ONLY on-device so local analysts know what to cut/keep; that key must never
  be uploaded. The cloud-facing file is the diluted table without role labels.
- No network calls are required by this script's core libraries when models are
  already installed locally. Do not point Presidio/SDV at remote services.

ENVIRONMENT (DEVELOPMENT TIER)
------------------------------
Synthetic dummy data only. Do not substitute real student Canvas exports,
registrar extracts, or IRB participant files without a separate PRODUCTION
REVIEW and explicit IRB / FERPA authorization.

Usage
-----
    python3 scripts/ferpa_local_deid_synthesis_poc.py

Human audit gate:
    Enter auditor full name, NetID, then type APPROVE or REJECT.
    Each decision is appended to step2_human_audit_attestation.jsonl.
=============================================================================
"""

from __future__ import annotations

import getpass
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
from faker import Faker

# ---------------------------------------------------------------------------
# Local Presidio engines (Microsoft Presidio runs entirely on-device).
# LIABILITY MITIGATION: Direct identifiers (name, email, SSN) are detected
# and replaced with entity placeholders so raw PII never reaches synthesis
# or any subsequent cloud upload path.
# ---------------------------------------------------------------------------
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

# ---------------------------------------------------------------------------
# Local SDV synthesizer (Gaussian Copula). No cloud telemetry / upload.
# LIABILITY MITIGATION: We synthesize from scrubbed rows only AFTER human
# approval, so the generative model never trains on unredacted education
# records inside this PoC workflow.
# ---------------------------------------------------------------------------
from sdv.metadata import Metadata
from sdv.single_table import GaussianCopulaSynthesizer


# ---------------------------------------------------------------------------
# Paths — all artifacts stay on the local filesystem under this script's CWD.
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
WORK_DIR = Path.cwd()
AUDIT_CSV = WORK_DIR / "step2_human_audit_sample.csv"
ATTESTATION_LOG = WORK_DIR / "step2_human_audit_attestation.jsonl"
MOSAIC_REPORT = WORK_DIR / "step5_mosaic_risk_report.json"
DISTRACTOR_REPORT = WORK_DIR / "step6_distractor_protocol_report.json"
LOCAL_LINKAGE_KEY = WORK_DIR / "local_only_linkage_key.json"
FINAL_CSV = WORK_DIR / "final_safe_synthetic_data.csv"

# ---------------------------------------------------------------------------
# Mosaic-attack / linkage-risk controls (quasi-identifiers).
# Direct identifiers are already tokenized; these columns can still re-identify
# a student when joined to an external roster, gradebook, or survey file.
# ---------------------------------------------------------------------------
QID_COLUMNS: tuple[str, ...] = ("GPA", "Personality_Score")
# Equivalence-class bin widths for k-map style uniqueness checks.
QID_BIN_WIDTHS: dict[str, float] = {
    "GPA": 0.2,  # e.g., 3.41 -> 3.4
    "Personality_Score": 10.0,  # e.g., 72.4 -> 70.0
}
# Auditor-facing k-map threshold (reported even when not used for drops).
K_ANONYMITY_MIN = 5
# Drop synthetic rows that land in scrubbed bins with fewer than this many
# real rows. Default 2 = singling-out / singleton mosaic cells (highest risk).
# Classes with 2 <= size < K_ANONYMITY_MIN are reported but not auto-dropped,
# because small PoC cohorts are often entirely "rare" at k=5.
RARE_BIN_DROP_MAX_SIZE = 1
# Min Euclidean DCR on min-max-normalized QID space. Below this => near-clone.
DCR_MIN_THRESHOLD = 0.05
# Hard-stop: refuse export if mosaic filtering leaves fewer than this many rows.
MIN_SAFE_EXPORT_ROWS = 50
# Generate extra synthetic candidates so DCR/rare-bin culls can still fill export.
SYNTHETIC_OVERSAMPLE_FACTOR = 10

# ---------------------------------------------------------------------------
# Distractor dilution (variables + cases) + local-only linkage key
# Goal: DCR *violations* == 0 for every cloud-facing row; on-device key says
# what to cut/keep. DCR distance == 0 remains forbidden (clone).
# ---------------------------------------------------------------------------
# Labeled distractor *variables* keep the PoC honest for IT/IRB review.
# Distractor *cases* are extra rows mixed into the export. Production policy
# may covertly name decoy columns; privacy property is independence + key exile.
DISTRACTOR_COLUMNS: tuple[str, ...] = (
    "Distractor_Focus_Index",
    "Distractor_Teamwork_Index",
    "Distractor_Sleep_Proxy",
    "Distractor_Campus_Engagement",
)
DISTRACTOR_VALUE_RANGES: dict[str, tuple[float, float]] = {
    "Distractor_Focus_Index": (0.0, 100.0),
    "Distractor_Teamwork_Index": (0.0, 100.0),
    "Distractor_Sleep_Proxy": (3.0, 10.0),
    "Distractor_Campus_Engagement": (0.0, 50.0),
}
DISTRACTOR_MAX_RESAMPLE_ATTEMPTS = 25
DISTRACTOR_CASE_DRAW_MULTIPLIER = 20  # draw extras, keep those passing DCR floor

# Institutional brand strings to erase (hardcoded per PoC requirements).
# LIABILITY MITIGATION: Even after PII redaction, institutional identifiers can
# create brand / reputational risk and aid re-identification via known cohorts.
INSTITUTION_PATTERNS: Iterable[str] = (
    "Nicholls State University",
    "Nicholls",
)
INSTITUTION_REPLACEMENT = "Generic Earth University"

# Presidio entity types required by the PoC (direct identifiers).
PII_ENTITIES = ["PERSON", "EMAIL_ADDRESS", "US_SSN"]

N_ROWS = 100
RANDOM_SEED = 42
# Extra decoy rows mixed into the export (match analytic cohort => ~50/50 dilute).
DISTRACTOR_CASE_COUNT = N_ROWS

# Deliberately fictional "students" for IT demos — Disney characters only.
# FERPA RISK MITIGATION: Zero overlap with real registrant / SONA identities.
DISNEY_CHARACTER_NAMES: tuple[str, ...] = (
    "Mickey Mouse",
    "Minnie Mouse",
    "Donald Duck",
    "Daisy Duck",
    "Goofy Goof",
    "Pluto Dog",
    "Snow White",
    "Cinderella Tremaine",
    "Aurora Rose",
    "Belle Beast",
    "Ariel Mermaid",
    "Jasmine Agrabah",
    "Pocahontas Powhatan",
    "Mulan Fa",
    "Tiana Palace",
    "Rapunzel Corona",
    "Moana Waialiki",
    "Raya Kumandra",
    "Elsa Arendelle",
    "Anna Arendelle",
    "Olaf Snowman",
    "Kristoff Bjorgman",
    "Simba Pride",
    "Nala Pride",
    "Timon Meerkat",
    "Pumbaa Warthog",
    "Aladdin Street",
    "Genie Lamp",
    "Jafar Vizier",
    "Abu Monkey",
    "Peter Pan",
    "Tinker Bell",
    "Wendy Darling",
    "Captain Hook",
    "Woody Pride",
    "Buzz Lightyear",
    "Jessie Yodeling",
    "Bo Peep",
    "Rex Dinosaur",
    "Hamm Piggy",
    "Sulley Sullivan",
    "Mike Wazowski",
    "Boo Randall",
    "Remy Ratatouille",
    "Linguini Gusteau",
    "Wall-E Robot",
    "Eve Probe",
    "Stitch Experiment",
    "Lilo Pelekai",
    "Nemo Clownfish",
    "Dory Blue",
    "Marlin Clownfish",
    "Lightning McQueen",
    "Mater Tow",
    "Sally Carrera",
    "Merida DunBroch",
    "Hiro Hamada",
    "Baymax Care",
    "Judy Hopps",
    "Nick Wilde",
    "Miguel Rivera",
    "Hector Rivera",
    "Mirabel Madrigal",
    "Isabela Madrigal",
    "Luisa Madrigal",
    "Bruno Madrigal",
    "Encanto Alma",
    "Asha Rosas",
    "Star Wish",
    "Maui Demigod",
    "Heihei Rooster",
    "Pua Pig",
    "Quasimodo Bell",
    "Esmeralda NotreDame",
    "Phoebus Captain",
    "Hercules Hero",
    "Megara Thebes",
    "Philoctetes Trainer",
    "Hades Underworld",
    "Mushu Dragon",
    "Cri-Kee Cricket",
    "Shang Li",
    "Kuzco Emperor",
    "Pacha Village",
    "Yzma Palace",
    "Kronk Spinach",
    "Robin Hood",
    "Maid Marian",
    "Little John",
    "Baloo Bear",
    "Mowgli Man-Cub",
    "Bagheera Panther",
    "Dumbo Elephant",
    "Bambi Deer",
    "Thumper Rabbit",
    "Flower Skunk",
    "Pinocchio Puppet",
    "Jiminy Cricket",
    "Geppetto Woodcarver",
    "Beast Castle",
    "Gaston Hunter",
)


def generate_dummy_student_data(n_rows: int = N_ROWS, seed: int = RANDOM_SEED) -> pd.DataFrame:
    """
    Step 0 — Generate 100 rows of FAKE student data for PoC testing only.

    FERPA RISK MITIGATION:
    - Names are Disney characters (obviously non-student). Emails/SSNs are
      Faker-synthetic. No real education records.
    - University_Name is set to "Nicholls State University" so Step 1 can
      prove institutional anonymization works end-to-end.
    - Reviewers: replace this function with a local CSV loader ONLY after
      PRODUCTION REVIEW + IRB/FERPA authorization. Never commit real PII.
    """
    fake = Faker()
    Faker.seed(seed)

    if n_rows > len(DISNEY_CHARACTER_NAMES):
        raise ValueError(
            f"PoC supports at most {len(DISNEY_CHARACTER_NAMES)} Disney-named "
            f"dummy rows; requested {n_rows}."
        )

    rows = []
    for i in range(n_rows):
        name = DISNEY_CHARACTER_NAMES[i]
        # Institutional-looking fake mailbox so Presidio EMAIL_ADDRESS fires
        # on a Nicholls-style domain without using any real student address.
        local_part = re.sub(r"[^a-z0-9]+", ".", name.lower()).strip(".")
        email = f"{local_part}@students.nicholls.edu"
        # Deterministic-ish fake SSN format for Presidio US_SSN detection.
        # Still synthetic — not a real Social Security Number.
        ssn = fake.ssn()
        rows.append(
            {
                "Name": name,
                "Email": email,
                "SSN": ssn,
                "GPA": round(fake.pyfloat(min_value=2.0, max_value=4.0, right_digits=2), 2),
                "Personality_Score": round(
                    fake.pyfloat(min_value=1.0, max_value=100.0, right_digits=1), 1
                ),
                "University_Name": "Nicholls State University",
            }
        )

    df = pd.DataFrame(rows)
    print(f"[Step 0] Generated {len(df)} FAKE Disney-named rows (PoC / DEVELOPMENT tier only).")
    print("         No real education records are present in this dataframe.")
    return df


def _anonymize_text(text: str, analyzer: AnalyzerEngine, anonymizer: AnonymizerEngine) -> str:
    """Run Presidio analyze + anonymize on a single string cell."""
    if text is None or (isinstance(text, float) and pd.isna(text)):
        return text
    value = str(text)
    results = analyzer.analyze(text=value, entities=PII_ENTITIES, language="en")
    if not results:
        return value
    anonymized = anonymizer.anonymize(
        text=value,
        analyzer_results=results,
        # Replace with entity-type tokens (e.g., <PERSON>) rather than hashes
        # so auditors can visually confirm which identifier class was removed.
        operators={
            "DEFAULT": OperatorConfig("replace", {"new_value": None}),
            "PERSON": OperatorConfig("replace", {"new_value": "<PERSON>"}),
            "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<EMAIL_ADDRESS>"}),
            "US_SSN": OperatorConfig("replace", {"new_value": "<US_SSN>"}),
        },
    )
    return anonymized.text


def redact_direct_pii(df: pd.DataFrame) -> pd.DataFrame:
    """
    Step 1a — Direct PII redaction via Microsoft Presidio (local).

    FERPA / LEGAL LIABILITY MITIGATION:
    - Targets PERSON, EMAIL_ADDRESS, and US_SSN — classic direct identifiers
      that alone can constitute education-record PII under FERPA.
    - Presidio Analyzer + Anonymizer run locally (spaCy model on disk).
      No third-party cloud DLP API is invoked by this function.
    - Output retains structural columns for synthesis but strips clear-text PII.
    - DEFENSE IN DEPTH: Known PII columns (Name / Email / SSN) are then
      force-tokenized. NLP detectors can miss edge cases (titles, uncommon
      names); schema-aware overwrite closes that gap before the human audit.
    """
    print("[Step 1a] Loading local Presidio Analyzer / Anonymizer engines...")
    analyzer = AnalyzerEngine()
    anonymizer = AnonymizerEngine()

    scrubbed = df.copy()
    # Apply Presidio to all object (string) columns. Numeric GPA / scores are
    # quasi-identifiers at most and are left for the human auditor + SDV stage.
    text_columns = [c for c in scrubbed.columns if scrubbed[c].dtype == object]
    for col in text_columns:
        scrubbed[col] = scrubbed[col].map(
            lambda cell: _anonymize_text(cell, analyzer, anonymizer)
        )

    # Schema-aware overwrite: these columns are definitionally direct identifiers
    # in this PoC schema. Force-tokenizing them prevents residual clear-text PII
    # (e.g., names Presidio partially missed) from reaching the audit CSV.
    column_token_map = {
        "Name": "<PERSON>",
        "Email": "<EMAIL_ADDRESS>",
        "SSN": "<US_SSN>",
    }
    for col, token in column_token_map.items():
        if col in scrubbed.columns:
            scrubbed[col] = token

    print(
        f"[Step 1a] Presidio redacted entities {PII_ENTITIES} across "
        f"{len(text_columns)} text column(s): {text_columns}"
    )
    print(
        "[Step 1a] Defense-in-depth: forced tokenization of columns "
        f"{list(column_token_map.keys())}."
    )
    return scrubbed


def anonymize_institution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Step 1b — Hardcoded institutional brand removal.

    INSTITUTIONAL / BRAND RISK MITIGATION:
    - Replaces "Nicholls State University" and "Nicholls" with
      "Generic Earth University" everywhere in the dataframe.
    - Prevents institutional fingerprinting even if a leaked synthetic file
      reaches a public or vendor environment.
    - Runs AFTER Presidio so leftover brand strings in free text are also wiped.
    """
    scrubbed = df.copy()
    # Longest phrases first so "Nicholls State University" is replaced before
    # the shorter token "Nicholls" (avoids partial double-rewrites).
    patterns = sorted(INSTITUTION_PATTERNS, key=len, reverse=True)

    def _replace_brands(value):
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return value
        if not isinstance(value, str):
            return value
        out = value
        for pattern in patterns:
            out = re.sub(re.escape(pattern), INSTITUTION_REPLACEMENT, out, flags=re.IGNORECASE)
        return out

    for col in scrubbed.columns:
        if scrubbed[col].dtype == object:
            scrubbed[col] = scrubbed[col].map(_replace_brands)

    print(
        f"[Step 1b] Institutional strings {list(INSTITUTION_PATTERNS)} -> "
        f"'{INSTITUTION_REPLACEMENT}'."
    )
    return scrubbed


def _sha256_file(path: Path) -> str:
    """Content hash of the audit CSV — binds the sign-off to exact file bytes."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _os_session_user() -> str:
    """Best-effort local OS account (not student PII) for workstation attribution."""
    try:
        return getpass.getuser()
    except Exception:
        return "UNKNOWN"


def write_attestation_record(
    *,
    auditor_name: str,
    auditor_netid: str,
    decision: str,
    row_count: int,
) -> Path:
    """
    Append a durable local attestation record (JSON Lines).

    LEGAL / IT ACCOUNTABILITY MITIGATION:
    - Records WHO signed off (name + NetID), WHEN (UTC ISO-8601), WHAT they
      decided (APPROVE/REJECT), and WHICH scrubbed file they reviewed
      (path + SHA-256). This is the compliance artifact IT can retain.
    - Does NOT log any student row contents — only a hash of the scrubbed
      audit CSV — so the attestation log itself stays free of education-record
      payloads while still proving file integrity at sign-off time.
    - Append-only JSONL preserves prior decisions if the gate is re-run.
    """
    record = {
        "event": "human_deidentification_attestation",
        "utc_timestamp": datetime.now(timezone.utc).isoformat(),
        "auditor_full_name": auditor_name,
        "auditor_netid": auditor_netid,
        "os_session_user": _os_session_user(),
        "decision": decision,
        "audit_csv_path": str(AUDIT_CSV.resolve()),
        "audit_csv_sha256": _sha256_file(AUDIT_CSV),
        "audit_row_count": row_count,
        "script": str(Path(__file__).resolve()),
    }
    with ATTESTATION_LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    print(f"[Step 2] Attestation logged -> {ATTESTATION_LOG.resolve()}")
    print(f"         SHA-256(audit CSV) = {record['audit_csv_sha256']}")
    return ATTESTATION_LOG


def human_in_the_loop_audit(scrubbed_df: pd.DataFrame) -> None:
    """
    Step 2 — CRITICAL human-in-the-loop security audit gate.

    LEGAL LIABILITY MITIGATION (why this MUST halt):
    - Automated tools miss edge cases (nicknames, alternate email formats,
      free-text comments, atypical SSN layouts, institutional abbreviations).
    - FERPA / university IT policy typically require a responsible official to
      attest that education records have been de-identified before any further
      processing or potential cloud transfer.
    - Exporting 'step2_human_audit_sample.csv' creates an auditable artifact
      for compliance review. The script refuses to synthesize until APPROVE.
    - Sign-off identity (full name + NetID), UTC timestamp, decision, and the
      SHA-256 of the audit CSV are written to
      'step2_human_audit_attestation.jsonl' for both APPROVE and REJECT.
    - Typing REJECT aborts with a non-zero exit — no synthetic data is written.
    """
    scrubbed_df.to_csv(AUDIT_CSV, index=False)
    print(f"[Step 2] Wrote human audit sample -> {AUDIT_CSV.resolve()}")
    print(
        "         OPEN THIS FILE LOCALLY and verify every row is free of "
        "direct PII and institutional brand identifiers before continuing."
    )

    print(
        "SECURITY AUDIT REQUIRED: Please open 'step2_human_audit_sample.csv' "
        "and verify all PII and institutional identifiers are removed."
    )

    # Identity prompts — required so IT can answer "who signed off?"
    auditor_name = input("Auditor full name: ").strip()
    if not auditor_name:
        print("[Step 2] Auditor full name is required. Halting.")
        sys.exit(1)

    auditor_netid = input("Auditor NetID / institutional username: ").strip()
    if not auditor_netid:
        print("[Step 2] Auditor NetID is required. Halting.")
        sys.exit(1)

    decision = input(
        "Type 'APPROVE' to confirm legal de-identification and proceed to "
        "synthesis, or 'REJECT' to halt.\n> "
    ).strip()

    if decision not in {"APPROVE", "REJECT"}:
        # Still log invalid attempts for accountability (decision recorded as-is).
        write_attestation_record(
            auditor_name=auditor_name,
            auditor_netid=auditor_netid,
            decision=f"INVALID:{decision}",
            row_count=len(scrubbed_df),
        )
        print(
            f"[Step 2] Invalid response {decision!r}. "
            "Only exact 'APPROVE' or 'REJECT' are accepted. Halting."
        )
        sys.exit(1)

    # Persist attestation BEFORE branching so REJECT is also retained.
    write_attestation_record(
        auditor_name=auditor_name,
        auditor_netid=auditor_netid,
        decision=decision,
        row_count=len(scrubbed_df),
    )

    if decision == "APPROVE":
        print(
            f"[Step 2] {auditor_name} ({auditor_netid}) APPROVED "
            "legal de-identification. Proceeding."
        )
        return

    print(
        f"[Step 2] {auditor_name} ({auditor_netid}) REJECTED the scrubbed "
        "sample. Halting. No synthetic data will be generated."
    )
    sys.exit(1)


def synthesize_with_sdv(scrubbed_df: pd.DataFrame, n_rows: int | None = None) -> pd.DataFrame:
    """
    Step 3 — Local synthetic data generation with SDV GaussianCopulaSynthesizer.

    FERPA / CLOUD-UPLOAD RISK MITIGATION:
    - Trains ONLY on the human-approved scrubbed dataframe (no raw PII columns
      in clear text when Presidio + brand wipe succeeded).
    - GaussianCopulaSynthesizer runs entirely locally via the open-source SDV
      package — no vendor SaaS, no telemetry required for this PoC path.
    - Output size matches the scrubbed set so downstream checks are 1:1 fair.
    """
    if n_rows is None:
        n_rows = len(scrubbed_df)

    print("[Step 3] Fitting local SDV GaussianCopulaSynthesizer on scrubbed data...")
    # Use current SDV Metadata API (SingleTableMetadata is deprecated).
    metadata = Metadata.detect_from_dataframe(data=scrubbed_df, table_name="scrubbed_students")

    # LIABILITY MITIGATION: Column-name heuristics in SDV may label Email/SSN as
    # PII-like sdtypes and invent NEW faker emails/SSNs during sampling. That
    # would reintroduce PII-*looking* values into the "safe" export and confuse
    # auditors. Force categorical sdtypes so synthesis only remixes approved
    # token categories (e.g., "<EMAIL_ADDRESS>"), never fabricated identifiers.
    for col in ("Name", "Email", "SSN", "University_Name"):
        if col in scrubbed_df.columns:
            metadata.update_column(
                column_name=col,
                sdtype="categorical",
                table_name="scrubbed_students",
            )

    synthesizer = GaussianCopulaSynthesizer(metadata)
    synthesizer.fit(scrubbed_df)
    synthetic = synthesizer.sample(num_rows=n_rows)

    # Re-apply institutional wipe + known-PII tokenization on synthetic output
    # so any generative quirk cannot reintroduce brand strings or clear-text IDs.
    synthetic = anonymize_institution(synthetic)
    for col, token in (
        ("Name", "<PERSON>"),
        ("Email", "<EMAIL_ADDRESS>"),
        ("SSN", "<US_SSN>"),
    ):
        if col in synthetic.columns:
            synthetic[col] = token

    print(f"[Step 3] Generated {len(synthetic)} synthetic rows (local SDV only).")
    return synthetic


def remove_exact_clones(
    synthetic_df: pd.DataFrame, scrubbed_df: pd.DataFrame
) -> tuple[pd.DataFrame, int]:
    """
    Step 4 — Overfit / clone testing (exact 1:1 row match removal).

    OVERFITTING / RE-IDENTIFICATION RISK MITIGATION:
    - If a synthetic row is an exact duplicate of a scrubbed real row, that
      "clone" can leak a training example into any later cloud upload.
    - Membership-inference and singling-out attacks are easier when clones
      exist; deleting them enforces a zero-exact-clone export for this PoC.
    - Comparison is row-by-row against the scrubbed (not raw) dataset, which
      matches the human-approved artifact under review.
    - Exact-match only. Near-duplicates / mosaic linkage are handled in Step 5.
    """
    print("[Step 4] Running exact clone check (synthetic vs scrubbed)...")

    # Normalize to string for stable equality across mixed dtypes / floats.
    scrubbed_norm = scrubbed_df.astype(str).reset_index(drop=True)
    synthetic_norm = synthetic_df.astype(str).reset_index(drop=True)
    scrubbed_keys = set(map(tuple, scrubbed_norm.to_numpy().tolist()))

    keep_mask = []
    clones_removed = 0
    for row in synthetic_norm.to_numpy().tolist():
        if tuple(row) in scrubbed_keys:
            clones_removed += 1
            keep_mask.append(False)
        else:
            keep_mask.append(True)

    cleaned = synthetic_df.loc[keep_mask].reset_index(drop=True)
    print(
        f"[Step 4] Removed {clones_removed} exact clone row(s). "
        f"Retained {len(cleaned)} mathematically non-identical synthetic row(s)."
    )
    return cleaned, clones_removed


def _require_qid_columns(df: pd.DataFrame, context: str) -> None:
    missing = [c for c in QID_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"{context}: missing quasi-identifier columns {missing}")


def bin_quasi_identifiers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Bin numeric QIDs into equivalence classes for k-map uniqueness checks.

    MOSAIC MITIGATION:
    - Continuous values are almost always unique; binning approximates how an
      attacker would match 'about the same GPA / score' across datasets.
    """
    _require_qid_columns(df, "bin_quasi_identifiers")
    binned = pd.DataFrame(index=df.index)
    for col in QID_COLUMNS:
        width = QID_BIN_WIDTHS[col]
        values = pd.to_numeric(df[col], errors="coerce")
        binned[col] = (np.floor(values / width) * width).round(10)
    return binned


def assess_scrubbed_qid_kmap(scrubbed_df: pd.DataFrame) -> dict[str, Any]:
    """
    Measure scrubbed-data quasi-identifier uniqueness (k-map style).

    MOSAIC / LINKAGE RISK:
    - Equivalence classes with size < K_ANONYMITY_MIN are high-risk join keys
      against auxiliary files (rosters, gradebooks, other study extracts).
    - This does not modify scrubbed data; it informs the synthetic filter and
      produces an auditor-facing risk summary.
    """
    binned = bin_quasi_identifiers(scrubbed_df)
    class_sizes = binned.value_counts(dropna=False)
    rare_mask = class_sizes < K_ANONYMITY_MIN
    rare_classes = int(rare_mask.sum())
    rows_in_rare = int(class_sizes[rare_mask].sum()) if rare_classes else 0
    report = {
        "qid_columns": list(QID_COLUMNS),
        "bin_widths": dict(QID_BIN_WIDTHS),
        "k_anonymity_min": K_ANONYMITY_MIN,
        "n_rows": int(len(scrubbed_df)),
        "n_equivalence_classes": int(len(class_sizes)),
        "n_rare_classes_lt_k": rare_classes,
        "n_rows_in_rare_classes": rows_in_rare,
        "min_class_size": int(class_sizes.min()) if len(class_sizes) else 0,
        "median_class_size": float(class_sizes.median()) if len(class_sizes) else 0.0,
        "share_rows_in_rare_classes": (
            round(rows_in_rare / len(scrubbed_df), 4) if len(scrubbed_df) else 0.0
        ),
    }
    print(
        f"[Step 5a] Scrubbed QID k-map: {report['n_equivalence_classes']} classes; "
        f"{rare_classes} rare (< k={K_ANONYMITY_MIN}); "
        f"{rows_in_rare}/{len(scrubbed_df)} rows sit in rare classes."
    )
    return report


def _minmax_normalize_qids(
    frame: pd.DataFrame, mins: pd.Series, maxs: pd.Series
) -> np.ndarray:
    """Min-max normalize QID columns using scrubbed-data ranges."""
    arr = frame[list(QID_COLUMNS)].apply(pd.to_numeric, errors="coerce").astype(float)
    denom = (maxs - mins).replace(0, 1.0)
    normalized = (arr - mins) / denom
    return normalized.to_numpy(dtype=float)


def _pairwise_min_euclidean(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Min Euclidean distance from each row in a to any row in b."""
    a_sq = np.sum(a**2, axis=1, keepdims=True)
    b_sq = np.sum(b**2, axis=1, keepdims=True).T
    cross = a @ b.T
    dists = np.sqrt(np.maximum(a_sq + b_sq - 2.0 * cross, 0.0))
    return dists.min(axis=1)


def compute_dcr_to_scrubbed(
    synthetic_df: pd.DataFrame, scrubbed_df: pd.DataFrame
) -> np.ndarray:
    """
    Distance to Closest Record (Euclidean) in min-max-normalized QID space.

    Each synthetic row's DCR is min distance to any scrubbed row. Low DCR means
    the synthetic point is a near-neighbor of a real (scrubbed) record — useful
    for mosaic / membership attacks even when not an exact clone.
    """
    _require_qid_columns(synthetic_df, "compute_dcr_to_scrubbed/synthetic")
    _require_qid_columns(scrubbed_df, "compute_dcr_to_scrubbed/scrubbed")

    scrubbed_qid = scrubbed_df[list(QID_COLUMNS)].apply(pd.to_numeric, errors="coerce")
    mins = scrubbed_qid.min()
    maxs = scrubbed_qid.max()
    scrubbed_norm = _minmax_normalize_qids(scrubbed_df, mins, maxs)
    synthetic_norm = _minmax_normalize_qids(synthetic_df, mins, maxs)
    return _pairwise_min_euclidean(synthetic_norm, scrubbed_norm)


def compute_scrubbed_loo_dcr(scrubbed_df: pd.DataFrame) -> np.ndarray:
    """
    Leave-one-out DCR among scrubbed rows (baseline denseness of real QIDs).

    Reported for IT context: if real records are already tightly clustered,
    a fixed DCR floor must be interpreted against that baseline.
    """
    _require_qid_columns(scrubbed_df, "compute_scrubbed_loo_dcr")
    scrubbed_qid = scrubbed_df[list(QID_COLUMNS)].apply(pd.to_numeric, errors="coerce")
    mins = scrubbed_qid.min()
    maxs = scrubbed_qid.max()
    norm = _minmax_normalize_qids(scrubbed_df, mins, maxs)
    # Distance to nearest *other* scrubbed row.
    a_sq = np.sum(norm**2, axis=1, keepdims=True)
    cross = norm @ norm.T
    dists = np.sqrt(np.maximum(a_sq + a_sq.T - 2.0 * cross, 0.0))
    np.fill_diagonal(dists, np.inf)
    return dists.min(axis=1)


def mosaic_attack_gate(
    synthetic_df: pd.DataFrame, scrubbed_df: pd.DataFrame
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Step 5 — Mosaic-attack / linkage-risk gate (QID k-map + DCR).

    MOSAIC ATTACK MITIGATION (what this blocks):
    1) Singleton QID bins: if a synthetic row lands in a scrubbed equivalence
       class of size <= RARE_BIN_DROP_MAX_SIZE (default 1), it reproduces a
       singling-out cell an attacker can join to auxiliary files — dropped.
       Classes with size < K_ANONYMITY_MIN are still measured in the report.
    2) Near-neighbors (DCR): synthetic rows closer than DCR_MIN_THRESHOLD to
       any scrubbed row (normalized QID Euclidean distance) are dropped even
       when not exact clones — this is the near-duplicate / linkage screen.
    3) Export hard-stop: if fewer than MIN_SAFE_EXPORT_ROWS survive, the script
       refuses to write final_safe_synthetic_data.csv.

    LIMITATION (documented for IT):
    - This is a local PoC control, not a full differential-privacy budget or
      attacker-model simulation against a real auxiliary dataset. It materially
      reduces the obvious mosaic vectors present in this schema.
    """
    print("[Step 5] Running mosaic-attack gate (QID k-map + DCR)...")
    kmap = assess_scrubbed_qid_kmap(scrubbed_df)
    loo_dcr = compute_scrubbed_loo_dcr(scrubbed_df)

    scrubbed_bins = bin_quasi_identifiers(scrubbed_df)
    scrubbed_keys = pd.Series(
        list(map(tuple, scrubbed_bins.to_numpy().tolist())), index=scrubbed_bins.index
    )
    scrubbed_counts = scrubbed_keys.value_counts(dropna=False)
    # Auto-drop only singleton / ultra-rare bins (see RARE_BIN_DROP_MAX_SIZE).
    drop_keys = set(
        scrubbed_counts[scrubbed_counts <= RARE_BIN_DROP_MAX_SIZE].index.tolist()
    )
    report_rare_keys = set(
        scrubbed_counts[scrubbed_counts < K_ANONYMITY_MIN].index.tolist()
    )

    synthetic_bins = bin_quasi_identifiers(synthetic_df)
    synthetic_keys = pd.Series(
        list(map(tuple, synthetic_bins.to_numpy().tolist())), index=synthetic_bins.index
    )
    rare_bin_mask_arr = synthetic_keys.isin(drop_keys).to_numpy(dtype=bool)
    report_rare_hit_arr = synthetic_keys.isin(report_rare_keys).to_numpy(dtype=bool)

    dcr = compute_dcr_to_scrubbed(synthetic_df, scrubbed_df)
    near_mask = dcr < DCR_MIN_THRESHOLD

    drop_mask = rare_bin_mask_arr | near_mask
    kept = synthetic_df.loc[~drop_mask].reset_index(drop=True)
    kept_dcr = dcr[~drop_mask]

    report: dict[str, Any] = {
        "event": "mosaic_attack_gate",
        "utc_timestamp": datetime.now(timezone.utc).isoformat(),
        "scrubbed_kmap": kmap,
        "scrubbed_loo_dcr": {
            "min": float(loo_dcr.min()) if len(loo_dcr) else None,
            "median": float(np.median(loo_dcr)) if len(loo_dcr) else None,
            "p05": float(np.percentile(loo_dcr, 5)) if len(loo_dcr) else None,
        },
        "dcr_min_threshold": DCR_MIN_THRESHOLD,
        "rare_bin_drop_max_size": RARE_BIN_DROP_MAX_SIZE,
        "min_safe_export_rows": MIN_SAFE_EXPORT_ROWS,
        "input_synthetic_rows": int(len(synthetic_df)),
        "dropped_rare_qid_bin": int(rare_bin_mask_arr.sum()),
        "synthetic_rows_in_kmap_rare_bins_lt_k": int(report_rare_hit_arr.sum()),
        "dropped_low_dcr": int(near_mask.sum()),
        "dropped_union": int(drop_mask.sum()),
        "retained_rows": int(len(kept)),
        "dcr_stats_all_synthetic": {
            "min": float(dcr.min()) if len(dcr) else None,
            "median": float(np.median(dcr)) if len(dcr) else None,
            "p05": float(np.percentile(dcr, 5)) if len(dcr) else None,
        },
        "dcr_stats_retained": {
            "min": float(kept_dcr.min()) if len(kept_dcr) else None,
            "median": float(np.median(kept_dcr)) if len(kept_dcr) else None,
            "p05": float(np.percentile(kept_dcr, 5)) if len(kept_dcr) else None,
        },
        "export_blocked": False,
        "block_reason": None,
    }

    MOSAIC_REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"[Step 5] Dropped {report['dropped_rare_qid_bin']} rare-QID-bin row(s); "
        f"{report['dropped_low_dcr']} low-DCR row(s); "
        f"union={report['dropped_union']}. Retained {len(kept)}."
    )
    print(f"[Step 5] Mosaic risk report -> {MOSAIC_REPORT.resolve()}")

    if len(kept) < MIN_SAFE_EXPORT_ROWS:
        report["export_blocked"] = True
        report["block_reason"] = (
            f"Retained {len(kept)} rows < MIN_SAFE_EXPORT_ROWS={MIN_SAFE_EXPORT_ROWS}"
        )
        MOSAIC_REPORT.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(
            f"[Step 5] EXPORT BLOCKED: {report['block_reason']}. "
            "Refusing to write final_safe_synthetic_data.csv."
        )
        sys.exit(2)

    # Post-condition: no retained row may sit under the DCR floor.
    if len(kept_dcr) and float(kept_dcr.min()) < DCR_MIN_THRESHOLD:
        report["export_blocked"] = True
        report["block_reason"] = "Retained set still contains DCR below threshold"
        MOSAIC_REPORT.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print("[Step 5] EXPORT BLOCKED: DCR post-condition failed.")
        sys.exit(2)

    return kept, report


def compute_dcr_on_columns(
    synthetic_df: pd.DataFrame,
    scrubbed_df: pd.DataFrame,
    columns: tuple[str, ...] | list[str],
) -> np.ndarray:
    """DCR on an explicit numeric column set (QIDs and/or distractors)."""
    cols = list(columns)
    for col in cols:
        if col not in synthetic_df.columns or col not in scrubbed_df.columns:
            raise ValueError(f"DCR column missing from frame(s): {col}")
    scrubbed_num = scrubbed_df[cols].apply(pd.to_numeric, errors="coerce").astype(float)
    mins = scrubbed_num.min()
    maxs = scrubbed_num.max()
    denom = (maxs - mins).replace(0, 1.0)
    scrubbed_norm = ((scrubbed_num - mins) / denom).to_numpy(dtype=float)
    synthetic_num = synthetic_df[cols].apply(pd.to_numeric, errors="coerce").astype(float)
    synthetic_norm = ((synthetic_num - mins) / denom).to_numpy(dtype=float)
    return _pairwise_min_euclidean(synthetic_norm, scrubbed_norm)


def _draw_distractor_frame(n_rows: int, rng: np.random.Generator) -> pd.DataFrame:
    """Independent distractor columns — intentionally uncorrelated with QIDs."""
    data: dict[str, np.ndarray] = {}
    for col in DISTRACTOR_COLUMNS:
        lo, hi = DISTRACTOR_VALUE_RANGES[col]
        data[col] = np.round(rng.uniform(lo, hi, size=n_rows), 2)
    return pd.DataFrame(data)


def _draw_distractor_cases(
    scrubbed_df: pd.DataFrame, n_wanted: int, rng: np.random.Generator
) -> pd.DataFrame:
    """
    Build decoy *cases* (rows) with plausible QID-like values that still clear
    the DCR floor vs scrubbed data — decoys must not accidentally near-clone
    a real scrubbed student.
    """
    scrubbed_qid = scrubbed_df[list(QID_COLUMNS)].apply(pd.to_numeric, errors="coerce")
    mins = scrubbed_qid.min()
    maxs = scrubbed_qid.max()
    draw_n = max(n_wanted * DISTRACTOR_CASE_DRAW_MULTIPLIER, n_wanted)
    candidates = pd.DataFrame(
        {
            "Name": "<PERSON>",
            "Email": "<EMAIL_ADDRESS>",
            "SSN": "<US_SSN>",
            "GPA": np.round(rng.uniform(float(mins["GPA"]), float(maxs["GPA"]), draw_n), 2),
            "Personality_Score": np.round(
                rng.uniform(
                    float(mins["Personality_Score"]),
                    float(maxs["Personality_Score"]),
                    draw_n,
                ),
                1,
            ),
            "University_Name": INSTITUTION_REPLACEMENT,
        }
    )
    dcr = compute_dcr_on_columns(candidates, scrubbed_df, QID_COLUMNS)
    safe = candidates.loc[dcr >= DCR_MIN_THRESHOLD].reset_index(drop=True)
    if len(safe) < n_wanted:
        raise RuntimeError(
            f"Could only mint {len(safe)} DCR-safe distractor cases; need {n_wanted}."
        )
    return safe.sample(n=n_wanted, random_state=int(rng.integers(0, 1_000_000))).reset_index(
        drop=True
    )


def apply_distractor_dilution_protocol(
    synthetic_df: pd.DataFrame, scrubbed_df: pd.DataFrame
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Step 6 — Distractor dilution (variables + cases) with LOCAL-ONLY linking key.

    THREAT MODEL / INTENT:
    - Cloud-facing release should frustrate re-identification (mosaic / linkage).
    - On-device, analysts still need to know which rows/columns are analytic vs
      decoy so they can cut/keep correctly for local research use.
    - The linking key is the authoritative cut/keep map and MUST remain local.
      Uploading it alongside the diluted CSV would defeat the dilution.

    PROTOCOL:
    1) Require zero true-QID DCR violations on analytic synthetic rows.
    2) Add distractor *variables* (columns) to analytic rows.
    3) Mint distractor *cases* (rows) that also clear the DCR floor.
    4) Add the same distractor variables to distractor cases.
    5) Shuffle into one unlabeled export table.
    6) Write local_only_linkage_key.json (row roles + column roles).
    7) Return only the diluted table for final export (no role columns).
    """
    print(
        "[Step 6] Distractor dilution — variables + cases; "
        "local-only linkage key for cut/keep."
    )

    analytic = synthetic_df.reset_index(drop=True).copy()
    qid_dcr = compute_dcr_on_columns(analytic, scrubbed_df, QID_COLUMNS)
    qid_violations = int(np.sum(qid_dcr < DCR_MIN_THRESHOLD))
    if qid_violations != 0:
        print(
            f"[Step 6] PROTOCOL FAIL: {qid_violations} true-QID DCR violation(s) "
            "remain after the mosaic gate."
        )
        sys.exit(2)

    rng = np.random.default_rng(RANDOM_SEED)
    eval_columns = tuple(QID_COLUMNS) + tuple(DISTRACTOR_COLUMNS)

    # Distractor variables on analytic rows (resample until naive DCR is clean).
    analytic_enriched: pd.DataFrame | None = None
    naive_dcr_analytic: np.ndarray | None = None
    attempts = 0
    for attempts in range(1, DISTRACTOR_MAX_RESAMPLE_ATTEMPTS + 1):
        syn_distract = _draw_distractor_frame(len(analytic), rng)
        scrub_distract = _draw_distractor_frame(len(scrubbed_df), rng)
        candidate = pd.concat([analytic, syn_distract], axis=1)
        scrubbed_eval = pd.concat(
            [scrubbed_df.reset_index(drop=True), scrub_distract], axis=1
        )
        naive_dcr_analytic = compute_dcr_on_columns(
            candidate, scrubbed_eval, eval_columns
        )
        if int(np.sum(naive_dcr_analytic < DCR_MIN_THRESHOLD)) == 0:
            analytic_enriched = candidate
            break

    if analytic_enriched is None or naive_dcr_analytic is None:
        print("[Step 6] PROTOCOL FAIL: could not clear naive DCR with distractor vars.")
        sys.exit(2)

    # Distractor cases (rows), DCR-safe vs scrubbed, then same distractor columns.
    decoy_cases = _draw_distractor_cases(scrubbed_df, DISTRACTOR_CASE_COUNT, rng)
    decoy_cases = pd.concat(
        [decoy_cases, _draw_distractor_frame(len(decoy_cases), rng)], axis=1
    )
    decoy_dcr = compute_dcr_on_columns(decoy_cases, scrubbed_df, QID_COLUMNS)
    if int(np.sum(decoy_dcr < DCR_MIN_THRESHOLD)) != 0:
        print("[Step 6] PROTOCOL FAIL: distractor cases failed QID DCR floor.")
        sys.exit(2)

    analytic_enriched = analytic_enriched.copy()
    analytic_enriched["_case_role"] = "analytic_synthetic"
    analytic_enriched["_keep_for_local_analysis"] = True

    decoy_cases = decoy_cases.copy()
    decoy_cases["_case_role"] = "distractor_case"
    decoy_cases["_keep_for_local_analysis"] = False

    combined = pd.concat([analytic_enriched, decoy_cases], axis=0, ignore_index=True)
    combined = combined.sample(frac=1.0, random_state=RANDOM_SEED).reset_index(drop=True)
    combined.insert(0, "export_row_id", np.arange(len(combined), dtype=int))

    # LOCAL-ONLY linking key: how to cut/keep on-device. Never upload this.
    linkage = {
        "event": "local_only_linkage_key",
        "utc_timestamp": datetime.now(timezone.utc).isoformat(),
        "WARNING": (
            "ON-DEVICE ONLY. Do not upload, email, or commit this file. "
            "It reveals which export rows/columns are analytic vs distractors "
            "and would undo dilution if paired with the cloud CSV."
        ),
        "column_roles": {
            **{c: "direct_identifier_token" for c in ("Name", "Email", "SSN")},
            **{c: "true_quasi_identifier" for c in QID_COLUMNS},
            "University_Name": "institutional_anonymized",
            **{c: "distractor_variable" for c in DISTRACTOR_COLUMNS},
            "export_row_id": "export_sequence_only",
        },
        "rows": [
            {
                "export_row_id": int(rec["export_row_id"]),
                "case_role": rec["_case_role"],
                "keep_for_local_analysis": bool(rec["_keep_for_local_analysis"]),
            }
            for rec in combined[
                ["export_row_id", "_case_role", "_keep_for_local_analysis"]
            ].to_dict("records")
        ],
        "counts": {
            "analytic_synthetic": int((combined["_case_role"] == "analytic_synthetic").sum()),
            "distractor_case": int((combined["_case_role"] == "distractor_case").sum()),
            "total_export_rows": int(len(combined)),
        },
    }
    LOCAL_LINKAGE_KEY.write_text(
        json.dumps(linkage, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    # Cloud-facing table: strip role/key columns.
    export_df = combined.drop(
        columns=["_case_role", "_keep_for_local_analysis", "export_row_id"]
    )

    # Final safety: every exported row (analytic + decoy) clears QID DCR floor.
    all_dcr = compute_dcr_on_columns(export_df, scrubbed_df, QID_COLUMNS)
    all_violations = int(np.sum(all_dcr < DCR_MIN_THRESHOLD))
    if all_violations != 0:
        print(
            f"[Step 6] PROTOCOL FAIL: {all_violations} export row(s) under DCR floor "
            "after dilution merge."
        )
        sys.exit(2)

    report = {
        "event": "distractor_dilution_protocol",
        "utc_timestamp": datetime.now(timezone.utc).isoformat(),
        "protocol_passed": True,
        "semantics": (
            "Zero DCR violations for all cloud-facing rows. "
            "Local linkage key retained on-device for cut/keep; not in export."
        ),
        "true_qid_columns": list(QID_COLUMNS),
        "distractor_variables": list(DISTRACTOR_COLUMNS),
        "n_analytic_cases": int(linkage["counts"]["analytic_synthetic"]),
        "n_distractor_cases": int(linkage["counts"]["distractor_case"]),
        "n_export_rows": int(len(export_df)),
        "dcr_min_threshold": DCR_MIN_THRESHOLD,
        "qid_dcr_violations_export": 0,
        "qid_dcr_min_export": float(all_dcr.min()),
        "qid_dcr_min_analytic": float(qid_dcr.min()),
        "naive_full_vector_dcr_min_analytic": float(naive_dcr_analytic.min()),
        "distractor_variable_resample_attempts": attempts,
        "local_linkage_key_path": str(LOCAL_LINKAGE_KEY.resolve()),
        "cloud_export_must_exclude": str(LOCAL_LINKAGE_KEY.name),
        "note": (
            "Dilution reduces re-identification utility of the released table. "
            "The on-device key is required to recover analytic rows/columns locally. "
            "Never transmit the key with the CSV."
        ),
    }
    DISTRACTOR_REPORT.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(
        f"[Step 6] Analytic cases={report['n_analytic_cases']}; "
        f"distractor cases={report['n_distractor_cases']}; "
        f"export rows={report['n_export_rows']}."
    )
    print(
        f"[Step 6] DCR violations = 0 on full export "
        f"(min DCR={report['qid_dcr_min_export']:.4f})."
    )
    print(
        f"[Step 6] LOCAL-ONLY linkage key -> {LOCAL_LINKAGE_KEY.resolve()} "
        "(do not upload)."
    )
    print(f"[Step 6] Protocol report -> {DISTRACTOR_REPORT.resolve()}")
    return export_df, report


def export_final(synthetic_df: pd.DataFrame) -> Path:
    """
    Step 7 — Final local export of diluted, institution-agnostic synthetic data.

    CLOUD-UPLOAD GATE:
    - This CSV is the only cloud-candidate artifact from the PoC.
    - local_only_linkage_key.json is intentionally excluded and must stay on-device.
    """
    synthetic_df.to_csv(FINAL_CSV, index=False)
    print(f"[Step 7] Wrote final safe synthetic data -> {FINAL_CSV.resolve()}")
    print(
        "         DO NOT upload local_only_linkage_key.json with this file. "
        "Cloud transfer still requires a separate institutional approval workflow."
    )
    return FINAL_CSV


def main() -> int:
    print("=" * 72)
    print("LOCAL FERPA DE-ID + SYNTHESIS PoC (100% on-device libraries)")
    print("=" * 72)

    # Step 0 — Dummy data only (DEVELOPMENT). Never real student records here.
    raw_df = generate_dummy_student_data()

    # Step 1 — Presidio PII redaction + institutional anonymization.
    scrubbed = redact_direct_pii(raw_df)
    scrubbed = anonymize_institution(scrubbed)

    # Step 2 — HARD STOP for human security audit (APPROVE / REJECT).
    human_in_the_loop_audit(scrubbed)

    # Step 3 — Local SDV synthesis from approved scrubbed data.
    # Oversample so Step 5 mosaic culls (singleton QID bins + low DCR) can
    # still leave a usable export cohort without relaxing privacy thresholds.
    synthetic = synthesize_with_sdv(
        scrubbed, n_rows=N_ROWS * SYNTHETIC_OVERSAMPLE_FACTOR
    )

    # Step 4 — Delete any exact 1:1 clones vs scrubbed rows.
    synthetic_clean, _clones = remove_exact_clones(synthetic, scrubbed)

    # Step 5 — Mosaic gate: rare QID bins + DCR near-match cull (may hard-stop).
    synthetic_safe, _mosaic_report = mosaic_attack_gate(synthetic_clean, scrubbed)
    if len(synthetic_safe) > N_ROWS:
        synthetic_safe = synthetic_safe.sample(
            n=N_ROWS, random_state=RANDOM_SEED
        ).reset_index(drop=True)
        print(f"[Step 5] Downsampled retained rows to target size n={N_ROWS}.")

    # Step 6 — Distractor vars + cases; local-only key for cut/keep.
    synthetic_export, _dvp_report = apply_distractor_dilution_protocol(
        synthetic_safe, scrubbed
    )

    # Step 7 — Export diluted CSV only (linkage key stays local).
    export_final(synthetic_export)

    print("=" * 72)
    print("PoC complete. Artifacts:")
    print(f"  - Audit sample : {AUDIT_CSV.resolve()}")
    print(f"  - Attestation  : {ATTESTATION_LOG.resolve()}")
    print(f"  - Mosaic report: {MOSAIC_REPORT.resolve()}")
    print(f"  - Distractor   : {DISTRACTOR_REPORT.resolve()}")
    print(f"  - LOCAL key    : {LOCAL_LINKAGE_KEY.resolve()}  << do not upload")
    print(f"  - Cloud candidate CSV: {FINAL_CSV.resolve()}")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
