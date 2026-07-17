#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
 DECOUPLED AI PROTOCOL — AOL SYNTHETIC DATA / COMPLIANCE PROOF OF CONCEPT
==============================================================================
 Institution : Nicholls State University
 Classification: DEVELOPMENT / SYNTHETIC DATA ONLY
 Audience     : AOL Chair, Faculty, University Senate, IT Security, IRB
 Dependencies: pandas, numpy, scipy  (standard open-source; local execution)
 Network      : NONE. This script performs zero outbound API or cloud calls.

 PURPOSE
 -------
 Operationalize the Decoupled AI Protocol with an Assurance of Learning (AOL)
 synthetic demonstration:

   CONTROL PLANE  — Cloud LLM (e.g., Gemini) receives ONLY empty structural
                    metadata / mock schemas and returns analysis *code logic*.
   DATA PLANE     — University-managed hardware executes that code locally
                    against sealed synthetic stand-ins for student datasets.

 This PoC generates N=100 synthetic cases with:
   • Key AOL variables : GPA, ETS Major Field Test score, program of study
   • Demographics      : age band, gender, race/ethnicity, residency
   • Synthetic PII     : Disney-character names + fake emails (NEVER shared
                         with any cloud AI; stand-ins for real identifiers)

 Privacy controls demonstrated:
   1. Demographics are SEPARATED from key academic variables. Linking them
      for analysis requires a logged BREAK-GLASS authorization.
   2. Tables are unlinkable in ordinary use: independent opaque IDs, row
      shuffles, AND synthpop-style synthesis/noise so recombination fails.
   3. Simulated Control Plane prompts show exactly what an AI would see
      (schema only) vs what remains sealed locally (row data / PII).

 LEGAL / COMPLIANCE ANCHORS (informational)
 ------------------------------------------
   • FERPA, 20 U.S.C. § 1232g; 34 C.F.R. Part 99
   • Louisiana La. R.S. 17:3914 (student information privacy)
   • CITI Program — Information Security / Data Security modules
   • 45 C.F.R. Part 46 (Common Rule) — human subjects research principles

 Run (from the repository root — not from ~):
   cd ~/SONA-System
   git checkout cursor/decoupled-ai-protocol-poc-6005
   python3 -m venv .venv && source .venv/bin/activate
   python3 -m pip install pandas numpy scipy
   python3 scripts/decoupled_ai_protocol_poc.py
   # At the HITL gate, type: YES
   # Optional break-glass demo when prompted

 macOS note: use "python3 -m pip" (Homebrew often has no bare "pip" command).

 Non-interactive / CI:
   DECOUPLED_AI_HITL_CONFIRM=YES \\
   DECOUPLED_AI_BREAK_GLASS=YES \\
   DECOUPLED_AI_BREAK_GLASS_REASON="AOL equity audit demo" \\
   DECOUPLED_AI_BREAK_GLASS_APPROVER="AOL Chair (synthetic)" \\
   python3 scripts/decoupled_ai_protocol_poc.py
==============================================================================
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import sys
import textwrap
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from scipy import stats

# =============================================================================
# COMPONENT 1 — THE VISUAL WORKFLOW (ASCII ARCHITECTURE MAP)
# =============================================================================

ARCHITECTURE_MAP = r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║     DECOUPLED AI PROTOCOL — AOL SYNTHETIC DEMO (STRICT PLANE SEPARATION)     ║
║                    Nicholls State University (PoC)                           ║
╚══════════════════════════════════════════════════════════════════════════════╝

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  CONTROL PLANE: Structural Metadata / Mock Schema Only                  │
  │  (Cloud — Gemini or equivalent LLM vendor)  [SIMULATED IN THIS PoC]     │
  │                                                                         │
  │   MAY receive: empty column names / dtypes for ONE approved table       │
  │                (key-academic OR demographics — never both linked)       │
  │   Returns    : analysis / visualization CODE LOGIC only                 │
  │   NEVER      : PII, row data, linkage keys, or demo↔academic joins      │
  └───────────────────────────────┬─────────────────────────────────────────┘
                                  │ schema-only (no IPI)
                                  ▼
  ═══════════════════════════════════════════════════════════════════════════
  ║  ████████████████  AIR GAP / TRUST BOUNDARY  ████████████████████████  ║
  ║  No education records cross this line. No outbound data plane traffic. ║
  ═══════════════════════════════════════════════════════════════════════════
                                  │
                                  ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  DATA PLANE: Sealed Local Execution Environment (No Internet Outbound)  │
  │                                                                         │
  │   ┌─ identity_pii.csv ──────┐  Disney names + emails (PII vault)        │
  │   │  opaque_id_pii          │  NEVER sent to Control Plane              │
  │   └─────────────────────────┘                                           │
  │   ┌─ demographics.csv ──────┐  age/gender/race/residency                │
  │   │  opaque_id_demo (≠key)  │  shuffled + synthpop-style                │
  │   └─────────────────────────┘                                           │
  │   ┌─ key_academic.csv ──────┐  GPA, ETS, program_of_study               │
  │   │  opaque_id_key (≠demo)  │  shuffled + synthpop-style                │
  │   └─────────────────────────┘                                           │
  │   ┌─ linkage_vault.json ────┐  sealed join map — BREAK-GLASS only       │
  │   │  + break_glass_log.jsonl│  local authorization audit trail          │
  │   └─────────────────────────┘                                           │
  └─────────────────────────────────────────────────────────────────────────┘

  RULE: Demographics × key-academic correlations are BLOCKED unless break-glass
        authorization is logged. Ordinary AOL trends (GPA by program; GPA~ETS)
        use the key-academic table alone — no demographic linkage required.
