from django.apps import AppConfig


class StudiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.studies'
    verbose_name = 'Research Studies'
    
    def ready(self):
        """Import signals when app is ready and configure admin."""
        import apps.studies.signals  # noqa
        
        # Clean up admin by hiding technical models
        from config.admin import setup_admin
        setup_admin()




