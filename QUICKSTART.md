# Quick Start Guide

## ✅ System Successfully Created!

Your research participant recruitment system (SONA-like platform) has been fully generated and is ready to run.

## 📋 What's Been Created

### Core Components
- ✅ **Django Project**: Fully configured with settings, URLs, WSGI, and Celery
- ✅ **6 Django Apps**: accounts, studies, courses, credits, prescreening, reporting
- ✅ **Database Models**: User, Profile, Study, Timeslot, Signup, Course, Enrollment, Credits, Audit Logs
- ✅ **Views & URLs**: Complete routing for all features
- ✅ **Admin Interface**: Pre-configured Django admin for all models
- ✅ **Templates**: Base layout, home page, login/register, study browsing
- ✅ **Celery Tasks**: Automated email reminders (24h, 2h) and no-show tracking
- ✅ **Static Files**: Bootstrap 5 integration, custom CSS
- ✅ **Docker Setup**: docker-compose.yml for easy deployment

### Key Features Implemented
1. **User Management**: Role-based access (Admin, Researcher, Instructor, Participant)
2. **Study Management**: Create lab/online studies, manage timeslots
3. **Participant Recruitment**: Browse eligible studies, book/cancel timeslots
4. **Prescreening**: Questionnaire system for participant matching
5. **Credit System**: Automatic tracking and reporting
6. **Email Notifications**: Booking confirmations, reminders
7. **Reporting**: CSV exports for course credits, study analytics
8. **No-Show Management**: Automatic tracking and limits

## 🚀 Get Started in 5 Minutes

### Option 1: Local Development (Recommended for Testing)

```bash
# 1. Navigate to project
cd "/Users/ccastille/Documents/GitHub/SONA System"

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment file
cp .env.example .env

# 5. Set up database (SQLite for quick start)
python manage.py migrate

# 6. Create admin user
python manage.py createsuperuser

# 7. Run server
python manage.py runserver
```

**Access the system at:** `http://localhost:8000`
**Admin panel:** `http://localhost:8000/admin`

### Option 2: Docker (Recommended for Production)

```bash
# 1. Start all services
docker-compose up -d

# 2. Run migrations
docker-compose exec web python manage.py migrate

# 3. Create admin user
docker-compose exec web python manage.py createsuperuser

# 4. Access at http://localhost:8000
```

## 📊 Database Setup

### SQLite (Quick Testing - Default)
The system works out of the box with SQLite. No additional setup needed!

### PostgreSQL (Recommended for Production)

```bash
# Install PostgreSQL (macOS)
brew install postgresql
brew services start postgresql

# Create database
createdb recruitment_db

# Update .env file
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/recruitment_db
```

## 📧 Email Configuration

### Development (Console Backend - Default)
Emails print to console. No configuration needed!

### Production (SMTP)
Edit `.env`:
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@university.edu
EMAIL_HOST_PASSWORD=your-app-password
```

## 🔄 Running Celery (For Email Reminders)

### Terminal 2 - Celery Worker
```bash
source venv/bin/activate
celery -A config worker -l info
```

### Terminal 3 - Celery Beat (Scheduled Tasks)
```bash
source venv/bin/activate
celery -A config beat -l info
```

**Note**: Celery requires Redis. Install with:
- macOS: `brew install redis && brew services start redis`
- Ubuntu: `sudo apt install redis-server && sudo systemctl start redis`

## 🎯 First Steps After Setup

### 1. Log in to Admin Panel
Visit `http://localhost:8000/admin/` with your superuser credentials

### 2. Create Test Data

**Create a Course:**
1. Go to Courses → Add Course
2. Code: `PSYC-101`, Name: `Introduction to Psychology`
3. Term: `2025-Fall`, Credits Required: `3.0`

**Create Prescreen Questions:**
1. Go to Prescreen Questions → Add
2. Example: "What is your age?" (type: Number)
3. Example: "What languages do you speak?" (type: Multi Choice)

**Create a Study:**
1. Register as a researcher (or create in admin)
2. Go to `http://localhost:8000/studies/researcher/create/`
3. Fill in study details
4. Add timeslots

### 3. Test the Participant Flow

1. Register as a participant at `http://localhost:8000/register/`
2. Complete prescreen questionnaire
3. Browse studies at `http://localhost:8000/studies/`
4. Book a timeslot
5. View bookings at `http://localhost:8000/studies/my-bookings/`

## 📁 Project Structure

```
SONA System/
├── apps/                    # Django applications
│   ├── accounts/           # User authentication & profiles
│   ├── studies/            # Study & timeslot management
│   ├── courses/            # Course & enrollment tracking
│   ├── credits/            # Credit transactions & audit
│   ├── prescreening/       # Participant screening
│   └── reporting/          # Analytics & CSV exports
├── config/                 # Project configuration
├── templates/              # HTML templates
├── static/                 # CSS, JavaScript, images
├── manage.py              # Django management script
├── requirements.txt        # Python dependencies
├── docker-compose.yml      # Docker orchestration
└── README.md              # Full documentation
```

## 🔑 User Roles & Access

| Role | Capabilities |
|------|-------------|
| **Participant** | Browse studies, book timeslots, track credits |
| **Researcher** | Create studies, manage signups, mark attendance |
| **Instructor** | View course rosters, download credit reports |
| **Admin** | Full system access, manage all data |

## 📖 Common Commands

```bash
# Create database migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run development server
python manage.py runserver

# Open Django shell
python manage.py shell

# Run tests (when you add them)
python manage.py test
```

## 🐛 Troubleshooting

### Import Errors
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Database Errors
```bash
# Delete database and start fresh
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### Static Files Not Loading
```bash
python manage.py collectstatic --noinput
```

### Port Already in Use
```bash
# Use different port
python manage.py runserver 8001
```

## 🎨 Customization

### Change Site Name
Edit `.env`:
```
SITE_NAME=Your Research System
INSTITUTION_NAME=Your University
```

### Customize Policies
Edit `.env`:
```
CANCELLATION_WINDOW_HOURS=2
MAX_WEEKLY_SIGNUPS=3
NO_SHOW_LIMIT=2
```

### Modify Templates
Templates are in `templates/` directory. Edit HTML files to customize look and feel.

### Add Custom CSS
Edit `static/css/style.css` for styling changes.

## 🚀 Deployment

See `README.md` for detailed deployment instructions for:
- **Low-cost hosting**: Fly.io, Render, Railway ($25-60/month)
- **University infrastructure**: On-premise VM deployment
- **Docker**: Production-ready containerized deployment

## 📚 Next Steps

1. ✅ **Review** `setup_instructions.md` for detailed configuration
2. ✅ **Read** `README.md` for full feature documentation
3. ✅ **Customize** settings for your institution
4. ✅ **Test** all workflows (participant, researcher, instructor)
5. ✅ **Deploy** to production when ready

## 🆘 Support & Resources

- **Django Documentation**: https://docs.djangoproject.com/
- **Celery Documentation**: https://docs.celeryq.dev/
- **Bootstrap Documentation**: https://getbootstrap.com/docs/

## 📝 System Information

- **Framework**: Django 5.0
- **Database**: PostgreSQL 16 (SQLite for development)
- **Task Queue**: Celery + Redis
- **Frontend**: Bootstrap 5 + HTMX
- **Python Version**: 3.11+

---

## 🎉 You're All Set!

Your SONA-like research participant recruitment system is ready to use. Start by running the development server and exploring the admin interface.

**Questions?** Check the README.md for comprehensive documentation.

**Inspired by**: [Sona Systems](https://www.sona-systems.com) - The industry-leading research participant management platform.




