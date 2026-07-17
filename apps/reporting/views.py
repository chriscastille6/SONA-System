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
from apps.courses.models import Course, Enrollment
from apps.studies.models import Study, Signup
from apps.credits.models import CreditTransaction


@login_required
def reports_home(request):
    """Reports dashboard."""
    if not (request.user.is_instructor or request.user.is_admin or request.user.is_researcher):
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    return render(request, 'reporting/home.html')


@login_required
def course_credits_csv(request, course_id):
    """Export course credits as CSV. Contains FERPA data; access restricted to instructor/admin."""
    from apps.compliance.guardrails import evaluate_ferpa_export
    from apps.compliance.explainability import log_compliance_decision, outcome_from_report

    course = get_object_or_404(Course, pk=course_id)
    logger.info(
        'course_credits_csv accessed',
        extra={'course_id': str(course_id), 'user_id': str(request.user.id)},
    )
    # Check permission
    if not (request.user.is_admin or course.instructor == request.user):
        messages.error(request, 'Access denied.')
        return redirect('reporting:home')

    hitl_attested = bool(
        request.GET.get('hitl_attest')
        or request.POST.get('hitl_attest')
        or request.session.get(f'export_hitl_{course_id}')
    )
    if request.method == 'POST' and request.POST.get('hitl_attest'):
        request.session[f'export_hitl_{course_id}'] = True
        hitl_attested = True

    compliance_report = evaluate_ferpa_export(
        export_type='course_credits_csv',
        includes_direct_identifiers=True,
        hitl_attested=hitl_attested,
        destination='download',
    )

    if compliance_report.is_blocked or request.GET.get('preview_warnings'):
        if compliance_report.is_blocked:
            try:
                log_compliance_decision(
                    actor=request.user,
                    action='ferpa_export_blocked',
                    entity='course',
                    entity_id=course.id,
                    report=compliance_report,
                    outcome='block',
                    request=request,
                    extra={'course_code': getattr(course, 'code', ''), 'export_type': 'course_credits_csv'},
                )
            except Exception:
                pass
        return render(request, 'reporting/export_compliance_gate.html', {
            'course': course,
            'compliance_report': compliance_report,
            'export_label': f'Course credits CSV ({course.code})',
        })

    try:
        log_compliance_decision(
            actor=request.user,
            action='ferpa_export',
            entity='course',
            entity_id=course.id,
            report=compliance_report,
            outcome=outcome_from_report(compliance_report, proceeded=True),
            request=request,
            actor_note='Instructor/admin downloaded course credits CSV after HITL attestation.',
            extra={'course_code': getattr(course, 'code', ''), 'export_type': 'course_credits_csv'},
        )
    except Exception:
        pass

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
