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
    is_classroom_based = models.BooleanField(
        default=False,
        help_text="Classroom-based study (not available for general signup, IRB monitoring only)"
    )
    
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
    involves_deception = models.BooleanField(
        default=False,
        help_text="Protocol involves deception (requires chair review)"
    )
    
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
    irb_reviewers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='IRBReviewerAssignment',
        related_name='assigned_irb_studies',
        blank=True,
        help_text="IRB members assigned to audit this study"
    )
    
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
        verbose_name = 'Research Study'
        verbose_name_plural = 'Research Studies'
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
        """Count available slots across all timeslots. Returns 'N/A' for online studies."""
        if self.mode == 'online':
            return 'N/A'
        now = timezone.now()
        return sum(
            ts.available_capacity
            for ts in self.timeslots.filter(starts_at__gte=now)
        )
    
    @property
    def response_count(self):
        """Count total protocol responses."""
        return self.responses.count()
    
    @property
    def latest_irb_review(self):
        """Get the most recent IRB review for this study."""
        return self.irb_reviews.order_by('-version').first()
    
    @property
    def irb_review_status(self):
        """Get IRB review status summary."""
        latest = self.latest_irb_review
        if not latest:
            return 'not_reviewed'
        if latest.status != 'completed':
            return latest.status
        if latest.critical_issues:
            return 'critical_issues'
        if latest.moderate_issues:
            return 'moderate_issues'
        if latest.minor_issues:
            return 'minor_issues'
        return 'clear'
    
    def is_assigned_reviewer(self, user):
        """Check whether the user is an assigned IRB reviewer for this study."""
        if not getattr(user, 'is_irb_member', False):
            return False
        return self.reviewer_assignments.filter(reviewer=user).exists()


