#!/usr/bin/env python3
"""
Scan or anonymize free text / JSON / CSV exports for PII using Microsoft Presidio.

Examples:
  python scripts/presidio_scan.py --text "Contact Jane Doe at jane@example.com"
  python scripts/presidio_scan.py --input responses.csv --text-columns payload,comments
  python scripts/presidio_scan.py --input export.json --anonymize --output export_redacted.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.presidio_utils import (  # noqa: E402
    anonymize_text,
    deep_anonymize,
    deep_scan,
    is_presidio_available,
    scan_text,
)


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _load_csv(path: Path):
    import pandas as pd

    return pd.read_csv(path)


def _scan_csv(path: Path, text_columns: list[str], score_threshold: float | None) -> dict:
    df = _load_csv(path)
    columns = text_columns or [
        c for c in df.columns if df[c].dtype == object or str(df[c].dtype) == "string"
    ]
    findings = []
    for column in columns:
        if column not in df.columns:
            continue
        for idx, value in df[column].dropna().astype(str).items():
            scan = scan_text(value, score_threshold=score_threshold)
            if scan["has_pii"]:
                findings.append({"row": int(idx), "column": column, **scan})
    return {
        "has_pii": bool(findings),
        "field_count": len(findings),
        "findings": findings,
    }


def _anonymize_csv(path: Path, text_columns: list[str], score_threshold: float | None, output: Path):
    import pandas as pd

    df = _load_csv(path)
    columns = text_columns or [
        c for c in df.columns if df[c].dtype == object or str(df[c].dtype) == "string"
    ]
    out = df.copy()
    for column in columns:
        if column not in out.columns:
            continue
        out[column] = out[column].map(
            lambda v: anonymize_text(str(v), score_threshold=score_threshold)
            if pd.notna(v)
            else v
        )
    out.to_csv(output, index=False)


def run(args: argparse.Namespace) -> int:
    if not is_presidio_available():
        print(
            "Presidio is not available. Install dependencies and the spaCy model:\n"
            "  pip install -r requirements.txt\n"
            "  python -m spacy download en_core_web_lg",
            file=sys.stderr,
        )
        return 1

    score_threshold = args.score_threshold

    if args.text:
        if args.anonymize:
            print(anonymize_text(args.text, score_threshold=score_threshold))
        else:
            print(json.dumps(scan_text(args.text, score_threshold=score_threshold), indent=2))
        return 0

    if not args.input:
        print("Provide --text or --input.", file=sys.stderr)
        return 2

    path = Path(args.input)
    suffix = path.suffix.lower()
    text_columns = [c.strip() for c in args.text_columns.split(",") if c.strip()]

    if suffix == ".csv":
        if args.anonymize:
            output = Path(args.output or f"{path.stem}_redacted.csv")
            _anonymize_csv(path, text_columns, score_threshold, output)
            print(json.dumps({"output": str(output)}, indent=2))
        else:
            print(json.dumps(_scan_csv(path, text_columns, score_threshold), indent=2))
        return 0

    if suffix == ".json":
        data = _load_json(path)
        if args.anonymize:
            data = deep_anonymize(data, score_threshold=score_threshold)
            output = Path(args.output or f"{path.stem}_redacted.json")
            output.write_text(json.dumps(data, indent=2), encoding="utf-8")
            print(json.dumps({"output": str(output)}, indent=2))
        else:
            print(json.dumps(deep_scan(data, score_threshold=score_threshold), indent=2))
        return 0

    text = _load_text(path)
    if args.anonymize:
        output = Path(args.output or f"{path.stem}_redacted{path.suffix}")
        output.write_text(anonymize_text(text, score_threshold=score_threshold), encoding="utf-8")
        print(json.dumps({"output": str(output)}, indent=2))
    else:
        print(json.dumps(scan_text(text, score_threshold=score_threshold), indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scan or redact PII with Microsoft Presidio")
    parser.add_argument("--text", help="Inline text to scan or anonymize")
    parser.add_argument("--input", help="Path to .txt, .json, or .csv input")
    parser.add_argument(
        "--text-columns",
        default="",
        help="Comma-separated CSV text columns (default: all object/string columns)",
    )
    parser.add_argument("--anonymize", action="store_true", help="Redact detected PII")
    parser.add_argument("--output", default="", help="Output path when using --anonymize")
    parser.add_argument(
        "--score-threshold",
        type=float,
        default=None,
        help="Minimum confidence score (default: 0.35 or PRESIDIO_SCORE_THRESHOLD)",
    )
    return parser


if __name__ == "__main__":
    raise SystemExit(run(build_parser().parse_args()))
