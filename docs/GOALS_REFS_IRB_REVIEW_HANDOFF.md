# Goals as Reference Points (`goals-refs`) — IRB review handoff

Use this after deploying the SONA System / HSIRB branch that contains the Wave 1 materials.

## What reviewers should open

| What | URL pattern (production) |
|------|---------------------------|
| **Run Protocol** (summary + links) | `https://bayoupal.nicholls.edu/hsirb/studies/goals-refs/run/` |
| **Protocol preview** (PI/staff; consent flow optional) | `https://bayoupal.nicholls.edu/hsirb/studies/goals-refs/protocol/preview/` |
| **Vignettes + priors / predicted patterns** (login + protocol access) | `https://bayoupal.nicholls.edu/hsirb/studies/goals-refs/protocol/documentation/` |
| **Compact vignette pool (JSON UI)** | `https://bayoupal.nicholls.edu/hsirb/studies/goals-refs/protocol/vignettes/` |
| **Live participant survey (Wave 1, hosted)** | `https://bayoupal.nicholls.edu/hsirb/studies/goals-refs/survey/` |
| **Protocol submissions queue** | `https://bayoupal.nicholls.edu/hsirb/studies/protocol/submissions/` |

**Note:** Documentation and vignette pool routes require an account with access to that study’s protocol materials (staff, PI, or assigned IRB reviewer).

## Wave 1 scope (single story)

- **Four** vignettes only: **R1, R2, E1, E2** (`apps/studies/assets/irb/goals-refs/vignettes.json`).
- All four per participant; random order; one **below** or **above** goal frame per vignette.
- Extended HTML (`vignettes_with_predicted_patterns.html`) = reference / future waves unless amended.

## Repo files (canonical)

- `apps/studies/assets/irb/goals-refs/INSTRUMENT_WAVE1.md` — one-paragraph instrument summary  
- `apps/studies/assets/irb/goals-refs/QUALTRICS_PARITY_CHECKLIST.md` — survey implementation checklist  
- `apps/studies/assets/irb/goals-refs/protocol.json` — protocol submission source  
- `apps/studies/assets/irb/goals-refs/study_config.json` — study seed (`credit_value` 0.5; `external_link` → hosted survey on bayoupal)  
- `apps/studies/assets/irb/goals-refs/irb_reviewer_full_study.html` — printable reviewer packet (optional PDF)

## Deploy & DB sync (server)

1. Pull latest code on **bayoupal**, install deps if needed, `migrate`, restart `hsirb-system` (see `docs/DEPLOY_STUDY.md`).
2. Run: `python manage.py add_goals_refs_study_online`  
   - Refreshes study fields from `study_config.json` and updates draft protocol from `protocol.json`.
3. **Study.external_link** is set from `study_config.json` to the **hosted** survey (`/studies/goals-refs/survey/`). Re-run `add_goals_refs_study_online` after deploy. Optional: use Qualtrics instead by changing `external_link` to your Qualtrics URL.
4. Smoke-test the four URLs above as an authorized reviewer.

## Email blurb (paste for IRB)

> Wave 1 uses four hypothetical vignettes (two replication choices, two extension judgments) with goal framing; materials and priors are linked from the protocol submission. Run Protocol and full documentation are on PRAMS at the study’s `run` and `protocol/documentation` paths (login as assigned reviewer).
