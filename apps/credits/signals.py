"""
Signal handlers for credit audit logging.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CreditTransaction, AuditLog


@receiver(post_save, sender=CreditTransaction)
def log_credit_granted(sender, instance, created, **kwargs):
    """Log credit grant when a CreditTransaction is created (IRB / 45 CFR 46)."""
    if created:
        AuditLog.objects.create(
            actor=instance.created_by,
            action='credit_granted',
            entity='credit',
            entity_id=instance.id,
            metadata={
                'participant_id': str(instance.participant_id),
                'amount': str(instance.amount),
                'study_id': str(instance.study_id) if instance.study_id else None,
            },
        )
