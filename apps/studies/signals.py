"""
Signal handlers for IRB audit logging.
"""
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Study
from apps.credits.models import AuditLog


@receiver(pre_save, sender=Study)
def track_irb_changes(sender, instance, **kwargs):
    """Track IRB-related changes before saving."""
    if instance.pk:  # Only for updates, not new studies
        try:
            old_instance = Study.objects.get(pk=instance.pk)
            
            # Check if IRB status changed
            if old_instance.irb_status != instance.irb_status:
                # Log will be created in post_save with full context
                instance._irb_status_changed = True
                instance._old_irb_status = old_instance.irb_status
            
            # Check if is_approved changed
            if old_instance.is_approved != instance.is_approved:
                instance._approval_changed = True
                instance._old_approval = old_instance.is_approved
                
        except Study.DoesNotExist:
            pass


@receiver(post_save, sender=Study)
def log_irb_changes(sender, instance, created, **kwargs):
    """Log IRB-related changes after saving."""
    
    if created:
        # New study created
        AuditLog.objects.create(
            actor=instance.researcher,
            action='study_created',
            entity='study',
            entity_id=instance.id,
            metadata={
                'title': instance.title,
                'irb_status': instance.irb_status,
                'irb_number': instance.irb_number,
            }
        )
    else:
        # Check for IRB status change
        if hasattr(instance, '_irb_status_changed'):
            AuditLog.objects.create(
                actor=instance.irb_last_reviewed_by,
                action='irb_status_changed',
                entity='study',
                entity_id=instance.id,
                metadata={
                    'title': instance.title,
                    'old_status': instance._old_irb_status,
                    'new_status': instance.irb_status,
                    'irb_number': instance.irb_number,
                    'notes': instance.irb_approval_notes,
                }
            )
        
        # Check for approval status change
        if hasattr(instance, '_approval_changed'):
            action = 'study_approved' if instance.is_approved else 'study_deactivated'
            AuditLog.objects.create(
                actor=instance.irb_approved_by if instance.is_approved else instance.irb_last_reviewed_by,
                action=action,
                entity='study',
                entity_id=instance.id,
                metadata={
                    'title': instance.title,
                    'irb_status': instance.irb_status,
                    'irb_number': instance.irb_number,
                }
            )

