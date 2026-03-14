# Research Participant Recruitment System

A lean, participant recruitment and study management platform (PRAMS) for university psychology research departments.

**Repositories**
- **GitHub (public/shell):** [chriscastille6/prams-system](https://github.com/chriscastille6/prams-system) — code only, no institutional data; clone from here to use or adapt the product.
- **GitLab (institutional/IT):** [chriscastille/prams](https://gitlab.nicholls.edu/chriscastille/prams) — deployment and IT review at Nicholls; production deploys from here.

## Features

### MVP (Phase 1)
- **User Management**: Admin, Researcher, Instructor, and Participant roles
- **Study Management**: Create lab and online studies with flexible scheduling
- **Participant Recruitment**: Browse eligible studies, book timeslots, manage bookings
- **Prescreening**: Configurable questionnaire to match participants with studies
- **Eligibility Rules**: Age, language, course enrollment, participation history filters
- **Credit System**: Track and award research credits automatically
- **Email Notifications**: Booking confirmations, reminders (24h/2h), credit alerts
- **No-Show Management**: Track attendance, enforce cancellation windows, limit no-shows
- **Reporting**: Course credit reports (CSV), study participation analytics

## Tech Stack

- **Backend**: Django 5.0 + Django REST Framework
- **Database**: PostgreSQL 16
- **Task Queue**: Celery + Redis (for email reminders)
- **Frontend**: Django Templates + HTMX + Alpine.js
- **Email**: SMTP (configurable)
- **Deployment**: Docker + Docker Compose

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 16+
- Redis 7+
- Docker & Docker Compose (optional)

### Local Development

1. **Clone and setup environment**
```bash
cd "/Users/ccastille/Documents/GitHub/PRAMS"
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your database credentials and settings
```

3. **Initialize database**
```bash
python manage.py migrate
python manage.py createsuperuser
```

4. **Run development server**
```bash
python manage.py runserver
```

5. **Run Celery worker** (separate terminal)
```bash
celery -A config worker -l info
celery -A config beat -l info
```

Access the application at `http://localhost:8000`

## Project Structure

```
recruitment_system/
├── config/              # Django project settings
├── apps/
│   ├── accounts/        # User management, auth, profiles
│   ├── studies/         # Studies, timeslots, signups
│   ├── prescreening/    # Prescreen questions and responses
│   ├── credits/         # Credit transactions and ledger
│   ├── courses/         # Courses, enrollments, instructor management
│   └── reporting/       # Analytics and CSV exports
├── templates/           # HTML templates
├── static/              # CSS, JS, images
└── requirements.txt     # Python dependencies
```

## User Roles

| Role | Capabilities |
|------|-------------|
| **Admin** | System settings, manage all users/studies/courses, global reports |
| **Researcher** | Create studies, manage timeslots, mark attendance, grant credits |
| **Instructor** | View course enrollments, download credit reports |
| **Participant** | Complete prescreen, browse studies, book timeslots, track credits |

## Deployment Recommendations

### Low-Budget Hosting (~$25-60/month)
- **App**: Fly.io, Render, or Railway ($7-20/mo)
- **Database**: Managed PostgreSQL ($15-30/mo)
- **Email**: Amazon SES (<$5/mo)
- **Monitoring**: Sentry free tier

### University Infrastructure (Preferred)
- Deploy on university VM (Ubuntu 22.04 LTS)
- Use campus PostgreSQL cluster
- Leverage university SMTP relay (free)
- SSO via SAML/OIDC (Phase 3)

## License

MIT License. See [LICENSE](LICENSE) for the full text.

**Dependencies:** PyMuPDF is licensed under AGPL-3.0. If you distribute a modified version of this software, you must comply with the AGPL (e.g., offer corresponding source code).

## Acknowledgments

This system was designed and implemented with AI assistance. Inspired by [Sona Systems](https://www.sona-systems.com), a leading research participant management platform used by over 1,500 institutions globally.

This project is not affiliated with, endorsed by, or connected to Sona Systems, Ltd. "Sona Systems" and "SONA" are trademarks of Sona Systems, Ltd. This software is an independent implementation of participant recruitment and study management.

### References
Sona Systems, Ltd. (2025). *Participant recruitment & study management made simple*. Retrieved October 2, 2025, from https://www.sona-systems.com




