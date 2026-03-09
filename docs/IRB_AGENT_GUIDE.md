# IRB Agent Guide: Draft and Submit for Approval

**Purpose:** This guide tells an agent how to draft an IRB application and submit it for approval to **Jon Murphy** (college representative) and **Juliann Allen** (reviewer) on the PRAMS (Participant Recruitment and Management System) at Nicholls State University.

**You must:** Work through the protocol template section by section, **tailor every section** for the specific study, then use the toolkit (if generating documents) and complete the PRAMS submission with the correct approvers.

**Decision Making / EXT-AM4 study:** For that project’s file locations (IRB docs, vignettes, study pages, config), read **[docs/FILE_LOCATIONS_FOR_SONA_AGENT.md](FILE_LOCATIONS_FOR_SONA_AGENT.md)**. Paths there are relative to the Decision Making and Unethical Behavior project root.

---

## 0. When you're in the study project (getting details for one study)

**Use this when you've been sent to another project folder that contains one study.** Your job there is to produce one structured file so the SONA workflow can tailor the IRB protocol later.

**If the study project has `platform/docs/AGENT_IRB_EXTRACT_TASK.md`:** Follow that task spec. It tells you where to look (README, STUDY.md, docs, irb/, design/, etc.) and which headings to use. Output **`IRB_STUDY_DETAILS.md`** at repo root or **`irb/study_details.md`**.

**If there is no AGENT_IRB_EXTRACT_TASK.md:** Use the steps below and the **fixed section headings** so the SONA workflow can map each block to the protocol template.

### 0.1 Find where the study is described

- Look in: `README.md`, `STUDY.md`, `docs/` (e.g. study_design, methods), `irb/`, `design/`, and any filenames containing study, protocol, irb, design, consent, or recruitment.
- Read those files and any linked docs (procedures, instruments, consent, recruitment).

### 0.2 Write one file with these exact section headings

Produce **`IRB_STUDY_DETAILS.md`** (repo root) or **`irb/study_details.md`** with the following headings. SONA maps by these headings; do not rename them.

- **Study title**
- **Primary research question; hypothesis/prediction**
- **Population and relevant departments**
- **Duration (minutes) and credit value**
- **Procedures (consent → demographics → assessments → feedback → debriefing)**
- **Assessments and tasks (each named and briefly described)**
- **Research objectives and research questions (numbered)**
- **Main topic and key concepts (for debriefing/benefits)**
- **Educational justification; benefits to subjects; risks and mitigation**
- **Data collection methods**
- **Principal Investigator (PI) (name, title, department, email, phone)**
- **Co-Investigators (if any)**
- **Recruitment (PRAMS, etc.; inclusion/exclusion; technical requirements)**
- **Lab/sponsorship (if any)**
- **Optional: Consent text, Recruitment copy, Instrument descriptions** — include inline or paths.

Use the study's own wording; keep it accurate and specific. If something isn't stated, note "Not specified—confirm with PI."

### 0.3 Checklist (study project output)

- [ ] One file: `IRB_STUDY_DETAILS.md` or `irb/study_details.md`
- [ ] All fixed headings above present (same wording)
- [ ] Each section filled from study docs (or "Not specified—confirm with PI")
- [ ] Optional: consent text, recruitment copy, or instrument descriptions included or linked

When you're back in the SONA System repo with this file (or its contents), use it to tailor every section of the protocol template (Step 1 below).

---

## 1. Use the Protocol Template and Tailor Every Section

**Primary source:** `PROTOCOL_ENTRY_TEMPLATE.md` (repository root)

Do **not** only point to the template. You must:

1. **Open and follow** `PROTOCOL_ENTRY_TEMPLATE.md` as your section-by-section checklist.
2. **Tailor every section** for the study you are drafting:
   - Replace all placeholders (e.g. `[PRIMARY RESEARCH QUESTION]`, `[RELEVANT DEPARTMENTS]`, `[DURATION]`, `[OBJECTIVE 1]`, `[ASSESSMENT/TASK 1]`, `[STUDY TITLE]`, `[TOPIC]`, `[X]` credit/minutes) with the actual study details.
   - Adapt procedures, objectives, research questions, benefits, risks, and data handling to match the study.
   - Keep the **structure** (numbered lists, headings) and **required language** from the template.
