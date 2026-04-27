# Software IP and Copyright Risk Audit

**Repository:** PRAMS (repo: `prams-system`; folder: `PRAMS`). *Previously named SONA System.*  
**Audit focus:** Copyright, licensing, and trademark risks relative to **Sona Systems** (commercial participant management platform) and general IP exposure before public sharing.

**Note:** "SONA SYSTEMS" is a **registered trademark** of Sona Systems, Ltd. This audit treats that mark and related branding as potential sources of trademark/trade dress risk.

---

## 1. Code Origin Analysis

### 1.1 Findings

**No evidence of:**
- Code directly copied from proprietary Sona Systems software
- Decompiled or reverse‑engineered code (no decompilation comments, no obfuscated or vendor-specific structures)
- Replication of unique Sona implementation details (e.g., no Sona-specific APIs, SDKs, or internal naming)

**Code characteristics:**
- **Models** (`apps/studies/models.py` and related): Standard Django patterns (UUIDField, ForeignKey, choices, JSONField, custom managers). Naming (Study, Timeslot, signup, credits, eligibility) describes generic participant-management concepts, not Sona-specific features.
- **Views/URLs:** Django class- and function-based views, REST patterns; no imports or references to Sona libraries or proprietary modules.
- **Templates:** Bootstrap 5, Django template language, HTMX; layout and structure are generic (navbar, cards, tables).

**Suspicious / worth monitoring:**
- **None identified.** The codebase reads as an independent implementation of common participant-pool functionality (studies, timeslots, signups, credits, prescreening, IRB tracking), consistent with “inspired by” rather than derived from Sona.

### 1.2 Recommendation

- **No code changes required** for origin risk. If you have any legacy or third-party snippets, add a brief comment or NOTICE file indicating origin and license.

---

## 2. Text and Documentation Audit

### 2.1 Potential copying or derivative text

| Location | Quoted or paraphrased text | Assessment | Recommendation |
|----------|----------------------------|------------|----------------|
| **README.md** (line 119) | *"Sona Systems, Ltd. (2025). Participant recruitment & study management made simple. Retrieved ..."* | **Attribution/citation** of Sona’s tagline, not copied documentation. APA-style reference. | Keep as reference; ensure it’s clearly “inspired by” / “reference,” not implying endorsement. |
| **IRB_System_Guided_Tutorial.md** (line 2578) | Same citation as above | Same as README. | Same as above. |
| **IRB_System_Guided_Tutorial.md** (title, headers, body) | Repeated use of **"SONA Research Participant Management System"** as the **name of this system** (e.g. title line 2, header line 12, line 24, 1853, 2085, 2103, 2163, 2339, 2381, 2386, 2393, 2602, 2676, 2690) | **High risk.** Using “SONA” as the product name of your system blurs the line between “inspired by Sona” and implying this is Sona or a version of it. Could suggest affiliation or derivative product. | **Rewrite:** Use a distinct name everywhere (e.g. “PRAMS” or “Research Participant Management System” or “BayouPAL Participant System”). Use “SONA” only in a single “Inspired by / not affiliated” sentence. |
| **apps/studies/management/commands/enter_ei_rpm_protocol.py** (multiple lines) | Protocol text referring to “the SONA system,” “SONA (System for Online Research),” “SONA ID numbers,” “through the SONA system,” “posted on the SONA system,” “credit through SONA,” “stored in the SONA system,” etc. (e.g. 85, 115, 160–163, 184, 221, 236, 244, 259, 271, 285, 294, 299, 302, 309–310, 343, 361, 432, 441, 445) | **Medium–high risk.** (1) “System for Online Research” is commonly associated with Sona. (2) IRB/protocol text that says “SONA” could be read as referring to the commercial product or to your platform. (3) Your project already uses “PRAMS” and “PRAMS ID” elsewhere. | **Rewrite:** Replace all protocol references with “PRAMS” (or your chosen platform name) and “PRAMS ID numbers.” Use “Participant Recruitment and Management System (PRAMS)” or similar, not “SONA (System for Online Research).” |
| **apps/studies/assets/irb/conjoint-analysis/SONA_IRB_Summary.md** (title line 1, line 46–49) | Title “SONA IRB Summary” and “Deliverables for SONA Documentation,” “Reference this summary file … in SONA materials” | **Medium risk.** “SONA” used as the name of your system in IRB-facing docs. | Rename to “PRAMS IRB Summary” (or equivalent) and replace “SONA materials” with “PRAMS materials” or “platform materials.” |
| **env.example** (line 30) | `SITE_NAME=SONA Research Participation System` | **Medium risk.** Default display name uses “SONA” and “Research Participation System,” close to Sona’s space. | Change to e.g. `SITE_NAME=PRAMS` or `SITE_NAME=Participant Recruitment and Management System` (match `config/settings.py` default). |
| **QUICKSTART.md, DEMO_QUICK_START.md, ACTIVE_STUDIES.md, etc.** | Phrases like “Your SONA system is now …,” “SONA-like,” “SONA system ready” | **Low–medium risk.** Descriptive use (“SONA-like”) is less problematic than naming your product “SONA.” | Prefer “PRAMS” or “participant recruitment system” for the product; keep “SONA-like” only in a single disclaimer sentence if desired. |