"""


# =============================================================================
# PROTOCOL CONSTANTS
# =============================================================================

PROTOCOL_NAME = "Decoupled AI Protocol"
PROTOCOL_VERSION = "1.1.0-AOL-PoC"
INSTITUTION = "Nicholls State University"
N_CASES = 100
RNG_SEED = 20260717

PROGRAMS = (
    "Accounting",
    "Management",
    "Marketing",
    "Finance",
    "Computer Information Systems",
)
GENDERS = ("Woman", "Man", "Nonbinary", "Prefer not to say")
RACE_ETH = (
    "White",
    "Black or African American",
    "Hispanic or Latino",
    "Asian",
    "Two or more races",
    "Prefer not to say",
)
AGE_BANDS = ("18-20", "21-23", "24-29", "30+")
RESIDENCY = ("In-state", "Out-of-state", "International")

# Synthetic PII stand-ins only — Disney characters (NOT real students).
DISNEY_FIRST = (
    "Mickey", "Minnie", "Donald", "Daisy", "Goofy", "Pluto", "Ariel", "Belle",
    "Mulan", "Tiana", "Moana", "Elsa", "Anna", "Olaf", "Simba", "Nala",
    "Buzz", "Woody", "Jessie", "Rex", "Stitch", "Lilo", "Maui", "Rapunzel",
    "Merida", "Pocahontas", "Aladdin", "Jasmine", "Genie", "Hercules",
    "Megara", "Cinderella", "Aurora", "Snow", "Peter", "Wendy", "Hook",
    "Tinker", "Baymax", "Hiro", "Judy", "Nick", "Remy", "Linguini", "WallE",
    "Eve", "Miguel", "Hector", "Coco", "Luca",
)
DISNEY_LAST = (
    "Mouse", "Duck", "Dog", "Beast", "Lion", "Lightyear", "Pride", "Andersen",
    "Ocean", "Bayou", "Enchanted", "Galaxy", "Pixie", "Neverland", "Hamada",
    "Hopps", "Wilde", "Rivera", "Paguro", "Starkiller",
)

FORBIDDEN_NETWORK_CLIENTS = frozenset(
    {
        "requests", "httpx", "aiohttp", "paramiko", "google.genai",
        "google.generativeai", "openai", "anthropic", "boto3", "botocore",
    }
)
FORBIDDEN_SOURCE_IMPORT_ROOTS = frozenset(
    {
        "requests", "httpx", "aiohttp", "urllib", "urllib3", "http", "socket",
        "ftplib", "smtplib", "paramiko", "openai", "anthropic", "boto3",
        "botocore", "google",
    }
)

ARTIFACT_DIRNAME = "decoupled_ai_poc_artifacts"


# =============================================================================
# ARTIFACT PATHS / HELPERS
# =============================================================================

def artifact_dir() -> Path:
    root = Path(__file__).resolve().parent / ARTIFACT_DIRNAME
    root.mkdir(parents=True, exist_ok=True)
    return root


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def _opaque_id(prefix: str, n: int, rng: np.random.Generator) -> List[str]:
    """Generate unlinkable opaque IDs (no sequential student-number pattern)."""
    return [f"{prefix}_{uuid.UUID(bytes=rng.bytes(16), version=4).hex[:12]}" for _ in range(n)]


def print_architecture() -> None:
    print(ARCHITECTURE_MAP)


def schema_dict(df: pd.DataFrame) -> Dict[str, str]:
    return {c: str(t) for c, t in df.dtypes.items()}


def empty_schema_frame(columns_dtypes: Dict[str, str]) -> pd.DataFrame:
    return pd.DataFrame({c: pd.Series(dtype=d) for c, d in columns_dtypes.items()})


# =============================================================================
# SYNTHETIC MASTER DATASET (local generation only)
# =============================================================================

def generate_master_synthetic(n: int = N_CASES, seed: int = RNG_SEED) -> pd.DataFrame:
    """
    Build a linked synthetic master frame for PoC generation.

    IMPORTANT: This master exists only long enough to emit unlinked analysis
    tables + a sealed linkage vault. Disney names/emails are synthetic PII
    stand-ins proving how real identifiers would be vaulted — they are NOT
    real students and must never be sent to a cloud AI.
    """
    rng = np.random.default_rng(seed)

    first = rng.choice(DISNEY_FIRST, size=n)
    last = rng.choice(DISNEY_LAST, size=n)
    # Deduplicate display names lightly
    names = [f"{f} {l}" for f, l in zip(first, last)]
    emails = [
        f"{f.lower()}.{l.lower()}{rng.integers(1, 99)}@synthetic.nicholls.example"
        for f, l in zip(first, last)
    ]

    program = rng.choice(PROGRAMS, size=n, p=[0.18, 0.28, 0.22, 0.16, 0.16])
    gender = rng.choice(GENDERS, size=n, p=[0.48, 0.45, 0.04, 0.03])
    race = rng.choice(RACE_ETH, size=n, p=[0.55, 0.22, 0.10, 0.05, 0.05, 0.03])
    age_band = rng.choice(AGE_BANDS, size=n, p=[0.25, 0.45, 0.20, 0.10])
    residency = rng.choice(RESIDENCY, size=n, p=[0.78, 0.14, 0.08])

    # GPA / ETS with mild program effects (illustrative AOL signal only)
    prog_gpa_shift = {
        "Accounting": 0.05,
        "Management": 0.00,
        "Marketing": -0.02,
        "Finance": 0.08,
        "Computer Information Systems": 0.03,
    }
    base_gpa = rng.normal(3.05, 0.45, size=n)
    gpa = np.clip(
        base_gpa + np.array([prog_gpa_shift[p] for p in program]),
        1.5,
        4.0,
    )
    # ETS Major Field Test-style scale (~120–200); correlated with GPA
    ets = np.clip(
        140 + 12 * (gpa - 3.0) + rng.normal(0, 8, size=n),
        120,
        200,
    )

    master_id = [f"MASTER_{i:04d}" for i in range(n)]
    return pd.DataFrame(
        {
            "master_id": master_id,
            "disney_name": names,
            "email": emails,
            "age_band": age_band,
            "gender": gender,
            "race_ethnicity": race,
            "residency": residency,
            "program_of_study": program,
            "gpa": np.round(gpa, 2),
            "ets_score": np.round(ets, 1),
        }
    )


# =============================================================================
# SYNTHPOP-STYLE SYNTHESIS + UNLINKING
# =============================================================================

def synthpop_style_numeric(
    series: pd.Series,
    rng: np.random.Generator,
    noise_frac: float = 0.08,
) -> pd.Series:
    """
    Lightweight synthpop-style perturbation for continuous variables:
    rank-preserving jitter + small Gaussian noise scaled to sample SD.
    Preserves approximate marginal trends without exact row fidelity.
    """
    values = series.to_numpy(dtype=float).copy()
    sd = float(np.std(values)) or 1.0
    noise = rng.normal(0.0, noise_frac * sd, size=len(values))
    # Rank swap of a minority of values (local confidentiality booster)
    n_swap = max(1, int(0.15 * len(values)))
    idx = rng.choice(len(values), size=n_swap, replace=False)
    swapped = values[idx].copy()
    rng.shuffle(swapped)
    values[idx] = swapped
    return pd.Series(np.round(values + noise, 2), index=series.index)


def synthpop_style_categorical(series: pd.Series, rng: np.random.Generator) -> pd.Series:
    """
    Marginal-preserving categorical synthesis: resample from empirical
    frequencies (synthpop-like cart/sample approximation for PoC).
    """
    probs = series.value_counts(normalize=True)
    drawn = rng.choice(probs.index.to_numpy(), size=len(series), p=probs.to_numpy())
    return pd.Series(drawn, index=series.index)


@dataclass
class UnlinkedBundles:
    """Ordinary-use tables (unlinkable) + sealed vault materials."""

    identity_pii: pd.DataFrame
    demographics: pd.DataFrame
    key_academic: pd.DataFrame
    demographics_synth: pd.DataFrame
    key_academic_synth: pd.DataFrame
    linkage_vault: Dict[str, Any]
    master_preview_cols: List[str] = field(
        default_factory=lambda: [
            "master_id", "program_of_study", "gpa", "ets_score",
            "age_band", "gender",  # preview only in local console if needed
        ]
    )


def build_unlinked_bundles(master: pd.DataFrame, seed: int = RNG_SEED) -> UnlinkedBundles:
    """
    Split master into:
      • identity_pii (PII vault)
      • demographics / key_academic (independent IDs + independent shuffles)
      • synthpop-style variants of demo + key tables
      • sealed linkage_vault mapping master_id → the three opaque IDs

    Ordinary analysts receive shuffled tables whose row orders and IDs do not
    align. Synthpop-style copies further defeat accidental recombination by
    sort/match on quasi-identifiers while retaining communicable trends.
    """
    rng = np.random.default_rng(seed + 7)
    n = len(master)

    id_pii = _opaque_id("PII", n, rng)
    id_demo = _opaque_id("DEM", n, rng)
    id_key = _opaque_id("KEY", n, rng)

    identity = pd.DataFrame(
        {
            "opaque_id_pii": id_pii,
            "disney_name": master["disney_name"].to_numpy(),
            "email": master["email"].to_numpy(),
        }
    )
    demographics = pd.DataFrame(
        {
            "opaque_id_demo": id_demo,
            "age_band": master["age_band"].to_numpy(),
            "gender": master["gender"].to_numpy(),
            "race_ethnicity": master["race_ethnicity"].to_numpy(),
            "residency": master["residency"].to_numpy(),
        }
    )
    key_academic = pd.DataFrame(
        {
            "opaque_id_key": id_key,
            "program_of_study": master["program_of_study"].to_numpy(),
            "gpa": master["gpa"].to_numpy(),
            "ets_score": master["ets_score"].to_numpy(),
        }
    )

    # Independent shuffles — destroy row alignment across files
    identity = identity.sample(frac=1.0, random_state=int(rng.integers(0, 1_000_000))).reset_index(drop=True)
    demographics = demographics.sample(frac=1.0, random_state=int(rng.integers(0, 1_000_000))).reset_index(drop=True)
    key_academic = key_academic.sample(frac=1.0, random_state=int(rng.integers(0, 1_000_000))).reset_index(drop=True)

    # Synthpop-style copies (trend-communicating, recombination-resistant)
    demo_s = demographics.copy()
    for col in ("age_band", "gender", "race_ethnicity", "residency"):
        demo_s[col] = synthpop_style_categorical(demo_s[col], rng)
    demo_s["opaque_id_demo"] = _opaque_id("DEMS", n, rng)
    demo_s = demo_s.sample(frac=1.0, random_state=int(rng.integers(0, 1_000_000))).reset_index(drop=True)

    key_s = key_academic.copy()
    key_s["program_of_study"] = synthpop_style_categorical(key_s["program_of_study"], rng)
    key_s["gpa"] = synthpop_style_numeric(key_s["gpa"], rng).clip(1.5, 4.0)
    key_s["ets_score"] = synthpop_style_numeric(key_s["ets_score"], rng).clip(120, 200)
    key_s["opaque_id_key"] = _opaque_id("KEYS", n, rng)
    key_s = key_s.sample(frac=1.0, random_state=int(rng.integers(0, 1_000_000))).reset_index(drop=True)

    vault = {
        "created_utc": _utc_now(),
        "n": n,
        "note": (
            "SEALED LINKAGE VAULT — local only. Maps master_id to opaque IDs. "
            "Use requires break-glass authorization. Never transmit to Control Plane."
        ),
        "links": [
            {
                "master_id": mid,
                "opaque_id_pii": p,
                "opaque_id_demo": d,
                "opaque_id_key": k,
            }
            for mid, p, d, k in zip(
                master["master_id"].tolist(),
                id_pii,
                id_demo,
                id_key,
            )
        ],
        # Hash of master content for integrity / audit (not reversible to PII)
        "master_content_sha256": hashlib.sha256(
            pd.util.hash_pandas_object(master, index=True).values.tobytes()
        ).hexdigest(),
    }

    return UnlinkedBundles(
        identity_pii=identity,
        demographics=demographics,
        key_academic=key_academic,
        demographics_synth=demo_s,
        key_academic_synth=key_s,
        linkage_vault=vault,
    )


def write_artifacts(bundles: UnlinkedBundles) -> Dict[str, Path]:
    """Persist unlinked tables + sealed vault under local artifacts directory."""
    out = artifact_dir()
    paths = {
        "identity_pii": out / "identity_pii.csv",
        "demographics": out / "demographics.csv",
        "key_academic": out / "key_academic.csv",
        "demographics_synth": out / "demographics_synthpop.csv",
        "key_academic_synth": out / "key_academic_synthpop.csv",
        "linkage_vault": out / "linkage_vault.json",
        "break_glass_log": out / "break_glass_authorization_log.jsonl",
    }
    bundles.identity_pii.to_csv(paths["identity_pii"], index=False)
    bundles.demographics.to_csv(paths["demographics"], index=False)
    bundles.key_academic.to_csv(paths["key_academic"], index=False)
    bundles.demographics_synth.to_csv(paths["demographics_synth"], index=False)
    bundles.key_academic_synth.to_csv(paths["key_academic_synth"], index=False)
    with open(paths["linkage_vault"], "w", encoding="utf-8") as fh:
        json.dump(bundles.linkage_vault, fh, indent=2)
    # Ensure log file exists
    paths["break_glass_log"].touch(exist_ok=True)
    return paths


def demonstrate_unlinkability(bundles: UnlinkedBundles) -> None:
    """Show that ordinary tables do not share join keys or row alignment."""
    print("\n" + "─" * 78)
    print(" DATA PARTITIONING & UNLINKABILITY CHECK")
    print("─" * 78)
    d, k = bundles.demographics, bundles.key_academic
    print(f"  demographics rows     : {len(d)}  cols={list(d.columns)}")
    print(f"  key_academic rows     : {len(k)}  cols={list(k.columns)}")
    print(f"  identity_pii rows     : {len(bundles.identity_pii)}  (PII vault — local only)")
    print()
    shared = set(d.columns) & set(k.columns)
    print(f"  Shared column names across demo↔key : {shared or '∅ (none)'}")
    print(
        "  Opaque ID namespaces differ         : "
        f"demo={d['opaque_id_demo'].iloc[0][:7]}…  key={k['opaque_id_key'].iloc[0][:7]}…"
    )
    # Row-order alignment test on a quasi-identifier substitute: impossible
    # without vault; show GPA distribution still communicable on synth table.
    synth = bundles.key_academic_synth
    print()
    print("  Synthpop-style key table — GPA by program (communicable trends):")
    trend = (
        synth.groupby("program_of_study", observed=True)["gpa"]
        .agg(["count", "mean", "std"])
        .round(3)
        .sort_values("mean", ascending=False)
    )
    print(textwrap.indent(trend.to_string(), "    "))
    print()
    print(
        "  Interpretation: AOL chairs can discuss program-level GPA patterns\n"
        "  from the key (or synthpop) table without any demographic linkage.\n"
        "  Recombining demo↔key without the sealed vault is not supported."
    )


# =============================================================================
# CONTROL PLANE SIMULATION (no real cloud calls)
# =============================================================================

@dataclass
class ControlPlaneExchange:
    """What would be sent to / received from a cloud AI (simulated)."""

    research_question: str
    approved: bool
    block_reason: str
    schema_exposed_to_ai: Dict[str, str]
    sample_prompt_to_ai: str
    sample_code_logic_returned: str
    local_data_used: str
    pii_exposed: bool


def simulate_control_plane(exchange: ControlPlaneExchange) -> None:
    print("\n" + "─" * 78)
    print(" CONTROL PLANE SIMULATION — What the AI sees vs what stays local")
    print("─" * 78)
    status = "APPROVED FOR SCHEMA-ONLY ASSIST" if exchange.approved else "BLOCKED"
    print(f"  Research question : {exchange.research_question}")
    print(f"  Gate decision     : {status}")
    if not exchange.approved:
        print(f"  Block reason      : {exchange.block_reason}")
    print(f"  PII exposed to AI : {exchange.pii_exposed}")
    print(f"  Local data used   : {exchange.local_data_used}")
    print()
    print("  Schema exposed to Control Plane (empty structure only):")
    if exchange.schema_exposed_to_ai:
        for col, dtype in exchange.schema_exposed_to_ai.items():
            print(f"    • {col}: {dtype}")
    else:
        print("    • (none — request refused before schema share)")
    print()
    print("  --- Simulated prompt TO cloud AI (metadata only) ---")
    print(textwrap.indent(exchange.sample_prompt_to_ai.strip(), "  "))
    print()
    print("  --- Simulated code logic FROM cloud AI (no data) ---")
    print(textwrap.indent(exchange.sample_code_logic_returned.strip(), "  "))


def build_aol_control_plane_scenarios(
    key_df: pd.DataFrame,
    demo_df: pd.DataFrame,
) -> List[ControlPlaneExchange]:
    """Illustrate allowed AOL analyses vs blocked demo↔outcome linkage."""
    key_schema = schema_dict(empty_schema_frame(schema_dict(key_df.drop(columns=["opaque_id_key"], errors="ignore"))))
    # Prefer explicit academic columns only for AI schema
    key_schema = {
        "program_of_study": "object",
        "gpa": "float64",
        "ets_score": "float64",
    }
    demo_schema = {
        "age_band": "object",
        "gender": "object",
        "race_ethnicity": "object",
        "residency": "object",
    }

    scenarios = [
        ControlPlaneExchange(
            research_question="Compare mean GPA across degree programs (AOL group trend).",
            approved=True,
            block_reason="",
            schema_exposed_to_ai=key_schema,
            sample_prompt_to_ai=f"""
