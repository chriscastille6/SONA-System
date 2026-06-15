"""
Views for reporting app.
"""
import csv
import logging
from django.shortcuts import render, get_object_or_404, redirect

logger = logging.getLogger(__name__)
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
from apps.accounts.models import User
from apps.courses.models import Course, Enrollment
from apps.studies.models import Study, Signup
from apps.credits.models import AuditLog


@login_required
def reports_home(request):
    """Reports dashboard."""
    if not (request.user.is_instructor or request.user.is_admin or request.user.is_researcher or request.user.is_irb_member):
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    return render(request, 'reporting/home.html')


@login_required
def irb_audit_report(request):
    """IRB-focused audit report with filters by IRB member, researcher, and project."""
    if not (request.user.is_irb_member or request.user.is_admin or request.user.is_staff):
        messages.error(request, 'Access denied.')
        return redirect('reporting:home')

    irb_member_id = request.GET.get('irb_member_id') or ''
    researcher_id = request.GET.get('researcher_id') or ''
    study_id = request.GET.get('study_id') or ''

    logs = AuditLog.objects.select_related('actor').order_by('-created_at')

    # Filter 1: specific IRB member activity
    if irb_member_id:
        logs = logs.filter(actor_id=irb_member_id)

    # Filter 2: specific researcher activity
    if researcher_id:
        researcher_studies = list(
            Study.objects.filter(researcher_id=researcher_id).values_list('id', flat=True)
        )
        researcher_study_ids = [str(sid) for sid in researcher_studies]
        logs = logs.filter(
            Q(actor_id=researcher_id)
            | Q(entity='study', entity_id__in=researcher_studies)
            | Q(metadata__study_id__in=researcher_study_ids)
        )

    # Filter 3: specific project/study activity
    if study_id:
        logs = logs.filter(
            Q(entity='study', entity_id=study_id)
            | Q(metadata__study_id=study_id)
        )

    logs = list(logs[:300])

    study_ids = {log.study_id for log in logs if log.study_id}

    studies_by_id = {
        study.id: study
        for study in Study.objects.filter(id__in=study_ids).select_related('researcher')
    }

    audit_rows = [
        {
            'log': log,
            'study': studies_by_id.get(log.study_id),
        }
        for log in logs
    ]

    irb_members = User.objects.filter(role='irb_member', is_active=True).order_by('last_name', 'first_name')
    researchers = User.objects.filter(role='researcher', is_active=True).order_by('last_name', 'first_name')
    studies = Study.objects.select_related('researcher').order_by('title')

    return render(request, 'reporting/irb_audit_report.html', {
        'audit_rows': audit_rows,
        'irb_members': irb_members,
        'researchers': researchers,
        'studies': studies,
        'selected_irb_member_id': irb_member_id,
        'selected_researcher_id': researcher_id,
        'selected_study_id': study_id,
    })


@login_required
def course_credits_csv(request, course_id):
    """Export course credits as CSV. Contains FERPA data; access restricted to instructor/admin."""
    course = get_object_or_404(Course, pk=course_id)
    logger.info(
        'course_credits_csv accessed',
        extra={'course_id': str(course_id), 'user_id': str(request.user.id)},
    )
    # Check permission
    if not (request.user.is_admin or course.instructor == request.user):
        messages.error(request, 'Access denied.')
        return redirect('reporting:home')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="credits_{course.code}_{course.term}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Student ID', 'Name', 'Email', 'Credits Earned', 'Credits Required', 'Status'])
    
    enrollments = Enrollment.objects.filter(course=course).select_related('participant')
    
    for enrollment in enrollments:
        credits_earned = enrollment.credits_earned()
        status = 'Complete' if enrollment.is_complete() else 'In Progress'
        
        writer.writerow([
            enrollment.participant.profile.student_id or 'N/A',
            enrollment.participant.get_full_name(),
            enrollment.participant.email,
            f"{credits_earned:.2f}",
            f"{course.credits_required:.2f}",
            status
        ])
    
    return response


@login_required
def study_report(request, study_id):
    """Study participation report."""
    study = get_object_or_404(Study, pk=study_id)
    
    # Check permission
    if not (request.user.is_admin or study.researcher == request.user):
        messages.error(request, 'Access denied.')
        return redirect('reporting:home')
    
    # Calculate statistics
    total_signups = Signup.objects.filter(timeslot__study=study).count()
    attended = Signup.objects.filter(timeslot__study=study, status='attended').count()
    no_shows = Signup.objects.filter(timeslot__study=study, status='no_show').count()
    cancelled = Signup.objects.filter(timeslot__study=study, status='cancelled').count()
    
    attendance_rate = (attended / total_signups * 100) if total_signups > 0 else 0
    no_show_rate = (no_shows / total_signups * 100) if total_signups > 0 else 0
    
    return render(request, 'reporting/study_report.html', {
        'study': study,
        'total_signups': total_signups,
        'attended': attended,
        'no_shows': no_shows,
        'cancelled': cancelled,
        'attendance_rate': attendance_rate,
        'no_show_rate': no_show_rate,
    })