### 2.2 Generic vs. potentially copied phrasing

- **“Participant recruitment,” “study management,” “research participant management”** – Generic domain terms; no change needed.
- **“Streamline research participant recruitment,” “IRB compliance”** – Generic; no change needed.
- **Tagline “Participant recruitment & study management made simple”** – Used only as a **cited** title of Sona’s offering (README, IRB tutorial). Retain only as attribution; do not use as your product’s tagline.

### 2.3 Summary of text recommendations

1. **Replace all uses of “SONA” as the name of this system** in documentation and protocol text with a distinct name (e.g. PRAMS or “Research Participant Management System”).
2. **In protocol text** (e.g. `enter_ei_rpm_protocol.py`): use “PRAMS” and “PRAMS ID numbers” consistently; remove “SONA (System for Online Research).”
3. **In IRB_System_Guided_Tutorial.md:** Retitle to a name that does not include “SONA”; add one clear “Inspired by Sona Systems. Not affiliated with Sona Systems.” (or similar).
4. **env.example:** Set `SITE_NAME` to a non‑SONA name (e.g. PRAMS or the same default as in `config/settings.py`).

---

## 3. UI / UX Similarity Check

### 3.1 What was reviewed

- **Layout:** `templates/base.html` – Navbar, container, footer; Bootstrap 5.
- **Participant flow:** Browse Studies → Study detail (timeslots) → Book → My Bookings; My Credits; Profile; Login/Register.
- **Terminology in UI:** “Browse Studies,” “My Bookings,” “My Credits,” “timeslot,” “signup,” “credit,” “Researcher Dashboard,” “IRB Dashboard,” “Protocol Submissions,” “Admin Panel.”

### 3.2 Assessment

- **Layout:** Generic (top nav, main content, footer). No distinctive Sona layout or trade dress identified.
- **Workflow:** Standard for participant-pool systems (list studies → choose timeslot → book → manage bookings → credits). This is **generic participant-management functionality**, not a copy of Sona’s proprietary flow.
- **Terminology:** “Browse Studies,” “My Bookings,” “My Credits,” “timeslot,” “signup,” “credit” are common in the domain. Sona may use similar terms; here they describe the same concepts any such system would have. **Not, by themselves, infringing replication of proprietary UI.**

### 3.3 Conclusion

- **No specific UI/UX changes recommended** for IP risk. The interface and workflow are generic participant-management patterns. To further reduce any trade dress concern, avoid copying Sona’s exact wording, color schemes, or layout details if you ever do a side‑by‑side comparison.

---

## 4. Trademark Risk (SONA / Sona Systems / SONA System)

### 4.1 Every occurrence (by file)

**Code / config / templates**

