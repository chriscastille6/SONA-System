# Goals as Reference Points — emails (copy/paste)

Production base (adjust if your HSIRB mount differs): `https://bayoupal.nicholls.edu/hsirb/`

## A) IRB / faculty reviewers (what to open)

**Subject:** PRAMS review — Goals as Reference Points and Risk Taking (goals-refs)

Hello,

Please use the links below in order. **Login** may be required for some reviewer-only pages.

1. **Run Protocol** (overview, Wave 1 = four vignettes)  
   https://bayoupal.nicholls.edu/hsirb/studies/goals-refs/run/

2. **Vignettes + predicted patterns & priors** (extended reference document)  
   https://bayoupal.nicholls.edu/hsirb/studies/goals-refs/protocol/documentation/

3. **Compact Wave 1 pool** (JSON viewer)  
   https://bayoupal.nicholls.edu/hsirb/studies/goals-refs/protocol/vignettes/

4. **Protocol submissions** (if you use the queue)  
   https://bayoupal.nicholls.edu/hsirb/studies/protocol/submissions/

**PI:** Dr. Christopher Castille — christopher.castille@nicholls.edu — 985-449-7015  
**IRB:** Dr. Alaina Daigle — 985-448-4697  

Thank you,  
[Your name]

---

## B) Participants (after PRAMS signup — “easy path”)

**Subject:** (none — this is the study link text for PRAMS)

**Study link (hosted on PRAMS):**  
https://bayoupal.nicholls.edu/hsirb/studies/goals-refs/survey/

**Optional — pass PRAMS participant id** (if your redirect supports query strings):  
https://bayoupal.nicholls.edu/hsirb/studies/goals-refs/survey/?participant=PARTICIPANT_ID  

Replace `PARTICIPANT_ID` with the value your system uses, or omit the query string.

**What they do:** Consent → short demographics → 4 scenarios (random order) → attention checks → optional email → debrief → submit.

**Note:** Automated saving requires the study to be **active** and **IRB-approved** in PRAMS (`active_approved`). If submission fails, check IRB status and that `add_goals_refs_study_online` has been run after deploy.

---

## C) You (PI) — after deploy

1. Deploy code and run: `python manage.py add_goals_refs_study_online` (updates `external_link` from `study_config.json`).
2. Confirm **Study → external link** in admin points to `/studies/goals-refs/survey/`.
3. Open the survey in a private window and complete a test run once the study is approved.