You are assisting with code logic only. Do NOT request row data.
Schema (empty): {json.dumps(key_schema)}
Task: pandas groupby program_of_study → mean/std/count of gpa.
Return only Python code using local DataFrame `key_academic`.
""",
            sample_code_logic_returned="""
summary = (
    key_academic.groupby("program_of_study")["gpa"]
    .agg(["count", "mean", "std"])
    .sort_values("mean", ascending=False)
)
print(summary)
""",
            local_data_used="key_academic.csv (or key_academic_synthpop.csv)",
            pii_exposed=False,
        ),
        ControlPlaneExchange(
            research_question="Correlate GPA with ETS Major Field Test scores.",
            approved=True,
            block_reason="",
            schema_exposed_to_ai={"gpa": "float64", "ets_score": "float64"},
            sample_prompt_to_ai="""
Schema (empty): {"gpa": "float64", "ets_score": "float64"}
Task: Pearson correlation and simple OLS of ets_score ~ gpa using scipy/numpy.
No demographics. No identifiers. Return code only.
""",
            sample_code_logic_returned="""
from scipy import stats
import numpy as np
r, p = stats.pearsonr(key_academic["gpa"], key_academic["ets_score"])
X = np.column_stack([np.ones(len(key_academic)), key_academic["gpa"]])
beta, *_ = np.linalg.lstsq(X, key_academic["ets_score"], rcond=None)
print({"pearson_r": r, "p": p, "intercept": beta[0], "slope_gpa": beta[1]})
""",
            local_data_used="key_academic.csv (GPA + ETS only)",
            pii_exposed=False,
        ),
        ControlPlaneExchange(
            research_question="Correlate gender (demographic) with GPA (key outcome).",
            approved=False,
            block_reason=(
                "Demographics↔key-academic linkage requires BREAK-GLASS. "
                "Ordinary Control Plane assist is refused; no joint schema shared."
            ),
            schema_exposed_to_ai={},
            sample_prompt_to_ai="""
