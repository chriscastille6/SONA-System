"""
Course and enrollment models.
"""
import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class Course(models.Model):
    """Academic course requiring research participation."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    code = models.CharField(max_length=50, help_text="e.g., PSYC-101")
    name = models.CharField(max_length=300)
    term = models.CharField(max_length=50, help_text="e.g., 2025-Fall", db_index=True)
    section = models.CharField(max_length=20, blank=True)
    
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='courses_taught',
        limit_choices_to={'role__in': ['instructor', 'admin']}
    )
    
    # Requirements
    credits_required = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=3.0,
        validators=[MinValueValidator(0)],
        help_text="Total credits students must earn"
    )
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'courses'
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        ordering = ['-term', 'code']
        unique_together = [['code', 'term', 'section']]
    
    def __str__(self):
        section_str = f"-{self.section}" if self.section else ""
        return f"{self.code}{section_str} ({self.term})"


class Enrollment(models.Model):
    """Student enrollment in a course."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'role': 'participant'}
    )
    
    enrolled_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'course_enrollments'
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'
        unique_together = [['course', 'participant']]
        indexes = [
            models.Index(fields=['course', 'participant']),
            models.Index(fields=['participant']),
        ]
    
    def __str__(self):
        return f"{self.participant.get_full_name()} in {self.course.code}"
    
    def credits_earned(self):
        """Calculate total credits earned for this course."""
        from apps.credits.models import CreditTransaction
        return CreditTransaction.objects.filter(
            participant=self.participant,
            course=self.course,
            amount__gt=0
        ).aggregate(total=models.Sum('amount'))['total'] or 0
    
    def credits_remaining(self):
        """Calculate credits still needed."""
        return max(0, float(self.course.credits_required) - float(self.credits_earned()))
    
    def is_complete(self):
        """Check if credit requirement is met."""
        return self.credits_earned() >= self.course.credits_required




