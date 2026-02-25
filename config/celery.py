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


from celery.signals import task_prerun


@task_prerun.connect
def set_rls_context_for_celery_task(sender=None, **kwargs):
    """Set PostgreSQL session variables for Celery tasks so RLS policies allow access."""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SET app.current_user_role = %s", ['admin'])
            cursor.execute("SET app.current_user_id = %s", [''])
    except Exception:
        pass




