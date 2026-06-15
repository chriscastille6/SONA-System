#!/usr/bin/env python3
"""
Population-analytic Monte Carlo simulation of mosaic / quasi-identifier re-identification risk.

Models a finite study sample of size N with categorical quasi-identifiers (QIs) drawn from
known marginal distributions (Nicholls-style student + optional HR professional cohort).
Reports:

  - P(unique): probability a random participant is in a sample-unique QI cell (k=1)
  - P(k < K): probability a random participant is in a cell smaller than threshold K
  - Fraction of sample in unique cells (empirical disclosure rate if QIs are released)
  - Effect of coarsening (exact age -> bands) and local suppression

This is a *sample uniqueness* model (attacker sees released microdata or fine cross-tabs).
It does not model external linkage to roster/email unless you enable the linkage scenario.

Usage:
  python3 scripts/mosaic_reidentification_simulation.py
  python3 scripts/mosaic_reidentification_simulation.py --cohort student --reps 5000
  python3 scripts/mosaic_reidentification_simulation.py --output-csv /tmp/mosaic_sim.csv
"""
from __future__ import annotations

import argparse
import itertools
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Marginal distributions (approximate; tune from your codebook)
# ---------------------------------------------------------------------------

STUDENT_GENDER = {"woman": 0.52, "man": 0.45, "nonbinary": 0.02, "prefer_not": 0.01}
STUDENT_STATUS = {"ug": 0.85, "grad": 0.10, "other": 0.05}
# Exact age 18-45 for undergrad-heavy pool
STUDENT_AGE_EXACT = list(range(18, 46))  # 28 values
# Unimodal-ish weights centered on typical undergrad ages
_weights = np.exp(-0.5 * ((np.array(STUDENT_AGE_EXACT) - 21) / 4) ** 2)
STUDENT_AGE_EXACT_P = _weights / _weights.sum()

AGE_BANDS = ["18-24", "25-34", "35-44", "45+"]
AGE_BAND_MAP = {a: "18-24" if a < 25 else "25-34" if a < 35 else "35-44" if a < 45 else "45+" for a in STUDENT_AGE_EXACT}

HR_RACE = {
    "white": 0.62,
    "black-african-american": 0.18,
    "hispanic-latino": 0.10,
    "asian": 0.05,
    "two-or-more": 0.03,
    "prefer_not": 0.02,
}
HR_JOB = {"hr_manager": 0.35, "director": 0.30, "vp": 0.15, "other": 0.20}
HR_YEARS = {"0-2": 0.20, "3-5": 0.25, "6-10": 0.30, "11+": 0.25}
HR_CRED_COUNT = {0: 0.25, 1: 0.40, 2: 0.25, 3: 0.10}  # number of credentials (collapsed)

QI_SCENARIOS_STUDENT = {
    "gender": ["gender"],
    "gender+age_exact": ["gender", "age_exact"],
    "gender+age_band+status": ["gender", "age_band", "student_status"],
    "gender+age_exact+status": ["gender", "age_exact", "student_status"],
    "gender+age_band+status+week": ["gender", "age_band", "student_status", "completion_week"],
}

QI_SCENARIOS_HR = {
    "race": ["race_ethnicity"],
    "race+job": ["race_ethnicity", "job_level"],
    "race+job+years": ["race_ethnicity", "job_level", "years_in_hr"],
    "race+job+years+creds": ["race_ethnicity", "job_level", "years_in_hr", "credential_count"],
}


@dataclass
class SimConfig:
    n: int
    qi_cols: List[str]
    reps: int
    k_threshold: int
    cohort: str
    seed: int


def _draw_from_dict(rng: np.random.Generator, dist: Dict[str, float], n: int) -> np.ndarray:
    keys = list(dist.keys())
    p = np.array([dist[k] for k in keys], dtype=float)
    p /= p.sum()
    return rng.choice(keys, size=n, p=p)


