# Links for Juliann Allen — HR SJT IRB follow-up

Use these exact URLs (note the **`/hsirb/`** prefix on PRAMS pages).

## Scenarios (confirmed good)

Interactive packet — all 27 situations, skip + optional ratings (no Begin Assessment API needed):

https://bayoupal.nicholls.edu/hsirb/studies/hr-sjt/run/

## Survey / Begin Assessment

The live host at https://bayoupal.nicholls.edu/hr-sjt-assessment/ currently errors on **Begin Assessment** because the session API (`/platform-api/hr-sjt/sessions`) is not available (proxy/backend).  

**For IRB wording and skip/optional-rating review, use the interactive packet above** — same 27 situations and tactics; nothing is submitted.

## Consent — professionals (updated)

Live:  
https://bayoupal.nicholls.edu/hsirb/studies/hr-sjt/professional-consent/

Static document (always works; attach or open in browser):  
- Repo: `docs/HR_SJT_PROFESSIONAL_CONSENT.html`  
- On GitHub (this PR): https://github.com/chriscastille6/SONA-System/blob/cursor/hr-sjt-irb-cloud-packet-7d1c/docs/HR_SJT_PROFESSIONAL_CONSENT.html  

Updates per your note: potential benefits, potential risks, and HSIRB Consent §9 verbiage.

## Consent — class / MNGT 425 (fixed link + document)

**Working live link** (must include `/hsirb/`):  
https://bayoupal.nicholls.edu/hsirb/studies/hr-sjt/student-data-consent/

Paths **without** `/hsirb/` return 404 (likely what broke earlier).

Static document:  
- Repo: `docs/HR_SJT_STUDENT_CONSENT.html`  
- On GitHub: https://github.com/chriscastille6/SONA-System/blob/cursor/hr-sjt-irb-cloud-packet-7d1c/docs/HR_SJT_STUDENT_CONSENT.html  

## HSIRB application packet (familiar reviewer format — primary)

Same Nicholls-branded style as *A Study in Decision Making* (cover, project information form, narrative, appendices A–E):

- **PDF:** `apps/studies/assets/irb/hr-sjt/materials/pdf/HSIRB_Application_HR_SJT_Rating_Effectiveness_full_packet.pdf`
- **GitHub:** https://github.com/chriscastille6/SONA-System/blob/cursor/hr-sjt-irb-cloud-packet-7d1c/apps/studies/assets/irb/hr-sjt/materials/pdf/HSIRB_Application_HR_SJT_Rating_Effectiveness_full_packet.pdf
- **Rebuild:** `python3 scripts/build_hr_sjt_hsirb_packet.py`
- **PRAMS:** Protocol Submissions → HR SJT → “View HSIRB application packet”

### Appendices in the packet
- A Professional consent  
- B Class/student consent  
- C Instrument (all 27 situations)  
- D Recruitment script (verbatim)  
- E CITI certificate (PI)

### Official rev9 exempt form (Juliann request — filled)
- Blank: `apps/studies/assets/irb/hr-sjt/HSIRB-exempt_review_request.rev9_2019.v2_BLANK.pdf`
- Filled PDF (pages 1–4 overlay + Attachment A + CITI): `apps/studies/assets/irb/hr-sjt/HSIRB_EXEMPT_REVIEW_REQUEST.pdf`
- Field map: `apps/studies/assets/irb/hr-sjt/HSIRB_EXEMPT_REVIEW_REQUEST.md`
- Rebuild: `python3 scripts/fill_hr_sjt_hsirb_exempt_form.py`
- Exemption: **Category D**, techniques **1** (educational tests) and **3** (survey/interview)

PR: https://github.com/chriscastille6/SONA-System/pull/4
