"""
Custom admin configuration for PRAMS.
Hides technical third-party models and provides a cleaner admin interface.
"""
from django.contrib import admin
from django.contrib.auth.models import Group


def setup_admin():
    """
    Configure the admin site by hiding technical models.
    Call this after all apps are ready.
    """
    # Unregister the default Group model since we use role-based access
    try:
        admin.site.unregister(Group)
    except admin.sites.NotRegistered:
        pass
    
    # Unregister Celery Beat models (technical, not needed in day-to-day admin)
    try:
        from django_celery_beat.models import (
            PeriodicTask,
            IntervalSchedule,
            CrontabSchedule,
            SolarSchedule,
            ClockedSchedule,
        )
        admin.site.unregister(PeriodicTask)
        admin.site.unregister(IntervalSchedule)
        admin.site.unregister(CrontabSchedule)
        admin.site.unregister(SolarSchedule)
        admin.site.unregister(ClockedSchedule)
    except (ImportError, admin.sites.NotRegistered):
        pass
    
    # Unregister Celery Results models (technical)
    try:
        from django_celery_results.models import TaskResult, GroupResult
        admin.site.unregister(TaskResult)
        admin.site.unregister(GroupResult)
    except (ImportError, admin.sites.NotRegistered):
        pass
