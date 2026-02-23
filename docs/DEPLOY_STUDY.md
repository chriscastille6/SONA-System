# Deploy a study to bayoupal

To deploy a **specific study** to PRAMS on bayoupal (code pull + migrate + run that study’s setup), use the deploy-study script from the **SONA System** repo.

## One command

From the SONA System repo root:

```bash
./scripts/deploy-study.sh <study-slug>
```

Examples:

```bash
./scripts/deploy-study.sh whole-person-fit
./scripts/deploy-study.sh ei-rpm
./scripts/deploy-study.sh conjoint-analysis
```

This will, on the server:

1. `git pull origin main`
2. `pip install -r requirements.txt`
3. `python manage.py migrate --noinput`
4. `python manage.py collectstatic --noinput`
5. Run the management command(s) for that study (e.g. `add_whole_person_fit_study_online`)

## Config: which studies and commands

**File:** `config/deployable_studies.txt`

Format: `slug:command1,command2` (one or more commands, comma-separated).

| Slug                | Command(s) |
|---------------------|------------|
| `tro`               | `add_tro_study_online` |
| `conjoint-analysis`  | `add_tro_study_online` |
| `ei-rpm`             | `create_ei_rpm_study`, `enter_ei_rpm_protocol` |
| `whole-person-fit`   | `add_whole_person_fit_study_online` |
| `hr-sjt`             | `add_hr_sjt_study_online` |

To add a new study:

1. Add a line to `config/deployable_studies.txt`: `my-study:add_my_study_online`
2. Create `apps/studies/assets/irb/my-study/study_config.json` (study basics)
3. Create `apps/studies/assets/irb/my-study/protocol.json` (full IRB protocol – so reviewers can see details; see `add_whole_person_fit_study_online` or `add_hr_sjt_study_online` for the JSON structure)
4. Implement `apps/studies/management/commands/add_my_study_online.py` (create study + call `create_or_update_protocol_from_json` from `apps.studies.irb_utils`)
5. Run `./scripts/deploy-study.sh my-study`

## Whole Person Fit

The command `add_whole_person_fit_study_online` reads from:

**`apps/studies/assets/irb/whole-person-fit/study_config.json`** – Study basics (slug, title, description, PI, credit, etc.)

**`apps/studies/assets/irb/whole-person-fit/protocol.json`** – Full IRB protocol (all 16 sections). If present, the command creates a draft ProtocolSubmission so reviewers can see the protocol details in PRAMS without manual entry.

If `study_config.json` is missing, the command prints where to create it and exits. Copy from `study_config.json.example` and fill in at least: `slug`, `title`, `description`, `researcher_email`, `credit_value`, `mode`.

After deployment, the study and protocol draft appear in PRAMS. The researcher can submit for approval to Jon Murphy and Juliann Allen (see `docs/IRB_AGENT_GUIDE.md`).

## Requirements

- SSH access to bayoupal: `ssh bayoupal` works from your Mac.
- Code for the study (and any new command) pushed to GitHub so the server can `git pull`.
- For Whole Person Fit: `study_config.json` present in the repo (so after pull the server has it).

## Telling an agent to deploy

You can say:

- “Deploy the whole-person-fit study to bayoupal” → run `./scripts/deploy-study.sh whole-person-fit`
- “Deploy the ei-rpm study” → run `./scripts/deploy-study.sh ei-rpm`
- “Deploy the hr-sjt study” → run `./scripts/deploy-study.sh hr-sjt`

## HR Situational Judgment Test (hr-sjt)

The HR SJT study is from the MNGT 425 – HR Analytics teaching project. The assessment is hosted at `https://bayoupal.nicholls.edu/hr-sjt-assessment/`. The command `add_hr_sjt_study_online` reads from **`apps/studies/assets/irb/hr-sjt/study_config.json`**. After deployment, the study URL for participants is `https://bayoupal.nicholls.edu/hr-sjt-assessment/index.html?study={study-id}` (use the study UUID from the database).

The agent should run the script from the SONA System repo root. If the study slug is unknown, run `./scripts/deploy-study.sh` with no arguments to list available slugs.
