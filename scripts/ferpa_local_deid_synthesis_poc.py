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
  7) Exports only the verified synthetic file for potential later cloud upload

LEGAL / FERPA LIABILITY NOTES (for reviewers)
---------------------------------------------
- This PoC NEVER ships real student education records. Step 0 creates fake data
  solely so IT can exercise the controls without touching FERPA-covered PII.
- Automated redaction is necessary but NOT sufficient under FERPA / institutional
  policy. The mandatory human audit gate (Step 2) creates an explicit approval
  artifact before synthesis proceeds — documenting that a responsible official
  attested to legal de-identification.
- Synthetic data derived from scrubbed records is still treated as sensitive
  until clone-checked. Exact row matches can leak training examples (membership
  inference / overfitting), so Step 4 deletes clones before export.
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
    Type APPROVE to continue, or REJECT to halt.
=============================================================================
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterable

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
FINAL_CSV = WORK_DIR / "final_safe_synthetic_data.csv"

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
    - Typing REJECT aborts with a non-zero exit — no synthetic file is written.
    """
    scrubbed_df.to_csv(AUDIT_CSV, index=False)
    print(f"[Step 2] Wrote human audit sample -> {AUDIT_CSV.resolve()}")
    print(
        "         OPEN THIS FILE LOCALLY and verify every row is free of "
        "direct PII and institutional brand identifiers before continuing."
    )

    prompt = (
        "SECURITY AUDIT REQUIRED: Please open 'step2_human_audit_sample.csv' "
        "and verify all PII and institutional identifiers are removed. "
        "Type 'APPROVE' to confirm legal de-identification and proceed to "
        "synthesis, or 'REJECT' to halt."
    )

    # HARD STOP — do not proceed past this point without human attestation.
    decision = input(prompt + "\n> ").strip()

    if decision == "APPROVE":
        print("[Step 2] Human auditor APPROVED legal de-identification. Proceeding.")
        return
    if decision == "REJECT":
        print(
            "[Step 2] Human auditor REJECTED the scrubbed sample. "
            "Halting. No synthetic data will be generated."
        )
        sys.exit(1)

    print(
        f"[Step 2] Invalid response {decision!r}. "
        "Only exact 'APPROVE' or 'REJECT' are accepted. Halting."
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
    - NOTE: This is an exact-match screen, not a full privacy budget / DCR
      audit. IT may layer Distance to Closest Record (DCR) or k-map tests later.
    """
    print("[Step 4] Running exact clone check (synthetic vs scrubbed)...")

    # Normalize to string for stable equality across mixed dtypes / floats.
    scrubbed_norm = scrubbed_df.astype(str).reset_index(drop=True)
    synthetic_norm = synthetic_df.astype(str).reset_index(drop=True)
    scrubbed_keys = set(map(tuple, scrubbed_norm.to_numpy().tolist()))

    keep_mask = []
    clones_removed = 0
    for idx, row in enumerate(synthetic_norm.to_numpy().tolist()):
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


def export_final(synthetic_df: pd.DataFrame) -> Path:
    """
    Step 5 — Final local export of institution-agnostic synthetic data.

    CLOUD-UPLOAD GATE:
    - Only this file is intended as a candidate for later upload, and only
      after institutional policy review. The PoC itself performs no upload.
    - Raw dummy data and the audit CSV remain local working artifacts.
    """
    synthetic_df.to_csv(FINAL_CSV, index=False)
    print(f"[Step 5] Wrote final safe synthetic data -> {FINAL_CSV.resolve()}")
    print(
        "         Reminder: this PoC does NOT upload anything. Cloud transfer "
        "requires a separate institutional approval workflow."
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
    synthetic = synthesize_with_sdv(scrubbed)

    # Step 4 — Delete any exact 1:1 clones vs scrubbed rows.
    synthetic_clean, _clones = remove_exact_clones(synthetic, scrubbed)

    # Step 5 — Export verified synthetic CSV (still local; no cloud upload).
    export_final(synthetic_clean)

    print("=" * 72)
    print("PoC complete. Artifacts (local only):")
    print(f"  - Audit sample : {AUDIT_CSV.resolve()}")
    print(f"  - Final export : {FINAL_CSV.resolve()}")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
