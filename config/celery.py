"""
Celery configuration for async tasks.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('recruitment_system')

# Load config from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()

# Periodic tasks
app.conf.beat_schedule = {
    'send-24h-reminders': {
        'task': 'apps.studies.tasks.send_24h_reminders',
        'schedule': crontab(hour=9, minute=0),  # Daily at 9 AM
    },
    'send-2h-reminders': {
        'task': 'apps.studies.tasks.send_2h_reminders',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
    'mark-missed-sessions': {
        'task': 'apps.studies.tasks.mark_missed_sessions',
        'schedule': crontab(hour='*/1'),  # Hourly
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')




