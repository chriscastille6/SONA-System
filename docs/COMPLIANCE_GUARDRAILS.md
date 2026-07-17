# Compliance Guardrails & Decision Explainability

PRAMS includes an automated warning system aligned with:

- CITI (Human Subjects, Information Security, Data Privacy)
- FERPA
- Louisiana La. R.S. 17:3914
- **Nicholls Policy & Procedure Manual** (esp. §5.3.5 IT Policy; §5.7 FERPA monitoring; §2.7.1 AI syllabus policy) — https://www.nicholls.edu/policy-procedure-manual/
- **Nicholls IT Policies & Procedures** — https://www.nicholls.edu/information-tech/policyandprocedure/
- **Louisiana Executive Order JML 25-109** (Amended State Government's Use of AI) — https://www.doa.la.gov/media/tzqptbak/jml-25-109-amended-state-government-s-use-of-ai.pdf
- APA CPTA *Responsible Use of AI in Assessment* (2026)
- SIOP CAPE AI Ethics Considerations Brief (2025)
- Landers & Nakamoto (2025) + APA Ethical Principles

See also: [`AUTHORITIES_PPM_JML25109.md`](AUTHORITIES_PPM_JML25109.md).

This is **not** a senate proposal layer. It makes day-to-day workflows explainable and hard to violate unwittingly.

## What it does

| Gate | Soft warning | Hard block | Audit trail |
|------|--------------|------------|-------------|
| Protocol submit | Missing confidentiality/storage/consent; third-party share; mosaic cues; cloud AI provider context | Public/consumer LLM processing of data; DeepSeek / prohibited foreign AI (`COMPLIANCE_BLOCK_PUBLIC_AI_IN_PROTOCOL`) | `AuditLog` action `protocol_submit` / `_blocked` with principle citations |
| AI IRB review preflight | Cloud provider + possible IPI (JML 25-109 §6; PPM §5.3.5) | Optional (`COMPLIANCE_BLOCK_CLOUD_AI_WITH_IPI`); always block DeepSeek | Stored on `IRBReview.ai_model_versions.compliance_preflight` |
| Course credits CSV export | Identifiable FERPA export; no public AI | HITL attestation required (`COMPLIANCE_REQUIRE_HITL_FOR_EXPORT`) | `ferpa_export` / `_blocked` |
| IRB determination / decision | — | Substantive written rationale required | `college_rep_determination` / `protocol_decision` |

## Settings (`env.example`)

```
COMPLIANCE_WARNINGS_ENABLED=True
COMPLIANCE_BLOCK_PUBLIC_AI_IN_PROTOCOL=True
COMPLIANCE_BLOCK_CLOUD_AI_WITH_IPI=False
COMPLIANCE_REQUIRE_HITL_FOR_EXPORT=True
COMPLIANCE_REQUIRE_DECISION_RATIONALE=True
```

Prefer `IRB_AI_PROVIDER=ollama` on university-managed hardware when materials may contain IPI.

## Code map

- `apps/compliance/principles.py` — principle registry + authority language
- `apps/compliance/scanners.py` — IPI / public-AI / DeepSeek / mosaic heuristics (counts only; no raw PII in logs)
- `apps/compliance/guardrails.py` — evaluation engine
- `apps/compliance/explainability.py` — `AuditLog` decision traces
- Templates: `templates/compliance/_warnings_panel.html`, `templates/reporting/export_compliance_gate.html`

## Tests

```bash
python manage.py test apps.compliance.tests.test_guardrails
```

Synthetic data only; scanners assert matched emails are not retained in scan result strings.
