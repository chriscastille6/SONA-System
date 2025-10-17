"""
Prescreening questionnaire models.
"""
import uuid
from django.db import models
from django.conf import settings


class PrescreenQuestion(models.Model):
    """Question in the prescreening questionnaire."""
    
    TYPE_CHOICES = [
        ('boolean', 'Yes/No'),
        ('number', 'Number'),
        ('single_choice', 'Single Choice'),
        ('multi_choice', 'Multiple Choice'),
        ('text', 'Free Text'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    question_text = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    options = models.JSONField(
        default=list,
        blank=True,
        help_text="List of options for choice questions"
    )
    
    order = models.IntegerField(default=0, help_text="Display order")
    is_required = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    
    help_text = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'prescreen_questions'
        verbose_name = 'Prescreen Question'
        verbose_name_plural = 'Prescreen Questions'
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return self.question_text[:100]


class PrescreenResponse(models.Model):
    """Participant's prescreen responses."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    participant = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='prescreen_response',
        limit_choices_to={'role': 'participant'}
    )
    
    answers = models.JSONField(
        default=dict,
        help_text="Dictionary of {question_id: answer_value}"
    )
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'prescreen_responses'
        verbose_name = 'Prescreen Response'
        verbose_name_plural = 'Prescreen Responses'
    
    def __str__(self):
        return f"Prescreen: {self.participant.get_full_name()}"




