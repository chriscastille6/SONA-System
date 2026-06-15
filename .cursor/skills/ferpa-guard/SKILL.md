---
name: ferpa-guard
description: >-
  Screen text, prompts, exports, and AI payloads for FERPA-protected student
  data before it leaves institutional control. Use before external AI calls,
  sharing CSV/JSON, pasting rosters into Cursor, or any workflow that could
  send student identifiers to OpenAI/Anthropic/Gemini or other external servers.
---

# FERPA Guard (In-Flight Screening)

Student education records must not reach external servers without review. This
repo enforces that at two layers:

1. **Cursor hook** — blocks user prompts (and attached files) before they are
   sent to external AI (`beforeSubmitPrompt`, fail-closed).
2. **Django IRB AI** — blocks prompts to OpenAI/Anthropic/Gemini inside
   `apps/studies/irb_ai/agents/base.py`. Ollama on institutional infrastructure
   is treated as internal.

## Allowlist (not FERPA concerns here)

Faculty/staff you routinely mention are allowlisted in
`config/ferpa_allowlist.yaml` (e.g. Christopher Castille). Their names and
`@nicholls.edu` email are masked before screening.

**Do not** add student names or `@my.nicholls.edu` addresses to the allowlist.

## Python API

```python
from config.ferpa_guard import screen_text, assert_safe_for_external_transfer

verdict = screen_text(text, destination="external")
if verdict.blocked:
    ...

assert_safe_for_external_transfer(prompt, context="my_workflow")
```

Presidio helpers remain in `config/presidio_utils.py` for redaction workflows.

## Cursor hook behavior

When student data is detected in a prompt, Cursor **cannot** show a native Yes/No
button or auto-replace the outgoing prompt (API limit). Instead the hook:

1. Blocks the original prompt (nothing sent externally)
2. Builds a synthetic/redacted version
3. Saves it to `.cursor/ferpa-redacted/latest.txt`
4. Copies it to your clipboard on macOS
5. Shows a message asking whether to paste the synthetic version and resend

Opt in on the first try by prefixing your prompt:

```text
USE_SYNTHETIC: analyze this roster export for Emily Johnson emily.johnson@my.nicholls.edu
```

Or generate synthetic text manually:

```bash
echo "Emily Johnson emily.johnson@my.nicholls.edu roster" | ./scripts/ferpa_screen.sh --synthesize
```

## CLI / manual audit

From the repo root (use the wrapper — macOS often has no `python` command):

```bash
echo "Christopher Castille is the PI" | ./scripts/ferpa_screen.sh --json

echo "Emily Johnson emily.johnson@my.nicholls.edu roster" | ./scripts/ferpa_screen.sh --json
```

Equivalent if you prefer the venv directly:

```bash
./venv312/bin/python scripts/ferpa_screen_cli.py --json <<< "Christopher Castille is the PI"
```

Exit code `2` means blocked.

## What triggers a block (external destination)

| Signal | Example |
|--------|---------|
| Student email | `name@my.nicholls.edu` |
| Student ID | `N12345678` |
| Person name + academic context | name near "student", "roster", "credit", "signup" |
| Structured PII fields in academic context | `student_email`, `first_name` in export-like text |

Generic `@nicholls.edu` faculty email is **not** auto-blocked unless paired with
student-context PII after allowlist masking.

## Agent checklist

Before suggesting commands that upload/share data externally (`curl`, cloud
APIs, public gists, etc.):

1. Run mental or CLI FERPA screen on the payload.
2. Redact with `deep_anonymize()` from `config/presidio_utils.py` if needed.
3. Prefer institutional Ollama for IRB AI when documents may contain incidental
   student references.
4. Never paste live rosters, grade data, or signup exports into Cursor prompts.

## Troubleshooting

- Hook blocks a safe prompt: add faculty identifiers to `config/ferpa_allowlist.yaml`.
- Hook always fails closed: run `./scripts/setup_presidio.sh` so Presidio/spaCy load.
- Restart Cursor after editing `.cursor/hooks.json`.
