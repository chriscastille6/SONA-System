"""Aggregate signup counts for studies (registered + anonymous, no PII)."""

from .models import AnonymousSignup, Signup


def get_study_signup_stats(study):
    """Return active signup totals for a study."""
    registered = Signup.objects.filter(timeslot__study=study).exclude(status='cancelled').count()
    anonymous = AnonymousSignup.objects.filter(timeslot__study=study, status='booked').count()
    return {
        'total': registered + anonymous,
        'registered': registered,
        'anonymous': anonymous,
    }