3. **Preserve PRAMS/Nicholls wording** from the template:
   - Use **"PRAMS"** (Participant Recruitment and Management System), never "SONA."
   - Use **"may receive"** or **"potentially receiving"** for course credit (not "will receive").
   - Include **"Feedback reports are made available"** in compensation where applicable.
   - Use **"PRAMS ID numbers"** for participant identification.
   - Data sharing: **"Individual participant data will be shared but in anonymized form"** when applicable.
4. **Apply the Quick Checklist** at the end of the template (PRAMS wording, dates, PI/department, consent opt-out, OSF if applicable, exempt justification).
5. **Set dates** from the template guidance: start date typically ~2 weeks from current date; completion typically ~6 months from start.

Result: one fully tailored protocol text (all 16 sections) ready for documents and/or PRAMS entry.

---

## 2. Generate IRB Documents (When Needed)

If the submission requires a formal IRB application PDF/Word (e.g. for upload to PRAMS or for the college rep):

**Toolkit:** `IRB_Automation_Toolkit/`  
**README:** `IRB_Automation_Toolkit/README.md`  
**Process guide:** `IRB_Automation_Toolkit/docs/NICHOLLS_IRB_GUIDE.md`

1. **Content:** Populate the toolkit templates using your **tailored** content from Step 1 (PI/Co-I, title, description, population, procedures, consent, etc.).
2. **Templates to use:**
   - Exempt studies: `IRB_Automation_Toolkit/templates/IRB_Exempt_Template.Rmd`
   - Non-exempt: `IRB_Automation_Toolkit/templates/IRB_Application_Template.Rmd`
