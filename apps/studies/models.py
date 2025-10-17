"""
Study, timeslot, and signup models.
"""
import uuid
from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.validators import MinValueValidator


class Study(models.Model):
    """Research study that participants can sign up for."""
    
    MODE_CHOICES = [
        ('lab', 'In-Person Lab Study'),
        ('online', 'Online Study'),
    ]
    
    IRB_STATUS_CHOICES = [
        ('not_required', 'Not Required'),
        ('approved', 'Approved'),
        ('exempt', 'Exempt'),
        ('pending', 'Pending'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic info
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True, blank=True, help_text="URL-friendly identifier")
    description = models.TextField(help_text="Detailed study description shown to participants")
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, db_index=True)
    
    # Researcher
    researcher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='studies',
        limit_choices_to={'role': 'researcher'}
    )
    
    # Credits and compensation
    credit_value = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1.0,
        validators=[MinValueValidator(0)],
        help_text="Research credits awarded upon completion"
    )
    
    # Status
    is_active = models.BooleanField(default=True, help_text="Study is visible to participants")
    is_approved = models.BooleanField(default=True, help_text="Admin approval status")
    
    # Eligibility criteria (JSON)
    eligibility = models.JSONField(
        default=dict,
        blank=True,
        help_text="Eligibility rules: age_min, age_max, languages, courses, excluded_studies"
    )
    
    # Consent
    consent_text = models.TextField(help_text="Consent form text participants must agree to")
    
    # External link (for online studies)
    external_link = models.URLField(blank=True, help_text="Survey/experiment URL for online studies")
    
    # IRB fields
    irb_status = models.CharField(
        max_length=20,
        choices=IRB_STATUS_CHOICES,
        default='not_required',
        help_text="IRB approval status"
    )
    irb_number = models.CharField(max_length=100, blank=True, help_text="IRB protocol number")
    irb_expiration = models.DateField(null=True, blank=True, help_text="IRB approval expiration date")
    
    # IRB Audit Trail
    irb_approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='irb_approvals',
        help_text="Administrator who approved this study"
    )
    irb_approved_at = models.DateTimeField(null=True, blank=True, help_text="When IRB approval was granted")
    irb_approval_notes = models.TextField(blank=True, help_text="IRB reviewer notes and comments")
    irb_last_reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='irb_reviews',
        help_text="Last person to review IRB status"
    )
    irb_last_reviewed_at = models.DateTimeField(null=True, blank=True, help_text="Last IRB review date")
    
    # OSF fields
    osf_enabled = models.BooleanField(default=False, help_text="Project is on Open Science Framework")
    osf_project_id = models.CharField(max_length=100, blank=True, help_text="OSF project identifier")
    osf_link = models.URLField(blank=True, help_text="Full OSF project URL")
    
    # Analysis and monitoring fields
    min_sample_size = models.IntegerField(
        default=20,
        validators=[MinValueValidator(1)],
        help_text="Minimum N before Bayesian monitoring begins"
    )
    bf_threshold = models.FloatField(
        default=10.0,
        validators=[MinValueValidator(0.1)],
        help_text="Bayes Factor threshold for hypothesis support (e.g., BF > 10)"
    )
    analysis_plugin = models.CharField(
        max_length=500,
        default='apps.studies.analysis.placeholder:compute_bf',
        help_text="Python import path to BF computation function"
    )
    current_bf = models.FloatField(null=True, blank=True, help_text="Current Bayes Factor value")
    monitoring_enabled = models.BooleanField(default=False, help_text="Enable sequential Bayesian monitoring")
    monitoring_notified = models.BooleanField(default=False, help_text="Notification sent when BF >= threshold")
    
    # Metadata
    duration_minutes = models.IntegerField(default=30, help_text="Estimated duration")
    max_participants = models.IntegerField(
        null=True,
        blank=True,
        help_text="Maximum total participants (leave blank for unlimited)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'studies'
        verbose_name = 'Study'
        verbose_name_plural = 'Studies'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['mode', 'is_active']),
            models.Index(fields=['researcher', 'is_active']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Auto-generate slug if not provided."""
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.title)[:250]  # Leave room for uniqueness suffix
            slug = base_slug
            counter = 1
            while Study.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    @property
    def total_signups(self):
        """Count total signups across all timeslots."""
        return self.timeslots.aggregate(
            total=models.Count('signups')
        )['total'] or 0
    
    @property
    def available_slots(self):
        """Count available slots across all timeslots."""
        now = timezone.now()
        return sum(
            ts.available_capacity
            for ts in self.timeslots.filter(starts_at__gte=now)
        )
    
    @property
    def response_count(self):
        """Count total protocol responses."""
        return self.responses.count()


class Timeslot(models.Model):
    """Specific time slot for a study."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name='timeslots')
    
    starts_at = models.DateTimeField(db_index=True)
    ends_at = models.DateTimeField()
    
    capacity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Number of participants per timeslot"
    )
    
    location = models.CharField(
        max_length=300,
        blank=True,
        help_text="Lab room number, building, or Zoom link"
    )
    
    notes = models.TextField(blank=True, help_text="Internal notes for researcher")
    
    is_cancelled = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'timeslots'
        verbose_name = 'Timeslot'
        verbose_name_plural = 'Timeslots'
        ordering = ['starts_at']
        indexes = [
            models.Index(fields=['study', 'starts_at']),
            models.Index(fields=['starts_at', 'is_cancelled']),
        ]
    
    def __str__(self):
        return f"{self.study.title} - {self.starts_at.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def current_signups(self):
        """Count active signups (not cancelled)."""
        return self.signups.exclude(status='cancelled').count()
    
    @property
    def available_capacity(self):
        """Remaining capacity."""
        return max(0, self.capacity - self.current_signups)
    
    @property
    def is_full(self):
        """Check if timeslot is at capacity."""
        return self.available_capacity == 0
    
    @property
    def is_past(self):
        """Check if timeslot has already occurred."""
        return timezone.now() > self.ends_at
    
    @property
    def can_cancel(self):
        """Check if still within cancellation window."""
        hours = settings.CANCELLATION_WINDOW_HOURS
        cutoff = self.starts_at - timedelta(hours=hours)
        return timezone.now() < cutoff


