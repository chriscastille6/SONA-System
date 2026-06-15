#!/usr/bin/env python3
"""
Re-identification (mosaic effect) risk audit helper.

Usage examples:
  python scripts/reid_risk_audit.py --input responses.csv
  python scripts/reid_risk_audit.py --input responses.csv --qi-columns age,gender,zip3,created_date
  python scripts/reid_risk_audit.py --input responses.csv --remediate --output-sanitized responses_sanitized.csv
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

import pandas as pd


DEFAULT_K_THRESHOLD = 5
DEFAULT_MAX_COMBO = 3

# Name-based hints for fields that often contribute to re-identification.
QI_NAME_HINTS = [
    "age",
    "gender",
    "sex",
    "race",
    "ethnic",
    "zip",
    "postal",
    "city",
    "state",
    "region",
    "country",
    "major",
    "department",
    "education",
    "income",
    "occupation",
    "job",
    "student_status",
    "created",
    "submitted",
    "timestamp",
    "date",
    "time",
]

# Direct and hidden identifiers that should be stripped before sharing.
IDENTIFIER_HINTS = [
    "name",
    "first_name",
    "last_name",
    "full_name",
    "email",
    "phone",
    "address",
    "ssn",
    "student_id",
    "participant_id",
    "session_id",
    "response_id",
    "user_id",
    "id",
    "ip",
    "user_agent",
    "device_id",
    "cookie",
    "token",
]


def load_table(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix in {".csv", ".txt"}:
        return pd.read_csv(path)
    if suffix in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    if suffix in {".json"}:
        return pd.read_json(path)
    raise ValueError(f"Unsupported input format: {suffix}")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).strip() for c in out.columns]
    return out


def flatten_payload_column(df: pd.DataFrame, payload_column: str = "payload") -> pd.DataFrame:
    """
    If a JSON payload column exists, expand it to tabular columns with prefix payload_.
    """
    if payload_column not in df.columns:
        return df

    def _parse_payload_cell(v):
        if isinstance(v, dict):
            return v
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                return parsed if isinstance(parsed, dict) else {}
            except json.JSONDecodeError:
                return {}
        return {}

    parsed = df[payload_column].map(_parse_payload_cell)
    expanded = pd.json_normalize(parsed).add_prefix(f"{payload_column}_")
    return pd.concat([df.drop(columns=[payload_column]), expanded], axis=1)


def _looks_like_datetime(series: pd.Series) -> bool:
    if pd.api.types.is_datetime64_any_dtype(series):
        return True
    if not (pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series)):
        return False
    sample = series.dropna().astype(str).head(200)
    if sample.empty:
        return False
    parsed = pd.to_datetime(sample, errors="coerce", utc=True)
    return parsed.notna().mean() >= 0.8


def detect_qi_candidates(df: pd.DataFrame) -> List[str]:
    n = len(df)
    candidates: List[str] = []

    for col in df.columns:
        col_l = col.lower()
        nunique = df[col].nunique(dropna=True)
        unique_ratio = (nunique / n) if n else 0.0

        # Exclude almost-constant and almost-fully-unique columns by default.
        is_reasonable_cardinality = 1 < nunique < n
        has_qi_name = any(h in col_l for h in QI_NAME_HINTS)
        is_likely_type = (
            pd.api.types.is_numeric_dtype(df[col])
            or pd.api.types.is_object_dtype(df[col])
            or pd.api.types.is_string_dtype(df[col])
            or pd.api.types.is_categorical_dtype(df[col])
            or _looks_like_datetime(df[col])
        )

        if is_reasonable_cardinality and is_likely_type:
            # Include fields hinted by name or medium cardinality.
            if has_qi_name or (0.01 <= unique_ratio <= 0.95):
                candidates.append(col)
    return sorted(set(candidates))


def combinations_upto(items: Sequence[str], max_size: int) -> Iterable[Tuple[str, ...]]:
    for r in range(1, max_size + 1):
        yield from itertools.combinations(items, r)


def k_anonymity_table(
    df: pd.DataFrame,
    combos: Iterable[Tuple[str, ...]],
    k_threshold: int,
) -> pd.DataFrame:
    rows = []
    n = len(df)
    for combo in combos:
        grouped = df.groupby(list(combo), dropna=False).size()
        min_k = int(grouped.min()) if len(grouped) else 0
        n_groups = int(grouped.shape[0])
        n_groups_below_k = int((grouped < k_threshold).sum())
        rows_below_k = int(grouped[grouped < k_threshold].sum()) if len(grouped) else 0
        pct_rows_below_k = (rows_below_k / n) if n else 0.0
        pct_unique_rows = (int(grouped[grouped == 1].sum()) / n) if n else 0.0
        rows.append(
            {
                "combo": "|".join(combo),
                "combo_size": len(combo),
                "min_k": min_k,
                "groups": n_groups,
                "groups_below_k": n_groups_below_k,
                "rows_below_k": rows_below_k,
                "pct_rows_below_k": round(pct_rows_below_k, 6),
                "pct_unique_rows": round(pct_unique_rows, 6),
            }
        )
    out = pd.DataFrame(rows)
    return out.sort_values(
        by=["min_k", "pct_rows_below_k", "combo_size"],
        ascending=[True, False, False],
    ).reset_index(drop=True)


def col_matches_hint(column: str, hints: Sequence[str]) -> bool:
    c = column.lower()
    return any(h in c for h in hints)


def metadata_columns(df: pd.DataFrame) -> List[str]:
    return [c for c in df.columns if col_matches_hint(c, IDENTIFIER_HINTS)]


def coarsen_age_columns(df: pd.DataFrame, bins: Sequence[int] = (18, 25, 35, 45, 55, 65, 200)) -> pd.DataFrame:
    out = df.copy()
    labels = [f"{bins[i]}-{bins[i + 1] - 1}" for i in range(len(bins) - 2)] + [f"{bins[-2]}+"]
    for col in out.columns:
        if "age" in col.lower() and pd.api.types.is_numeric_dtype(out[col]):
            out[col] = pd.cut(out[col], bins=bins, labels=labels, right=False, include_lowest=True)
    return out


def coarsen_datetime_columns(df: pd.DataFrame, freq: str = "D") -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        if _looks_like_datetime(out[col]):
            parsed = pd.to_datetime(out[col], errors="coerce", utc=True)
            out[col] = parsed.dt.floor(freq)
    return out


def top_bottom_code_numeric(df: pd.DataFrame, lower_q: float = 0.01, upper_q: float = 0.99) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_numeric_dtype(out[col]):
            s = out[col]
            if s.notna().sum() < 20:
                continue
            low = s.quantile(lower_q)
            high = s.quantile(upper_q)
            out[col] = s.clip(lower=low, upper=high)
    return out


def strip_metadata(df: pd.DataFrame, extra_drop: Sequence[str] | None = None) -> pd.DataFrame:
    drop_cols = set(metadata_columns(df))
    if extra_drop:
        drop_cols.update(c for c in extra_drop if c in df.columns)
    return df.drop(columns=[c for c in drop_cols if c in df.columns], errors="ignore")


def local_suppress(df: pd.DataFrame, combo: Sequence[str], k_threshold: int, mask_value: str = "*") -> pd.DataFrame:
    """
    Suppress records in low-k cells by masking combo columns for only those rows.
    """
    out = df.copy()
    counts = out.groupby(list(combo), dropna=False)[list(combo)[0]].transform("size")
    at_risk = counts < k_threshold
    for col in combo:
        out.loc[at_risk, col] = mask_value
    return out


def parse_columns_arg(raw: str | None) -> List[str]:
    if not raw:
        return []
    return [c.strip() for c in raw.split(",") if c.strip()]


def run(args: argparse.Namespace) -> None:
    df = normalize_columns(load_table(Path(args.input)))
    if args.flatten_payload:
        df = flatten_payload_column(df, payload_column=args.payload_column)

    # Strip direct/hidden identifiers before risk scoring if requested.
    if args.strip_identifiers:
        df = strip_metadata(df)

    qi_columns = parse_columns_arg(args.qi_columns) or detect_qi_candidates(df)
    qi_columns = [c for c in qi_columns if c in df.columns]
    if not qi_columns:
        raise ValueError("No quasi-identifier columns detected. Provide --qi-columns explicitly.")

    combos = list(combinations_upto(qi_columns, args.max_combo))
    risk_df = k_anonymity_table(df, combos, args.k_threshold)
    risk_df.to_csv(args.output_risk, index=False)

    print(f"[INFO] rows={len(df)} columns={len(df.columns)}")
    print(f"[INFO] qi_columns={qi_columns}")
    print(f"[INFO] combinations_tested={len(combos)}")
    print(f"[INFO] risk_report={args.output_risk}")
    print("\nTop high-risk combinations:")
    print(risk_df.head(args.top_n).to_string(index=False))

    if args.remediate:
        rem = df.copy()
        rem = coarsen_age_columns(rem)
        rem = coarsen_datetime_columns(rem, freq=args.time_floor)
        rem = top_bottom_code_numeric(rem, lower_q=args.lower_quantile, upper_q=args.upper_quantile)
        rem = strip_metadata(rem)

        # Apply local suppression using riskiest combo.
        if not risk_df.empty:
            riskiest = risk_df.iloc[0]["combo"].split("|")
            rem = local_suppress(rem, riskiest, args.k_threshold, mask_value=args.suppress_value)

        out_path = args.output_sanitized
        if not out_path:
            stem = Path(args.input).stem
            out_path = f"{stem}_sanitized.csv"
        rem.to_csv(out_path, index=False)
        print(f"[INFO] sanitized_output={out_path}")

    if args.output_summary_json:
        summary = {
            "rows": int(len(df)),
            "columns": int(len(df.columns)),
            "qi_columns": qi_columns,
            "k_threshold": args.k_threshold,
            "max_combo": args.max_combo,
            "top_risk": json.loads(risk_df.head(args.top_n).to_json(orient="records")),
        }
        with open(args.output_summary_json, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        print(f"[INFO] summary_json={args.output_summary_json}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Mosaic-effect / k-anonymity risk auditor")
    p.add_argument("--input", required=True, help="Input data file (.csv, .parquet, .json)")
    p.add_argument("--qi-columns", default="", help="Comma-separated quasi-identifier columns (override auto-detect)")
    p.add_argument("--max-combo", type=int, default=DEFAULT_MAX_COMBO, help="Max QI combination size")
    p.add_argument("--k-threshold", type=int, default=DEFAULT_K_THRESHOLD, help="Unsafe if group size < k")
    p.add_argument("--top-n", type=int, default=20, help="Top risky combinations to print")
    p.add_argument("--output-risk", default="k_risk_report.csv", help="CSV output with combination-level risk")
    p.add_argument("--output-summary-json", default="", help="Optional JSON summary output path")
    p.add_argument("--strip-identifiers", action="store_true", help="Strip identifier-like columns before scoring")
    p.add_argument("--flatten-payload", action="store_true", help="Expand JSON payload column into tabular columns")
    p.add_argument("--payload-column", default="payload", help="JSON payload column name to flatten")

    # Remediation controls
    p.add_argument("--remediate", action="store_true", help="Create a sanitized dataset")
    p.add_argument("--output-sanitized", default="", help="Path for sanitized CSV output")
    p.add_argument("--time-floor", default="D", help="Datetime coarsening granularity, e.g. D, W, M")
    p.add_argument("--lower-quantile", type=float, default=0.01, help="Lower quantile for bottom-coding")
    p.add_argument("--upper-quantile", type=float, default=0.99, help="Upper quantile for top-coding")
    p.add_argument("--suppress-value", default="*", help="Mask value for local suppression")
    return p


if __name__ == "__main__":
    parser = build_parser()
    run(parser.parse_args())
