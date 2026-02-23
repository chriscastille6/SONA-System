# Goal Setting Study: IRB Deployment Plan for PRAMS

**Purpose:** Put your approved IRB for the goal setting study online on PRAMS (Participant Recruitment and Management System) at https://bayoupal.nicholls.edu/hsirb/

**Status:** Planning phase — the goal setting study was not found in the current project files. This plan uses the TRO/Conjoint Analysis deployment as the template.

---

## 1. What You Need Before Starting

| Item | Description | Where to Get |
|------|-------------|--------------|
| **IRB Approval Letter (PDF)** | Signed approval from HSIRB/college rep | Your IRB correspondence |
| **Protocol Number** | e.g., `IRBE20251031-005CBA` | On the approval letter |
| **Protocol Application (PDF)** | Full IRB application document | Your submission package |
| **Study Details** | Title, description, PI, Co-I, dates | From your protocol |
| **Approval Date** | When IRB approved | On the approval letter |
| **Approver** | College rep who approved (e.g., Jon Murphy) | On the approval letter |

---

## 2. Deployment Pattern (Based on TRO Study)

The TRO (Conjoint Analysis) study deployment in `add_tro_study_online.py` is the reference. For the goal setting study, you will need to:

### A. Create IRB Assets Folder

```
apps/studies/assets/irb/goal-setting/
├── [approval_letter].pdf      # e.g., castille_goal_setting_approval.pdf
├── [protocol_application].pdf  # Full IRB application
└── SONA_IRB_Summary.md         # Optional: brief summary for reviewers
```

### B. Create Management Command

Create `apps/studies/management/commands/add_goal_setting_study_online.py` modeled on `add_tro_study_online.py`. It will:

1. **Get or create the study** with slug `goal-setting` (or your preferred slug)
2. **Get or create PI and Co-I** user accounts
3. **Get or create college rep** (approver)
4. **Create ProtocolSubmission** with:
   - Protocol number from your approval letter
   - Decision: `approved`
   - Submitted/reviewed/decided dates
   - Approval notes
5. **Copy PDFs** from `apps/studies/assets/irb/goal-setting/` to `media/protocol_submissions/`
6. **Update study** `irb_status` to `approved`, set `irb_number`, `irb_approved_by`, `irb_approved_at`

### C. Study Must Exist in PRAMS

The study record must exist before the protocol can be linked. Options:

- **Option 1:** Create the study via the PRAMS web UI (Researcher Dashboard → Create Study), then run the command to add the protocol and approval.
- **Option 2:** Have the management command create the study (like TRO) if it doesn’t exist.

---

## 3. Step-by-Step Deployment Checklist

### Phase 1: Gather Materials

- [ ] Locate your IRB approval letter (PDF)
- [ ] Locate your protocol application (PDF)
- [ ] Note protocol number (e.g., `IRBE2025XXXX-XXXXXX`)
- [ ] Note PI name, email, department
- [ ] Note Co-I (if any)
- [ ] Note approval date and approver name
- [ ] Decide study slug (e.g., `goal-setting`)

### Phase 2: Add Files to Project

- [ ] Create folder: `apps/studies/assets/irb/goal-setting/`
- [ ] Copy approval PDF into that folder
- [ ] Copy protocol PDF into that folder
- [ ] (Optional) Add `SONA_IRB_Summary.md`

### Phase 3: Create Deployment Command

- [ ] Copy `add_tro_study_online.py` → `add_goal_setting_study_online.py`
- [ ] Replace TRO-specific values with goal setting study values:
  - `slug`, `title`, `description`
  - `protocol_number`
  - PI and Co-I emails
  - Approval dates and notes
  - PDF filenames in `possible_locations`

### Phase 4: Deploy to PRAMS (bayoupal)

1. SSH to server:
   ```bash
   ssh bayoupal
   ```

2. Navigate and activate:
   ```bash
   cd ~/hsirb-system
   source venv/bin/activate
   ```

3. Pull latest code:
   ```bash
   git pull origin main
   ```

4. Run the command:
   ```bash
   python manage.py add_goal_setting_study_online
   ```

5. Verify:
   - https://bayoupal.nicholls.edu/hsirb/studies/researcher/ — study appears and IRB status is approved
   - https://bayoupal.nicholls.edu/hsirb/studies/protocol/submissions/ — protocol submission shows as approved

---

## 4. Key Differences from TRO

| Aspect | TRO Study | Goal Setting Study |
|--------|-----------|--------------------|
| Slug | `conjoint-analysis` | `goal-setting` (or your choice) |
| PI | Martin Meder | _Your PI_ |
| Co-I | Christopher Castille | _Your Co-I_ |
| Protocol # | IRBE20251031-005CBA | _From your approval_ |
| Approval Date | Oct 31, 2025 | _From your approval_ |
| College Rep | Jon Murphy (Business) | _Depends on college_ |

---

## 5. If the Goal Setting Study Already Exists in PRAMS

If the study is already created (e.g., via web UI) but not yet approved:

1. Ensure the study has the correct slug (e.g., `goal-setting`).
2. The command should use `get_or_create` with that slug so it finds the existing study.
3. The command will only add the protocol submission and approval metadata; it will not overwrite the study if it already exists (unless you change the logic).

---

## 6. Next Steps

1. **Locate the goal setting study** — Confirm whether it exists in the repo or only in PRAMS.
2. **Provide IRB details** — Protocol number, approval date, PI/Co-I, approver.
3. **Add IRB files** — Place approval and protocol PDFs in `apps/studies/assets/irb/goal-setting/`.
4. **Generate the command** — I can draft `add_goal_setting_study_online.py` once you provide the exact values.

---

## 7. Reference Files

- **Deployment template:** `apps/studies/management/commands/add_tro_study_online.py`
- **TRO deployment guide:** `DEPLOY_TRO_STUDY.md`
- **Protocol model:** `apps.studies.models.ProtocolSubmission`
- **Study model:** `apps.studies.models.Study`