[NOT SENT] Joint schema including gender + gpa would enable sensitive
equity linkage. Protocol withholds schema until break-glass authorization
is recorded in the local audit log.
""",
            sample_code_logic_returned="""
# No code returned. Researcher must invoke break-glass locally, then
# re-request schema-only assist on the AUTHORIZED linked extract only.
""",
            local_data_used="none (blocked)",
            pii_exposed=False,
        ),
        ControlPlaneExchange(
            research_question="Draft a demographic summary chart (demographics table only).",
            approved=True,
            block_reason="",
            schema_exposed_to_ai=demo_schema,
            sample_prompt_to_ai=f"""
Schema (empty): {json.dumps(demo_schema)}
Task: frequency tables for gender and residency. No academic outcomes.
""",
            sample_code_logic_returned="""
print(demographics["gender"].value_counts(normalize=True).round(3))
print(demographics["residency"].value_counts(normalize=True).round(3))
""",
            local_data_used="demographics.csv (no GPA/ETS)",
            pii_exposed=False,
        ),
    ]
    return scenarios


# =============================================================================
# DATA PLANE ANALYSES (allowed paths)
# =============================================================================

def run_gpa_by_program(key_df: pd.DataFrame) -> pd.DataFrame:
    return (
        key_df.groupby("program_of_study", observed=True)["gpa"]
        .agg(n="count", mean_gpa="mean", sd_gpa="std")
        .round(3)
        .sort_values("mean_gpa", ascending=False)
    )


def run_gpa_ets_correlation(key_df: pd.DataFrame) -> Dict[str, float]:
    r, p = stats.pearsonr(key_df["gpa"], key_df["ets_score"])
    x = np.column_stack([np.ones(len(key_df)), key_df["gpa"].to_numpy()])
    y = key_df["ets_score"].to_numpy()
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)
    return {
        "n": float(len(key_df)),
        "pearson_r": float(r),
        "p_value": float(p),
        "ols_intercept": float(beta[0]),
        "ols_slope_gpa": float(beta[1]),
    }


def print_allowed_analyses(key_df: pd.DataFrame, key_synth: pd.DataFrame) -> Dict[str, Any]:
    print("\n" + "─" * 78)
    print(" DATA PLANE — ALLOWED AOL ANALYSES (key_academic only; no demos)")
    print("─" * 78)
    print("\n  [Trend] Mean GPA by program_of_study (observed key table):")
    gpa_prog = run_gpa_by_program(key_df)
    print(textwrap.indent(gpa_prog.to_string(), "    "))
    print("\n  [Trend] Same analysis on synthpop-style table (confidentiality-preserving):")
    gpa_prog_s = run_gpa_by_program(key_synth)
    print(textwrap.indent(gpa_prog_s.to_string(), "    "))
    corr = run_gpa_ets_correlation(key_df)
    corr_s = run_gpa_ets_correlation(key_synth)
    print("\n  [Correlation] GPA ↔ ETS (observed key table):")
    print(f"    r = {corr['pearson_r']:.4f}, p = {corr['p_value']:.4g}, "
          f"ETS ≈ {corr['ols_intercept']:.2f} + {corr['ols_slope_gpa']:.2f}·GPA")
    print("  [Correlation] GPA ↔ ETS (synthpop-style table):")
    print(f"    r = {corr_s['pearson_r']:.4f}, p = {corr_s['p_value']:.4g}, "
          f"ETS ≈ {corr_s['ols_intercept']:.2f} + {corr_s['ols_slope_gpa']:.2f}·GPA")
    print(
        "\n  Note: Synthpop-style results communicate the same *direction* of\n"
        "  relationship for stakeholder discussion while reducing exact-row risk."
    )
    return {"gpa_by_program": gpa_prog, "correlation": corr, "correlation_synth": corr_s}


# =============================================================================
# BREAK-GLASS AUTHORIZATION (logged)
# =============================================================================

@dataclass
class BreakGlassRecord:
    timestamp_utc: str
    approved: bool
    approver: str
    reason: str
    analysis_requested: str
    tables_linked: List[str]
    authorization_id: str


def append_break_glass_log(record: BreakGlassRecord, log_path: Path) -> None:
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(asdict(record)) + "\n")


def request_break_glass(log_path: Path) -> Optional[BreakGlassRecord]:
    """
    Interactive (or env-driven) break-glass authorization.

    Linking demographics to key academic outcomes is prohibited unless this
    gate succeeds and a durable local audit record is written.
    """
    print("\n" + "─" * 78)
    print(" BREAK-GLASS GATE — Demographics × Key Academic Linkage")
    print("─" * 78)
    print(
        textwrap.dedent(
            """
            Ordinary AOL monitoring does NOT require this gate.
            Invoke break-glass ONLY for authorized equity / compliance reviews
            that truly need demographic linkage to academic outcomes.

            This action will be logged locally (approver, reason, timestamp).
            """
        ).strip()
    )

    env_flag = os.environ.get("DECOUPLED_AI_BREAK_GLASS", "").strip().upper()
    if env_flag in {"YES", "Y", "TRUE", "1"}:
        proceed = "BREAK-GLASS"
        reason = os.environ.get(
            "DECOUPLED_AI_BREAK_GLASS_REASON",
            "CI/demo equity audit (synthetic)",
        ).strip()
        approver = os.environ.get(
            "DECOUPLED_AI_BREAK_GLASS_APPROVER",
            "AOL Chair (synthetic env)",
        ).strip()
        print("  [INFO] Non-interactive break-glass credentials supplied via environment.")
    else:
        try:
            proceed = input(
                "\n  Type BREAK-GLASS to request linkage, or press Enter to skip > "
            ).strip().upper()
        except EOFError:
            proceed = ""
        if proceed != "BREAK-GLASS":
            print("\n  [OK] Break-glass skipped. Demographic↔outcome analyses remain blocked.")
            return None
        try:
            reason = input("  Reason (required) > ").strip()
            approver = input("  Approver name/role (required) > ").strip()
        except EOFError:
            print("  [HALT] Incomplete break-glass attestation.")
            return None

    if not reason or not approver:
        print("  [HALT] Break-glass requires both reason and approver. Denied.")
        denied = BreakGlassRecord(
            timestamp_utc=_utc_now(),
            approved=False,
            approver=approver or "(missing)",
            reason=reason or "(missing)",
            analysis_requested="demographics × GPA/ETS linkage",
            tables_linked=[],
            authorization_id=str(uuid.uuid4()),
        )
        append_break_glass_log(denied, log_path)
        return None

    record = BreakGlassRecord(
        timestamp_utc=_utc_now(),
        approved=True,
        approver=approver,
        reason=reason,
        analysis_requested="demographics × GPA/ETS linkage (synthetic PoC)",
        tables_linked=["demographics", "key_academic", "linkage_vault"],
        authorization_id=str(uuid.uuid4()),
    )
    append_break_glass_log(record, log_path)
    print(f"\n  [AUTHORIZED] Break-glass recorded: {record.authorization_id}")
    print(f"  Log file     : {log_path}")
    return record


def relink_with_vault(
    bundles: UnlinkedBundles,
) -> pd.DataFrame:
    """
    Reconstruct a linked analytic frame using the sealed vault.

    PII columns are intentionally EXCLUDED from the linked analytic extract.
    """
    links = pd.DataFrame(bundles.linkage_vault["links"])
    demo = bundles.demographics.merge(
        links[["opaque_id_demo", "master_id", "opaque_id_key"]],
        on="opaque_id_demo",
        how="inner",
    )
    key = bundles.key_academic.merge(
        links[["opaque_id_key", "master_id"]],
        on="opaque_id_key",
        how="inner",
    )
    linked = demo.merge(
        key.drop(columns=["opaque_id_key"]),
        on="master_id",
        how="inner",
        suffixes=("_demo", "_key"),
    )
    # Drop opaque IDs from analyst-facing linked extract; keep master_id only
    # as an internal synthetic key (still not PII).
    keep = [
        "master_id",
        "age_band",
        "gender",
        "race_ethnicity",
        "residency",
        "program_of_study",
        "gpa",
        "ets_score",
    ]
    return linked[keep]


def run_break_glass_analyses(linked: pd.DataFrame) -> None:
    print("\n" + "─" * 78)
    print(" DATA PLANE — BREAK-GLASS ANALYSES (demographics × outcomes)")
    print("─" * 78)
    print("  Mean GPA by gender (authorized equity view; synthetic data):")
    by_gender = (
        linked.groupby("gender", observed=True)["gpa"]
        .agg(n="count", mean_gpa="mean")
        .round(3)
    )
    print(textwrap.indent(by_gender.to_string(), "    "))
    print("\n  Mean GPA by race_ethnicity (authorized equity view; synthetic data):")
    by_race = (
        linked.groupby("race_ethnicity", observed=True)["gpa"]
        .agg(n="count", mean_gpa="mean")
        .round(3)
    )
    print(textwrap.indent(by_race.to_string(), "    "))
    print(
        "\n  Control Plane note: AFTER break-glass, an AI may receive only the\n"
        "  empty schema of the authorized linked extract (still NO row data,\n"
        "  NO PII). Disney-name/email vault remains sealed."
    )


# =============================================================================
# HUMAN-IN-THE-LOOP (network attestation)
# =============================================================================

def _imported_module_names() -> List[str]:
    return sorted(sys.modules.keys())


def audit_no_forbidden_network_imports() -> Tuple[bool, List[str]]:
    loaded = set(_imported_module_names())
    offenders = sorted(
        m
        for m in FORBIDDEN_NETWORK_CLIENTS
        if m in loaded
        or any(x == m or x.startswith(m + ".") for x in loaded)
    )
    return (len(offenders) == 0, offenders)


def scan_source_for_network_calls(source_path: str) -> Tuple[bool, List[str]]:
    findings: List[str] = []
    with open(source_path, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read(), filename=source_path)

    suspicious_attrs = {
        "urlopen", "urlretrieve", "Session", "GenerativeModel",
        "create_client", "Client",
    }
    network_call_roots = {
        "requests", "httpx", "aiohttp", "urllib", "socket",
        "openai", "anthropic", "genai", "boto3",
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if (
                    alias.name in FORBIDDEN_NETWORK_CLIENTS
                    or root in FORBIDDEN_SOURCE_IMPORT_ROOTS
                ):
                    findings.append(f"import {alias.name} (line {node.lineno})")
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            root = mod.split(".")[0] if mod else ""
            if (
                mod in FORBIDDEN_NETWORK_CLIENTS
                or root in FORBIDDEN_SOURCE_IMPORT_ROOTS
            ):
                findings.append(f"from {mod} import ... (line {node.lineno})")
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                if (
                    func.value.id in network_call_roots
                    and func.attr in suspicious_attrs
                ):
                    findings.append(
                        f"call {func.value.id}.{func.attr}() (line {node.lineno})"
                    )
                if (
                    func.value.id in {"requests", "httpx"}
                    and func.attr in {"get", "post", "put", "delete", "patch", "request"}
                ):
                    findings.append(
                        f"call {func.value.id}.{func.attr}() (line {node.lineno})"
                    )
    return (len(findings) == 0, findings)


def human_in_the_loop_gate(source_path: str) -> None:
    print("\n" + "─" * 78)
    print(" STEP — HUMAN-IN-THE-LOOP VALIDATION (MANDATORY GATE)")
    print("─" * 78)
    print(
        textwrap.dedent(
            """
            PROTOCOL HOLD: Confirm this process initiates NO external API calls
            and will NOT transmit synthetic or real education records to a cloud AI.
            """
        ).strip()
    )
    imports_ok, offenders = audit_no_forbidden_network_imports()
    if imports_ok:
        print("  [PASS] No forbidden network/cloud modules loaded.")
    else:
        print("  [FAIL] Forbidden modules:", ", ".join(offenders))
        sys.exit(2)
    ast_ok, findings = scan_source_for_network_calls(source_path)
    if ast_ok:
        print("  [PASS] AST scan found no forbidden network import/call patterns.")
    else:
        print("  [FAIL] AST findings:")
        for item in findings:
            print(f"         - {item}")
        sys.exit(2)

    env_confirm = os.environ.get("DECOUPLED_AI_HITL_CONFIRM", "").strip().upper()
    if env_confirm in {"YES", "Y", "TRUE", "1"}:
        print("  [INFO] DECOUPLED_AI_HITL_CONFIRM set — accepting attestation.")
        response = "YES"
    else:
        try:
            response = input(
                "\n  Type YES to attest: NO external API/network data egress > "
            ).strip().upper()
        except EOFError:
            print("\n  [HALT] No TTY and no DECOUPLED_AI_HITL_CONFIRM.")
            sys.exit(3)
    if response != "YES":
        print("\n  [HALT] Attestation not confirmed.")
        sys.exit(1)
    print("\n  [OK] Human-in-the-Loop attestation recorded. Proceeding locally.")


# =============================================================================
# COMPONENT 3 — CITI-ALIGNED COMPLIANCE SUMMARY
# =============================================================================

def print_citi_compliance_report(paths: Dict[str, Path], results: Dict[str, Any]) -> None:
    border = "═" * 78
    corr = results.get("correlation", {})
    print("\n" + border)
    print(" CITI-ALIGNED COMPLIANCE SUMMARY — DECOUPLED AI PROTOCOL (AOL PoC)")
    print(border)
    print(
        f"""
  Institution        : {INSTITUTION}
  Protocol           : {PROTOCOL_NAME}  v{PROTOCOL_VERSION}
  Report generated   : {_utc_now()}
  Data classification: SYNTHETIC / DEVELOPMENT — Disney PII stand-ins only

  ┌──────────────────────────────────────────────────────────────────────────┐
  │  DETERMINATION: Cloud AI receives structural metadata ONLY.              │
  │  PII vault sealed. Demo↔outcome linkage requires logged break-glass.     │
  └──────────────────────────────────────────────────────────────────────────┘

  1. CITI PROGRAM — INFORMATION SECURITY ALIGNMENT
     Minimization of Identifiable Private Information (IPI), least privilege,
     and prohibition on unauthorized external transmission are operationalized by:
       • Control Plane schema-only assists (simulated; zero egress in this PoC)
       • Separate demographics vs key-academic tables
       • Unlinking (independent IDs + shuffles) AND synthpop-style synthesis
       • Break-glass authorization log for sensitive linkages
       • PII (names/emails) retained in a local vault never shared with AI

  2. WHAT WAS EXPOSED TO A CLOUD AI IN THIS DESIGN
     • Empty schemas for approved single-table questions (e.g., GPA by program;
       GPA↔ETS; demographics frequencies alone)
     • NOT exposed: Disney-name/email PII, row-level records, linkage vault,
       or joint demo×outcome schemas absent break-glass

  3. AOL ANALYTIC UTILITY PRESERVED
     • GPA-by-program trends runnable on key_academic and synthpop tables
     • GPA↔ETS correlation: r ≈ {corr.get('pearson_r', float('nan')):.3f}
       (synthetic observed table; local Data Plane only)
     • Equity-style demo×GPA views available ONLY after break-glass logging

  4. LOCAL ARTIFACTS (university custody; not transmitted)
     • {paths.get('key_academic')}
     • {paths.get('demographics')}
     • {paths.get('key_academic_synth')}
     • {paths.get('demographics_synth')}
     • {paths.get('identity_pii')}          ← PII vault
     • {paths.get('linkage_vault')}         ← sealed
     • {paths.get('break_glass_log')}       ← authorization audit trail

  5. FERPA / La. R.S. 17:3914
     This PoC uses synthetic data only. The same control pattern is designed
     so that, in production, third-party AI vendors never ingest education
     records or student information — satisfying zero cloud-ingestion liability
     for the Control Plane path described herein.

  STATUS: COMPLIANT WITH DECOUPLED AI PROTOCOL — AOL PoC DEMONSTRATION COMPLETE