| File | Line(s) | Text |
|------|--------|------|
| `env.example` | 30 | `SITE_NAME=SONA Research Participation System` |
| `templates/base.html` | 94 | “Inspired by … Sona Systems. Not affiliated with Sona Systems.” |
| `config/urls.py` | 31 | Comment: “EXT-AM4 SONA summary” (internal doc reference) |
| `apps/studies/management/commands/enter_ei_rpm_protocol.py` | 85, 115, 160–163, 184, 221, 236, 244, 259, 271, 285, 294, 299, 302, 309–310, 343, 361, 432, 441, 445 | Protocol text: “SONA system,” “SONA (System for Online Research),” “SONA ID numbers,” etc. |
| `apps/studies/migrations/0007_conjoint_study.py` | 49, 78 | “SONA_IRB_Summary.md,” “SONA-facing protocol summary” |
| `templates/projects/ei-cat/protocol/index.html` | 15 | Comment: “SONA System Integration” |

**Documentation / markdown**

| File | Line(s) | Text |
|------|--------|------|
| `README.md` | 3, 39, 116, 119 | “SONA-like,” path “SONA System,” acknowledgment + Sona citation |
| `IRB_System_Guided_Tutorial.md` | 2, 12, 24, 1853, 2085, 2103, 2163, 2339, 2381, 2386, 2393, 2578, 2602, 2676, 2690 | “SONA Research Participant Management System,” “SONA System,” “Commercial SONA Systems,” “Open-Source SONA,” Sona citation |
| `IRB_DEMO_ONE_PAGER.md` | 1, 22, 29, 153–154, 158 | “SONA System Demo,” “commercial SONA,” “Title (SONA),” “SONA_IRB_Summary.md” |
| `IRB_SYSTEM_OVERVIEW.html` | 6, 226, 257, 482, 836 | “SONA Research Participation System” |
| `apps/studies/assets/irb/conjoint-analysis/SONA_IRB_Summary.md` | 1, 46, 49 | “SONA IRB Summary,” “SONA Documentation,” “SONA materials” |
| `QUICKSTART.md` | 5, 36, 163, 300, 304 | “SONA-like,” path “SONA System,” “Sona Systems” link |
| `RHEL_DEPLOYMENT_GUIDE.md` | 3, 162, 165, 256, 717 | “SONA System,” “SONA-System” repo, “SONA System Gunicorn” |
| `rhel_setup.sh` | 2, 8 | “SONA System” |
| `MERGE_COMPLETE_SUMMARY.md` | 5, 46, 72, 91, 98 | “SONA System,” “SONA,” “SONA platform” |
| `ACTIVE_STUDIES.md` | 1, 25, 202 | “SONA System” |
| `DEMO_QUICK_START.md` | 1, 3, 188, 235 | “SONA System Demo,” “Your SONA system” |
| `DEMO_GUIDE.md` | 1, 3, 239 | “SONA System Demo,” “SONA System” |
| `EI_PILOT_QUICK_START.md` | 5 | “SONA system” |
| `EI_PILOT_IMPLEMENTATION_SUMMARY.md` | 5, 348 | “SONA system” |
| `RAILWAY_DEPLOYMENT_GUIDE.md` | 5, 25, 33, 36–37, 52, 183 | “SONA demo,” “SONA System,” “SONA-System” repo |
| `RENDER_DEPLOYMENT_GUIDE.md` | 1, 9, 44, 232, 280 | “SONA System,” “SONA-System” repo |
| `PROJECT_STATUS.md` | 1, 67, 77, 123, 137, 158–160, 170, 184 | “SONA System,” paths, “ACTIVE STUDIES IN SONA” |
| `PROJECT_COMPARISON_REPORT.md` | 3, 11–14, 19, 29, 32, 38, 58–61, 95, 104, 113–120, 131–132, 143–144, 156, 167, 181, 187–188, 192, 194, 209, 218 | “SONA System” vs Psych Assessments |
| `PROTOCOLS_INTEGRATED.md` | 40, 63, 97, 102, 116, 133, 163 | “SONA API,” “Submit to SONA” |
| `PARTICIPANT_INFO_LINK.md` | 3, 15, 19, 37 | “this SONA System,” “If SONA runs” |
| `IRB_AI_IMPLEMENTATION_SUMMARY.md` | 208, 320 | “SONA,” “integrated into SONA” |
| `IRB_AI_CONFIGURATION.md` | 28, 43, 66, 78, 102, 144, 153, 170, 233 | “Configure in SONA,” “SONA System” path, “Restart SONA” |
| `IRB_AI_QUICK_START.md` | 42 | Path “SONA System” |
| `IRB_COLLEAGUE_EMAIL_CONDENSED.txt` | 36 | “Commercial SONA” |
| `IRB_COLLEAGUE_DEMO_EMAIL.md` | 91, 328 | “Commercial SONA Systems” |
| `IRB_BRIEFING_JULIANN_JON.html` | 153, 201 | “SONA/PRAMS,” “Purchase SONA” |
| `DEPLOYMENT_SUCCESS.md` | 145, 206, 233 | Path, “SONA-like,” “inspired by Sona Systems” |
| `DEPLOYMENT_START_HERE.md` | 11, 32, 40, 69, 192 | “SONA-System” repo, “SONA System” directory |
| `FINAL_AUDIT_SUMMARY.md` | 4, 335, 348 | “SONA-like,” “analogous to SONA Systems,” path |
| `docs/EXTAM4_SONA_SUMMARY.html` | 6, 23–24, 30, 63, 81 | “SONA Summary,” “SONA agent” |
| `docs/DEPLOY_STUDY.md` | 3, 7, 81 | “SONA System” repo |
| `deploy-to-server.sh` | 13, 49 | “SONA-System” repo name |
| `GOAL_SETTING_STUDY_PRAM_DEPLOYMENT_PLAN.md` | 32, 76 | “SONA_IRB_Summary.md” |
| `PROTOCOL_INTEGRATION_GUIDE.md` | 5, 24, 147, 302 | “SONA system,” “Submit to SONA” |
| `PROTOCOL_ENTRY_TEMPLATE.md` | 11, 363 | “PRAMS (not SONA),” checklist “Replace all SONA with PRAMS” |
| `BAYESIAN_MONITORING_GUIDE.md` | 5 | “SONA system” |
| `AUDIT_FIXES_APPLIED.md` | 184 | Path “SONA System” |
| `TEST_AS_JON_MURPHY.md` | 20, 28 | Path “SONA System” |
| `setup_instructions.md` | 10 | Path “SONA System” |
| `YOU_DO_THIS.md` | 12 | Path “SONA System” |
| `FERPA_AUDIT_REPORT.md` | 12 | “SONA System” |
| `apps/studies/assets/irb/hr-sjt/HR_SJT_PROTOCOL_PRAMS.md` | 262 | Checklist “Replace all SONA with PRAMS” (done) |

