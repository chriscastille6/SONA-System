# Setup Instructions

## Initial Setup

Follow these steps to get your Research Participant Recruitment System up and running.

### 1. Create Virtual Environment

```bash
cd "/Users/ccastille/Documents/GitHub/SONA System"
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Copy the example environment file and edit it:

```bash
cp .env.example .env
```

Edit `.env` and configure:
- `SECRET_KEY`: Generate a new secret key (you can use `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- `DATABASE_URL`: Your PostgreSQL connection string
- Email settings (for production)

### 4. Set Up Database

Make sure PostgreSQL is running, then:

```bash
# Create database (if not using Docker)
createdb recruitment_db

# Run migrations
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 6. Create Static Files Directory

```bash
python manage.py collectstatic
```

### 7. Run Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` in your browser.

### 8. Start Celery (Optional but Recommended)

In separate terminal windows:

**Terminal 2 - Celery Worker:**
```bash
source venv/bin/activate
celery -A config worker -l info
```

**Terminal 3 - Celery Beat (for scheduled tasks):**
```bash
source venv/bin/activate
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

## Using Docker (Alternative)

If you prefer to use Docker:

```bash
# Start all services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# View logs
docker-compose logs -f web
```

## Initial Data Setup

### 1. Log in to Admin Panel

Visit `http://localhost:8000/admin/` and log in with your superuser account.

### 2. Create Initial Data

- **Courses**: Add courses that require research participation
- **Prescreen Questions**: Set up screening questions for participants
- **Users**: Invite researchers and instructors

### 3. Test the System

1. Register as a participant
2. Complete prescreen questionnaire
3. Browse available studies
4. Book a timeslot
5. Check email reminders (if configured)

## Troubleshooting

### Database Connection Issues

If you see database errors:
- Make sure PostgreSQL is running
- Check your `DATABASE_URL` in `.env`
- Verify the database exists: `psql -l`

### Static Files Not Loading

```bash
python manage.py collectstatic --noinput
```

### Celery Not Working

- Make sure Redis is running: `redis-cli ping` should return `PONG`
- Check `CELERY_BROKER_URL` in `.env`

### Email Not Sending

For development, emails are printed to console. For production:
- Configure SMTP settings in `.env`
- Test with: `python manage.py shell` then:
  ```python
  from django.core.mail import send_mail
  send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
  ```

## Next Steps

1. **Customize Settings**: Review `config/settings.py` for your institution
2. **Set Up Email**: Configure SMTP for email notifications
3. **Add Content**: Create studies, courses, and prescreen questions
4. **Invite Users**: Add researchers and instructors
5. **Test Workflows**: Run through participant and researcher workflows
6. **Deploy**: See README.md for deployment recommendations

## Security Checklist (Before Production)

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS` properly
- [ ] Enable HTTPS (`SECURE_SSL_REDIRECT = True`)
- [ ] Set up regular database backups
- [ ] Configure email for real SMTP server
- [ ] Review and tighten CORS settings
- [ ] Set up monitoring (e.g., Sentry)
- [ ] Enable database connection pooling
- [ ] Configure proper logging

## Support

For issues or questions:
1. Check the README.md
2. Review Django documentation: https://docs.djangoproject.com/
3. Check Celery documentation: https://docs.celeryq.dev/

---

**System Version**: 1.0.0 (MVP)  
**Last Updated**: October 2, 2025