class IRBReviewerAssignment(models.Model):
    """Link IRB members to studies they oversee."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    study = models.ForeignKey(
        Study,
        on_delete=models.CASCADE,
        related_name='reviewer_assignments'
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='irb_assignments',
        limit_choices_to={'role': 'irb_member'}
    )
    receive_email_updates = models.BooleanField(
        default=True,
        help_text="Send email notifications when there are new reviews or updates."
    )
    last_notified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time an automated notification was sent."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'irb_reviewer_assignments'
        verbose_name = 'IRB Reviewer Assignment'
        verbose_name_plural = 'IRB Reviewer Assignments'
        unique_together = [['study', 'reviewer']]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['study', 'reviewer']),
            models.Index(fields=['reviewer', '-created_at']),
        ]

    def __str__(self):
        return f"{self.reviewer.get_full_name()} → {self.study.title}"


class StudyUpdate(models.Model):
    """Researcher-authored updates shared with IRB reviewers."""

    VISIBILITY_CHOICES = [
        ('irb', 'IRB Reviewers'),
        ('team', 'Research Team Only'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    study = models.ForeignKey(
        Study,
        on_delete=models.CASCADE,
        related_name='updates'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='study_updates'
    )
    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default='irb',
        db_index=True,
        help_text="Choose who should see this update."
    )
    message = models.TextField(blank=True)
    attachment = models.FileField(
        upload_to='study_updates/%Y/%m/',
        blank=True
    )
    attachment_name = models.CharField(max_length=255, blank=True)
    attachment_size = models.IntegerField(default=0)
    notified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time IRB reviewers were emailed about this update."
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'study_updates'
        verbose_name = 'Study Update'
        verbose_name_plural = 'Study Updates'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['study', 'visibility', '-created_at']),
        ]

    def __str__(self):
        author = self.author.get_full_name() if self.author else "Unknown"
        return f"Update by {author} on {self.study.title}"

    def save(self, *args, **kwargs):
        """Populate attachment metadata automatically."""
        if self.attachment and not self.attachment_name:
            self.attachment_name = self.attachment.name
            try:
                self.attachment_size = self.attachment.size
            except Exception:
                pass
        super().save(*args, **kwargs)


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
        verbose_name = 'Study Timeslot'
        verbose_name_plural = 'Study Timeslots'
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
        verbose_name = 'Participant Signup'
        verbose_name_plural = 'Participant Signups'
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
        verbose_name = 'Study Response'
        verbose_name_plural = 'Study Responses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['study', 'created_at']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"Response for {self.study.title} at {self.created_at}"


class IRBReview(models.Model):
    """AI-assisted IRB review of study materials."""
    
    REVIEW_STATUS = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    RISK_LEVELS = [
        ('minimal', 'Minimal Risk'),
        ('low', 'Low Risk'),
        ('moderate', 'Moderate Risk'),
        ('high', 'High Risk'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name='irb_reviews')
    version = models.IntegerField(default=1, help_text="Protocol version number")
    
    # Initiation tracking
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='initiated_irb_reviews'
    )
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=REVIEW_STATUS, default='pending', db_index=True)
    
    # Material sources
    osf_repo_url = models.URLField(
        blank=True,
        help_text="OSF repository URL if materials are hosted there"
    )
    uploaded_files = models.JSONField(
        default=list,
        help_text="List of uploaded file metadata"
    )
    
    # AI Analysis results from each agent
    ethics_analysis = models.JSONField(
        null=True,
        blank=True,
        help_text="Ethics agent findings"
    )
    privacy_analysis = models.JSONField(
        null=True,
        blank=True,
        help_text="Privacy agent findings"
    )
    vulnerability_analysis = models.JSONField(
        null=True,
        blank=True,
        help_text="Vulnerable populations analysis"
    )
    data_security_analysis = models.JSONField(
        null=True,
        blank=True,
        help_text="Data handling and security findings"
    )
    consent_analysis = models.JSONField(
        null=True,
        blank=True,
        help_text="Consent adequacy analysis"
    )
    
    # Aggregated results
    overall_risk_level = models.CharField(
        max_length=20,
        choices=RISK_LEVELS,
        blank=True,
        help_text="Overall risk assessment"
    )
    critical_issues = models.JSONField(
        default=list,
        help_text="Critical ethical issues requiring immediate attention"
    )
    moderate_issues = models.JSONField(
        default=list,
        help_text="Moderate issues requiring attention"
    )
    minor_issues = models.JSONField(
        default=list,
        help_text="Minor suggestions for improvement"
    )
    recommendations = models.JSONField(
        default=list,
        help_text="Actionable recommendations from AI analysis"
    )
    
    # Researcher response
    researcher_notes = models.TextField(
        blank=True,
        help_text="Researcher's response to the review"
    )
    issues_addressed = models.JSONField(
        default=list,
        help_text="List of issue IDs that have been addressed"
    )
    
    # Audit trail
    ai_model_versions = models.JSONField(
        default=dict,
        help_text="Track which AI models and versions were used"
    )
    processing_time_seconds = models.IntegerField(
        null=True,
        blank=True,
        help_text="Time taken to complete the review"
    )
    
    class Meta:
        db_table = 'irb_reviews'
        verbose_name = 'AI IRB Review'
        verbose_name_plural = 'AI IRB Reviews'
        ordering = ['-initiated_at']
        indexes = [
            models.Index(fields=['study', '-version']),
            models.Index(fields=['status', 'initiated_at']),
            models.Index(fields=['overall_risk_level']),
        ]
        unique_together = [['study', 'version']]
    
    def __str__(self):
        return f"IRB Review v{self.version} for {self.study.title}"
    
    def save(self, *args, **kwargs):
        """Auto-increment version number for new reviews."""
        if not self.version or self.version == 1:
            # Get the max version for this study
            max_version = IRBReview.objects.filter(
                study=self.study
            ).aggregate(
                max_ver=models.Max('version')
            )['max_ver']
            self.version = (max_version or 0) + 1
        super().save(*args, **kwargs)


class ReviewDocument(models.Model):
    """Document uploaded for IRB review."""
    
    FILE_TYPES = [
        ('protocol', 'Study Protocol'),
        ('consent', 'Consent Form'),
        ('survey', 'Survey/Questionnaire'),
        ('recruitment', 'Recruitment Materials'),
        ('debrief', 'Debriefing Materials'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    review = models.ForeignKey(
        IRBReview,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    file = models.FileField(
        upload_to='irb_reviews/%Y/%m/',
        help_text="Uploaded document file"
    )
    filename = models.CharField(max_length=255)
    file_type = models.CharField(
        max_length=50,
        choices=FILE_TYPES,
        default='other',
        help_text="Type of document"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_hash = models.CharField(
        max_length=64,
        help_text="SHA256 hash for integrity verification"
    )
    file_size_bytes = models.IntegerField(
        default=0,
        help_text="File size in bytes"
    )
    
    class Meta:
        db_table = 'review_documents'
        verbose_name = 'IRB Review Document'
        verbose_name_plural = 'IRB Review Documents'
        ordering = ['file_type', 'uploaded_at']
    
    def __str__(self):
        return f"{self.filename} ({self.get_file_type_display()})"
    
    def save(self, *args, **kwargs):
        """Calculate file hash and size on save."""
        if self.file and not self.file_hash:
            import hashlib
            self.file.seek(0)
            file_content = self.file.read()
            self.file_hash = hashlib.sha256(file_content).hexdigest()
            self.file_size_bytes = len(file_content)
            self.file.seek(0)  # Reset file pointer
        super().save(*args, **kwargs)


class CollegeRepresentative(models.Model):
    """Maps colleges/departments to IRB representatives."""
    
    COLLEGE_CHOICES = [
        ('business', 'College of Business Administration'),
        ('education', 'College of Education and Behavioral Sciences'),
        ('liberal_arts', 'College of Liberal Arts'),
        ('sciences', 'College of Sciences & Technology'),
        ('nursing', 'Department of Nursing'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    college = models.CharField(max_length=50, choices=COLLEGE_CHOICES, unique=True)
    representative = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'irb_member'},
        related_name='college_representative_assignments',
        help_text="IRB member serving as college representative"
    )
    is_chair = models.BooleanField(
        default=False,
        help_text="This representative is the IRB Chair"
    )
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'college_representatives'
        verbose_name = 'College Representative'
        verbose_name_plural = 'College Representatives'
        ordering = ['college']
    
    def __str__(self):
        return f"{self.get_college_display()} - {self.representative.get_full_name() if self.representative else 'Unassigned'}"


class ProtocolSubmission(models.Model):
    """Formal IRB protocol submission with review workflow."""
    
    REVIEW_TYPE_CHOICES = [
        ('exempt', 'Exempt'),
        ('expedited', 'Expedited Review'),
        ('full', 'Full Board Review'),
    ]
    
    DECISION_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('revise_resubmit', 'Revise & Resubmit'),
        ('rejected', 'Rejected'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    study = models.ForeignKey(
        Study,
        on_delete=models.CASCADE,
        related_name='protocol_submissions'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        db_index=True,
        help_text="Whether this is a draft or has been submitted"
    )
    submission_number = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        help_text="Auto-generated submission number (only for submitted protocols)"
    )
    version = models.IntegerField(default=1, help_text="Submission version number")
    
    # PI's suggested review type
    pi_suggested_review_type = models.CharField(
        max_length=20,
        choices=REVIEW_TYPE_CHOICES,
        help_text="Review type suggested by Primary Investigator"
    )
    
    # College rep assignment
    college_rep = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_submissions',
        limit_choices_to={'role': 'irb_member'},
        help_text="College representative assigned to this submission"
    )
    college_rep_determination = models.CharField(
        max_length=20,
        choices=REVIEW_TYPE_CHOICES,
        blank=True,
        help_text="College rep's determination of review type"
    )
    
    # Deception flag (from study, but can be overridden)
    involves_deception = models.BooleanField(
        default=False,
        help_text="Protocol involves deception (requires chair review)"
    )
    
    # Current state
    review_type = models.CharField(
        max_length=20,
        choices=REVIEW_TYPE_CHOICES,
        help_text="Actual review type (may differ from PI suggestion)"
    )
    decision = models.CharField(
        max_length=20,
        choices=DECISION_CHOICES,
        default='pending',
        db_index=True,
        help_text="Current decision status"
    )
    
    # Protocol number (issued on approval)
    protocol_number = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        help_text="IRB protocol number (issued upon approval)"
    )
    
    # Decision details
    rejection_grounds = models.TextField(
        blank=True,
        help_text="Grounds for rejection (if rejected)"
    )
    rnr_notes = models.TextField(
        blank=True,
        help_text="Revise & resubmit notes and required changes"
    )
    approval_notes = models.TextField(
        blank=True,
        help_text="Approval notes and conditions"
    )
    
    # ========== DETAILED PROTOCOL INFORMATION ==========
    
    # 1. Protocol Description
    protocol_description = models.TextField(
        blank=True,
        help_text="Detailed description of the research project or proposal"
    )
    population_description = models.TextField(
        blank=True,
        help_text="Description of the population of human subjects"
    )
    research_procedures = models.TextField(
        blank=True,
        help_text="Detailed research procedures and data collection methods"
    )
    research_objectives = models.TextField(
        blank=True,
        help_text="Primary research objectives and goals"
    )
    research_questions = models.TextField(
        blank=True,
        help_text="Research questions or hypotheses (if applicable)"
    )
    educational_justification = models.TextField(
        blank=True,
        help_text="Educational justification (if this is an educational exercise)"
    )
    
    # 2. Recruitment
    recruitment_method = models.TextField(
        blank=True,
        help_text="How will you recruit subjects?"
    )
    recruitment_script = models.TextField(
        blank=True,
        help_text="Recruitment script or materials"
    )
    recruitment_flyer = models.FileField(
        upload_to='protocol_submissions/recruitment_flyers/%Y/%m/',
        blank=True,
        null=True,
        help_text="Upload a recruitment flyer or poster if applicable (PDF or image)"
    )
    inclusion_criteria = models.TextField(
        blank=True,
        help_text="Criteria for including subjects"
    )
    exclusion_criteria = models.TextField(
        blank=True,
        help_text="Criteria for excluding subjects"
    )
    
    # 3. Benefits and Costs
    benefits_to_subjects = models.TextField(
        blank=True,
        help_text="Benefits to the human subjects involved"
    )
    benefits_to_others = models.TextField(
        blank=True,
        help_text="Benefits to individuals who are not subjects but may have similar problems"
    )
    benefits_to_society = models.TextField(
        blank=True,
        help_text="Benefits to society in general"
    )
    payment_compensation = models.TextField(
        blank=True,
        help_text="Payment or compensation provided to participants"
    )
    costs_to_subjects = models.TextField(
        blank=True,
        help_text="Costs to subjects (time, money, repeated testing, etc.)"
    )
    
    # 4. Review Type Justification
    review_type_justification = models.TextField(
        blank=True,
        help_text="Basis for requesting exemption, expedited review, or full board review"
    )
    exemption_category = models.CharField(
        max_length=100,
        blank=True,
        help_text="Exemption category (if requesting exempt status)"
    )
    expedited_category = models.CharField(
        max_length=100,
        blank=True,
        help_text="Expedited review category (if requesting expedited review)"
    )
    
    # 5. Risks
    risk_statement = models.TextField(
        blank=True,
        help_text="Statement of risk - describe any physical, emotional, social, or legal risks"
    )
    risk_mitigation = models.TextField(
        blank=True,
        help_text="Risk mitigation strategies and protections for participants"
    )
    
    # 6. Data Handling
    data_collection_methods = models.TextField(
        blank=True,
        help_text="Detailed description of data collection methods and instruments"
    )
    data_storage = models.TextField(
        blank=True,
        help_text="How data will be stored and secured"
    )
    confidentiality_procedures = models.TextField(
        blank=True,
        help_text="Procedures for maintaining confidentiality or anonymity"
    )
    data_retention = models.TextField(
        blank=True,
        help_text="Data retention policy and timeline"
    )
    data_access = models.TextField(
        blank=True,
        help_text="Who will have access to the data"
    )
    
    # 7. Consent Procedures
    consent_procedures = models.TextField(
        blank=True,
        help_text="How informed consent will be obtained from participants"
    )
    
    # Additional Information
    estimated_start_date = models.CharField(
        max_length=100,
        blank=True,
        help_text="Estimated starting date"
    )
    estimated_completion_date = models.CharField(
        max_length=100,
        blank=True,
        help_text="Estimated completion date"
    )
    funding_source = models.TextField(
        blank=True,
        help_text="Source of project funds"
    )
    continuation_of_previous = models.BooleanField(
        default=False,
        help_text="Is this project a continuation of research previously approved by the HSIRB?"
    )
    previous_protocol_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Previous HSIRB protocol number (if continuation)"
    )
    
    # ========== ADDITIONAL IRB REQUIREMENTS ==========
    
    # Investigator Information
    pi_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Primary Investigator full name"
    )
    pi_title = models.CharField(
        max_length=200,
        blank=True,
        help_text="PI title/position"
    )
    pi_department = models.CharField(
        max_length=200,
        blank=True,
        help_text="PI department"
    )
    pi_email = models.EmailField(
        blank=True,
        help_text="PI email address"
    )
    pi_phone = models.CharField(
        max_length=50,
        blank=True,
        help_text="PI phone number"
    )
    co_investigators = models.TextField(
        blank=True,
        help_text="List of co-investigators (name, title, department, email)"
    )
    citi_training_completion = models.TextField(
        blank=True,
        help_text="CITI training completion dates and certificate numbers for all investigators"
    )
    citi_training_certificate = models.FileField(
        upload_to='protocol_submissions/citi_certificates/%Y/%m/',
        blank=True,
        null=True,
        help_text="Upload CITI training certificate(s) for all investigators"
    )
    
    # Vulnerable Populations
    involves_vulnerable_populations = models.BooleanField(
        default=False,
        help_text="Does this research involve vulnerable populations?"
    )
    vulnerable_populations_description = models.TextField(
        blank=True,
        help_text="Describe which vulnerable populations are involved and protections in place"
    )
    vulnerable_population_protections = models.TextField(
        blank=True,
        help_text="Specific protections and safeguards for vulnerable populations"
    )
    
    # International Research
    involves_international_research = models.BooleanField(
        default=False,
        help_text="Does this research involve international participants or locations?"
    )
    international_research_locations = models.TextField(
        blank=True,
        help_text="Geographic locations where research will be conducted"
    )
    cultural_considerations = models.TextField(
        blank=True,
        help_text="Cultural considerations and adaptations for international research"
    )
    
    # Financial Interests
    financial_interest_disclosure = models.TextField(
        blank=True,
        help_text="Disclosure of any financial interests or conflicts of interest"
    )
    financial_interest_none = models.BooleanField(
        default=False,
        help_text="No financial interests to disclose"
    )
    
    # Study Monitoring
    data_monitoring_plan = models.TextField(
        blank=True,
        help_text="Plan for monitoring data collection and quality assurance"
    )
    oversight_procedures = models.TextField(
        blank=True,
        help_text="Procedures for oversight and quality assurance"
    )
    
    # Publication and Dissemination
    publication_plan = models.TextField(
        blank=True,
        help_text="Plan for publication and dissemination of results"
    )
    data_sharing_plan = models.TextField(
        blank=True,
        help_text="Plan for sharing data with other researchers or repositories"
    )
    participant_access_to_results = models.TextField(
        blank=True,
        help_text="How participants can access study results (if applicable)"
    )
    
    # Appendices/Documents
    appendices_notes = models.TextField(
        blank=True,
        help_text="Notes about supporting documents, instruments, or analysis plans attached"
    )
    
    # Additional Contact Information
    study_contact_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Study contact person name (if different from PI)"
    )
    study_contact_email = models.EmailField(
        blank=True,
        help_text="Study contact email"
    )
    study_contact_phone = models.CharField(
        max_length=50,
        blank=True,
        help_text="Study contact phone"
    )
    irb_contact_notes = models.TextField(
        blank=True,
        help_text="Additional IRB contact information or notes"
    )
    
    # PI's reviewer suggestions (informational for college rep)
    suggested_reviewers = models.TextField(
        blank=True,
        help_text="PI's suggestions for reviewers (informational - college representative will make final assignment)"
    )
    
    # Signatures (workflow tracking)
    pi_signature_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date PI signed the submission"
    )
    co_investigator_signatures = models.TextField(
        blank=True,
        help_text="Co-investigator signatures and dates"
    )
    department_chair_signature_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date department chair signed (if required)"
    )
    
    # Reviewers (for expedited: 2 reviewers + college rep)
    reviewers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='protocol_reviews',
        blank=True,
        limit_choices_to={'role': 'irb_member'},
        help_text="IRB members assigned to review (for expedited reviews)"
    )
    
    # Chair review (for full board or deception)
    chair_reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chair_reviews',
        limit_choices_to={'role': 'irb_member'},
        help_text="IRB Chair reviewing this submission"
    )
    
    # Link to AI review (optional)
    ai_review = models.ForeignKey(
        IRBReview,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='protocol_submission',
        help_text="Optional AI-assisted review"
    )
    
    # Timestamps
    submitted_at = models.DateTimeField(null=True, blank=True, db_index=True, help_text="When protocol was submitted (not when draft was created)")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    
    # Submitted by
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='submitted_protocols',
        help_text="Primary Investigator who submitted"
    )
    
    # Decision made by
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='decided_protocols',
        help_text="IRB member who made the decision"
    )
    
    class Meta:
        db_table = 'protocol_submissions'
        verbose_name = 'IRB Protocol Submission'
        verbose_name_plural = 'IRB Protocol Submissions'
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['study', '-version']),
            models.Index(fields=['decision', 'submitted_at']),
            models.Index(fields=['review_type', 'decision']),
            models.Index(fields=['college_rep', 'decision']),
        ]
        unique_together = [['study', 'version']]
    
    def __str__(self):
        if self.submission_number:
            return f"Submission {self.submission_number} - {self.study.title} (v{self.version})"
        return f"Draft Protocol - {self.study.title} (v{self.version})"
    
    def save(self, *args, **kwargs):
        """Auto-generate submission number (only when submitting) and increment version."""
        # Only generate submission number when status is 'submitted' and it doesn't exist
        if self.status == 'submitted' and not self.submission_number:
            # Generate submission number: SUB-YYYY-NNN
            year = timezone.now().year
            count = ProtocolSubmission.objects.filter(
                submission_number__startswith=f'SUB-{year}'
            ).count() + 1
            self.submission_number = f'SUB-{year}-{count:03d}'
        
        # Set submitted_at when status changes to 'submitted'
        if self.status == 'submitted' and not self.submitted_at:
            self.submitted_at = timezone.now()
        
        if not self.version or self.version == 1:
            # Get the max version for this study
            max_version = ProtocolSubmission.objects.filter(
                study=self.study
            ).aggregate(
                max_ver=models.Max('version')
            )['max_ver']
            self.version = (max_version or 0) + 1
        
        # If deception is involved, route to chair (only for submitted protocols)
        if self.status == 'submitted' and self.involves_deception and not self.chair_reviewer:
            chair = CollegeRepresentative.objects.filter(is_chair=True, active=True).first()
            if chair and chair.representative:
                self.chair_reviewer = chair.representative
                self.review_type = 'full'  # Deception always requires full review
        
        super().save(*args, **kwargs)
    
    def generate_protocol_number(self):
        """Generate protocol number: HSIRB-YYYY-NNN"""
        if self.protocol_number:
            return self.protocol_number
        
        year = timezone.now().year
        count = ProtocolSubmission.objects.filter(
            protocol_number__startswith=f'HSIRB-{year}'
        ).exclude(protocol_number='').count() + 1
        self.protocol_number = f'HSIRB-{year}-{count:03d}'
        self.save(update_fields=['protocol_number'])
        return self.protocol_number
    
    @property
    def can_be_approved_by_college_rep(self):
        """Check if exempt protocols can be approved by college rep."""
        return self.review_type == 'exempt' and self.decision == 'pending'
    
    @property
    def requires_chair_review(self):
        """Check if submission requires chair review."""
        return (
            self.review_type == 'full' or
            self.involves_deception or
            (self.chair_reviewer is not None)
        )
    
    @property
    def requires_expedited_reviewers(self):
        """Check if expedited review needs 2 additional reviewers."""
        return (
            self.review_type == 'expedited' and
            self.decision == 'pending' and
            self.reviewers.count() < 2
        )


class ProtocolAmendment(models.Model):
    """Amendment to an approved IRB protocol submission."""

    AMENDMENT_TYPE_CHOICES = [
        ('minor', 'Minor Amendment'),
        ('major', 'Major Amendment'),
    ]

    DECISION_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('revise_resubmit', 'Revise & Resubmit'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    protocol_submission = models.ForeignKey(
        ProtocolSubmission,
        on_delete=models.CASCADE,
        related_name='amendments',
        help_text="The approved protocol being amended"
    )

    # Amendment metadata
    amendment_number = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        help_text="Auto-generated amendment number"
    )
    amendment_type = models.CharField(
        max_length=20,
        choices=AMENDMENT_TYPE_CHOICES,
        default='minor',
        help_text="Type of amendment"
    )
    title = models.CharField(
        max_length=300,
        help_text="Brief title of the amendment"
    )

    # Amendment details
    description = models.TextField(
        help_text="Detailed description of the proposed changes"
    )
    justification = models.TextField(
        help_text="Justification for the proposed changes"
    )
    impact_on_risk = models.TextField(
        blank=True,
        help_text="How does this amendment impact the risk level of the study?"
    )
    impact_on_consent = models.TextField(
        blank=True,
        help_text="Does this amendment require changes to the consent form?"
    )
    new_instruments = models.TextField(
        blank=True,
        help_text="Description of any new instruments, measures, or assessments being added"
    )
    instrument_url = models.URLField(
        blank=True,
        help_text="URL to the instrument or assessment (if applicable)"
    )

    # Supporting documents
    supporting_document = models.FileField(
        upload_to='protocol_submissions/amendments/%Y/%m/',
        blank=True,
        null=True,
        help_text="Supporting document (e.g., updated protocol, new instrument)"
    )

    # Review workflow
    decision = models.CharField(
        max_length=20,
        choices=DECISION_CHOICES,
        default='pending',
        db_index=True,
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='amendment_reviews',
        limit_choices_to={'role': 'irb_member'},
        help_text="IRB reviewer assigned to this amendment"
    )
    review_notes = models.TextField(
        blank=True,
        help_text="Reviewer notes / approval conditions"
    )

    # Timestamps
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='submitted_amendments',
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'protocol_amendments'
        verbose_name = 'Protocol Amendment'
        verbose_name_plural = 'Protocol Amendments'
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Amendment {self.amendment_number or 'Draft'}: {self.title}"

    def save(self, *args, **kwargs):
        if not self.amendment_number:
            parent = self.protocol_submission
            count = ProtocolAmendment.objects.filter(
                protocol_submission=parent
            ).count() + 1
            base = parent.protocol_number or parent.submission_number or 'AMEND'
            self.amendment_number = f'{base}-AMD-{count:02d}'
        super().save(*args, **kwargs)