### 4.2 Recommendations

- **Product name:** Use a **distinct name** (e.g. **PRAMS** – Participant Recruitment and Management System) everywhere for this software. Do not call this product “SONA” or “SONA System.”
- **User-facing strings:** Prefer `SITE_NAME` from config (default in code is already “Participant Recruitment and Management System”). Set `SITE_NAME` in `env.example` to that or “PRAMS” — not “SONA Research Participation System.”
- **Documentation:** In all docs, replace “SONA system” (meaning this platform) with “PRAMS” or “participant recruitment system.” Keep “SONA” only where clearly referring to the commercial company (e.g. “inspired by Sona Systems” or “compared to commercial SONA”).
- **Protocol and IRB text:** Use “PRAMS” and “PRAMS ID numbers” only (see Section 2).
- **Repo/deploy references:** Renaming the repo from “SONA-System” to e.g. “PRAMS” or “participant-recruitment-system” would reduce trademark use; if you keep the repo name, add a clear disclaimer in README (see below).
- **Disclaimer (suggested for README and/or footer):**  
  *“This project is not affiliated with, endorsed by, or connected to Sona Systems, Ltd. ‘Sona Systems’ and ‘SONA’ are trademarks of Sona Systems, Ltd. This software is an independent implementation of participant recruitment and study management.”*

---

## 5. Licensing Issues

### 5.1 Repository license

