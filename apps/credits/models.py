"""
Credit transaction and ledger models.
"""
import uuid
from django.db import models
from django.conf import settings


class CreditTransaction(models.Model):
    """Record of credit grants or revocations."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='credit_transactions',
        limit_choices_to={'role': 'participant'}
    )
    
    study = models.ForeignKey(
        'studies.Study',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='credit_transactions'
    )
    
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='credit_transactions'
    )
    
    amount = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        help_text="Positive for grant, negative for revoke"
    )
    
    reason = models.TextField(blank=True, help_text="Explanation for this transaction")
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='credits_issued'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'credit_transactions'
        verbose_name = 'Credit Transaction'
        verbose_name_plural = 'Credit Transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['participant', '-created_at']),
            models.Index(fields=['study', '-created_at']),
            models.Index(fields=['course', '-created_at']),
        ]
    
    def __str__(self):
        action = "grant" if self.amount > 0 else "revoke"
        return f"{action.title()} {abs(self.amount)} credits to {self.participant.get_full_name()}"


class AuditLog(models.Model):
    """Audit trail for sensitive operations."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_actions'
    )
    
    action = models.CharField(max_length=100, db_index=True, help_text="Action performed")
    entity = models.CharField(max_length=50, help_text="Entity type (study, signup, credit, etc.)")
    entity_id = models.UUIDField(null=True, blank=True)
    
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional context")
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['actor', '-created_at']),
            models.Index(fields=['action', '-created_at']),
            models.Index(fields=['entity', 'entity_id']),
        ]
    
    def __str__(self):
        actor_name = self.actor.get_full_name() if self.actor else "System"
        return f"{actor_name}: {self.action} on {self.entity}"




