# PRAMS — Nicholls AI Use Inventory

**System:** PRAMS (Participant Recruitment and Management System)  
**Institution:** Nicholls State University  
**Host:** `bayoupal.nicholls.edu` (internal)  
**Review path:** bayouops GitLab → IT review → deployment  
**Prepared for:** bayouops, IT, Academic Affairs, executive leadership  
**Date:** July 2026  
**Related:** [LOUISIANA_AI_FERPA_COMPLIANCE_STACK.md](LOUISIANA_AI_FERPA_COMPLIANCE_STACK.md) | [PRESIDENT_EXECUTIVE_BRIEF.md](PRESIDENT_EXECUTIVE_BRIEF.md) | [FERPA_COMPLIANCE_MAPPING.md](FERPA_COMPLIANCE_MAPPING.md)

This inventory satisfies **Louisiana EO JML 25-103/25-109** (inventory, cleansing, CIO path), **Board of Regents** expectations, and **FERPA** documentation before institution-wide AI policy is finalized.

---

## System summary (non-technical)

PRAMS is **Nicholls-hosted research infrastructure** — a SONA replacement for IRB-compliant study recruitment and hosting of faculty research protocols. It is **not** a student-facing chatbot and **not** a general-purpose AI product.

| Attribute | Value |
|-----------|-------|
| Primary purpose | Research participation & protocol hosting |
| Student data posture | Anonymous research responses by default; optional credit mode increases FERPA scope |
| Foreign hostile AI (e.g., DeepSeek) | **Not used** |
| Production hosting | Nicholls server (`bayoupal`) |
| Code review | bayouops GitLab + IT |

---

## AI use case inventory

| # | Use case | Where | Required? | Student data? | Provider / location | Default status | EO / Regents alignment |
|---|----------|-------|-----------|---------------|---------------------|----------------|------------------------|
| 1 | **Application development** (writing code, docs, tests) | Developer workstation; Cursor IDE | No — dev only | **No** — synthetic data only; never paste real rosters/grades into AI chat | Cursor → US model providers; **Privacy Mode ON** | Active (development) | Dev tooling; not production AI. Code reviewed via bayouops before deploy. |
| 2 | **Cloud Agent** (optional remote dev assistance) | Cursor cloud environment | No — dev only | **No** — repo contains no production DB dumps or student exports | Cursor infrastructure | Active (development) | Same as #1. Not participant-facing. |
| 3 | **IRB protocol AI review** (optional admin feature) | `apps/studies/irb_ai/` inside PRAMS | **No — disable-able** | **Should not** — protocol text only; screener blocks high-risk patterns | **Recommended:** Ollama on `bayoupal` or institutional server | **Configurable — recommend OFF until Nicholls AI policy** | CIO/IT-approved infra; no foreign hostile AI; data stays on campus |
| 4 | **External LLM IRB review** (OpenAI, Anthropic, Gemini) | PRAMS settings `IRB_AI_PROVIDER` | No | Risk if uploads contain identifiable student info | Third-party US vendors | **Recommend DISABLED** | Requires vendor review; prompt screener blocks worst cases; not needed for operation |
| 5 | **Participant-facing AI** | None | — | — | — | **Not implemented** | N/A |

---

## Data flows (production)

```
Participants → bayoupal (PRAMS) → PostgreSQL (on campus)
                      ↓
              Response table (anonymous session_id only)
                      ↓
         [Optional] Ollama on bayoupal for IRB staff only
                      ✗ No DeepSeek / foreign hostile AI
                      ✗ No external LLM (recommended default)
```

**Development flow (separate from production):**

```
Developer → Cursor (Privacy Mode) → Git push → bayouops GitLab → IT review → bayoupal deploy
```

---

## Controls already in place

| Control | Purpose |
|---------|---------|
| bayouops GitLab review | Institutional code review before production |
| Self-hosted deployment | Louisiana data stays on Nicholls infrastructure |
| `FERPAPromptScreener` | Blocks high-risk prompts to external LLMs |
| Hash-only AI audit log | Forensics without storing full prompts externally |
| Anonymous `Response` model | Research payloads not linked to participant identity |
| RBAC + PostgreSQL RLS | Access control on identifiable participation data |
| `AI_REVIEW_ENABLED` flag | IT can disable all runtime AI |

---

## Recommended institutional defaults (until Nicholls AI policy exists)

| Setting | Recommendation |
|---------|----------------|
| `AI_REVIEW_ENABLED` | `False` |
| `IRB_AI_PROVIDER` | `ollama` (only if AI review needed) |
| External LLM API keys | Not configured in production |
| Cursor Privacy Mode | **On** for all developers |
| Real student data in dev/AI chat | **Prohibited** |
| Course credit mode | **Off** unless Registrar/IRB require it |

---

## Approval checklist for bayouops / IT

- [ ] Code reviewed in bayouops GitLab
- [ ] Deployed only to `bayoupal.nicholls.edu` (or approved Nicholls VM)
- [ ] TLS/HTTPS via institutional certificate
- [ ] No DeepSeek or other EO-banned foreign AI platforms
- [ ] Runtime AI disabled OR limited to on-prem Ollama with IT approval
- [ ] No third-party analytics/tracking pixels on student record pages
- [ ] `.env` secrets not committed; production credentials IT-managed
- [ ] Inventory filed with IT (this document)

---

## Sign-off block (optional)

| Role | Name | Date | Notes |
|------|------|------|-------|
| Project lead | | | |
| bayouops reviewer | | | |
| IT | | | |
| Academic Affairs (awareness) | | | |

---

*This inventory supports GitLab review and leadership briefings. It is not a substitute for Nicholls General Counsel or a formal institutional AI policy.*
