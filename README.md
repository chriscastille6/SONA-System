# PRAMS — Research Participant Recruitment System

Participant Recruitment and Management System (PRAMS) for university research: study scheduling, IRB protocol workflows, and participant sign-up. Built for Nicholls State University HSIRB use on **bayoupal**.

**Production:** [https://bayoupal.nicholls.edu/hsirb/](https://bayoupal.nicholls.edu/hsirb/)

## Repositories

| Remote | URL | Use |
|--------|-----|-----|
| **GitLab (canonical)** | [gitlab.nicholls.edu/ccastille1/prams](https://gitlab.nicholls.edu/ccastille1/prams) | Institutional IT review and production deploys |
| **GitHub (mirror)** | [github.com/chriscastille6/SONA-System](https://github.com/chriscastille6/SONA-System) | Backup / public mirror of application code |

Push to GitLab `main`, then deploy to the server (see [Deployment](#deployment)).

## Features

### Participant recruitment
- **Browse studies** — lab and online studies with eligibility rules
- **Account-based booking** — participants register, book timeslots, track credits
- **Anonymous booking** — public sign-up with booking reference + PIN only (no login); QR-friendly landing pages, live signup counts, `.ics` calendar download
- **Prescreening** — configurable questionnaire for study matching
- **Email notifications** — booking confirmations and reminders (when SMTP is configured)

### Researcher & IRB
- **Study & timeslot management** — scheduling, roster, attendance
- **IRB protocol submission** — enter, submit, and track protocol workflows in PRAMS
- **AI-assisted IRB review** — multi-agent protocol analysis (optional; requires API keys)
- **Credit ledger** — course credit tracking and reporting (optional; some studies use cash compensation only)
- **Reporting** — participation analytics and CSV exports

## Tech stack

- **Backend:** Django 5.0, Django REST Framework
- **Database:** PostgreSQL (SQLite supported for local dev)
- **Tasks:** Celery + Redis (email reminders, background jobs)
- **Frontend:** Django templates, Bootstrap 5, HTMX
- **Production:** Gunicorn behind Apache on `bayoupal.nicholls.edu` (`/hsirb/` mount)

Docker Compose files are included for optional containerized local or cloud setups.

## Quick start (local)

### Prerequisites
- Python 3.12+
- PostgreSQL 16+ (or use SQLite for basic local dev)
- Redis 7+ (optional; needed for Celery)

### Setup

```bash
git clone https://gitlab.nicholls.edu/ccastille1/prams.git
cd prams
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp env.example .env
# Edit .env: SECRET_KEY, DATABASE_URL, SITE_URL, etc.

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

**Celery** (separate terminal, if using reminders/background tasks):

```bash
celery -A config worker -l info
celery -A config beat -l info
```

### Anonymous sign-up (example)

After creating a study with `allows_anonymous_booking=True` and open timeslots:

- Local: `/studies/signup/<study-slug>/`
- Production: `https://bayoupal.nicholls.edu/hsirb/studies/signup/<study-slug>/`

See `docs/ANONYMOUS_BOOKING_SECURITY.md` for security controls.

## Project structure

```
prams/
├── config/                 # Django settings, URLs, Celery
├── apps/
│   ├── accounts/           # Users, roles, CITI certificates
│   ├── studies/            # Studies, timeslots, signups, IRB protocols
│   ├── prescreening/
│   ├── credits/
│   ├── courses/
│   └── reporting/
├── templates/
├── static/
├── scripts/                # Flyer/build helpers, deploy utilities
├── docs/                   # IT security, deployment, IRB handoffs
├── deploy-to-server-rsync.sh
└── requirements.txt
```

## User roles

| Role | Capabilities |
|------|-------------|
| **Admin** | System settings, users, global configuration |
| **Researcher** | Create studies, manage timeslots/rosters, submit IRB protocols |
| **Instructor** | Course enrollments, credit reports |
| **Participant** | Prescreen, browse studies, book timeslots, track credits |
| **IRB member** | Review assigned protocols |

Anonymous participants have no account; they book via public URLs only.

## Deployment

### Nicholls production (bayoupal)

1. Push to GitLab: `git push gitlab main`  
   (HTTPS token help: `docs/GITLAB_PUSH_HTTPS.md`)
2. Deploy from your Mac:

```bash
./deploy-to-server-rsync.sh
```

This rsyncs code to `bayoupal.nicholls.edu:~/hsirb-system/`, runs migrations, `collectstatic`, and attempts a service restart.

3. If the site serves stale code after deploy, reload Gunicorn on the server:

```bash
kill -HUP $(pgrep -f 'hsirb-system/venv/bin/gunicorn' | head -1)
```

Full server setup: `HSIRB_DEPLOYMENT_GUIDE.md`.

### Other hosting

- **University VM** — Gunicorn + PostgreSQL + campus SMTP (see `CAMPUS_SERVER_DEPLOYMENT.md`)
- **Railway / Render** — `RAILWAY_DEPLOYMENT_GUIDE.md`, `RENDER_DEPLOYMENT_GUIDE.md`
- **Docker** — `docker-compose.yml` for local or small deployments

Set `SITE_URL`, `FORCE_SCRIPT_NAME=/hsirb`, and `ALLOWED_HOSTS` for production. See `env.example`.

## Documentation

| Topic | File |
|-------|------|
| HSIRB server deploy | `HSIRB_DEPLOYMENT_GUIDE.md` |
| GitLab push (HTTPS) | `docs/GITLAB_PUSH_HTTPS.md` |
| Anonymous booking security | `docs/ANONYMOUS_BOOKING_SECURITY.md` |
| IT compliance summary | `IT_EXECUTIVE_COMPLIANCE_SUMMARY.md` |
| Quick local reference | `QUICKSTART.md` |

## License

MIT License. See [LICENSE](LICENSE).

**Dependencies:** PyMuPDF is AGPL-3.0. If you distribute a modified version, comply with AGPL source-offer requirements.

## Acknowledgments

Developed with AI assistance for Nicholls State University research operations. This is an independent participant-recruitment platform and is not affiliated with any commercial study-management vendor.