- **No LICENSE file** found in the repository root. README states “MIT License” and IRB_System_Guided_Tutorial states “MIT License (Open Source).”
- **Risk:** Without a LICENSE file, downstream users have no explicit grant of rights; the “MIT” statement could be deemed ambiguous.

**Recommendation:** Add a root **LICENSE** file containing the full MIT License text and the correct year and copyright holder.

### 5.2 Dependencies (`requirements.txt`)

| Package | Typical license | Conflict? |
|---------|------------------|-----------|
| Django | BSD-3-Clause | No |
| djangorestframework | BSD-3-Clause | No |
| django-filter | BSD-3-Clause | No |
| django-cors-headers | MIT | No |
| psycopg2-binary | LGPL-2.0 / LGPL-3.0 | No (dynamic linking) |
| dj-database-url | BSD | No |
| celery | BSD-3-Clause | No |
| redis | MIT | No |
| django-celery-beat | BSD-3-Clause | No |
| django-celery-results | BSD-3-Clause | No |
| argon2-cffi | MIT | No |
| django-htmx | BSD-3-Clause | No |
| gunicorn | MIT | No |
| whitenoise | MIT | No |
| python-decouple | MIT | No |
| python-dateutil | Apache-2.0 / BSD | No |
| Pillow | HPND | No |
| anthropic | MIT | No |
| openai | Apache-2.0 | No |
| google-genai | Apache-2.0 | No |
| aiohttp | Apache-2.0 | No |
| PyPDF2 | BSD-3-Clause | No |
| python-docx | MIT | No |
| PyMuPDF | AGPL-3.0 | **Note:** AGPL has strong copyleft; ensure use is compliant (e.g. no proprietary distribution of modified versions without source). |
| qrcode | BSD-3-Clause | No |

**Summary:** No incompatible mix for normal use. **PyMuPDF (AGPL-3.0)** is the only strong copyleft dependency; if you distribute a modified version of the app, ensure AGPL compliance (source offer, etc.).

### 5.3 Code snippets / third-party code

- No “copied from …” or “© …” comments or obvious third-party snippets were found. The “cannot be printed (copyright)” strings in `templates/projects/ei-cat/protocol/comprehensive_item_bank.json` are **assessment item text** (likely “this option is disabled due to copyright”), not a license issue for the repo itself.

**Recommendation:** If you ever paste in code from Stack Overflow, docs, or other projects, add a short comment and comply with the snippet’s license.

---

## 6. Risk Summary

### HIGH RISK

| # | File(s) | Line(s) | Issue | Recommended fix |
|---|--------|--------|-------|------------------|
| 1 | `IRB_System_Guided_Tutorial.md` | 2, 12, 24, 1853, 2085, 2103, 2163, 2339, 2381, 2386, 2393, 2602, 2676, 2690 | This system is repeatedly named **“SONA Research Participant Management System,”** implying it is or is part of Sona’s product. | Rename the system throughout to “PRAMS” or “Research Participant Management System.” Use “SONA” only once in an “Inspired by Sona Systems. Not affiliated.” sentence. |
| 2 | `apps/studies/management/commands/enter_ei_rpm_protocol.py` | 85, 115, 160–163, 184, 221, 236, 244, 259, 271, 285, 294, 299, 302, 309–310, 343, 361, 432, 441, 445 | IRB/protocol text refers to “SONA system,” “SONA (System for Online Research),” “SONA ID numbers.” Blurs distinction between your platform and Sona’s trademark. | Replace all with “PRAMS” and “PRAMS ID numbers”; use “Participant Recruitment and Management System (PRAMS)” (or your chosen name), not “SONA (System for Online Research).” |

### MEDIUM RISK

