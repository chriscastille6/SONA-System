"""
Security helpers for anonymous timeslot booking (IT / FERPA review controls).
"""
import logging
import secrets
import uuid

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseForbidden

from apps.credits.models import AuditLog
from .tasks import notify_researcher_about_anonymous_signup

logger = logging.getLogger(__name__)

INVALID_CANCEL_MESSAGE = 'Booking not found or PIN invalid.'


def get_client_ip(request):
    """Return client IP (first X-Forwarded-For hop when behind a proxy)."""
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _rate_limit_key(scope, ip):
    return f'anonymous_booking:{scope}:{ip or "unknown"}'


def is_rate_limited(request, scope, limit, window_seconds):
    """Return True if the client IP exceeded the rate limit for scope."""
    ip = get_client_ip(request)
    key = _rate_limit_key(scope, ip)
    count = cache.get(key, 0)
    if count >= limit:
        logger.warning('Anonymous booking rate limit exceeded scope=%s ip=%s', scope, ip)
        return True
    cache.set(key, count + 1, window_seconds)
    return False


def rate_limit_response(request, scope, limit, window_seconds):
    """Return HttpResponseForbidden when limited; otherwise None."""
    if is_rate_limited(request, scope, limit, window_seconds):
        return HttpResponseForbidden('Too many requests. Please try again later.')
    return None


def booking_rate_limits():
    return (
        getattr(settings, 'ANONYMOUS_BOOKING_RATE_LIMIT_BOOK', 5),
        getattr(settings, 'ANONYMOUS_BOOKING_RATE_LIMIT_BOOK_WINDOW', 3600),
    )


def cancel_rate_limits():
    return (
        getattr(settings, 'ANONYMOUS_BOOKING_RATE_LIMIT_CANCEL', 15),
        getattr(settings, 'ANONYMOUS_BOOKING_RATE_LIMIT_CANCEL_WINDOW', 900),
    )


def parse_booking_reference(raw):
    """Validate booking reference is a UUID string."""
    if not raw:
        return None
    try:
        return uuid.UUID(str(raw).strip())
    except (ValueError, AttributeError, TypeError):
        return None


def pins_match(stored_pin, submitted_pin):
    """Constant-time PIN comparison."""
    if not stored_pin or not submitted_pin:
        return False
    return secrets.compare_digest(str(stored_pin).strip(), str(submitted_pin).strip())


def log_anonymous_signup_audit(signup, request):
    """Append-only audit entry with request context (no participant PII)."""
    AuditLog.objects.create(
        actor=None,
        action='anonymous_signup',
        entity='anonymous_signup',
        entity_id=signup.id,
        metadata={
            'study_id': str(signup.timeslot.study_id),
            'timeslot_id': str(signup.timeslot_id),
            'booked_at': signup.booked_at.isoformat() if signup.booked_at else None,
        },
        ip_address=get_client_ip(request),
        user_agent=(request.META.get('HTTP_USER_AGENT') or '')[:500],
    )


def log_anonymous_cancel_audit(signup, request, outcome):
    """Audit successful or failed cancellation attempts (no PIN in metadata)."""
    AuditLog.objects.create(
        actor=None,
        action='anonymous_cancel',
        entity='anonymous_signup',
        entity_id=signup.id if signup else None,
        metadata={
            'outcome': outcome,
            'study_id': str(signup.timeslot.study_id) if signup else None,
            'timeslot_id': str(signup.timeslot_id) if signup else None,
        },
        ip_address=get_client_ip(request),
        user_agent=(request.META.get('HTTP_USER_AGENT') or '')[:500],
    )


def finalize_anonymous_signup(signup, request):
    """Record audit trail and notify researcher after a successful booking."""
    log_anonymous_signup_audit(signup, request)
    notify_researcher_about_anonymous_signup(signup)