"""
    )
    print(border + "\n")


# =============================================================================
# COMPONENT 4 — FORMAL MEMO TO CHIEF IT SECURITY ADMINISTRATOR
# =============================================================================

MEMO_TO_IT_LEADERSHIP = """
--------------------------------------------------------------------------------
MEMORANDUM (INFORMATIONAL NOTIFICATION)
--------------------------------------------------------------------------------

TO:      Chris Usey
         IT Security Administrator
         Nicholls State University

CC:      Sam Cagle
         Chief Information Officer (CIO)
         Nicholls State University

         University Senate (Information Item, as appropriate)
         Human Subjects Institutional Review Board (HSIRB), for awareness
         Assurance of Learning (AOL) leadership (optional routing)

FROM:    [Faculty Researcher / University Senator]
         Nicholls State University

DATE:    [Insert Date]

RE:      Informational Notice — Decoupled AI Protocol for AOL Analytics
         (Schema-Only Cloud Assist; Local Sealed Execution; Break-Glass
         Logging for Demographic Linkage; Zero University Data Asset Ingestion
         by Third-Party AI)

--------------------------------------------------------------------------------

Mr. Usey and Mr. Cagle:

I write to provide formal informational notice that faculty / AOL analytic
workflows under my supervision have adopted the Decoupled AI Protocol. The
protocol separates (a) cloud-assisted generation of analytical code logic from
empty structural schemas from (b) sealed local execution on university-managed
hardware. Third-party AI services do not ingest Nicholls State University data
assets, education records, or Identifiable Private Information (IPI).