def simulate_student_sample(rng: np.random.Generator, n: int) -> pd.DataFrame:
    ages = rng.choice(STUDENT_AGE_EXACT, size=n, p=STUDENT_AGE_EXACT_P)
    df = pd.DataFrame(
        {
            "gender": _draw_from_dict(rng, STUDENT_GENDER, n),
            "student_status": _draw_from_dict(rng, STUDENT_STATUS, n),
            "age_exact": ages,
        }
    )
    df["age_band"] = df["age_exact"].map(AGE_BAND_MAP)
    # Completion week: 4 bins (mosaic via timing)
    df["completion_week"] = rng.integers(0, 4, size=n).astype(str)
    return df


def simulate_hr_sample(rng: np.random.Generator, n: int) -> pd.DataFrame:
    cred_n = rng.choice(list(HR_CRED_COUNT.keys()), size=n, p=list(HR_CRED_COUNT.values()))
    return pd.DataFrame(
        {
            "race_ethnicity": _draw_from_dict(rng, HR_RACE, n),
            "job_level": _draw_from_dict(rng, HR_JOB, n),
            "years_in_hr": _draw_from_dict(rng, HR_YEARS, n),
            "credential_count": cred_n.astype(str),
        }
    )


def cell_sizes(df: pd.DataFrame, qi_cols: Sequence[str]) -> pd.Series:
    return df.groupby(list(qi_cols), dropna=False).size()


def metrics_for_sample(df: pd.DataFrame, qi_cols: Sequence[str], k_threshold: int) -> Dict[str, float]:
    sizes = df.groupby(list(qi_cols), dropna=False)[qi_cols[0]].transform("size")
    k = sizes.values
    n = len(df)
    return {
        "frac_unique": float((k == 1).sum() / n),
        "frac_below_k": float((k < k_threshold).sum() / n),
        "min_k": int(sizes.min()) if len(sizes) else 0,
        "p_unique": float((k == 1).mean()),  # P(random row unique) = empirical frac
        "p_below_k": float((k < k_threshold).mean()),
        "n_cells": float(df.groupby(list(qi_cols), dropna=False).ngroups),
    }


def apply_suppression(df: pd.DataFrame, qi_cols: Sequence[str], k_threshold: int) -> pd.DataFrame:
    """Local suppression: mask QI values in cells with size < k_threshold."""
    out = df.copy()
    for c in qi_cols:
        out[c] = out[c].astype(str)
    sizes = out.groupby(list(qi_cols), dropna=False)[qi_cols[0]].transform("size")
    mask = sizes < k_threshold
    for c in qi_cols:
        out.loc[mask, c] = "*"
    return out


def linkage_attack_unique_rate(
    rng: np.random.Generator,
    n: int,
    roster_fraction: float,
    qi_cols: Sequence[str],
    cohort: str,
) -> float:
    """
    Simplified linkage: roster shares QIs for a fraction of campus.
    Attacker matches released row to roster if QI combo appears once in sample AND once in roster pool.
    Returns P(correct unique match | participant in sample) under heroic assumptions.
    """
    if roster_fraction <= 0:
        return 0.0
    df = simulate_student_sample(rng, n) if cohort == "student" else simulate_hr_sample(rng, n)
    roster_n = max(10, int(2000 * roster_fraction))
    roster = simulate_student_sample(rng, roster_n) if cohort == "student" else simulate_hr_sample(rng, roster_n)
    keys = list(qi_cols)
    sample_keys = df[keys].astype(str).agg("|".join, axis=1)
    roster_keys = roster[keys].astype(str).agg("|".join, axis=1)
    sample_counts = sample_keys.value_counts()
    roster_counts = roster_keys.value_counts()
    # Successful ID: sample cell size 1 and key appears exactly once in roster (simplified)
    identifiable = 0
    for i, sk in enumerate(sample_keys):
        if sample_counts[sk] == 1 and roster_counts.get(sk, 0) == 1:
            identifiable += 1
    return identifiable / n