| # | File(s) | Line(s) | Issue | Recommended fix |
|---|--------|--------|-------|------------------|
| 3 | `env.example` | 30 | `SITE_NAME=SONA Research Participation System` uses “SONA” as product name. | Set to e.g. `SITE_NAME=Participant Recruitment and Management System` or `SITE_NAME=PRAMS` (match code default). |
| 4 | `apps/studies/assets/irb/conjoint-analysis/SONA_IRB_Summary.md` | 1, 46, 49 | Title and body use “SONA” as the name of this system in IRB materials. | Rename file to e.g. `PRAMS_IRB_Summary.md`; replace “SONA” with “PRAMS” in body. |
| 5 | `IRB_SYSTEM_OVERVIEW.html` | 6, 226, 257, 482, 836 | “SONA Research Participation System” as the system name. | Replace with “PRAMS” or “Research Participant Management System.” |
| 6 | `IRB_DEMO_ONE_PAGER.md` | 1, 153–154, 158 | “SONA System Demo,” “Title (SONA),” “SONA_IRB_Summary.” | Use “PRAMS” for this system; keep “commercial SONA” only when comparing to vendor. |
| 7 | `apps/studies/migrations/0007_conjoint_study.py` | 49, 78 | References to “SONA_IRB_Summary.md” and “SONA-facing.” | If filename is renamed to PRAMS_IRB_Summary.md, add a migration or note that updates the reference; use “PRAMS-facing” in comments. |
| 8 | **No LICENSE file** | — | License grant is only stated in README/tutorial, not in a standard LICENSE file. | Add root **LICENSE** file with full MIT text and correct copyright holder. |

### LOW RISK

| # | File(s) | Line(s) | Issue | Recommended fix |
|---|--------|--------|-------|------------------|
| 9 | `templates/base.html` | 94 | “Inspired by … Sona Systems. Not affiliated with Sona Systems.” | **Keep.** Consider adding: “Sona Systems is a trademark of Sona Systems, Ltd.” |
| 10 | `README.md` | 116, 119 | Acknowledgment and citation of Sona. | **Keep** as attribution. Add the disclaimer from Section 4.2 (not affiliated, trademarks of Sona Systems, Ltd.). |
| 11 | Multiple docs (QUICKSTART, RAILWAY_DEPLOYMENT_GUIDE, etc.) | Various | “SONA system,” “SONA-like,” paths “SONA System.” | Replace “SONA system” (meaning this app) with “PRAMS” or “participant recruitment system.” Path “SONA System” is folder name; renaming to “PRAMS” or “prams-system” would reduce use. |
| 12 | `PROTOCOL_ENTRY_TEMPLATE.md`, `HR_SJT_PROTOCOL_PRAMS.md` | Checklist “Replace all SONA with PRAMS” | Good practice already; some protocol content elsewhere still uses SONA. | Ensure all protocol content and IRB-facing text follows this rule (see HIGH RISK #2). |
| 13 | `templates/projects/ei-cat/protocol/index.html` | 15 | Comment “SONA System Integration.” | Change to “PRAMS integration” or “participant system integration.” |
| 14 | `config/urls.py` | 31 | Comment “EXT-AM4 SONA summary.” | Change to “EXT-AM4 PRAMS summary” or “platform summary.” |
| 15 | PyMuPDF in `requirements.txt` | — | AGPL-3.0 dependency. | Document; ensure any distribution of modified software complies with AGPL (e.g. source offer). |

---

## 7. Suggested Order of Work

1. **Add LICENSE** (MIT) at repository root.
2. **Rename this system** in all user- and IRB-facing material from “SONA” to “PRAMS” (or chosen name), starting with HIGH RISK items (IRB_System_Guided_Tutorial.md, enter_ei_rpm_protocol.py).
3. **Update env.example** and any default SITE_NAME references to the same name (e.g. PRAMS).
4. **Rename SONA_IRB_Summary.md** to PRAMS_IRB_Summary.md (or equivalent) and update all references.
5. **Add disclaimer** in README (and optionally in footer) as in Section 4.2.
6. **Sweep remaining docs** for “SONA system” (meaning this platform) and replace with PRAMS or “participant recruitment system.”
7. **Optional:** Rename repo/folder from “SONA System” / “SONA-System” to “PRAMS” or “prams-system” and update paths in docs/scripts. *(Done: repo `prams-system`, folder `PRAMS`, paths and clone URLs updated.)*

---

*End of audit. This document is for internal risk assessment and does not constitute legal advice.*
