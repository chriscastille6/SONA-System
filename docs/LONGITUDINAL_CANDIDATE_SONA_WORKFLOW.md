# Longitudinal survey workflow: SONA + CANDIDATE + Form B

Authoritative package: [`templates/projects/longitudinal-candidate/`](../templates/projects/longitudinal-candidate/README.md)

This document is the researcher-facing overview for an IRB-approved, client-side longitudinal design that awards SONA credit anonymously and keeps contact information unlinked from survey responses.

## Goals

- Pass SONA `survey_code` into Wave 1 without storing identity in the research file  
- Link Wave 1 ↔ Wave 2 with a 16-character CANDIDATE Hash ID (Sandnes, 2021, adapted)  
- Auto-redirect to SONA `redirect_credit.aspx` with `experiment_id`, `credit_token`, and `survey_code`  
- Collect optional email on Form B only; schedule Wave 2 + one 72-hour nudge in Microsoft 365  
- Require zero external databases and zero re-identification lookup tables  

## Authority alignment

- CITI: IPI vs de-identified; mosaic risk; HITL before external share  
- FERPA / La. R.S. 17:3914: no education-record PII in research exports  
- EO JML 25-109 §6–§7: no confidential data into consumer AI; cleanse datasets  
- Synthetic data only in this repository’s examples and tests  

## End-to-end path

1. Participant clicks study in SONA → opens Wave 1 with `?survey_code=…`  
2. Consent → three security questions → CANDIDATE ID computed in-browser  
3. Survey items completed → research JSON = `{candidate_id, responses, …}` (**no** `survey_code`)  
4. Browser redirects to SONA credit URL with `survey_code`  
5. Optional Form B (MS Forms) stores email in isolated Excel  
6. Power Automate sends Wave 2 invite at T+lag and one nudge at +72h  
7. Wave 2 recomputes the same CANDIDATE ID; researcher joins waves offline on `candidate_id`  

## Configure before fielding

1. Set `STUDY.sona` in `wave1/js/survey.js`  
2. Host Wave 1/2 on university HTTPS (or Qualtrics with equivalent embedded JS)  
3. Create Form B + Excel + Automate flows per `form_b/POWER_AUTOMATE_SETUP.md`  
4. Replace `IRB-XXXX-YYYY` placeholders  
5. Dry-run with synthetic `survey_code` and synthetic email only  

## Production note

Deploying with real participant contact lists or enabling live SONA credit tokens is a **production-tier** action. Confirm IRB approval language covers Form B, automated email, and CANDIDATE linking before go-live.