3. **Screenshots:** If the study has a web app or survey, use the toolkit’s screenshot scripts and configs; add screenshots to the application per `IRB_Automation_Toolkit/README.md` and `docs/SCREENSHOT_GUIDE.md`.
4. **Formatting:** Follow Nicholls HSIRB formatting (Times New Roman 12pt, single-spaced, 1" margins, HSIRB page markers). See `IRB_Automation_Toolkit/docs/FORMATTING_STANDARDS.md` and `configs/nicholls_hsirb_settings.json`.
5. **Generate:** Use the toolkit’s R/Pandoc workflow to produce PDF and Word; verify with `verify_formatting.py` if available.

Use the **same tailored text** from the protocol template in these documents so PRAMS and submitted docs match.

---

## 3. Submit in PRAMS and Assign to Jon Murphy and Juliann Allen

**PRAMS base URL:** https://bayoupal.nicholls.edu/hsirb/

### 3.1 Create or Identify the Study

- If the study does not exist: create it via the Researcher Dashboard (e.g. studies/researcher/) with title, description, and basic details.
- If it already exists: note the study and ensure slug/title match the protocol.

### 3.2 Enter Protocol and Submit

- Use the **tailored** protocol from Step 1 to fill the protocol submission form in PRAMS (all 16 sections as in the template).
- Upload required documents (e.g. approval letter if post-approval, protocol application PDF, CITI certificates) per PRAMS prompts.
- **Suggested reviewers:** In the submission, specify:
  - **Jon Murphy** (College of Business Administration representative)
  - **Juliann Allen**
- Submit the protocol for IRB review so it enters the queue for the college rep.

### 3.3 Approvers

- **Jon Murphy** – College rep (CBA). Submissions for Business-admin studies are assigned to him; he can make determination (Exempt/Expedited/Full) and approve exempt protocols. Ensure the study’s college/department is such that he is the rep, or assign per system rules.
- **Juliann Allen** – IRB member/reviewer. She can be assigned as a reviewer (e.g. for expedited review). Her account must exist as an IRB member; if not, run `python manage.py add_juliann_allen_irb` (see `apps/studies/management/commands/add_juliann_allen_irb.py`).

### 3.4 References for Submission and Approval

- **Jon Murphy’s workflow and URLs:** `JON_MURPHY_APPROVAL_GUIDE.md`
- **System readiness (protocol list, determination, approval, emails):** `JON_MURPHY_READINESS_CHECKLIST.md`
- **Deploying an already-approved study into PRAMS:** `GOAL_SETTING_STUDY_PRAM_DEPLOYMENT_PLAN.md`
- **Reassigning to Business and Juliann Allen:** `apps/studies/management/commands/reassign_ei_protocol_to_business.py` (example of assigning to Jon Murphy and Juliann Allen)

---

## 4. Summary Checklist for the Agent

- [ ] Read `PROTOCOL_ENTRY_TEMPLATE.md` and work through **every section**.
- [ ] **Tailor** all placeholders and study-specific content (objectives, procedures, risks, benefits, etc.) for the study.
- [ ] Keep PRAMS/Nicholls language (PRAMS, “may receive” credit, feedback reports, anonymized data sharing, etc.).
- [ ] Run through the template’s **Quick Checklist** before submission.
- [ ] If generating PDF/Word, use `IRB_Automation_Toolkit` with the **same tailored content** and Nicholls formatting.
- [ ] Create or locate the study in PRAMS and enter the **full tailored protocol** into the protocol submission form.
- [ ] Set **suggested reviewers** to **Jon Murphy** and **Juliann Allen**; ensure submission is assigned to Jon Murphy as college rep and Juliann Allen as reviewer where applicable.
- [ ] Use `JON_MURPHY_APPROVAL_GUIDE.md` and `JON_MURPHY_READINESS_CHECKLIST.md` for submission/approval steps and verification.

---

## 5. Getting one study submitted (e.g. Whole Person Fit)

**Two-phase flow:**

| Phase | Where | What to do |
|-------|--------|------------|
| **A. Extract** | Study project folder | Follow `platform/docs/AGENT_IRB_EXTRACT_TASK.md` (or Section 0 above). Produce **`IRB_STUDY_DETAILS.md`** or **`irb/study_details.md`** with the fixed section headings. |
| **B. Draft & submit** | SONA System repo | Open that study's `IRB_STUDY_DETAILS.md` (or paste its contents). Use it to tailor **`PROTOCOL_ENTRY_TEMPLATE.md`** section by section (Section 1). Then generate docs if needed (Section 2), create/locate the study in PRAMS, enter the tailored protocol, set suggested reviewers **Jon Murphy** and **Juliann Allen**, and submit (Section 3). |

**For Whole Person Fit specifically:** Send an agent to the Psychological Assessments project with instructions to follow the task in `platform/docs/AGENT_IRB_EXTRACT_TASK.md` (full path: see `docs/PSYCHOLOGICAL_ASSESSMENTS_PATHS.md`). Once `IRB_STUDY_DETAILS.md` exists there, bring that file (or its contents) into the SONA System context and run the rest of this guide to draft the protocol and submit for approval to Jon Murphy and Juliann Allen. That paths doc also lists the Whole Person Fit flyer and FERPA/compliance files.

---

## 6. Key File Reference

| What | Where |
|------|--------|
| Section-by-section protocol content (tailor this) | `PROTOCOL_ENTRY_TEMPLATE.md` |
| IRB document generation + screenshots | `IRB_Automation_Toolkit/README.md` |
| Nicholls IRB process (categories, submission) | `IRB_Automation_Toolkit/docs/NICHOLLS_IRB_GUIDE.md` |
| Jon Murphy approval workflow | `JON_MURPHY_APPROVAL_GUIDE.md` |
| System readiness for protocol review | `JON_MURPHY_READINESS_CHECKLIST.md` |
| Add Juliann Allen as IRB member | `apps/studies/management/commands/add_juliann_allen_irb.py` |
| Example: assign to Jon Murphy + Juliann Allen | `apps/studies/management/commands/reassign_ei_protocol_to_business.py` |
| Study-project extract task (in study repo) | `platform/docs/AGENT_IRB_EXTRACT_TASK.md` |
| Psychological Assessments / Whole Person Fit paths | `docs/PSYCHOLOGICAL_ASSESSMENTS_PATHS.md` |
| Deploy a study to bayoupal | `docs/DEPLOY_STUDY.md` |
