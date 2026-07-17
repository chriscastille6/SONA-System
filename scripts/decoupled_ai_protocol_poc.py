#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
 DECOUPLED AI PROTOCOL — LOCAL COMPLIANCE & DATA SCIENCE PROOF OF CONCEPT
==============================================================================
 Institution : Nicholls State University
 Classification: DEVELOPMENT / SYNTHETIC DATA ONLY
 Audience     : Faculty researchers, University Senate, IT Security, IRB
 Dependencies: pandas, numpy, scipy  (standard open-source; local execution)
 Network      : NONE. This script performs zero outbound API or cloud calls.

 PURPOSE
 -------
 Operationalize the Decoupled AI Protocol by strictly separating:

   CONTROL PLANE  — Cloud LLM (e.g., Gemini) receives ONLY empty structural
                    metadata / mock schemas and returns analysis *code logic*.
   DATA PLANE     — University-managed hardware executes that code locally
                    against sealed human-subjects / student datasets. No
                    internet outbound. No third-party ingestion of IPI.

 This PoC uses exclusively synthetic, non-identifying mock columns
 (var_a, var_b, score_x). It never loads, logs, or transmits education
 records, student PII, or Identifiable Private Information (IPI).

 LEGAL / COMPLIANCE ANCHORS (informational)
 ------------------------------------------
   • FERPA, 20 U.S.C. § 1232g; 34 C.F.R. Part 99
   • Louisiana La. R.S. 17:3914 (student information privacy)
   • CITI Program — Information Security / Data Security modules
   • 45 C.F.R. Part 46 (Common Rule) — human subjects research principles

 Run (from the repository root — not from ~):
   cd /path/to/SONA-System
   git fetch origin cursor/decoupled-ai-protocol-poc-6005
   git checkout cursor/decoupled-ai-protocol-poc-6005
   python3 -m pip install pandas numpy scipy
   python3 scripts/decoupled_ai_protocol_poc.py
   # At the gate, type: YES

 macOS note: use "python3 -m pip" (Homebrew often has no bare "pip" command).

 Non-interactive confirmation (automation / CI only):
   DECOUPLED_AI_HITL_CONFIRM=YES python3 scripts/decoupled_ai_protocol_poc.py
==============================================================================
"""

from __future__ import annotations

import ast
import os
import sys
import textwrap
from datetime import datetime, timezone
from typing import Any, Dict, List, Sequence, Tuple

# ---------------------------------------------------------------------------
# DATA PLANE LIBRARIES ONLY — standard open-source scientific stack.
# Deliberately NO imports of: requests, urllib.request, httpx, aiohttp,
# google.genai, openai, anthropic, socket clients, or any cloud SDK.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
from scipy import stats

# =============================================================================
# COMPONENT 1 — THE VISUAL WORKFLOW (ASCII ARCHITECTURE MAP)
# =============================================================================
#
# Printed at runtime via ARCHITECTURE_MAP (see print_architecture()). Also
# retained here as the canonical reference diagram for code review and Senate /
# IT Security briefings.
#
ARCHITECTURE_MAP = r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          DECOUPLED AI PROTOCOL — STRICT PLANE SEPARATION DIAGRAM             ║
║                    Nicholls State University (PoC)                           ║
╚══════════════════════════════════════════════════════════════════════════════╝

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  CONTROL PLANE: Structural Metadata / Mock Schema Only                  │
  │  (Cloud — Gemini or equivalent LLM vendor)                              │
  │                                                                         │
  │   • Receives: empty DataFrame column names / dtypes / mock schema JSON  │
  │   • Receives: research question in abstract, non-identifying form       │
  │   • Returns : structural analysis CODE LOGIC only (no data in / out)    │
  │   • NEVER receives: student names, IDs, emails, grades, education       │
  │                     records, or any Identifiable Private Information    │
  └───────────────────────────────┬─────────────────────────────────────────┘
                                  │
                    schema-only   │   generated code artifacts
                    (no IPI)      │   (logic only; reviewed locally)
                                  ▼
  ═══════════════════════════════════════════════════════════════════════════
  ║  ████████████████  AIR GAP / TRUST BOUNDARY  ████████████████████████  ║
  ║  No education records cross this line. No outbound data plane traffic. ║
  ═══════════════════════════════════════════════════════════════════════════
                                  │
                                  ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  DATA PLANE: Sealed Local Execution Environment (No Internet Outbound)  │
  │  (University-managed hardware — faculty workstation / campus VM)        │
  │                                                                         │
  │   • Loads sealed local datasets under PI / IRB custody                  │
  │   • Executes cloud-generated logic ONLY after Human-in-the-Loop review  │
  │   • Libraries: pandas · numpy · scipy (local, open-source)              │
  │   • Outputs: aggregate statistics retained under university control     │
  │   • Network posture: outbound internet DISABLED for analysis session    │
  └─────────────────────────────────────────────────────────────────────────┘

  COMPLIANCE ASSERTION
  --------------------
  Cloud sees structure. Campus sees subjects. Never the reverse.
"""


