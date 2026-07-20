# Longitudinal CANDIDATE + SONA anonymous workflow

Client-side, decoupled three-part architecture for an IRB-approved longitudinal study:

1. **SONA anonymous pass-through** — `survey_code` in the Wave 1 URL  
2. **CANDIDATE linking + credit redirect** — 16-char hash ID in the research file; SONA credit via `redirect_credit.aspx`  
3. **Unlinked Form B + Power Automate nudges** — email-only contact store in Microsoft 365  

No external research database and **no master re-identification table**.

Citation: Sandnes, F. E. (2021). CANDIDATE… *PLOS ONE*, 16(12), e0260569.

---

## Package layout

```
templates/projects/longitudinal-candidate/
├── README.md                          ← this file
├── wave1/
│   ├── index.html                     ← Wave 1 instrument
│   ├── css/survey.css
│   └── js/
│       ├── candidate.js               ← CANDIDATE hashing
│       ├── sona_passthrough.js        ← survey_code capture + redirect
│       └── survey.js                  ← session + export (no survey_code in data)
├── wave2/
│   ├── index.html                     ← Wave 2 (same linking questions)
│   ├── css/survey.css
│   └── js/candidate.js, survey_wave2.js
└── form_b/
    ├── index.html                     ← Unlinked contact template / MS Forms mirror
    └── POWER_AUTOMATE_SETUP.md        ← Exact M365 flow setup

apps/compliance/candidate/protocol.py  ← Python twin for offline Wave 1↔2 join
apps/compliance/tests/test_candidate_protocol.py
docs/LONGITUDINAL_CANDIDATE_SONA_WORKFLOW.md
```

---

## 1. SONA configuration

In your SONA study (external survey / web study):

**Study URL**

```
https://YOUR-HOST/path/to/wave1/index.html?survey_code=%SURVEY_CODE%
```

SONA replaces `%SURVEY_CODE%` with the participant’s anonymous credit code.

**Credit completion URL** (built automatically by `sona_passthrough.js`):

```
https://YOUR-SCHOOL.sona-systems.com/redirect_credit.aspx?experiment_id=XXX&credit_token=YYY&survey_code=XXXX
```

Edit placeholders in `wave1/js/survey.js` → `STUDY.sona`:

| Key | Value |
|-----|--------|
| `baseCreditUrl` | `https://YOUR-SCHOOL.sona-systems.com/redirect_credit.aspx` |
| `experimentId` | From SONA study info |
| `creditToken` | From SONA study info |

### JavaScript capture (summary)

On load, `SonaPassthrough.captureSurveyCode()` reads `survey_code` from the query string and holds it in memory / `sessionStorage` for the tab session. It is **omitted** from `buildResearchRecord()`. At completion, `redirectToSonaCredit()` clears the session copy and `location.replace`s to the credit URL.

---

## 2. CANDIDATE protocol (client-side)

Three static security questions (Wave 1 and Wave 2 must match):

1. Mother’s maiden name — first two initials  
2. Birth day of month (1–31)  
3. Childhood street — first two initials  

Pipeline: normalize → compose `a|dd|c` → mix Sandnes-style djb2 + CRC-32(reverse) → SHA-256 → **first 16 hex chars**.

Raw answers are cleared from the form after hashing. Only `candidate_id` enters the research JSON.

Python parity:

```python
from apps.compliance.candidate import generate_candidate_id, merge_waves_by_candidate_id

cid = generate_candidate_id("MJ", 14, "OA")  # synthetic example
```

---

## 3. Form B + Power Automate

See [`form_b/POWER_AUTOMATE_SETUP.md`](form_b/POWER_AUTOMATE_SETUP.md) for:

- Isolated Excel columns (email only)  
- Flow A: store + schedule  
- Flow B: Wave 2 launch email  
- Flow C: single 72-hour nudge  
- Opt-out (`STOP`)  
- Required disclaimer: *If you have already completed Wave 2, thank you—you may safely disregard this message.*

---

## Privacy firewall (non-negotiable)

| Store | Allowed | Forbidden |
|-------|---------|-----------|
| Research (Wave 1/2) | `candidate_id`, item responses, timestamps | email, `survey_code`, raw security answers, student ID |
| Form B Excel | email, schedule flags, opt-out | `candidate_id`, responses, SONA codes |
| SONA redirect | `survey_code` + experiment credentials | survey answers |

---

## Local preview

Serve the folder over HTTP (file:// may block downloads in some browsers):

```bash
cd templates/projects/longitudinal-candidate
python -m http.server 8765
```

Open:

- Wave 1 preview: `http://127.0.0.1:8765/wave1/index.html`  
- Wave 1 with synthetic SONA code: `http://127.0.0.1:8765/wave1/index.html?survey_code=SYNTHETICCODE99`  
- Form B: `http://127.0.0.1:8765/form_b/index.html`  
- Wave 2: `http://127.0.0.1:8765/wave2/index.html`  

Replace `STUDY.sona` credentials before any real SONA redirect test.

---

## Tests

```bash
pytest apps/compliance/tests/test_candidate_protocol.py -q
```

All fixtures use synthetic answers only.
