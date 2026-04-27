# goals-refs on the `/platform` Studies page

## Two different “Studies” surfaces

| Where | URL (typical) | What lists studies |
|--------|----------------|---------------------|
| **HSIRB / PRAMS (this repo)** | `https://bayoupal.nicholls.edu/hsirb/studies/` | Django `study_list` → only studies in **`Study.active_approved`** (IRB status `approved`, `exempt`, or `not_required`; active; not expired). |
| **Assessment / lab platform** | `https://bayoupal.nicholls.edu/platform/...` | **Separate app or static site** — not defined in this repository. Studies are usually added in *that* project’s config, CMS, or build step. |

So: making the study show on **HSIRB** = fix IRB fields + run `add_goals_refs_study_online`.  
Making it show on **`/platform`** = add an entry **in the platform project** (or wherever `platform/studies/` is built).

---

## What to add on the `/platform` side

Use whatever structure that site already uses (e.g. `study.html?id=...` with a lookup table, or a JSON catalog). Suggested **canonical URLs** for **Goals as Reference Points** (`goals-refs`):

| Field | Suggested value |
|--------|-----------------|
| **id** | `goals-refs` (or match your platform’s pattern, e.g. UUID from HSIRB `Study.id`) |
| **title** | Goals as Reference Points and Risk Taking |
| **short description** | Four short scenarios about goals, risk-taking, and ethical judgments (about 15–25 minutes). Up to 0.5 course credit where applicable. |
| **Participant URL** | `https://bayoupal.nicholls.edu/hsirb/studies/goals-refs/survey/` |
| **Protocol / info (optional)** | `https://bayoupal.nicholls.edu/hsirb/studies/goals-refs/run/` |

Optional query for passing a participant token (if your platform supports it):

`https://bayoupal.nicholls.edu/hsirb/studies/goals-refs/survey/?participant=PARTICIPANT_ID`

---

## EXT-AM4 Run Protocol UI (`/studies/goals-refs/run/`)

The in-PRAMS protocol template (`templates/projects/goals-refs/protocol/`) is styled to match the **Psychological Assessment Library** assessment instruments (e.g. **Loss Aversion Inventory** at `loss-assessment-inventory/index.html` on BayouPAL): Nicholls brand header, `max-w-3xl` cards, horizontal **`.likert-scale`** rows with hidden radios + labels, blue selection state (`#2563eb`), and numbered item badges—so the experience aligns with **Assessments** launched from `platform/index.html` / `platform/assessment-flow.html`.

## Snippet file for platform maintainers

See **`docs/platform_study_catalog_snippet.json`** in this repo — one object you can merge into a larger catalog or use as a template.

---

## HSIRB list visibility (if you only care about `/hsirb/studies/`)

If the study does **not** appear under **Browse Studies** in HSIRB, it is usually because `irb_status` is still `pending`. The browse list only includes `approved` / `exempt` / `not_required`. Update `apps/studies/assets/irb/goals-refs/study_config.json` when IRB allows listing, then run:

`python manage.py add_goals_refs_study_online`
