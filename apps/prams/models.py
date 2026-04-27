"""
PRAMS models — FERPA compliant.
No name, email, or user_id. Only Secure Participant ID and cancellation PIN.
"""
import uuid
import random
import string
from django.db import models


def generate_cancellation_pin():
    """Generate a random 4-digit numeric PIN for cancellation."""
    return ''.join(random.choices(string.digits, k=4))


class PRAMSStudy(models.Model):
    """
    Study in the PRAMS catalog.
    Single datetime and max_capacity (no timeslots in this FERPA flow).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    datetime = models.DateTimeField(help_text='When the study takes place')
    max_capacity = models.PositiveIntegerField(
        default=1,
        help_text='Maximum number of participants'
    )
    # Optional: Microsoft Bookings integration (see docs/PRAMS_MICROSOFT_BOOKINGS_INTEGRATION.md)
    bookings_service_id = models.CharField(
        max_length=255,
        blank=True,
        help_text='Microsoft Bookings Service ID for flow mapping (optional)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'prams_study'
        verbose_name = 'PRAMS Study'
        verbose_name_plural = 'PRAMS Studies'
        ordering = ['datetime']

    def __str__(self):
        return self.title

    @property
    def current_signups(self):
        return self.signups.count()

    @property
    def available_slots(self):
        return max(0, self.max_capacity - self.current_signups)


class PRAMSSignup(models.Model):
    """
    Signup for a PRAMS study. FERPA compliant: no PII.
    Identified only by participant_secure_id (from external system) and cancellation_pin.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    study = models.ForeignKey(
        PRAMSStudy,
        on_delete=models.CASCADE,
        related_name='signups'
    )
    participant_secure_id = models.CharField(
        max_length=255,
        db_index=True,
        help_text='Secure Participant ID from external system (no PII)'
    )
    cancellation_pin = models.CharField(
        max_length=4,
        help_text='4-digit PIN for cancellation'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'prams_signup'
        verbose_name = 'PRAMS Signup'
        verbose_name_plural = 'PRAMS Signups'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['study', 'participant_secure_id'],
                name='prams_signup_unique_study_participant',
            )
        ]

    def __str__(self):
        return f"Signup for {self.study_id} (secure_id=***)"

    def save(self, *args, **kwargs):
        if not self.cancellation_pin:
            self.cancellation_pin = generate_cancellation_pin()
        super().save(*args, **kwargs)
