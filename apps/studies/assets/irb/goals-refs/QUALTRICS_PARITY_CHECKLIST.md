# Qualtrics (or host) parity — goals-refs Wave 1

**Hosted option (PRAMS):** A full Wave 1 survey is implemented in-app at `/studies/goals-refs/survey/` (see `goals_refs_live_survey` view). Point `study_config.json` `external_link` there if you are **not** using Qualtrics.

Use this checklist if you use **Qualtrics** (or another host) instead—or to verify parity with the hosted survey.

## Scope

- [ ] Survey implements **only** vignettes **R1, R2, E1, E2** as defined in `vignettes.json` (same text and options as approved).
- [ ] Each vignette appears **once** per session, in **one** frame: **below goal** OR **above goal** (randomize frame per vignette).
- [ ] **Order** of the four vignettes is randomized (or fixed with IRB justification—random is default).

## Consent & procedures

- [ ] Opening consent text matches `study_config.json` / protocol submission (Wave 1: **four** vignettes, not 3–6).
- [ ] Demographics: only items justified in the protocol (minimal set).
- [ ] **Attention checks:** 1–2 items as described in protocol.
- [ ] **Debrief** text matches protocol (goals as reference points; no deception).

## Data & IDs

- [ ] PRAMS participant ID passed into survey (embedded data / URL) and stored for linkage.
- [ ] Research data file: **no** names; PRAMS ID as key unless protocol amended.
- [ ] Optional email for results summary collected **separately** from main analytic fields if used.

## Timing & credits

- [ ] Pilot **median completion time** is consistent with **15–25 minutes**; adjust listing if not.
- [ ] Credit value in PRAMS study record matches what participants see (**0.5** SONA credit unless amended).

## After checklist

1. Set **Study.external_link** (and `study_config.json` `external_link` before re-running `add_goals_refs_study_online`) to the **participant** URL (hosted survey or Qualtrics)—not the protocol preview URL.
2. Smoke-test: complete one full path as a test account; export data and confirm four vignette rows + frame coding.
