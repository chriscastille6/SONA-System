"""
Celery tasks for studies app.
"""
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from typing import Tuple

from .models import Signup, Study, Response, IRBReviewerAssignment, StudyUpdate
import importlib


def _notify_irb_reviewers(study, subject, message) -> Tuple[int, str]:
    """Send an email to all subscribed IRB reviewers for a study."""
    assignments = IRBReviewerAssignment.objects.filter(
        study=study,
        receive_email_updates=True
    ).select_related('reviewer')
    
    recipients = []
    assignment_ids = []
    for assignment in assignments:
        reviewer = assignment.reviewer
        if reviewer and reviewer.email:
            recipients.append(reviewer.email)
            assignment_ids.append(assignment.id)
    
    if not recipients:
        return 0, "No IRB reviewers subscribed to email updates."
    
    if not getattr(settings, 'EMAIL_HOST', ''):
        return 0, "Email not configured; IRB reviewers were not notified."
    
    try:
        send_mail(
            subject=subject,
            message=message.strip(),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )
        now = timezone.now()
        if assignment_ids:
            IRBReviewerAssignment.objects.filter(id__in=assignment_ids).update(last_notified_at=now)
        return len(recipients), f"Notified {len(recipients)} IRB reviewers."
    except Exception as exc:
        return 0, f"Failed to notify IRB reviewers: {exc}"


def notify_irb_members_about_update(update: StudyUpdate) -> str:
    """Email IRB reviewers about a new study update."""
    study = update.study
    author_name = update.author.get_full_name() if update.author else "Research team"
    summary = (update.message or '').strip()
    if len(summary) > 500:
        summary = f"{summary[:497]}..."
    if not summary and update.attachment_name:
        summary = f"Attachment shared: {update.attachment_name}"
    link = f"{settings.SITE_URL}/studies/{study.slug}/status/"
    
    subject = f"IRB Update: {study.title}"
    message = f"""
Hello IRB team,

{author_name} posted a new update for the study "{study.title}".

Summary:
{summary or 'The update includes supporting materials for review.'}

View the live protocol dashboard: {link}

You are receiving this message because you are assigned as an IRB reviewer for this study.
"""
    count, response = _notify_irb_reviewers(study, subject, message)
    if count:
        update.notified_at = timezone.now()
        update.save(update_fields=['notified_at'])
    return response


def notify_irb_members_about_review(review) -> str:
    """Email IRB reviewers when a new AI review is completed."""
    study = review.study
    risk_label = review.get_overall_risk_level_display() if review.overall_risk_level else 'Pending'
    link = f"{settings.SITE_URL}/studies/{study.id}/irb-review/{review.version}/"
    
    subject = f"IRB Alert: AI Review v{review.version} for {study.title}"
    message = f"""
Hello IRB team,

An AI-generated IRB review (version {review.version}) is now available for "{study.title}".

Status: {review.get_status_display()}
Overall Risk Level: {risk_label}
Critical Issues: {len(review.critical_issues)}
Moderate Issues: {len(review.moderate_issues)}
Minor Issues: {len(review.minor_issues)}

View the detailed report: {link}

Thank you for keeping this protocol compliant.
"""
    count, response = _notify_irb_reviewers(study, subject, message)
    return response


def send_irb_test_email(study, subject=None, message=None) -> Tuple[int, str]:
    """Send a manual test email to IRB reviewers assigned to the study."""
    default_subject = subject or f"IRB Notification Test: {study.title}"
    default_message = message or f"""
Hello IRB team,

This is a test notification confirming that email delivery is configured for:
"{study.title}"

If you received this message, no further action is necessary.
"""
    return _notify_irb_reviewers(study, default_subject, default_message)


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


@shared_task
def run_irb_ai_review(review_id):
    """
    Run AI-assisted IRB review in background.
    
    This task:
    1. Updates status to 'in_progress'
    2. Initializes IRBAnalyzer with the review
    3. Runs all AI agents in parallel
    4. Aggregates findings and categorizes issues
    5. Sends email notification when complete
    
    Args:
        review_id: UUID of the IRBReview record
    
    Returns:
        Summary dict with results
    """
    import asyncio
    from apps.studies.irb_ai import IRBAnalyzer
    from apps.studies.models import IRBReview
    
    try:
        review = IRBReview.objects.get(id=review_id)
        study = review.study
        
        # Initialize analyzer
        analyzer = IRBAnalyzer(review_id)
        
        # Run async review
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(analyzer.run_review())
        loop.close()
        
        # Send notification email
        if result.get('success') and review.initiated_by:
            try:
                recipient = review.initiated_by.email
                risk_emoji = {'minimal': '✅', 'low': '🟢', 'moderate': '🟡', 'high': '🔴'}.get(
                    review.overall_risk_level, '⚪'
                )
                
                send_mail(
                    subject=f'IRB AI Review Complete: {study.title}',
                    message=f'''
Hello {review.initiated_by.first_name or 'Researcher'},

Your AI-assisted IRB review is complete for:

Study: {study.title}
Review Version: {review.version}

Results:
{risk_emoji} Overall Risk Level: {review.get_overall_risk_level_display()}
🔴 Critical Issues: {len(review.critical_issues)}
🟡 Moderate Issues: {len(review.moderate_issues)}
🟢 Minor Issues: {len(review.minor_issues)}

Processing Time: {review.processing_time_seconds} seconds

View detailed report: {settings.SITE_URL}/studies/{study.id}/irb-review/{review.version}/

{settings.INSTITUTION_NAME}
{settings.SITE_NAME}
                    '''.strip(),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Failed to send IRB review notification: {e}")
        
        if result.get('success'):
            try:
                irb_response = notify_irb_members_about_review(review)
                if irb_response:
                    print(irb_response)
            except Exception as exc:
                print(f"Failed to notify IRB reviewers about review {review.id}: {exc}")
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'review_id': review_id
        }



