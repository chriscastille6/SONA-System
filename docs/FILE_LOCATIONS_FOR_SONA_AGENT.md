# File Locations for SONA Agent — Decision Making and Unethical Behavior (EXT-AM4)

**Use this when:** You need to pull study materials, vignettes, IRB text, or deployment info for the **Decision Making and Unethical Behavior** study (EXT-AM4 / goals-refs). Paths below are **relative to that project’s root** (the “Decision Making and Unethical Behavior” project folder), not the SONA System repo.

If you are in the SONA System repo only, open or reference the other project and use these paths there.

---

## Paths grouped by use

### IRB
- **IRB vignettes, hypotheses, stopping, retirement:** `docs/IRB_EXTAM4_vignettes_hypotheses_stopping_retirement.md`
- **SONA summary:** (see docs index or IRB doc above)

### Study
- **Study page:** `docs/study/study_extam4.html`
- **Protocol:** `docs/study/protocol.html`
- **BayouPAL deployment:** `docs/BAYOUPAL_DEPLOYMENT.md`

### Vignettes
- **Vignettes with predicted patterns (HTML):** `docs/vignettes_with_predicted_patterns.html`
- **Vignette bank (JSON):** `config/vignette-bank.json`
- **Vignettes (CSV):** `config/vignettes.csv`

### Hypotheses / design / power
- **Hypotheses, frameworks, priors:** `docs/EXT-AM4_hypotheses_frameworks_priors.html`
- **Sequential power:** `docs/EXT-AM4_sequential_power.html`

### Index
- **Docs index:** `docs/index.html`  
  (Links to “Study (for SONA)” and this file.)

---

## Quick copy-paste (one-line paths)

```
docs/IRB_EXTAM4_vignettes_hypotheses_stopping_retirement.md
docs/study/study_extam4.html
docs/study/protocol.html
docs/BAYOUPAL_DEPLOYMENT.md
docs/vignettes_with_predicted_patterns.html
config/vignette-bank.json
config/vignettes.csv
docs/EXT-AM4_hypotheses_frameworks_priors.html
docs/EXT-AM4_sequential_power.html
docs/index.html
```

---

## Data collection decision rules (for SONA agent)

**Source of truth:** The full document is `docs/DATA_COLLECTION_DECISION_RULES.md` in the Decision Making and Unethical Behavior project. The rules below are the canonical summary for stopping and retiring vignettes. Use them when you cannot read that file (e.g. when working only in the SONA System repo).

### Global study rules
- **BF threshold:** 10 (stop data collection for a vignette when BF ≥ 10 for the designated hypothesis).
- **Min N:** 10 (do not evaluate stopping or retirement until at least 10 valid responses per vignette).
- **Max N:** 1000 (cap total responses per vignette at 1000; treat as a stopping boundary if reached before BF threshold).

### When to retire a vignette
A vignette is **retired** (no further data collection) when any of the following is reached:
- **BF_alt:** BF for the alternative hypothesis (e.g. goal-frame effect) ≥ threshold (10).
- **BF_null:** BF for the null hypothesis ≥ threshold (10).
- **max_n:** Total valid N for that vignette reaches 1000.

Once retired, do not collect or use new data for that vignette for the stopping-decision analysis.

### What counts as valid
- Only responses that meet the study’s validity criteria (e.g. completed vignette, attention checks if defined) count toward N and toward BF computation for stopping/retirement.
- Invalid or incomplete responses are excluded from N and from the analysis used for decision rules.

---

## Smoke test flow (goals-refs)

Pretend smoke test for PI notifications (no live wiring). Run: `python3 manage.py smoke_test_goals_refs_emails` or `./venv/bin/python manage.py smoke_test_goals_refs_emails` (or activate venv first: `source venv/bin/activate` then `python manage.py smoke_test_goals_refs_emails`). Optional: `--output docs/smoke_test_goals_refs_emails.txt` to write to a file.

1. **Sample size threshold (e.g. N ≥ 10 per vignette):** Analysis is triggered for that vignette; the PI is notified by email (Notification 1) that the threshold was reached and that a follow-up will be sent if the evidence threshold is reached.
2. **Evidence threshold (BF ≥ 10 for the hypothesis):** Analysis is summarized; the system suggests retiring the vignette; the PI is notified by email (Notification 2) with the summary, suggestion, and instructions.
3. **Retirement decision:** The PI replies to Notification 2 (e.g. "Retire R1" or "Keep R1"); that reply determines whether the vignette is retired. No automatic retirement is applied.

---

**Instructions for the SONA agent:** When working in this (SONA System) repo and you need EXT-AM4 study content, read this file for all file locations and the decision rules above. For files that live in the other project, open the Decision Making and Unethical Behavior project and use the paths above relative to that project’s root.
