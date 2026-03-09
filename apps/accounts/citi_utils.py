"""
CITI certificate validation utilities.
Used to block protocol submission when researcher CITI is expired
and to flag researchers for all parties.
"""
from django.utils import timezone

from .models import CITICertificate


def get_researcher_citi_status(user):
    """
    Get CITI certificate status for a researcher.

    Returns:
        dict with keys: status ('valid'|'expired'|'expiring_soon'|'none'),
                       certificate (CITICertificate or None),
                       message (str)
    """
    if not user:
        return {'status': 'none', 'certificate': None, 'message': 'No user'}

    cert = (
        CITICertificate.objects.filter(user=user)
        .order_by('-expiration_date')
        .first()
    )

    if not cert:
        return {
            'status': 'none',
            'certificate': None,
            'message': 'No CITI certificate on file. Upload a certificate to submit protocols.',
        }

    today = timezone.now().date()
    if cert.expiration_date < today:
        return {
            'status': 'expired',
            'certificate': cert,
            'message': f'CITI certificate expired {cert.expiration_date}. Renew to submit protocols.',
        }
    if cert.is_expiring_soon:
        return {
            'status': 'expiring_soon',
            'certificate': cert,
            'message': f'CITI certificate expires {cert.expiration_date}. Consider renewing soon.',
        }
    return {
        'status': 'valid',
        'certificate': cert,
        'message': f'CITI valid through {cert.expiration_date}',
    }


def researcher_can_submit_protocol(user):
    """
    Check if a researcher can submit a protocol (CITI must be valid and not expired).
    Admins and staff bypass this check.
    """
    if not user:
        return False, 'No user'
    if getattr(user, 'is_admin', False) or getattr(user, 'is_staff', False):
        return True, 'Admin/staff bypass'

    status = get_researcher_citi_status(user)
    if status['status'] in ('valid', 'expiring_soon'):
        return True, status['message']
    # Block if 'none' (no cert on file) or 'expired'
    return False, status['message']
