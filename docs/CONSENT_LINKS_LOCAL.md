# Consent pages — local

**1. Start the server first** (from repo root, with venv activated):

```bash
cd "/Users/ccastille/Documents/GitHub/PRAMS"
source venv/bin/activate
python manage.py runserver 127.0.0.1:8000
```

If you use a different port (e.g. `8002`), replace `8000` in the URLs below.

---

**2. Consent links** (base: `http://127.0.0.1:8000`)

| Page | URL |
|------|-----|
| Participant information (platform) | http://127.0.0.1:8000/participant-information/ |
| Same (under studies) | http://127.0.0.1:8000/studies/participant-information/ |
| HR SJT student data consent | http://127.0.0.1:8000/studies/hr-sjt/student-data-consent/ |
| HR SJT student consent done | http://127.0.0.1:8000/studies/hr-sjt/student-data-consent/done/ |
| HR SJT professional consent | http://127.0.0.1:8000/studies/hr-sjt/professional-consent/ |
| Study consent (e.g. hr-sjt) | http://127.0.0.1:8000/studies/hr-sjt/protocol/consent/ |

**Home (sanity check):** http://127.0.0.1:8000/

---

**If you deploy with `/hsirb/` prefix** (e.g. `FORCE_SCRIPT_NAME=/hsirb/`), use:

- http://127.0.0.1:8000/hsirb/participant-information/
- http://127.0.0.1:8000/hsirb/studies/hr-sjt/student-data-consent/
- etc.