def run_monte_carlo(cfg: SimConfig, scenario_name: str, qi_cols: List[str], mitigation: str) -> Dict:
    rng = np.random.default_rng(cfg.seed)
    accum = {k: [] for k in ["frac_unique", "frac_below_k", "min_k", "p_unique", "p_below_k", "n_cells"]}
    base_cols = list(qi_cols)
    for rep in range(cfg.reps):
        r = np.random.default_rng(cfg.seed + rep + hash(scenario_name) % 10_000)
        df = simulate_student_sample(r, cfg.n) if cfg.cohort == "student" else simulate_hr_sample(r, cfg.n)
        cols = [
            ("age_band" if c == "age_exact" else c)
            for c in base_cols
        ] if mitigation == "age_bands" else list(base_cols)
        if mitigation == "suppress_k":
            df = apply_suppression(df, cols, cfg.k_threshold)
        for k, v in metrics_for_sample(df, cols, cfg.k_threshold).items():
            accum[k].append(v)

    out = {
        "cohort": cfg.cohort,
        "N": cfg.n,
        "scenario": scenario_name,
        "qi_cols": "|".join(base_cols),
        "mitigation": mitigation,
        "K": cfg.k_threshold,
        "reps": cfg.reps,
    }
    for k, vals in accum.items():
        out[f"{k}_mean"] = float(np.mean(vals))
        out[f"{k}_p95"] = float(np.percentile(vals, 95))
    return out


def run_linkage_scenario(cfg: SimConfig, qi_cols: List[str], roster_fraction: float, reps: int = 200) -> Dict:
    """Separate smaller simulation for roster linkage (expensive)."""
    rates = []
    for rep in range(reps):
        r = np.random.default_rng(cfg.seed + 9000 + rep)
        rates.append(
            linkage_attack_unique_rate(r, cfg.n, roster_fraction=roster_fraction, qi_cols=qi_cols, cohort=cfg.cohort)
        )
    return {
        "cohort": cfg.cohort,
        "N": cfg.n,
        "scenario": "linkage_roster_attack",
        "qi_cols": "|".join(qi_cols),
        "mitigation": "none",
        "K": cfg.k_threshold,
        "reps": reps,
        "linkage_p_success_mean": float(np.mean(rates)),
        "linkage_p_success_p95": float(np.percentile(rates, 95)),
    }


def analytic_upper_bound_singleton(n: int, grid_cells: int) -> float:
    """
    Poisson heuristic: if N balls thrown uniformly across C cells,
    P(some cell gets exactly 1) ~ 1 - exp(-N/C) * ... rough upper bound for uniqueness pressure.
    Simpler: expected occupancy; P(unique row) <= N/C * (1 - 1/C)^(N-1) approx for uniform
    """
    if grid_cells <= 0:
        return 1.0
    # Expected fraction unique under uniform multinomial (approx): (1 - 1/C)^(N-1)
    p = (1 - 1 / grid_cells) ** max(n - 1, 0)
    return min(1.0, n / grid_cells * p) if grid_cells >= n else 1.0


def grid_size_for_scenario(cohort: str, scenario: str) -> int:
    if cohort == "student":
        if scenario == "gender":
            return 4
        if scenario == "gender+age_exact":
            return 4 * len(STUDENT_AGE_EXACT)
        if scenario == "gender+age_band+status":
            return 4 * 4 * 3
        if scenario == "gender+age_exact+status":
            return 4 * len(STUDENT_AGE_EXACT) * 3
        if scenario == "gender+age_band+status+week":
            return 4 * 4 * 3 * 4
    else:
        sizes = {
            "race": len(HR_RACE),
            "race+job": len(HR_RACE) * len(HR_JOB),
            "race+job+years": len(HR_RACE) * len(HR_JOB) * len(HR_YEARS),
            "race+job+years+creds": len(HR_RACE) * len(HR_JOB) * len(HR_YEARS) * len(HR_CRED_COUNT),
        }
        return sizes.get(scenario, 100)
    return 100