class Signup(models.Model):
    """Participant signup for a timeslot."""
    
    STATUS_CHOICES = [
        ('booked', 'Booked'),
        ('attended', 'Attended'),
        ('no_show', 'No Show'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    timeslot = models.ForeignKey(Timeslot, on_delete=models.CASCADE, related_name='signups')
    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='signups',
        limit_choices_to={'role': 'participant'}
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='booked', db_index=True)
    
    # Consent tracking
    consented_at = models.DateTimeField(auto_now_add=True)
    consent_text_version = models.TextField(help_text="Copy of consent text at time of signup")
    
    # Timestamps
    booked_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    attended_at = models.DateTimeField(null=True, blank=True)
    
    # Reminders sent
    reminder_24h_sent = models.BooleanField(default=False)
    reminder_2h_sent = models.BooleanField(default=False)
    
    # Notes
    participant_notes = models.TextField(blank=True, help_text="Notes from participant")
    researcher_notes = models.TextField(blank=True, help_text="Private notes from researcher")
    
    class Meta:
        db_table = 'signups'
        verbose_name = 'Signup'
        verbose_name_plural = 'Signups'
        ordering = ['-booked_at']
        unique_together = [['timeslot', 'participant']]
        indexes = [
            models.Index(fields=['participant', 'status']),
            models.Index(fields=['timeslot', 'status']),
            models.Index(fields=['status', 'booked_at']),
        ]
    
    def __str__(self):
        return f"{self.participant.get_full_name()} - {self.timeslot.study.title}"
    
    def cancel(self):
        """Mark signup as cancelled."""
        if self.status == 'booked':
            self.status = 'cancelled'
            self.cancelled_at = timezone.now()
            self.save()
    
    def mark_attended(self):
        """Mark participant as attended."""
        if self.status in ['booked', 'no_show']:
            self.status = 'attended'
            self.attended_at = timezone.now()
            self.save()
    
    def mark_no_show(self):
        """Mark participant as no-show."""
        if self.status == 'booked':
            self.status = 'no_show'
            self.save()
            
            # Increment no-show count
            profile = self.participant.profile
            profile.no_show_count += 1
            profile.save()


class Response(models.Model):
    """Protocol response submitted by a participant."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name='responses')
    session_id = models.UUIDField(default=uuid.uuid4, db_index=True, help_text="Anonymous session identifier")
    
    # Response data
    payload = models.JSONField(help_text="JSON data submitted from protocol")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="Participant IP (optional)")
    user_agent = models.TextField(blank=True, help_text="Browser user agent string")
    
    class Meta:
        db_table = 'responses'
        verbose_name = 'Protocol Response'
        verbose_name_plural = 'Protocol Responses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['study', 'created_at']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"Response for {self.study.title} at {self.created_at}"

