#!/usr/bin/env bash
# Install Presidio dependencies and the default English spaCy model.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -d "venv312/bin" ]]; then
  # shellcheck disable=SC1091
  source venv312/bin/activate
elif [[ -d "venv/bin" ]]; then
  # shellcheck disable=SC1091
  source venv/bin/activate
fi

pip install -r requirements.txt
python -m pip install --upgrade 'requests>=2.34.0'
python -m spacy download en_core_web_lg
python -c "from config.presidio_utils import is_presidio_available; assert is_presidio_available()"
echo "Presidio is ready."
