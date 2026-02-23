"""
Utilities for anonymized research exports.

Uses a system-specific salt so hashes from this application cannot be
reverse-engineered or linked to other anonymous research databases.
"""
import hmac
import hashlib
from django.conf import settings


def get_anonymized_participant_id(participant):
    """
    Return a stable, opaque participant ID for research exports.

    Uses HMAC-SHA256 with PARTICIPANT_EXPORT_SALT so the same participant
    always maps to the same ID within this system, but the ID cannot be
    linked to other databases without the salt.

    Args:
        participant: User model instance or UUID (participant id)

    Returns:
        str: 32-character hex string, or None if salt is not configured
    """
    salt = getattr(settings, 'PARTICIPANT_EXPORT_SALT', None)
    if not salt:
        return None
    participant_id = str(participant.id) if hasattr(participant, 'id') else str(participant)
    return hmac.new(
        salt.encode() if isinstance(salt, str) else salt,
        participant_id.encode(),
        hashlib.sha256,
    ).hexdigest()[:32]