def main():
    p = argparse.ArgumentParser(description="Mosaic re-identification population simulation")
    p.add_argument("--cohort", choices=["student", "hr", "both"], default="both")
    p.add_argument("--reps", type=int, default=1000, help="Monte Carlo replications per condition")
    p.add_argument("--k-threshold", type=int, default=5)
    p.add_argument("--output-csv", default="mosaic_simulation_results.csv")
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    sample_sizes = [20, 30, 50, 100, 200, 500]
    mitigations = ["none", "age_bands", "suppress_k"]

    rows = []
    cohorts = ["student", "hr"] if args.cohort == "both" else [args.cohort]
    for cohort in cohorts:
        scenarios = QI_SCENARIOS_STUDENT if cohort == "student" else QI_SCENARIOS_HR
        for n in sample_sizes:
            for scen_name, qi_cols in scenarios.items():
                grid = grid_size_for_scenario(cohort, scen_name)
                for mit in mitigations:
                    if mit == "age_bands" and "age_exact" not in qi_cols:
                        continue
                    cfg = SimConfig(
                        n=n,
                        qi_cols=list(qi_cols),
                        reps=args.reps,
                        k_threshold=args.k_threshold,
                        cohort=cohort,
                        seed=args.seed,
                    )
                    rows.append(run_monte_carlo(cfg, scen_name, list(qi_cols), mit))
                # analytic reference (uniform heuristic)
                rows.append(
                    {
                        "cohort": cohort,
                        "N": n,
                        "scenario": scen_name,
                        "qi_cols": "|".join(qi_cols),
                        "mitigation": "analytic_uniform_heuristic",
                        "K": args.k_threshold,
                        "reps": 0,
                        "p_unique_mean": analytic_upper_bound_singleton(n, grid),
                        "frac_unique_mean": analytic_upper_bound_singleton(n, grid),
                    }
                )
        if cohort == "student":
            for n in sample_sizes:
                cfg = SimConfig(
                    n=n,
                    qi_cols=["gender", "age_exact", "student_status"],
                    reps=args.reps,
                    k_threshold=args.k_threshold,
                    cohort="student",
                    seed=args.seed,
                )
                rows.append(
                    run_linkage_scenario(cfg, ["gender", "age_exact", "student_status"], roster_fraction=0.15, reps=200)
                )

    results = pd.DataFrame(rows)
    results.to_csv(args.output_csv, index=False)
    print(f"Wrote {len(results)} rows to {args.output_csv}\n")

    # Highlight tables for report
    for cohort in cohorts:
        print("=" * 72)
        print(f"Cohort: {cohort.upper()}  |  K threshold = {args.k_threshold}  |  reps = {args.reps}")
        print("=" * 72)
        sub = results[
            (results["cohort"] == cohort)
            & (results["mitigation"] == "none")
            & (results["scenario"].isin(list((QI_SCENARIOS_STUDENT if cohort == "student" else QI_SCENARIOS_HR).keys())))
        ]
        cols = ["N", "scenario", "p_unique_mean", "frac_unique_mean", "frac_below_k_mean", "min_k_mean"]
        print(sub[cols].sort_values(["scenario", "N"]).to_string(index=False, float_format=lambda x: f"{x:.3f}"))
        print()

        print("Mitigation comparison (student goals-refs-like scenario, N=100):")
        if cohort == "student":
            m = results[
                (results["cohort"] == "student")
                & (results["N"] == 100)
                & (results["scenario"] == "gender+age_exact+status")
            ]
            print(
                m[["mitigation", "p_unique_mean", "frac_below_k_mean", "min_k_mean"]].to_string(
                    index=False, float_format=lambda x: f"{x:.3f}"
                )
            )
        print()

    # Conditions narrative
    print("INTERPRETATION (population-analytic)")
    print("-" * 72)
    print(
        "p_unique_mean ≈ probability a randomly chosen participant is the ONLY person in their"
    )
    print(
        "released quasi-identifier cell (sample uniqueness). If an attacker also holds a roster"
    )
    print(
        "with the same fields, unique cells often imply successful re-identification."
    )
    print(
        "frac_below_k_mean ≈ share of sample that would fail cell-size rules for publication (k < K)."
    )
    print()


if __name__ == "__main__":
    main()
