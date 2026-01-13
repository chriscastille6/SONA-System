# SONA System - Project Status

**Last Updated**: October 22, 2025  
**Server Running On**: Port 8002  
**Login**: researcher@example.com / demo123

---

## ✅ COMPLETED FEATURES

### 1. EI × Dunning-Kruger Study Integration
- **Location**: `/studies/ei-dk/run/`
- **Status**: ✅ FULLY FUNCTIONAL
- **Components**:
  - ✅ 60-item mixed format (24 tendency + 36 ability) - `ei60_mixed_format.json`
  - ✅ 15 face perception items - `perception_items_page.json`
  - ✅ Dynamic video URLs in item bank (uses `item.videoUrl`)
  - ✅ Yes/No consent buttons (not just "Yes" checkbox)
  - ✅ BLS/EEO race and ethnicity categories in demographics
  - ✅ Data submission to `/api/ei-dk/submit/`
  - ✅ Bayesian feedback with percentiles and Bayes Factors

### 2. AI-Assisted IRB Review System
- **Status**: ✅ INSTALLED, READY TO TEST
- **Access Points**:
  - Researcher Dashboard: http://localhost:8002/studies/researcher/
  - Create Review: http://localhost:8002/studies/{study_id}/irb-review/create/
  - Review History: http://localhost:8002/studies/{study_id}/irb-review/history/
  - Committee Dashboard: http://localhost:8002/studies/committee/
  - Admin: http://localhost:8002/admin/studies/irbreview/

- **Features**:
  - ✅ Multi-agent AI analysis (ethics, privacy, vulnerability, data security, consent)
  - ✅ File upload interface for protocols, consent forms, surveys
  - ✅ OSF repository integration (planned)
  - ✅ Risk level assessment (minimal/low/moderate/high)
  - ✅ Categorized issues (critical/moderate/minor)
  - ✅ Researcher response tracking
  - ✅ Version control and audit trail
  - ✅ OpenAI support (default: gpt-4o)
  - ✅ Anthropic/Claude support (optional)
  - ✅ Celery background processing (using Django database backend)

---

## 🔧 PENDING CONFIGURATIONS

### AI API Keys (Choose One)
1. **OpenAI** (default, recommended):
   - Find or create key at: https://platform.openai.com/api-keys
   - Add to `.env`: `OPENAI_API_KEY=sk-...`
   
2. **Anthropic Claude** (alternative):
   - Get key at: https://console.anthropic.com/
   - Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-...`
   - Change in `.env`: `IRB_AI_PROVIDER=anthropic`

3. **No API Key** (testing mode):
   - System runs with placeholder results
   - Use for UI/workflow testing only

### Celery Worker (for background tasks)
Currently configured for Django database backend (no Redis needed).

To process IRB reviews in the background:
```bash
cd "/Users/ccastille/Documents/GitHub/SONA System"
source venv/bin/activate
celery -A config worker -l info
```

---

## 📂 FILE STRUCTURE (EI × DK Study)

```
/Users/ccastille/Documents/GitHub/SONA System/
├── templates/projects/ei-dk/
│   ├── protocol/
│   │   └── index.html              # Main study protocol (consent, demographics, instructions)
│   └── feedback/
│       └── index.html              # Bayesian feedback page
│
├── static/projects/ei-dk/
│   ├── sheldon_replication.js      # Main study logic
│   ├── data/
│   │   ├── ei60_mixed_format.json  # 60 EI items (24 tendency + 36 ability)
│   │   └── perception_items_page.json  # 15 face perception items
│   └── videos/
│       ├── video1.mp4
│       ├── video2.mp4
│       └── ... (more videos)
│
└── apps/studies/
    ├── models.py                   # Study, IRBReview, ReviewDocument models
    ├── views.py                    # Study views + IRB review views
    ├── urls.py                     # URL routing
    ├── tasks.py                    # Celery tasks (run_irb_ai_review)
    └── irb_ai/
        ├── analyzer.py             # Main IRB analyzer orchestrator
        ├── agents/
        │   ├── base.py             # BaseAgent with OpenAI/Anthropic support
        │   ├── ethics.py           # Ethics review agent
        │   ├── privacy.py          # Privacy review agent
        │   ├── vulnerability.py    # Vulnerable populations agent
        │   ├── data_security.py    # Data security agent
        │   └── consent.py          # Consent adequacy agent
        └── osf_client.py           # OSF integration (planned)
```

---

## 🚀 QUICK TEST COMMANDS

### Test EI × DK Study
```bash
# Server already running on port 8002
# Visit: http://localhost:8002/studies/ei-dk/run/
```

### Test AI IRB Review (Terminal)
```bash
cd "/Users/ccastille/Documents/GitHub/SONA System"
source venv/bin/activate
python manage.py test_irb_review
```

### Test AI IRB Review (Web)
1. Visit: http://localhost:8002/studies/researcher/
2. Login: researcher@example.com / demo123
3. Click "🤖 AI IRB Review" on any study card
4. Upload files or provide OSF link
5. Submit and view results

---

## 📋 ACTIVE STUDIES IN SONA

| Study Name | ID | Status | Run URL |
|------------|-----|--------|---------|
| EI Pilot | (UUID) | Active | http://localhost:8002/studies/ei-dk/run/ |
| EI × Dunning–Kruger Study | 95bc0b80-af71-4221-a7ac-72c6bbe20fb9 | Active | http://localhost:8002/studies/ei-dk/run/ |

Both use the same protocol currently.

---

## 🔄 AVOIDING DUPLICATE WORK ACROSS CURSOR PROJECTS

### Current Issue
You mentioned editing two Cursor projects simultaneously. This can cause:
- Duplicate file edits
- Conflicting changes
- Lost work if files are modified in both projects

### Solution: Project Boundaries

**Project 1: SONA System** (This Project)
- Location: `/Users/ccastille/Documents/GitHub/SONA System`
- Scope: Main SONA platform, IRB review system, researcher dashboard
- Server: Port 8002

**Project 2: Unknown** (Your other Cursor window)
- Location: ?
- Scope: ?

### Recommended Workflow
1. **Identify what's in Project 2**: Tell me the folder path
2. **Assign clear responsibilities**:
   - SONA System = Backend, database, Django views, IRB system
   - Other project = ? (Frontend only? Different app?)
3. **Use Git branches** if working on same repo:
   - Branch 1: `feature/irb-review`
   - Branch 2: `feature/ei-study-updates`
4. **Close one Cursor window** when editing shared files

---

## ❓ NEXT STEPS - PLEASE CLARIFY

1. **What is your second Cursor project?**
   - Folder path?
   - What are you working on there?
   - Is it the same SONA repo or different?

2. **What needs finishing for Dunning-Kruger study?**
   - The study appears fully functional
   - 60 items + 15 perception items ✅
   - Consent with Yes/No ✅
   - BLS demographics ✅
   - What else is missing?

3. **API Key for IRB Review?**
   - Do you have an OpenAI key to use?
   - Should we test in placeholder mode first?

---

## 🐛 RECENT FIXES

- ✅ Fixed Celery 'memory' backend error (now using Django database)
- ✅ Fixed LOGIN_URL redirect (was `/login/`, now `/accounts/login/`)
- ✅ Added django-celery-results package
- ✅ Server restarted on port 8002

---

**Server Status**: ✅ RUNNING on http://localhost:8002/