# =============================================================================
# PROTOCOL CONSTANTS
# =============================================================================

PROTOCOL_NAME = "Decoupled AI Protocol"
PROTOCOL_VERSION = "1.0.0-PoC"
INSTITUTION = "Nicholls State University"

# Intentional HTTP / cloud SDK clients that must NEVER be loaded for Data Plane
# analysis. (Stdlib modules such as socket/urllib may appear transitively via
# pandas/numpy/scipy; those are not treated as Control Plane egress clients.)
FORBIDDEN_NETWORK_CLIENTS = frozenset(
    {
        "requests",
        "httpx",
        "aiohttp",
        "paramiko",
        "google.genai",
        "google.generativeai",
        "openai",
        "anthropic",
        "boto3",
        "botocore",
    }
)

# Imports that researcher-authored analysis code must not declare explicitly
# (caught via AST of this script / pasted cloud-generated logic).
FORBIDDEN_SOURCE_IMPORT_ROOTS = frozenset(
    {
        "requests",
        "httpx",
        "aiohttp",
        "urllib",
        "urllib3",
        "http",
        "socket",
        "ftplib",
        "smtplib",
        "paramiko",
        "openai",
        "anthropic",
        "boto3",
        "botocore",
        "google",  # blocks google.genai / generativeai in researcher source
    }
)

# Structural schema shared with the Control Plane (cloud). Column names only.
# This is the ONLY artifact that would ever leave the university boundary.
MOCK_SCHEMA_SHARED_WITH_CLOUD: Dict[str, str] = {
    "var_a": "float64",
    "var_b": "float64",
    "score_x": "float64",
}


# =============================================================================
# COMPONENT 2 — COMPLIANCE-FIRST CODE GENERATION (THE PYTHON DEMO)
# =============================================================================


def print_architecture() -> None:
    """Emit the ASCII architecture map to the terminal."""
    print(ARCHITECTURE_MAP)


# ---------------------------------------------------------------------------
# STEP A — Mock structural schema (Control Plane artifact)
# ---------------------------------------------------------------------------

