---
name: presidio-pii
description: >-
  Detect and redact PII in text, JSON payloads, and exports using Microsoft
  Presidio. Use when screening IRB/FERPA data, anonymizing exports, validating
  response payloads, auditing free-text fields, or before sharing CSV/JSON
  outside Django.
---

# Presidio PII Workflows

This repository ships Microsoft Presidio for PII detection and anonymization.

## Setup (new environment)

```bash
./scripts/setup_presidio.sh
```

Or manually:

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_lg
```

## Python API (preferred in app code)

Import from `config.presidio_utils`:

```python
from config.presidio_utils import (
    analyze_text,
    anonymize_text,
    deep_scan,
    deep_anonymize,
    is_presidio_available,
)

scan = deep_scan(response_payload)
if scan["has_pii"]:
    safe_payload = deep_anonymize(response_payload)
```

Optional Django settings:

- `PRESIDIO_LANGUAGE` (default: `en`)
- `PRESIDIO_SCORE_THRESHOLD` (default: `0.35`)

Engines lazy-load on first use; do not import Presidio at module import time in hot paths unless needed.

## CLI (scripts and one-off audits)

```bash
python scripts/presidio_scan.py --text "Jane Doe, jane@example.com"
python scripts/presidio_scan.py --input export.json
python scripts/presidio_scan.py --input responses.csv --text-columns payload,comments
python scripts/presidio_scan.py --input export.json --anonymize --output export_redacted.json
```

## When to use Presidio vs existing tools

| Need | Tool |
|------|------|
| Names, emails, phones, locations in free text | Presidio (`config.presidio_utils`) |
| Stable opaque participant IDs for exports | `config.export_utils.get_anonymized_participant_id()` |
| k-anonymity / mosaic-effect risk on tabular QI combos | `scripts/reid_risk_audit.py` |

Use Presidio before external sharing when payloads may contain unstructured PII. Use `reid_risk_audit.py` for quasi-identifier combination risk on structured columns.

For outbound transfers (Cursor prompts, external AI APIs), use **`config/ferpa_guard.py`** — see the `ferpa-guard` skill. It allowlists faculty/staff (e.g. Christopher Castille) and blocks likely student FERPA data in flight.

## Workflow checklist

1. Scan first (`deep_scan` or `presidio_scan.py` without `--anonymize`).
2. Review `entity_types` and affected paths/columns.
3. Redact with `deep_anonymize` or `--anonymize`.
4. For research exports, still apply HMAC participant IDs and column stripping where applicable.

## Troubleshooting

- `OSError: Can't find model 'en_core_web_lg'`: run `python -m spacy download en_core_web_lg`.
- Slow first call: spaCy model loads once per process; reuse process/worker where possible.
- False positives in academic prose: raise `PRESIDIO_SCORE_THRESHOLD` or pass `entities=` to limit detector scope.
