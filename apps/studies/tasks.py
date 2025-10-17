"""
Celery tasks for studies app.
"""
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from .models import Signup, Study, Response
import importlib


@shared_task
def send_24h_reminders():
    """Send 24-hour reminders for upcoming sessions."""
    now = timezone.now()
    start_window = now + timedelta(hours=23, minutes=30)
    end_window = now + timedelta(hours=24, minutes=30)
    
    signups = Signup.objects.filter(
        status='booked',
        reminder_24h_sent=False,
        timeslot__starts_at__gte=start_window,
        timeslot__starts_at__lt=end_window,
        timeslot__is_cancelled=False
    ).select_related('participant', 'timeslot', 'timeslot__study')
    
    count = 0
    for signup in signups:
        try:
            send_mail(
                subject=f'Reminder: Study tomorrow - {signup.timeslot.study.title}',
                message=f'''
Hello {signup.participant.first_name},

This is a reminder that you have a research study scheduled tomorrow:

Study: {signup.timeslot.study.title}
Time: {signup.timeslot.starts_at.strftime('%A, %B %d at %I:%M %p')}
Location: {signup.timeslot.location or 'See study details'}
Duration: {signup.timeslot.study.duration_minutes} minutes

If you can no longer attend, please cancel as soon as possible at:
{settings.SITE_URL}/studies/signup/{signup.id}/cancel/

Thank you for participating in research!

{settings.INSTITUTION_NAME}
{settings.SITE_NAME}
                '''.strip(),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[signup.participant.email],
                fail_silently=False,
            )
            signup.reminder_24h_sent = True
            signup.save(update_fields=['reminder_24h_sent'])
            count += 1
        except Exception as e:
            print(f"Failed to send 24h reminder to {signup.participant.email}: {e}")
    
    return f"Sent {count} 24-hour reminders"


@shared_task
def send_2h_reminders():
    """Send 2-hour reminders for upcoming sessions."""
    now = timezone.now()
    start_window = now + timedelta(hours=1, minutes=45)
    end_window = now + timedelta(hours=2, minutes=15)
    
    signups = Signup.objects.filter(
        status='booked',
        reminder_2h_sent=False,
        timeslot__starts_at__gte=start_window,
        timeslot__starts_at__lt=end_window,
        timeslot__is_cancelled=False
    ).select_related('participant', 'timeslot', 'timeslot__study')
    
    count = 0
    for signup in signups:
        try:
            send_mail(
                subject=f'Reminder: Study in 2 hours - {signup.timeslot.study.title}',
                message=f'''
Hello {signup.participant.first_name},

This is a reminder that you have a research study in 2 hours:

Study: {signup.timeslot.study.title}
Time: {signup.timeslot.starts_at.strftime('%I:%M %p today')}
Location: {signup.timeslot.location or 'See study details'}

Please arrive on time. If you cannot attend, it may be too late to cancel online.
Please contact the researcher directly if you have an emergency.

Thank you!

{settings.INSTITUTION_NAME}
{settings.SITE_NAME}
                '''.strip(),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[signup.participant.email],
                fail_silently=False,
            )
            signup.reminder_2h_sent = True
            signup.save(update_fields=['reminder_2h_sent'])
            count += 1
        except Exception as e:
            print(f"Failed to send 2h reminder to {signup.participant.email}: {e}")
    
    return f"Sent {count} 2-hour reminders"


@shared_task
def mark_missed_sessions():
    """Mark no-shows for sessions that have passed."""
    now = timezone.now()
    cutoff = now - timedelta(hours=1)  # Grace period
    
    missed_signups = Signup.objects.filter(
        status='booked',
        timeslot__ends_at__lt=cutoff
    )
    
    count = 0
    for signup in missed_signups:
        signup.mark_no_show()
        count += 1
    
    return f"Marked {count} no-shows"


@shared_task
def run_sequential_bayes_monitoring(study_id):
    """
    Run sequential Bayesian monitoring for a study.
    
    This task:
    1. Checks if monitoring is enabled and minimum N is reached
    2. Loads the analysis plugin
    3. Computes the Bayes Factor with all responses
    4. Updates the study's current_bf
    5. Sends notification if BF >= threshold (and not already notified)
    """
    try:
        study = Study.objects.get(id=study_id)
    except Study.DoesNotExist:
        return f"Study {study_id} not found"
    
    if not study.monitoring_enabled:
        return f"Monitoring disabled for study {study.slug}"
    
    # Get response count
    n = study.response_count
    
    if n < study.min_sample_size:
        return f"Study {study.slug}: N={n} < min_sample_size={study.min_sample_size}, skipping monitoring"
    
    # Load analysis plugin
    try:
        module_path, func_name = study.analysis_plugin.rsplit(':', 1)
        module = importlib.import_module(module_path)
        compute_bf = getattr(module, func_name)
    except Exception as e:
        return f"Study {study.slug}: Failed to load analysis plugin: {e}"
    
    # Get all responses
    responses = list(study.responses.order_by('created_at').values_list('payload', flat=True))
    
    # Compute BF
    try:
        bf_value = compute_bf(responses, params={})
        study.current_bf = bf_value
        study.save(update_fields=['current_bf'])
    except Exception as e:
        return f"Study {study.slug}: Failed to compute BF: {e}"
    
    # Check if we should notify
    if bf_value >= study.bf_threshold and not study.monitoring_notified:
        # Send notification (call directly to avoid Celery setup issues)
        try:
            notification_result = send_bf_notification(study_id)
        except Exception as e:
            notification_result = f"Notification failed: {e}"
        
        study.monitoring_notified = True
        study.save(update_fields=['monitoring_notified'])
        return f"Study {study.slug}: BF={bf_value:.2f} >= {study.bf_threshold}, notification: {notification_result}"
    
    return f"Study {study.slug}: BF={bf_value:.2f}, N={n}"


@shared_task
def send_bf_notification(study_id):
    """
    Send notification when BF threshold is reached.
    """
    try:
        study = Study.objects.get(id=study_id)
    except Study.DoesNotExist:
        return f"Study {study_id} not found"
    
    # Try to send email if configured
    if hasattr(settings, 'EMAIL_HOST') and settings.EMAIL_HOST:
        try:
            recipient = study.researcher.email if study.researcher else settings.DEFAULT_FROM_EMAIL
            send_mail(
                subject=f'Bayesian Monitoring Alert: {study.title}',
                message=f'''
Hello,

The sequential Bayesian monitoring for your study "{study.title}" has reached the threshold.

Current Bayes Factor: {study.current_bf:.2f}
Threshold: {study.bf_threshold}
Sample Size: {study.response_count}

The hypothesis is now supported with a BF >= {study.bf_threshold}.

View study dashboard: {settings.SITE_URL}/studies/{study.slug}/status/

{settings.INSTITUTION_NAME}
{settings.SITE_NAME}
                '''.strip(),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
            return f"Email notification sent to {recipient}"
        except Exception as e:
            return f"Failed to send email: {e}"
    else:
        # Email not configured, notification will show in dashboard only
        return f"Email not configured; notification visible in dashboard only"