def build_mock_structural_schema() -> pd.DataFrame:
    """
    Step A: Define a purely mock, empty pandas DataFrame structure.

    COMPLIANCE RATIONALE
    --------------------
    Only this *structural* schema (column names + dtypes, with zero rows of
    real observations) is what a researcher may share with a cloud LLM such
    as Gemini in the Control Plane.

    Proving zero FERPA / La. R.S. 17:3914 exposure:
      • No student names, IDs, emails, SSNs, or institutional identifiers.
      • No grades, course enrollments, or education-record fields.
      • No rows of observational / human-subjects data.
      • Generic abstract column labels (var_a, var_b, score_x) convey
        statistical roles only — not directory information or IPI.

    The cloud model therefore assists with *code structure* (e.g., which
    scipy routine to call) without ever ingesting university data assets.
    """
    # Empty frame: shape (0, n) — structure without substance.
    mock_df = pd.DataFrame(
        {
            "var_a": pd.Series(dtype="float64"),
            "var_b": pd.Series(dtype="float64"),
            "score_x": pd.Series(dtype="float64"),
        }
    )

    assert mock_df.empty, "Structural schema must contain ZERO rows of subject data."
    assert list(mock_df.columns) == ["var_a", "var_b", "score_x"]
    assert set(mock_df.dtypes.astype(str)) == {"float64"}

    print("\n" + "─" * 78)
    print(" STEP A — CONTROL PLANE ARTIFACT: Empty Structural Mock Schema")
    print("─" * 78)
    print(
        textwrap.dedent(
            """
            The following schema is the ONLY metadata that would be shared with
            Gemini (or any third-party AI) to obtain analysis code logic.
            It contains NO real student data and NO Identifiable Private
            Information (IPI). FERPA education records and La. R.S. 17:3914
            protected student information are structurally incapable of
            exposure because the frame has zero rows and abstract labels.
            """
        ).strip()
    )
    print()
    print(f"  Columns : {list(mock_df.columns)}")
    print(f"  Dtypes  : { {c: str(t) for c, t in mock_df.dtypes.items()} }")
    print(f"  Shape   : {mock_df.shape}  ← (rows=0, cols=3) — empty by design")
    print(f"  Empty?  : {mock_df.empty}")
    print()
    print("  Schema JSON equivalent shared with Control Plane:")
    for col, dtype in MOCK_SCHEMA_SHARED_WITH_CLOUD.items():
        print(f"    {{ \"name\": \"{col}\", \"dtype\": \"{dtype}\" }}")
    print()
    return mock_df


# ---------------------------------------------------------------------------
# STEP B — Simulated local analysis on synthetic Data Plane data
# ---------------------------------------------------------------------------

def generate_synthetic_local_observations(
    n: int = 120,
    seed: int = 20260717,
) -> pd.DataFrame:
    """
    Generate SYNTHETIC local observations for the PoC Data Plane demo.

    IMPORTANT: In production research, this function would be replaced by a
    local loader that reads sealed university-managed files (never uploaded
    to a cloud LLM). Here we use a fixed RNG seed and abstract variables so
    the PoC remains DEVELOPMENT-tier with zero real subject data.
    """
    rng = np.random.default_rng(seed)
    var_a = rng.normal(loc=50.0, scale=10.0, size=n)
    var_b = rng.normal(loc=0.0, scale=1.0, size=n)
    # Linear signal + noise — illustrative only; not a real study outcome.
    score_x = 2.5 + 0.35 * var_a + 1.1 * var_b + rng.normal(0.0, 3.0, size=n)
    return pd.DataFrame({"var_a": var_a, "var_b": var_b, "score_x": score_x})


