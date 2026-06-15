#!/usr/bin/env bash
# Block Cursor prompts that would send likely FERPA-protected content externally.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PYTHON="$ROOT/venv312/bin/python"
CLI="$ROOT/scripts/ferpa_screen_cli.py"

if [[ ! -x "$PYTHON" ]]; then
  PYTHON="$(command -v python3)"
fi

if [[ ! -f "$CLI" ]]; then
  echo '{"continue":false,"user_message":"FERPA guard script missing. Prompt blocked (fail closed)."}'
  exit 0
fi

input="$(cat)"
if ! "$PYTHON" "$CLI" --cursor-prompt <<<"$input"; then
  echo '{"continue":false,"user_message":"FERPA guard failed while screening this prompt. Prompt blocked (fail closed)."}'
fi
