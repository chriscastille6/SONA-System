#!/usr/bin/env python3
"""CLI: generate a CANDIDATE Hash ID from three security answers (synthetic/dev)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.compliance.candidate.protocol import generate_candidate_id


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a 16-char CANDIDATE Hash ID. "
            "Use synthetic answers only in development."
        )
    )
    parser.add_argument("maiden_initials", help="Mother's maiden initials, e.g. MJ")
    parser.add_argument("birth_day", type=int, help="Day of month 1-31")
    parser.add_argument("street_initials", help="Childhood street initials, e.g. OA")
    args = parser.parse_args()
    print(
        generate_candidate_id(
            args.maiden_initials, args.birth_day, args.street_initials
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
