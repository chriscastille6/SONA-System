#!/usr/bin/env bash
# FERPA screen wrapper — uses project venv when present (macOS often has no `python`).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLI="$ROOT/scripts/ferpa_screen_cli.py"

if [[ -x "$ROOT/venv312/bin/python" ]]; then
  exec "$ROOT/venv312/bin/python" "$CLI" "$@"
elif [[ -x "$ROOT/venv/bin/python" ]]; then
  exec "$ROOT/venv/bin/python" "$CLI" "$@"
elif command -v python3 >/dev/null 2>&1; then
  exec python3 "$CLI" "$@"
else
  echo "No Python found. Run: ./scripts/setup_presidio.sh" >&2
  exit 127
fi
