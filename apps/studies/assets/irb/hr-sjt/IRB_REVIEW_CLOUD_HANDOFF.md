# HR SJT — IRB Review Cloud Handoff

Use this packet when asking a cloud agent to address IRB review concerns for the **HR Situational Judgment Test** (`hr-sjt`).

## What is ready

| Item | Location | Status |
|------|----------|--------|
| IRB application (structured) | `apps/studies/assets/irb/hr-sjt/protocol.json` | Drafted for PRAMS submission |
| IRB application (narrative) | `apps/studies/assets/irb/hr-sjt/HR_SJT_PROTOCOL_PRAMS.md` | Drafted for PRAMS submission |
| Study config | `apps/studies/assets/irb/hr-sjt/study_config.json` | `irb_status: pending` |
| All 27 situations + tactics | `apps/studies/assets/irb/hr-sjt/incidents.json` | Vendored for offline IRB review |
| Interactive IRB packet | `/studies/hr-sjt/run/` and `/studies/hr-sjt/protocol/vignettes/` | Skip + optional ratings demo |
| Documentation summary | `docs/HR_SJT_DOCUMENTATION.html` | Linked from protocol submission detail |

## IRB concern already addressed in materials

**Participants must not be forced to rate effectiveness on every item.**

Protocol language and the interactive packet state that:

1. Effectiveness ratings are **optional** (no `required` attributes on rating inputs).
2. Each situation has a **Skip this situation** control.
3. Participants may leave any or all ratings blank and may withdraw at any time.
4. There is no forced-choice ranking.

Reviewers verify this by opening the interactive packet and trying blank ratings + Skip.

## How to request follow-up work

Paste IRB comments into a cloud agent session on this branch/PR and point to this file. Example prompts:

- “Update the HR SJT protocol response to IRB comment: …”
- “Revise consent / risk language in `protocol.json` and `HR_SJT_PROTOCOL_PRAMS.md` for …”
- “Confirm incidents.json still matches the live instrument for situations X–Y.”

## Deploy / submit notes

- Load study online: `python manage.py add_hr_sjt_study_online` (or `./scripts/deploy-study.sh hr-sjt`).
- Suggested reviewers: Jon Murphy (CBA), Juliann Allen.
- Live participant app (API required): `https://bayoupal.nicholls.edu/hr-sjt-assessment/`.
- PI: Dr. Christopher Castille — christopher.castille@nicholls.edu.

## Suggested agent checklist when responding to IRB

1. Read the IRB comment verbatim.
2. Update `protocol.json` and keep `HR_SJT_PROTOCOL_PRAMS.md` in sync.
3. If wording/skip UX is questioned, update `templates/studies/hr_sjt_irb_full_study.html` and/or `incidents.json` as needed.
4. Refresh `docs/HR_SJT_DOCUMENTATION.html` if the summary changed.
5. Commit, push, and update the PR description with what changed for the reviewers.