def run_local_correlation_and_regression(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Step B: Execute a localized correlation + OLS-style analysis with scipy.

    This simulates the Data Plane execution of code whose *structure* was
    suggested by the Control Plane, but which runs entirely on local hardware
    using open-source libraries (pandas, numpy, scipy). No network I/O occurs.
    """
    if df.empty:
        raise ValueError("Data Plane analysis requires local observations.")

    # Pearson correlations (local)
    r_a_x, p_a_x = stats.pearsonr(df["var_a"], df["score_x"])
    r_b_x, p_b_x = stats.pearsonr(df["var_b"], df["score_x"])

    # Multiple linear regression via ordinary least squares (scipy.linalg)
    # Design matrix: intercept + var_a + var_b
    x_mat = np.column_stack(
        [np.ones(len(df)), df["var_a"].to_numpy(), df["var_b"].to_numpy()]
    )
    y = df["score_x"].to_numpy()
    coeffs, residuals, rank, singular = np.linalg.lstsq(x_mat, y, rcond=None)
    y_hat = x_mat @ coeffs
    ss_res = float(np.sum((y - y_hat) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r_squared = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else float("nan")

    results: Dict[str, Any] = {
        "n": int(len(df)),
        "pearson_var_a_score_x": {"r": float(r_a_x), "p": float(p_a_x)},
        "pearson_var_b_score_x": {"r": float(r_b_x), "p": float(p_b_x)},
        "ols_coefficients": {
            "intercept": float(coeffs[0]),
            "var_a": float(coeffs[1]),
            "var_b": float(coeffs[2]),
        },
        "ols_r_squared": float(r_squared),
        "ols_rank": int(rank),
        "execution_locus": "LOCAL_DATA_PLANE",
        "libraries": ["pandas", "numpy", "scipy"],
    }
    return results


def print_analysis_results(results: Dict[str, Any]) -> None:
    """Pretty-print local analysis results (aggregate statistics only)."""
    print("\n" + "─" * 78)
    print(" STEP B — DATA PLANE: Localized Correlation & Regression (Synthetic)")
    print("─" * 78)
    print(f"  Execution locus : {results['execution_locus']}")
    print(f"  Libraries       : {', '.join(results['libraries'])}")
    print(f"  N (synthetic)   : {results['n']}")
    print()
    pa = results["pearson_var_a_score_x"]
    pb = results["pearson_var_b_score_x"]
    print("  Pearson correlations")
    print(f"    var_a ↔ score_x : r = {pa['r']:.4f},  p = {pa['p']:.4g}")
    print(f"    var_b ↔ score_x : r = {pb['r']:.4f},  p = {pb['p']:.4g}")
    print()
    ols = results["ols_coefficients"]
    print("  OLS: score_x ~ intercept + var_a + var_b")
    print(f"    intercept = {ols['intercept']:.4f}")
    print(f"    β_var_a   = {ols['var_a']:.4f}")
    print(f"    β_var_b   = {ols['var_b']:.4f}")
    print(f"    R²        = {results['ols_r_squared']:.4f}")
    print()
    print(
        "  NOTE: Results above are derived from SYNTHETIC local observations\n"
        "  solely to demonstrate sealed Data Plane execution. They are not\n"
        "  research findings and contain no human-subjects or student data."
    )


# ---------------------------------------------------------------------------
# STEP C — Mandatory Human-in-the-Loop validation gate
# ---------------------------------------------------------------------------

def _imported_module_names() -> List[str]:
    """Return names of modules currently present in sys.modules."""
    return sorted(sys.modules.keys())


def audit_no_forbidden_network_imports() -> Tuple[bool, List[str]]:
    """
    Ensure intentional HTTP / cloud SDK clients are not loaded before Data
    Plane analysis proceeds. Transitive stdlib imports from pandas/numpy/scipy
    are ignored; those libraries do not constitute vendor data egress.
    """
    loaded = set(_imported_module_names())
    offenders = sorted(
        m
        for m in FORBIDDEN_NETWORK_CLIENTS
        if m in loaded
        or any(
            loaded_name == m or loaded_name.startswith(m + ".")
            for loaded_name in loaded
        )
    )
    return (len(offenders) == 0, offenders)


def scan_source_for_network_calls(source_path: str) -> Tuple[bool, List[str]]:
    """
    Parse this script's AST and flag researcher-declared network imports or
    obvious network-oriented call patterns.

    This is a researcher-facing safeguard, not a substitute for host firewall
    policy. It reinforces the Human-in-the-Loop obligation to verify that
    cloud-suggested code does not open sockets or call external APIs.
    """
    findings: List[str] = []
    with open(source_path, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read(), filename=source_path)

    suspicious_attrs = {
        "urlopen",
        "urlretrieve",
        "Session",
        "GenerativeModel",
        "create_client",
        "Client",
    }
    network_call_roots = {
        "requests",
        "httpx",
        "aiohttp",
        "urllib",
        "socket",
        "openai",
        "anthropic",
        "genai",
        "boto3",
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
            # requests.get / requests.post style
            if (
                isinstance(func, ast.Attribute)
                and isinstance(func.value, ast.Name)
                and func.value.id in {"requests", "httpx"}
                and func.attr in {"get", "post", "put", "delete", "patch", "request"}
            ):
                findings.append(
                    f"call {func.value.id}.{func.attr}() (line {node.lineno})"
                )

    return (len(findings) == 0, findings)


def human_in_the_loop_gate(source_path: str) -> None:
    """
    Step C: Mandatory Human-in-the-Loop validation.

    Halts execution via input() until the researcher explicitly confirms that
    the analysis code does not initiate external API calls or network
    requests before any run against live local data (or, in this PoC, before
    synthetic local execution that stands in for that sealed workflow).
    """
    print("\n" + "─" * 78)
    print(" STEP C — HUMAN-IN-THE-LOOP VALIDATION (MANDATORY GATE)")
    print("─" * 78)
    print(
        textwrap.dedent(
            """
            PROTOCOL HOLD: Execution is paused pending researcher attestation.

            Before any analysis proceeds on local (or live sealed) datasets,
            you must confirm that:

              1. No external API calls will be initiated from this process.
              2. No network requests will transmit observations off-host.
              3. Cloud LLMs (Gemini, etc.) will NOT receive row-level data,
                 education records, or Identifiable Private Information.
              4. Only aggregate results remain under university custody.

            Automated pre-checks (advisory — do not replace your judgment):
            """
        ).strip()
    )

    imports_ok, offenders = audit_no_forbidden_network_imports()
    if imports_ok:
        print("  [PASS] No forbidden network/cloud modules loaded in sys.modules.")
    else:
        print("  [FAIL] Forbidden modules detected in process:")
        for item in offenders:
            print(f"         - {item}")
        print("\n  Aborting: remove network clients before Data Plane execution.")
        sys.exit(2)

    ast_ok, findings = scan_source_for_network_calls(source_path)
    if ast_ok:
        print("  [PASS] AST scan found no forbidden network import/call patterns.")
    else:
        print("  [FAIL] AST scan flagged potential network activity:")
        for item in findings:
            print(f"         - {item}")
        print("\n  Aborting: remediate flagged patterns before proceeding.")
        sys.exit(2)

    print()
    env_confirm = os.environ.get("DECOUPLED_AI_HITL_CONFIRM", "").strip().upper()
    if env_confirm in {"YES", "Y", "TRUE", "1"}:
        # Automation escape hatch for CI / non-interactive demos ONLY.
        # Live research workflows must use interactive attestation below.
        print(
            "  [INFO] DECOUPLED_AI_HITL_CONFIRM is set — accepting attestation\n"
            "         non-interactively (automation / PoC CI path only)."
        )
        response = "YES"
    else:
        prompt = (
            "\n  Type YES to attest: this code initiates NO external API calls\n"
            "  or network requests, and is safe to run on sealed local data.\n"
            "  Confirmation > "
        )
        try:
            response = input(prompt).strip().upper()
        except EOFError:
            print(
                "\n  [HALT] No interactive TTY and no DECOUPLED_AI_HITL_CONFIRM.\n"
                "         Refusing to proceed without Human-in-the-Loop attestation."
            )
            sys.exit(3)

    if response != "YES":
        print("\n  [HALT] Attestation not confirmed. Data Plane execution cancelled.")
        sys.exit(1)

    print("\n  [OK] Human-in-the-Loop attestation recorded. Proceeding locally.")


# =============================================================================
# COMPONENT 3 — CITI-ALIGNED COMPLIANCE SUMMARY (TERMINAL REPORT)
# =============================================================================


def print_citi_compliance_report(
    schema: pd.DataFrame,
    results: Dict[str, Any],
) -> None:
    """
    Emit a formatted CITI-aligned compliance report for terminal users.

    Explains how processing empty structural mock schemas via third-party AI
    models leaves Identifiable Private Information (IPI) entirely unexposed.
    """
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    border = "═" * 78
    print("\n" + border)
    print(" CITI-ALIGNED COMPLIANCE SUMMARY — DECOUPLED AI PROTOCOL")
    print(border)
    print(
        f"""
  Institution        : {INSTITUTION}
  Protocol           : {PROTOCOL_NAME}  v{PROTOCOL_VERSION}
  Report generated   : {ts}
  Data classification: SYNTHETIC / DEVELOPMENT (PoC) — no education records

  ┌──────────────────────────────────────────────────────────────────────────┐
  │  DETERMINATION: ABSOLUTE ZERO-LIABILITY PATH FOR CLOUD CODE ASSIST       │
  │  Third-party AI ingested structural metadata ONLY. IPI was not exposed.  │
  └──────────────────────────────────────────────────────────────────────────┘

  1. CITI PROGRAM — INFORMATION SECURITY ALIGNMENT
     CITI Program Information Security / Data Security training emphasizes
     minimizing collection and disclosure of Identifiable Private Information
     (IPI), applying least-privilege access, and preventing unauthorized
     transmission of research data to external systems. This PoC operationalizes
     those standards by:

       • Separating Control Plane (code logic from mock schema) from Data Plane
         (local execution on university-managed hardware);
       • Ensuring cloud models never receive row-level observations;
       • Requiring Human-in-the-Loop attestation before sealed-data execution;
       • Restricting analytics to local open-source libraries (pandas, numpy,
         scipy) with no outbound network clients loaded.

  2. WHY EMPTY STRUCTURAL MOCK SCHEMAS CREATE ZERO IPI EXPOSURE
     Identifiable Private Information requires data that can identify a living
     individual alone or in combination with other information. An empty
     pandas DataFrame that exposes only abstract column labels
     ({list(schema.columns)}) and dtypes — with shape {schema.shape} —
     contains:

       • Zero subject rows
       • Zero direct identifiers
       • Zero indirect identifiers / quasi-identifiers
       • Zero education-record content under FERPA
       • Zero student information under Louisiana La. R.S. 17:3914

     Therefore, transmitting this structural schema to a third-party AI model
     for code-generation assistance leaves IPI entirely unexposed and satisfies
     absolute zero-liability protocols with respect to cloud ingestion of
     university data assets. The vendor processes *metadata about structure*,
     not *data about persons*.

  3. DATA PLANE ATTESTATION (THIS RUN)
     Execution locus     : {results.get("execution_locus", "N/A")}
     Libraries used      : {", ".join(results.get("libraries", []))}
     Synthetic N         : {results.get("n", "N/A")}
     Outbound API calls  : NONE (forbidden modules absent; HITL attested)
     Cloud data egress   : NONE
     FERPA education data: NOT PRESENT IN THIS PoC
     La. R.S. 17:3914    : NOT IMPLICATED (no student information processed
                           by any third party)

  4. OPERATIONAL RULE FOR LIVE RESEARCH (WHEN GRADUATING THIS PoC)
     Control Plane may receive: column names, dtypes, abstract code specs.
     Data Plane alone may receive: sealed local datasets under IRB / PI custody.
     Crossing that boundary with IPI or education records is PROHIBITED.

  STATUS: COMPLIANT WITH DECOUPLED AI PROTOCOL — PoC DEMONSTRATION COMPLETE
"""
    )
    print(border + "\n")


# =============================================================================
# COMPONENT 4 — FORMAL MEMO TO CHIEF IT SECURITY ADMINISTRATOR
# =============================================================================
#
# Informational notification draft for institutional routing. Embedded so the
# PoC artifact is self-contained for Senate, IRB, and IT Security review.
# It is NOT sent automatically. Print with:
#   python3 -c "import importlib.util, pathlib; p=pathlib.Path('scripts/decoupled_ai_protocol_poc.py'); s=importlib.util.spec_from_file_location('poc', p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.MEMO_TO_CHIEF_IT_SECURITY)"
#
MEMO_TO_CHIEF_IT_SECURITY = """
--------------------------------------------------------------------------------
MEMORANDUM (INFORMATIONAL NOTIFICATION)
--------------------------------------------------------------------------------

TO:      Chris Usey
         Chief IT Security Administrator
         Nicholls State University

FROM:    [Faculty Researcher / University Senator]
         Nicholls State University

DATE:    [Insert Date]

RE:      Informational Notice — Adoption of the Decoupled AI Protocol for
         Research Analytics Involving Structural Code Assistance from
         Third-Party AI (Zero University Data Asset Ingestion)

CC:      University Senate (Information Item, as appropriate)
         Human Subjects Institutional Review Board (HSIRB), for awareness
         Office of Academic Affairs (optional routing)

--------------------------------------------------------------------------------

Mr. Usey:

I write to provide formal informational notice that faculty research workflows
under my supervision have adopted the Decoupled AI Protocol, a zero-risk
operational control separating (a) cloud-assisted generation of analytical
*code logic* from (b) sealed local execution against human-subjects or student-
related datasets on university-managed hardware.

I.  PURPOSE OF THIS NOTICE

This memorandum is informational. It documents a newly adopted operational
protocol designed to ensure that third-party artificial intelligence services
(including, without limitation, Google Gemini or equivalent large language
model vendors) never ingest Nicholls State University data assets, education
records, or Identifiable Private Information (IPI). Because no university
data assets are disclosed to vendors under this protocol, this notice asserts
that the workflow does not introduce a new data-processor relationship
requiring further vendor security review for the limited Control Plane use
described herein.

II.  PROTOCOL SUMMARY — STRICT PLANE SEPARATION

A. Control Plane (Cloud — Structural Metadata / Mock Schema Only)
   Researchers may share solely empty structural schemas: abstract column
   names, data types, and non-identifying analytical specifications. No row-
   level observations, student identifiers, grades, directory information, or
   other education records are transmitted. The vendor returns structural code
   logic only.

B. Data Plane (Local — Sealed Execution Environment; No Internet Outbound)
   Code artifacts are reviewed under a mandatory Human-in-the-Loop gate and
   executed exclusively on university-managed systems using standard open-
   source libraries (pandas, numpy, scipy). Outbound internet access is not
   used for analysis execution. Sealed datasets remain under institutional
   custody.

III.  COMPLIANCE POSTURE

The protocol is aligned with:

  • FERPA (20 U.S.C. § 1232g; 34 C.F.R. Part 99) — no disclosure of education
    records to third-party AI vendors;
  • Louisiana La. R.S. 17:3914 — no transmission of protected student
    information to external AI services;
  • CITI Program Information Security standards — minimization of IPI
    exposure and prohibition on unauthorized external transmission of
    research data;
  • 45 C.F.R. Part 46 principles — respect for persons and data stewardship
    through local custody and researcher attestation.

Because third parties receive only non-identifying structural metadata (empty
mock schemas) and never receive university data assets, IPI remains entirely
unexposed at the cloud boundary. This satisfies an absolute zero-liability
path with respect to vendor ingestion of institutional research or student
data under the described Control Plane use.

IV.  REQUESTED ACTION

No approval action is requested at this time. Please treat this memorandum as
an informational notification for IT Security awareness files. Should your
office wish to inventory the protocol, the accompanying proof-of-concept
script (`scripts/decoupled_ai_protocol_poc.py`) demonstrates the architecture,
Human-in-the-Loop gate, and local-only analytics path.

I remain available to walk through the ASCII architecture map, the attestation
gate, and the CITI-aligned compliance summary at your convenience.

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
    """
    Orchestrate the Decoupled AI Protocol PoC:

      print architecture → mock schema → HITL gate → local analysis → report
    """
    _ = argv  # reserved for future CLI flags; PoC keeps a single path
    source_path = os.path.abspath(__file__)

    print("\n" + "═" * 78)
    print(f" {PROTOCOL_NAME} — LOCAL PoC  |  {INSTITUTION}")
    print(f" Version {PROTOCOL_VERSION}")
    print("═" * 78)

    # Component 1
    print_architecture()

    # Component 2 / Step A — Control Plane structural artifact (empty schema)
    schema = build_mock_structural_schema()

    # Component 2 / Step C — HITL BEFORE any Data Plane work on observations
    # (Even synthetic demos must exercise the mandatory gate.)
    human_in_the_loop_gate(source_path)

    # Component 2 / Step B — sealed local analysis on synthetic stand-in data
    local_df = generate_synthetic_local_observations()
    # Bind to the Control Plane schema columns (structure match check)
    assert list(local_df.columns) == list(schema.columns), (
        "Data Plane columns must match Control Plane structural schema."
    )
    results = run_local_correlation_and_regression(local_df)
    print_analysis_results(results)

    # Component 3 — CITI-aligned terminal compliance report
    print_citi_compliance_report(schema, results)

    # Component 4 — surface memo pointer (full text retained in source / constant)
    print(" FORMAL MEMO ON FILE")
    print("─" * 78)
    print(
        "  Draft informational memorandum to Chris Usey, Chief IT Security\n"
        "  Administrator, is embedded in this script as MEMO_TO_CHIEF_IT_SECURITY\n"
        "  (Component 4, bottom of source). It is not transmitted by this program."
    )
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