I.  PURPOSE OF THIS NOTICE

This memorandum is informational. Because no university data assets are
disclosed to vendors under the Control Plane path, this notice asserts that the
workflow does not introduce a new data-processor relationship requiring further
vendor security review for that limited schema-only use.

II.  PROTOCOL CONTROLS (AOL DEMONSTRATION)

A. Control Plane — Structural metadata / mock schema only (e.g., Gemini)
B. Data Plane — Local pandas/numpy/scipy execution; no outbound analysis egress
C. Table separation — Demographics separated from key academic variables
   (GPA, ETS, program of study); PII held in a local identity vault
D. Unlinking — Independent opaque IDs, independent shuffles, and synthpop-style
   synthesis so ordinary tables cannot be easily recombined
E. Break-glass — Demographic↔outcome linkage requires logged authorization
   (timestamp, approver, reason, authorization ID) before sealed vault use

III.  COMPLIANCE POSTURE

Aligned with FERPA; Louisiana La. R.S. 17:3914; CITI Information Security
standards; and 45 C.F.R. Part 46 stewardship principles. Cloud vendors receive
metadata about structure, not data about persons.

IV.  REQUESTED ACTION

No approval action is requested at this time. Please file this notification for
IT Security and CIO awareness. The proof-of-concept script
`scripts/decoupled_ai_protocol_poc.py` demonstrates the architecture, AOL
synthetic walkthrough, Human-in-the-Loop gate, and break-glass audit log.

