"""
Custom context processors for templates.
"""
from django.conf import settings


def site_settings(request):
    """Add site-wide settings to template context."""
    return {
        'SITE_NAME': settings.SITE_NAME,
        'INSTITUTION_NAME': settings.INSTITUTION_NAME,
        'SITE_URL': settings.SITE_URL,
    }




