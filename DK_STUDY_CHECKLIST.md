# Dunning-Kruger × EI Study - Final Checklist

**Date**: October 22, 2025  
**Project**: SONA System  
**Study ID**: 95bc0b80-af71-4221-a7ac-72c6bbe20fb9  
**Test URL**: http://localhost:8002/studies/ei-dk/run/

---

## ✅ PROTOCOL COMPONENTS - ALL COMPLETE

### 1. Item Banks ✅
- **EI Items**: 60 total (24 tendency + 36 ability) 
  - File: `static/projects/ei-dk/data/ei60_mixed_format.json`
  - All items have dynamic `videoUrl` fields
  - Verified counts: 24 tendency, 36 ability
  
- **Perception Items**: 15 rapid face perception items
  - File: `static/projects/ei-dk/data/perception_items_page.json`
  - Emotion recognition task format

### 2. Consent Form ✅
- **Yes/No Options**: Two distinct buttons implemented
  - "No, I do not consent" → Redirects to /studies/ with alert
  - "Yes, I consent to participate →" → Proceeds to demographics
  - File: `templates/projects/ei-dk/protocol/index.html` (lines 168-176)

### 3. Demographics ✅
- **BLS/EEO-1 Race/Ethnicity Categories**: 
  - Hispanic or Latino
  - White (Not Hispanic or Latino)
  - Black or African American
  - Asian
  - American Indian or Alaska Native
  - Native Hawaiian or Other Pacific Islander
  - Two or More Races
  - File: `templates/projects/ei-dk/protocol/index.html` (lines 223-229)

### 4. Data Flow ✅
- **JavaScript**: `static/projects/ei-dk/sheldon_replication.js`
  - Captures consent (yes/no)
  - Captures demographics including ethnicity
  - Loads 60-item bank correctly
  - Uses dynamic video URLs from item bank
  - Submits to `/api/ei-dk/submit/`

### 5. Feedback ✅
- **Bayesian Analysis**: 
  - Percentile estimation
  - Bayes Factor reporting
  - Categorized by item format (tendency vs ability)
  - File: `templates/projects/ei-dk/feedback/index.html`

---

## 🧪 TESTING STATUS

### Manual Testing Completed ✅
- [x] Server runs without errors on port 8002
- [x] Study accessible at `/studies/ei-dk/run/`
- [x] Consent form displays with Yes/No buttons
- [x] Demographics form includes BLS ethnicity categories
- [x] Item bank loads all 60 items
- [x] Videos play correctly with dynamic URLs
- [x] Data submission endpoint exists (`/api/ei-dk/submit/`)

### Pending Manual Tests (Before OSF Upload)
- [ ] Complete full study run-through (consent → demographics → all items → feedback)
- [ ] Verify all 60 items display correctly
- [ ] Test perception items (15 face tasks)
- [ ] Confirm data saves to database (check Response model in admin)
- [ ] Verify Bayesian feedback displays correctly
- [ ] Test "No consent" redirect works
- [ ] Export sample data to verify all fields captured

---

## 📊 PRE-REGISTRATION MATERIALS (For OSF)

### Required Documents to Upload
1. **Pre-registered Hypotheses**
   - [ ] Document prepared
   - [ ] Uploaded to OSF

2. **Methods Section**
   - [ ] Full protocol description
   - [ ] Item bank details (60 EI + 15 perception)
   - [ ] Sampling plan
   - [ ] Analysis plan (Bayesian approach)
   - [ ] Uploaded to OSF

3. **Study Materials**
   - [ ] Consent form (HTML)
   - [ ] Demographics questionnaire
   - [ ] Item bank JSON files
   - [ ] Video stimuli (or links to video hosting)
   - [ ] Uploaded to OSF

4. **Analysis Code**
   - [ ] Bayesian feedback algorithm
   - [ ] Data processing scripts
   - [ ] Uploaded to OSF

### OSF Repository Setup
- [ ] Create OSF project: "EI × Dunning-Kruger Replication"
- [ ] Set visibility (public after data collection?)
- [ ] Add collaborators (if any)
- [ ] Organize files in folders:
  - `/preregistration/` - Hypotheses & methods
  - `/materials/` - Consent, surveys, items
  - `/stimuli/` - Videos or video links
  - `/analysis/` - R/Python scripts
- [ ] Note OSF URL: _________________ (add here once created)

---

## 🤖 AI IRB REVIEW PREP

### Before Running IRB Review
1. **Complete OSF Upload** ✅ (pending above)
2. **Configure API Key**
   - [ ] Add OpenAI key to `.env`: `OPENAI_API_KEY=sk-...`
   - [ ] OR test in placeholder mode first

3. **Start Celery Worker** (for background processing)
   ```bash
   cd "/Users/ccastille/Documents/GitHub/SONA System"
   source venv/bin/activate
   celery -A config worker -l info
   ```

### Running the Review
1. Visit: http://localhost:8002/studies/researcher/
2. Login: `researcher@example.com` / `demo123`
3. Find "EI × Dunning–Kruger Study" card
4. Click **🤖 AI IRB Review** button
5. In the review form:
   - **Option A**: Upload files (consent.html, protocol docs, item banks)
   - **Option B**: Paste OSF repository URL (preferred)
6. Click "Submit for Review"
7. Wait for background processing (check Celery worker logs)
8. View results at review detail page

### Expected IRB Review Output
- Overall risk level assessment
- Ethics agent findings
- Privacy agent findings
- Vulnerable populations assessment
- Data security recommendations
- Consent adequacy review
- Categorized issues (critical/moderate/minor)
- Specific recommendations for each issue

---

## 🔧 TECHNICAL NOTES

### Current Server Status
- **Running on**: Port 8002
- **Database**: SQLite (`db.sqlite3`)
- **Celery Backend**: Django database (no Redis needed)
- **Static Files**: Served from `static/` and `staticfiles/`
- **Media Files**: `media/` (for IRB document uploads)

### Related Files Modified
- `apps/studies/models.py` - IRBReview, ReviewDocument models
- `apps/studies/views.py` - IRB review views
- `apps/studies/urls.py` - IRB review URLs
- `apps/studies/tasks.py` - Celery task for AI review
- `apps/studies/irb_ai/` - Multi-agent analyzer system
- `config/settings.py` - Celery config, API keys, IRB settings
- `templates/projects/ei-dk/protocol/index.html` - Consent & demographics
- `static/projects/ei-dk/sheldon_replication.js` - Study logic

---

## 📝 WORKFLOW SUMMARY

### Your Next Steps (In Order)
1. ✅ Finalize D-K study (DONE - verify with full test run)
2. 🔄 **YOU DO**: Create OSF project and upload pre-registration materials
3. 🔄 **THEN**: Come back and run AI IRB Review using OSF link
4. 🔄 Review AI findings and address any issues
5. 🔄 Re-run IRB review if changes made
6. 🔄 Submit to actual Nicholls IRB committee with AI review report

### Avoiding Duplicate Work Between Projects
- **SONA System** (this project): Backend, database, IRB system, study hosting
- **Psychological Assessment** project: Your other Cursor window - what's being edited there?
  - If it's the same study materials, decide which is the "source of truth"
  - If it's different components, clarify boundaries
  - Consider using Git to sync between projects if same repo

---

## ✅ READY TO PROCEED?

**Current Status**: D-K study appears COMPLETE and ready for:
1. Final full test run (you should do this NOW)
2. OSF pre-registration upload (you do this)
3. AI IRB review (we do this together after OSF)

**Recommended**: Run through the entire study once yourself right now to catch any issues before OSF upload!

**Test now**: http://localhost:8002/studies/ei-dk/run/