Respectfully,

____________________________________________
[Name], Ph.D.
Professor / University Senator
Nicholls State University
[Department]
[Institutional Email]

Enclosure: scripts/decoupled_ai_protocol_poc.py
--------------------------------------------------------------------------------
END OF MEMORANDUM
--------------------------------------------------------------------------------
"""


# =============================================================================
# MAIN ORCHESTRATION
# =============================================================================

def main(argv: Sequence[str] | None = None) -> int:
    _ = argv
    source_path = os.path.abspath(__file__)

    print("\n" + "═" * 78)
    print(f" {PROTOCOL_NAME} — AOL SYNTHETIC PoC  |  {INSTITUTION}")
    print(f" Version {PROTOCOL_VERSION}")
    print("═" * 78)

    print_architecture()
    human_in_the_loop_gate(source_path)

    # --- Generate synthetic master & unlinked bundles ---
    print("\n" + "─" * 78)
    print(f" STEP A — GENERATE SYNTHETIC MASTER (N={N_CASES}) + SPLIT/UNLINK")
    print("─" * 78)
    master = generate_master_synthetic()
    print(
        "  Master includes synthetic PII (Disney names/emails), demographics,\n"
        "  and key AOL variables. Master is NOT written as a single analysis\n"
        "  file for ordinary use — only split/unlinked products + sealed vault."
    )
    print("\n  Sample synthetic PII rows (LOCAL CONSOLE ONLY — never sent to AI):")
    print(textwrap.indent(
        master[["disney_name", "email", "program_of_study", "gpa"]].head(5).to_string(index=False),
        "    ",
    ))

    bundles = build_unlinked_bundles(master)
    paths = write_artifacts(bundles)
    print("\n  Wrote local artifacts:")
    for label, path in paths.items():
        print(f"    • {label:22s} → {path}")

    # Empty schemas that WOULD be shareable with Control Plane
    key_empty = empty_schema_frame(
        {"program_of_study": "object", "gpa": "float64", "ets_score": "float64"}
    )
    demo_empty = empty_schema_frame(
        {
            "age_band": "object",
            "gender": "object",
            "race_ethnicity": "object",
            "residency": "object",
        }
    )
    assert key_empty.empty and demo_empty.empty
    print("\n  Control Plane shareable schemas (EMPTY frames; zero rows):")
    print(f"    key_academic schema : {schema_dict(key_empty)}  shape={key_empty.shape}")
    print(f"    demographics schema : {schema_dict(demo_empty)}  shape={demo_empty.shape}")
    print("    identity_pii schema : NOT SHAREABLE with Control Plane")

    demonstrate_unlinkability(bundles)

    # --- Simulated AI exchanges ---
    for exchange in build_aol_control_plane_scenarios(
        bundles.key_academic, bundles.demographics
    ):
        simulate_control_plane(exchange)

    # --- Allowed local analyses ---
    results = print_allowed_analyses(bundles.key_academic, bundles.key_academic_synth)

    # --- Optional break-glass ---
    bg = request_break_glass(paths["break_glass_log"])
    if bg and bg.approved:
        linked = relink_with_vault(bundles)
        run_break_glass_analyses(linked)
        # Show post-break-glass Control Plane posture
        simulate_control_plane(
            ControlPlaneExchange(
                research_question=(
                    "Post-break-glass: code for mean GPA by gender on AUTHORIZED linked extract."
                ),
                approved=True,
                block_reason="",
                schema_exposed_to_ai={
                    "gender": "object",
                    "gpa": "float64",
                },
                sample_prompt_to_ai="""
AUTHORIZED linked extract schema (empty only):
{"gender": "object", "gpa": "float64"}
Authorization was logged locally before this schema share.
Return groupby code only. Do not request names, emails, or raw rows.
""",
                sample_code_logic_returned="""
print(linked.groupby("gender")["gpa"].agg(["count", "mean"]))
""",
                local_data_used="break-glass linked extract (PII columns excluded)",
                pii_exposed=False,
            )
        )
    else:
        print(
            "\n  [INFO] Equity-style demographic×GPA analyses were not run.\n"
            "         Re-run and enter BREAK-GLASS when prompted, or set\n"
            "         DECOUPLED_AI_BREAK_GLASS=YES with reason/approver env vars."
        )

    print_citi_compliance_report(paths, results)

    print(" FORMAL MEMO ON FILE")
    print("─" * 78)
    print(
        "  Draft informational memorandum to Chris Usey (IT Security\n"
        "  Administrator) and Sam Cagle (CIO) is embedded as\n"
        "  MEMO_TO_IT_LEADERSHIP. It is not transmitted by this program."
    )
    print()
    return 0


# Backward-compatible alias for earlier PoC references
MEMO_TO_CHIEF_IT_SECURITY = MEMO_TO_IT_LEADERSHIP


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
