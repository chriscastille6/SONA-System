from django.apps import AppConfig


class StudiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.studies'
    verbose_name = 'Studies & Timeslots'
    
    def ready(self):
        """Import signals when app is ready."""
        import apps.studies.signals  # noqa




