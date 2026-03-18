"""
Views for studies app.
"""
from django.db.models import Prefetch, Q
from django.db import models, transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.conf import settings
import json
import logging
import re
import uuid
from pathlib import Path

import markdown

logger = logging.getLogger(__name__)
from .models import (
    Study,
    Timeslot,
    Signup,
    Response,
    StudyEmailContact,
    StudentDataConsent,
    IRBReview,
    ReviewDocument,
    IRBReviewerAssignment,
    StudyUpdate,
    ProtocolSubmission,
    CollegeRepresentative,
    ProtocolAmendment,
)
from .irb_utils import assign_college_rep, route_submission, get_irb_chair
from .tasks import (
    run_sequential_bayes_monitoring,
    run_irb_ai_review,
    notify_irb_members_about_update,
)
from apps.credits.models import AuditLog


def user_can_access_study(user, study):
    """Determine if the given user can view protected study information."""
    if not getattr(user, 'is_authenticated', False):
        return False
    if getattr(user, 'is_admin', False) or getattr(user, 'is_staff', False):
        return True
    if getattr(user, 'is_researcher', False) and study.researcher_id == getattr(user, 'id', None):
        return True
    return study.is_assigned_reviewer(user)


def extam4_summary_html(request):
    """Serve the EXT-AM4 / goals-refs PRAMS summary HTML (file locations, quick reference). Deployed at /studies/docs/extam4-summary/."""
    path = Path(settings.BASE_DIR) / "docs" / "EXTAM4_SONA_SUMMARY.html"
    if not path.exists():
        raise Http404("Summary not found.")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return HttpResponse(f.read(), content_type="text/html; charset=utf-8")
    except OSError:
        raise Http404("Summary could not be read.")


def participant_information_consent(request):
    """Serve the full participant information and consent document. Linked from the assessment platform 'Your Rights and Options' page."""
    return render(request, 'studies/participant_information_consent.html', {
        'platform_name': getattr(settings, 'PLATFORM_NAME', None) or settings.SITE_NAME,
        'institution_name': getattr(settings, 'INSTITUTION_NAME', ''),
        'irb_protocol_number': getattr(settings, 'IRB_PROTOCOL_NUMBER', 'To be assigned'),
        'platform_support_email': getattr(settings, 'PLATFORM_SUPPORT_EMAIL', ''),
        'pi_name': getattr(settings, 'PARTICIPANT_INFO_PI_NAME', ''),
        'pi_email': getattr(settings, 'PARTICIPANT_INFO_PI_EMAIL', ''),
        'pi_phone': getattr(settings, 'PARTICIPANT_INFO_PI_PHONE', ''),
        'irb_office_name': getattr(settings, 'IRB_OFFICE_NAME', ''),
        'irb_office_phone': getattr(settings, 'IRB_OFFICE_PHONE', ''),
        'irb_office_email': getattr(settings, 'IRB_OFFICE_EMAIL', ''),
    })


def _render_social_science_irb_standards_html():
    """Read docs/SOCIAL_SCIENCE_IRB_STANDARDS.md, convert to HTML, preserve mermaid blocks for client-side render."""
    path = Path(settings.BASE_DIR) / "docs" / "SOCIAL_SCIENCE_IRB_STANDARDS.md"
    if not path.exists():
        return "<p>Standards document not found.</p>"
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return "<p>Could not read standards document.</p>"
    # Split on ```mermaid so we can leave mermaid blocks as <div class="mermaid"> for Mermaid.js
    parts = re.split(r"```mermaid\s*\n", raw)
    out = []
    mermaid_index = 0
    for i, segment in enumerate(parts):
        if i == 0:
            # Optional leading markdown (no mermaid before it)
            if segment.strip():
                out.append(markdown.markdown(segment, extensions=["fenced_code"]))
        else:
            # After ```mermaid: content is "flowchart...\n```\nrest" or "flowchart...\n```"
            match = re.match(r"^([\s\S]*?)\n```\s*\n?([\s\S]*)$", segment)
            if match:
                mermaid_body, rest = match.group(1), match.group(2)
                mermaid_index += 1
                if mermaid_index == 1:
                    out.append(
                        '<div class="diagram-1-wrapper">'
                        '<div class="mermaid mermaid-diagram-1">\n' + mermaid_body.strip() + "\n</div>"
                        "</div>"
                    )
                else:
                    out.append('<div class="diagram-2-wrapper"><div class="mermaid">\n' + mermaid_body.strip() + "\n</div></div>")
                if rest.strip():
                    out.append(markdown.markdown(rest, extensions=["fenced_code"]))
            else:
                # Fallback: treat whole segment as markdown
                out.append(markdown.markdown(segment, extensions=["fenced_code"]))
    return "\n".join(out)


@login_required
def social_science_irb_standards(request):
    """Shared guidance for applying proportionate standards to social and behavioral studies."""
    allowed = (
        request.user.is_researcher or
        request.user.is_instructor or
        getattr(request.user, 'is_irb_member', False) or
        request.user.is_staff or
        getattr(request.user, 'is_admin', False)
    )
    if not allowed:
        messages.error(request, 'Access denied.')
        return redirect('home')

    standards_html = _render_social_science_irb_standards_html()
    return render(request, 'studies/social_science_irb_standards.html', {
        'standards_html': standards_html,
    })


def study_list(request):
    """Browse available studies. Uses active_approved (IRB-compliant: excludes expired)."""
    studies = Study.active_approved.all()
    
    # Filter by mode if specified
    mode = request.GET.get('mode')
    if mode in ['lab', 'online']:
        studies = studies.filter(mode=mode)
    
    # TODO: Apply eligibility filtering based on user's prescreen
    
    return render(request, 'studies/list.html', {'studies': studies})


def study_detail(request, pk):
    """Study detail view. Uses active_approved so expired studies return 404 (IRB compliance)."""
    study = get_object_or_404(Study.active_approved, pk=pk)
    
    # Get upcoming timeslots
    timeslots = study.timeslots.filter(
        starts_at__gte=timezone.now(),
        is_cancelled=False
    ).order_by('starts_at')
    
    return render(request, 'studies/detail.html', {
        'study': study,
        'timeslots': timeslots
    })


@login_required
def book_timeslot(request, pk):
    """Book a timeslot. Study must be active_approved (IRB compliance)."""
    timeslot = get_object_or_404(Timeslot, pk=pk)
    if not Study.active_approved.filter(pk=timeslot.study_id).exists():
        raise Http404("Study is not available for signup.")
    
    if not request.user.is_participant:
        messages.error(request, 'Only participants can book timeslots.')
        return redirect('studies:list')
    
    if request.method == 'POST':
        # Check if already booked
        existing = Signup.objects.filter(
            timeslot=timeslot,
            participant=request.user
        ).first()
        
        if existing:
            messages.warning(request, 'You have already signed up for this timeslot.')
            return redirect('studies:detail', pk=timeslot.study.id)
        
        # Check capacity
        if timeslot.is_full:
            messages.error(request, 'This timeslot is full.')
            return redirect('studies:detail', pk=timeslot.study.id)
        
        # Create signup
        Signup.objects.create(
            timeslot=timeslot,
            participant=request.user,
            consent_text_version=timeslot.study.consent_text
        )
        
        messages.success(request, 'Successfully booked timeslot!')
        return redirect('studies:my_bookings')
    
    return render(request, 'studies/book_confirm.html', {'timeslot': timeslot})


@login_required
def cancel_signup(request, pk):
    """Cancel a signup."""
    signup = get_object_or_404(Signup, pk=pk, participant=request.user)
    
    if signup.status != 'booked':
        messages.error(request, 'This signup cannot be cancelled.')
        return redirect('studies:my_bookings')
    
    if not signup.timeslot.can_cancel:
        messages.error(request, f'Cancellation window has closed. Please contact the researcher.')
        return redirect('studies:my_bookings')
    
    if request.method == 'POST':
        signup.cancel()
        messages.success(request, 'Signup cancelled successfully.')
        return redirect('studies:my_bookings')
    
    return render(request, 'studies/cancel_confirm.html', {'signup': signup})


@login_required
def my_bookings(request):
    """View participant's bookings."""
    if not request.user.is_participant:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    signups = Signup.objects.filter(participant=request.user).order_by('-booked_at')
    
    return render(request, 'studies/my_bookings.html', {'signups': signups})


@login_required
def researcher_dashboard(request):
    """Researcher dashboard - shows ALL studies by this researcher."""
    # Allow admin, researcher, or instructor roles
    if not (request.user.is_researcher or request.user.is_instructor or request.user.is_admin or request.user.is_staff):
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Get ALL studies by this researcher (not just those with protocol submissions)
    # Also include studies where user is listed as co-investigator in protocol submissions
    from django.db.models import Q
    from apps.studies.models import ProtocolSubmission
    
    # Use Q objects to combine queries safely (PI, or co-I via text or PRAMS user link)
    studies = Study.objects.filter(
        Q(researcher=request.user) |
        Q(protocol_submissions__co_investigators__icontains=request.user.email) |
        Q(protocol_submissions__co_investigator_users=request.user)
    ).distinct().order_by('-created_at')
    
    # Annotate each study with draft and submitted protocol info
    # Defer detailed protocol fields that may not exist in the database yet
    from apps.studies.models import ProtocolSubmission
    detailed_fields = [
        'protocol_description', 'population_description', 'research_procedures', 'research_objectives',
        'data_collection_methods', 'recruitment_methods', 'informed_consent_procedures',
        'risks_and_benefits', 'confidentiality_procedures', 'data_storage', 'data_retention',
        'debriefing_procedures', 'compensation_details', 'pi_name', 'pi_title', 'pi_department',
        'pi_email', 'pi_phone', 'co_investigators', 'previous_protocol_number', 'suggested_reviewers',
        'citi_training_certificate'
    ]
    
    studies_with_protocols = []
    for study in studies:
        try:
            draft = ProtocolSubmission.objects.filter(
                study=study, 
                status='draft'
            ).defer(*detailed_fields).first()
        except Exception:
            draft = None
        
        try:
            submitted = ProtocolSubmission.objects.filter(
                study=study,
                status='submitted',
                is_archived=False
            ).defer(*detailed_fields).order_by('-submitted_at').first()
        except Exception:
            submitted = None
        # Show "Addendum pending" if this study has any protocol submission with a pending amendment
        pending_amendment = ProtocolAmendment.objects.filter(
            protocol_submission__study=study, decision='pending'
        ).exists()
        studies_with_protocols.append({
            'study': study,
            'draft_protocol': draft,
            'submitted_protocol': submitted,
            'pending_amendment': pending_amendment,
        })
    
    # CITI status for researcher (PI) - flag when expired or expiring
    citi_status = None
    if request.user.is_researcher or request.user.is_instructor:
        from apps.accounts.citi_utils import get_researcher_citi_status
        citi_status = get_researcher_citi_status(request.user)

    return render(request, 'studies/researcher_dashboard.html', {
        'studies': studies,
        'studies_with_protocols': studies_with_protocols,
        'ai_review_enabled': getattr(settings, 'AI_REVIEW_ENABLED', False),
        'citi_status': citi_status,
        'citi_required': getattr(settings, 'CITI_REQUIRED_FOR_SUBMISSION', False),
    })


@login_required
def create_study(request):
    """Create new study."""
    # Allow admin, researcher, or instructor roles
    if not (request.user.is_researcher or request.user.is_instructor or request.user.is_admin or request.user.is_staff):
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    from .forms import StudyForm
    
    if request.method == 'POST':
        form = StudyForm(request.POST)
        if form.is_valid():
            study = form.save(commit=False)
            study.researcher = request.user
            # Generate a slug from the title
            from django.utils.text import slugify
            base_slug = slugify(study.title)[:290]
            slug = base_slug
            counter = 1
            while Study.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            study.slug = slug
            study.save()
            protocol_url = request.build_absolute_uri(reverse('studies:protocol_submit', args=[study.id]))
            dashboard_url = request.build_absolute_uri(reverse('studies:researcher_dashboard'))
            messages.success(
                request,
                f'Study "{study.title}" created successfully! '
                f'Submit for IRB review: {protocol_url} or return to dashboard: {dashboard_url}'
            )
            return redirect('studies:researcher_dashboard')
    else:
        form = StudyForm()
    
    return render(request, 'studies/create.html', {'form': form})


@login_required
def edit_study(request, pk):
    """Edit study."""
    # Allow admin/staff to edit any study, others can only edit their own
    if request.user.is_admin or request.user.is_staff:
        study = get_object_or_404(Study, pk=pk)
    else:
        study = get_object_or_404(Study, pk=pk, researcher=request.user)
    
    from .forms import StudyForm
    
    if request.method == 'POST':
        form = StudyForm(request.POST, instance=study)
        if form.is_valid():
            form.save()
            messages.success(request, f'Study "{study.title}" updated successfully!')
            return redirect('studies:researcher_dashboard')
    else:
        form = StudyForm(instance=study)
    
    return render(request, 'studies/edit.html', {'study': study, 'form': form})


@login_required
def manage_timeslots(request, pk):
    """Manage study timeslots."""
    study = get_object_or_404(Study, pk=pk, researcher=request.user)
    timeslots = study.timeslots.all().order_by('starts_at')
    
    return render(request, 'studies/manage_timeslots.html', {
        'study': study,
        'timeslots': timeslots
    })


@login_required
def study_roster(request, pk):
    """View study roster."""
    study = get_object_or_404(Study, pk=pk, researcher=request.user)
    signups = Signup.objects.filter(timeslot__study=study).select_related(
        'participant', 'timeslot'
    ).order_by('-booked_at')
    
    return render(request, 'studies/roster.html', {
        'study': study,
        'signups': signups
    })


@login_required
def mark_attendance(request, pk):
    """Mark attendance for signup."""
    signup = get_object_or_404(Signup, pk=pk)
    study = signup.timeslot.study
    if study.researcher != request.user and not getattr(request.user, 'is_admin', False):
        raise Http404()
    
    if request.method == 'POST':
        status = request.POST.get('status')
        if status == 'attended':
            signup.mark_attended()
            messages.success(request, 'Marked as attended.')
            
            # TODO: Auto-grant credits
            
        elif status == 'no_show':
            signup.mark_no_show()
            messages.warning(request, 'Marked as no-show.')
        
        return redirect('studies:roster', pk=signup.timeslot.study.id)
    
    return render(request, 'studies/mark_attendance.html', {'signup': signup})


def run_protocol(request, slug):
    """
    Serve the protocol HTML for a study.
    Uses active_approved so expired studies return 404 (IRB compliance).
    """
    study = get_object_or_404(Study.active_approved, slug=slug)
    
    # Try to load project-specific protocol template
    try:
        template = get_template(f'projects/{slug}/protocol/index.html')
        return render(request, f'projects/{slug}/protocol/index.html', {
            'study': study,
        })
    except TemplateDoesNotExist:
        # Show placeholder
        return render(request, 'studies/protocol_placeholder.html', {
            'study': study,
        })


@login_required
def protocol_preview(request, slug):
    """
    Serve the protocol HTML for a study for review (e.g. pending IRB).
    Does not require active_approved; allows staff and PI to view before approval.
    """
    study = get_object_or_404(Study.objects.all(), slug=slug)
    if not (request.user.is_staff or (study.researcher and study.researcher_id == request.user.id)):
        raise Http404("Not authorized to preview this protocol")
    try:
        return render(request, f'projects/{slug}/protocol/index.html', {
            'study': study,
            'use_consent_flow': True,
        })
    except TemplateDoesNotExist:
        return render(request, 'studies/protocol_placeholder.html', {
            'study': study,
        })


def _can_preview_study(request, study):
    """True if user can preview this study (staff or PI)."""
    return request.user.is_authenticated and (
        request.user.is_staff or (study.researcher and study.researcher_id == request.user.id)
    )


@login_required
def protocol_consent(request, slug):
    """
    Consent page for protocol preview flow. Shows study consent text and I agree / I do not agree.
    On agree, redirects to consent-done placeholder so the user is not stuck.
    """
    study = get_object_or_404(Study.objects.all(), slug=slug)
    if not _can_preview_study(request, study):
        raise Http404("Not authorized to preview this protocol")
    if request.method == 'POST':
        agreed = request.POST.get('consent') == 'agree'
        if agreed:
            return redirect('studies:protocol_consent_done', slug=slug)
        return redirect('studies:protocol_preview', slug=slug)
    return render(request, 'studies/protocol_consent.html', {
        'study': study,
    })


@login_required
def protocol_consent_done(request, slug):
    """
    Post-consent page for preview flow. Confirms consent and notes that the full
    survey (vignettes) will be available when the participant frontend is deployed.
    """
    study = get_object_or_404(Study.objects.all(), slug=slug)
    if not _can_preview_study(request, study):
        raise Http404("Not authorized to preview this protocol")
    return render(request, 'studies/protocol_consent_done.html', {
        'study': study,
    })


# Consent form text for HR SJT student secondary-data consent (MNGT 425).
# Placeholders: pi_name, pi_department, withdraw_contact_name, withdraw_contact_email, infographic_preview_link.
HR_SJT_STUDENT_CONSENT_BODY = """
<strong>Informed Consent for Participation in Research</strong>
<strong>Project Title:</strong> HR Situational Judgment Test: Evidence-Based HR Decision-Making

<strong>Principal Investigator:</strong> {pi_name}, {pi_department}

<strong>1. Introduction and Purpose</strong>
You are being asked to participate in a research study comparing how students and HR professionals evaluate specific workplace tactics. You were selected because you completed the case study exercises in MNGT 425 HR Analytics.

<strong>2. Procedures</strong>
If you agree to participate, you grant the researcher permission to include your previously submitted case study ratings in a research dataset.

<strong>No New Work:</strong> You do not need to complete any new assignments or surveys.

<strong>Data Extraction:</strong> Only the numerical ratings and categorical responses from your LMS submission will be used. Your written reflections or personal identifiers will be removed during the analysis phase.

<strong>Appreciation:</strong> As a token of our appreciation for participating, we will share an aggregated report highlighting how individuals from different perspectives (e.g., students, working professionals, MBA students, executives) rated the content in these vignettes. No individuals will be identified. You may sign up to receive the infographic when it is ready. {infographic_preview_link}

<strong>3. Confidentiality</strong>
<strong>Your privacy is our priority.</strong>

While the researcher (your instructor) has access to your original submission for grading purposes, the research dataset will be coded. Your name and student ID will be replaced with a <strong>candidate ID</strong> (a unique code linking only to you for the purpose of withdrawal and deletion requests). This allows you to request that your records be deleted at any time.

<strong>No identifiable information will be included in any publications, presentations, or shared with the participating managers.</strong>

<strong>4. Voluntary Participation and "Grade Shield"</strong>
<strong>Your participation is completely voluntary.</strong>

<strong>No Penalty:</strong> Your decision to participate, or not to participate, will have <strong>zero impact on your grade in MNGT 425</strong> or your relationship with the instructor.

<strong>Blinded Access:</strong> To ensure there is no bias, the instructor will not access the list of consenting students until after the final semester grades have been submitted to the Registrar.

<strong>5. Right to Withdraw</strong>
You may <strong>withdraw your consent at any time without penalty</strong> by contacting {withdraw_contact_name} at {withdraw_contact_email}.

<strong>6. Right to Deletion</strong>
You may <strong>request that your data be deleted at any time without penalty</strong>. Because your record is linked to a candidate ID, the researcher can locate and remove your data from the research dataset. There are no penalties or consequences for requesting deletion. Contact {withdraw_contact_name} at {withdraw_contact_email} to request deletion.

<strong>7. Consent</strong>
By clicking "I Agree" below, you confirm that:

• You are <strong>at least 18 years of age</strong>.

• You have <strong>read this form and understand</strong> the nature of the study.

• You <strong>voluntarily agree</strong> to let your course assignment data be used for this research.

• You understand you may <strong>request deletion of your data at any time without penalty</strong>.
"""


def _hr_sjt_student_consent_context():
    """Context for HR SJT student data consent form (PI and withdraw contact)."""
    return {
        'pi_name': getattr(settings, 'PARTICIPANT_INFO_PI_NAME', 'Dr. Christopher Castille'),
        'pi_department': getattr(settings, 'HR_SJT_CONSENT_PI_DEPARTMENT', 'Management and Marketing'),
        'withdraw_contact_name': getattr(
            settings, 'HR_SJT_WITHDRAW_CONTACT_NAME',
            getattr(settings, 'IRB_OFFICE_NAME', 'Department of Management and Marketing')
        ),
        'withdraw_contact_email': getattr(
            settings, 'HR_SJT_WITHDRAW_CONTACT_EMAIL',
            getattr(settings, 'IRB_OFFICE_EMAIL', '')
        ),
    }


@require_http_methods(['GET', 'POST'])
def hr_sjt_student_data_consent(request):
    """
    Public consent page for MNGT 425 students to consent to secondary use of
    their course assignment data for the HR SJT study. No login required.
    On POST with consent=agree and email, records consent and redirects to thank-you.
    """
    study = get_object_or_404(Study.objects.all(), slug='hr-sjt')
    ctx = {
        **_hr_sjt_student_consent_context(),
        'infographic_preview_link': '<a href="{}" target="_blank" rel="noopener">See a sample infographic here</a>.'.format(
            request.build_absolute_uri(reverse('studies:hr_sjt_infographic_preview'))
        ),
    }
    consent_body = HR_SJT_STUDENT_CONSENT_BODY.format(**ctx).strip()

    if request.method == 'POST':
        if request.POST.get('consent') != 'agree':
            return render(request, 'studies/hr_sjt_student_data_consent.html', {
                'study': study,
                'consent_body': consent_body,
                'error': 'You must agree to participate for your consent to be recorded.',
            })
        email = (request.POST.get('email') or '').strip().lower()
        if not email:
            return render(request, 'studies/hr_sjt_student_data_consent.html', {
                'study': study,
                'consent_body': consent_body,
                'error': 'Please enter your email address so we can record your consent.',
            })
        try:
            with transaction.atomic():
                obj, created = StudentDataConsent.objects.update_or_create(
                    study=study,
                    email=email,
                    defaults={
                        'consent_text_version': consent_body,
                        'withdrawn_at': None,
                    },
                )
        except Exception:
            return render(request, 'studies/hr_sjt_student_data_consent.html', {
                'study': study,
                'consent_body': consent_body,
                'error': 'We could not save your consent. Please try again or contact the researcher.',
            })
        return redirect('studies:hr_sjt_student_data_consent_done')

    return render(request, 'studies/hr_sjt_student_data_consent.html', {
        'study': study,
        'consent_body': consent_body,
    })


def hr_sjt_student_data_consent_done(request):
    """Thank-you page after submitting student data consent."""
    study = get_object_or_404(Study.objects.all(), slug='hr-sjt')
    return render(request, 'studies/hr_sjt_student_data_consent_done.html', {
        'study': study,
    })


# Consent form for HR professionals (working professionals) taking the HR SJT.
# Placeholders: pi_name, pi_department, withdraw_contact_name, withdraw_contact_email, infographic_preview_link.
HR_SJT_PROFESSIONAL_CONSENT_BODY = """
<strong>Informed Consent for Participation in Research</strong>
<strong>Project Title:</strong> HR Situational Judgment Test: Evidence-Based HR Decision-Making

<strong>Principal Investigator:</strong> {pi_name}, {pi_department}

<strong>1. Introduction and Purpose</strong>
Working professionals, such as HR professionals.

You are invited to participate in a research study comparing how HR professionals and students evaluate workplace tactics in situational judgment scenarios. Your responses will help researchers understand how practitioners apply evidence-based HR practices.

<strong>2. Procedures</strong>
If you agree to participate, you will:
• Complete a brief demographic questionnaire (including optional BLS race/ethnicity and HR credentials).
• Complete the HR Situational Judgment Test (27 scenarios; rate effectiveness of tactics 1–5).
• Receive a feedback report summarizing your ratings.

<strong>3. Your Report and Data Ownership</strong>
At the conclusion of the study, you will receive a <strong>PDF report of your data</strong>, which you may keep. The report will contain a <strong>unique identifying code</strong> that gives you ownership over your data. If you would prefer to have your data removed from the study, we will honor that request.

<strong>4. Time and Compensation</strong>
The study takes approximately 45–60 minutes. <strong>There is no monetary compensation.</strong> As a token of our appreciation, we will share an aggregated report highlighting how individuals from different perspectives (e.g., students, working professionals, MBA students, executives) rated the content in these vignettes. No individuals will be identified. You may sign up to receive the infographic when it is ready. {infographic_preview_link} Your participation is voluntary and appreciated.

<strong>5. Confidentiality</strong>
<strong>Your privacy is our priority.</strong> Your responses will be de-identified and stored with a unique code. No identifiable information will be included in any publications or shared with others.

<strong>6. Right to Withdraw</strong>
You may <strong>withdraw your consent at any time without penalty</strong> by closing the browser or contacting {withdraw_contact_name} at {withdraw_contact_email}.

<strong>7. Consent</strong>
By clicking "I Agree" below, you confirm that you are at least 18 years of age, have read this form, and voluntarily agree to participate.
"""


@require_http_methods(['GET', 'POST'])
def hr_sjt_professional_consent(request):
    """
    Consent page for HR professionals (working professionals) taking the HR SJT.
    No login required. On agree, store consent in session and redirect to demographics.
    """
    study = get_object_or_404(Study.objects.all(), slug='hr-sjt')
    ctx = {
        **_hr_sjt_student_consent_context(),
        'infographic_preview_link': '<a href="{}" target="_blank" rel="noopener">See a sample infographic here</a>.'.format(
            request.build_absolute_uri(reverse('studies:hr_sjt_infographic_preview'))
        ),
    }
    consent_body = HR_SJT_PROFESSIONAL_CONSENT_BODY.format(**ctx).strip()

    if request.method == 'POST':
        if request.POST.get('consent') != 'agree':
            return render(request, 'studies/hr_sjt_professional_consent.html', {
                'study': study,
                'consent_body': consent_body,
                'error': 'You must agree to participate to continue.',
            })
        from django.utils import timezone
        request.session['hr_sjt_professional_consent'] = {
            'at': timezone.now().isoformat(),
            'version': consent_body[:200],
        }
        request.session.modified = True
        return redirect('studies:hr_sjt_professional_demographics')

    return render(request, 'studies/hr_sjt_professional_consent.html', {
        'study': study,
        'consent_body': consent_body,
    })


@require_http_methods(['GET', 'POST'])
def hr_sjt_professional_demographics(request):
    """
    Demographics for HR professionals: BLS race/ethnicity + Rynes-style credentials.
    Requires session from professional consent. On submit, save Response and redirect to assessment.
    """
    study = get_object_or_404(Study.objects.all(), slug='hr-sjt')
    if not request.session.get('hr_sjt_professional_consent'):
        return redirect('studies:hr_sjt_professional_consent')

    if request.method == 'POST':
        from django.utils import timezone
        consent_data = request.session.get('hr_sjt_professional_consent', {})
        demographics = {
            'participant_type': 'professional',
            'consent_at': consent_data.get('at'),
            'race_ethnicity': request.POST.get('race_ethnicity', ''),
            'job_level': request.POST.get('job_level', ''),
            'years_in_hr': request.POST.get('years_in_hr', ''),
            'education': request.POST.get('education', ''),
            'hr_major': request.POST.get('hr_major', ''),
            'credentials': request.POST.getlist('credentials'),  # multi
        }
        if request.POST.get('credentials_other'):
            demographics['credentials_other'] = request.POST.get('credentials_other', '')[:200]
        payload = {'consent': True, 'demographics': demographics}
        Response.objects.create(
            study=study,
            payload=payload,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        )
        del request.session['hr_sjt_professional_consent']
        request.session.modified = True
        base = getattr(settings, 'HR_SJT_ASSESSMENT_BASE_URL', 'https://bayoupal.nicholls.edu/hr-sjt-assessment/index.html')
        if study.external_link:
            link = study.external_link.rstrip('/')
            url = f"{link}?study={study.id}" if '?' not in link else f"{link}&study={study.id}"
        else:
            url = f"{base.rstrip('/')}?study={study.id}"
        return redirect(url)

    return render(request, 'studies/hr_sjt_professional_demographics.html', {
        'study': study,
    })


def get_client_ip(request):
    """Return client IP from request (respect X-Forwarded-For if present)."""
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _can_view_study_protocol_materials(request, study):
    """True if user can view protocol materials (e.g. vignette pool) for this study: staff, PI, or assigned rep/chair/reviewer on any submission."""
    if not request.user.is_authenticated:
        return False
    if request.user.is_staff or getattr(request.user, 'is_admin', False):
        return True
    if study.researcher_id and study.researcher_id == request.user.id:
        return True
    from .models import ProtocolSubmission
    qs = ProtocolSubmission.objects.filter(study=study)
    if qs.filter(college_rep=request.user).exists():
        return True
    if qs.filter(chair_reviewer=request.user).exists():
        return True
    if qs.filter(reviewers=request.user).exists():
        return True
    return False


@login_required
def protocol_vignettes(request, slug):
    """
    Show the full vignette pool for a study. Access: staff, PI, college rep, chair, or reviewer
    for any submission of this study (so Jon and Juliann can view goals-refs vignettes).
    """
    study = get_object_or_404(Study.objects.all(), slug=slug)
    if not _can_view_study_protocol_materials(request, study):
        messages.error(request, 'You do not have access to view this study’s vignette pool.')
        return redirect('studies:protocol_submission_list')
    base = Path(__file__).resolve().parent.parent.parent
    vignettes_path = base / "apps" / "studies" / "assets" / "irb" / slug / "vignettes.json"
    if not vignettes_path.exists():
        raise Http404("Vignette pool file not found for this study.")
    try:
        with open(vignettes_path, "r", encoding="utf-8") as f:
            vignettes_data = json.load(f)
    except (OSError, json.JSONDecodeError):
        raise Http404("Vignette pool could not be loaded for this study.")
    if request.GET.get("format") == "json":
        return JsonResponse(vignettes_data, json_dumps_params={"indent": 2})
    return render(request, "studies/protocol_vignettes.html", {
        "study": study,
        "vignettes_data": vignettes_data,
    })


# Study slug -> docs filename for "full documentation" HTML (all cases / protocol summary)
STUDY_DOCUMENTATION_FILES = {
    'hr-sjt': 'HR_SJT_DOCUMENTATION.html',
}


@login_required
def protocol_study_documentation(request, slug):
    """
    Serve the full documentation HTML for a study (e.g. hr-sjt: all 27 scenarios + protocol).
    Access: staff, PI, college rep, chair, or reviewer for any submission of this study.
    """
    study = get_object_or_404(Study.objects.all(), slug=slug)
    if not _can_view_study_protocol_materials(request, study):
        messages.error(request, 'You do not have access to view this study’s documentation.')
        return redirect('studies:protocol_submission_list')
    filename = STUDY_DOCUMENTATION_FILES.get(slug)
    if not filename:
        raise Http404("No documentation page for this study.")
    path = Path(settings.BASE_DIR) / "docs" / filename
    if not path.exists():
        raise Http404("Documentation file not found.")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return HttpResponse(f.read(), content_type="text/html; charset=utf-8")
    except OSError:
        raise Http404("Documentation file could not be read.")


@require_http_methods(["POST"])
def submit_response(request, study_id):
    """
    Accept JSON protocol response submission.
    
    Expected POST body: JSON with response data
    Optional query param: session_id (otherwise generated)
    Uses active_approved so expired studies are rejected (IRB compliance).
    """
    study = get_object_or_404(Study.active_approved, pk=study_id)
    
    # Parse JSON payload
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    # Get or create session_id
    session_id = request.GET.get('session_id')
    if not session_id:
        session_id = uuid.uuid4()
    
    # Get metadata
    ip_address = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    try:
        response = Response.objects.create(
            study=study,
            session_id=session_id,
            payload=payload,
            ip_address=ip_address,
            user_agent=user_agent
        )
    except Exception as e:
        logger.exception('submit_response: failed to save response for study %s', study_id)
        return JsonResponse(
            {'error': 'Unable to save response. Please try again later.'},
            status=503
        )
    
    # Trigger monitoring if enabled
    if study.monitoring_enabled:
        try:
            run_sequential_bayes_monitoring.delay(str(study.id))
        except Exception:
            logger.warning('submit_response: monitoring task enqueue failed for study %s', study_id)
    
    return JsonResponse({
        'success': True,
        'response_id': str(response.id),
        'session_id': str(response.session_id)
    })


@require_http_methods(["POST"])
def submit_infographic_email(request, study_id):
    """
    Accept optional email signup for sending study infographics.
    Only available when study.collect_emails_for_infographics is True.
    Data is stored in StudyEmailContact (separate from Response payloads).
    """
    study = get_object_or_404(Study.active_approved, pk=study_id)
    if not study.collect_emails_for_infographics:
        return JsonResponse({'error': 'This study does not collect emails for infographics.'}, status=404)
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    email = (payload.get('email') or '').strip()
    if not email:
        return JsonResponse({'error': 'Email is required.'}, status=400)
    if len(email) > 254:
        return JsonResponse({'error': 'Email is too long.'}, status=400)
    # Basic email format check
    if '@' not in email or '.' not in email.split('@')[-1]:
        return JsonResponse({'error': 'Invalid email format.'}, status=400)
    session_id = payload.get('session_id')
    if session_id is not None:
        try:
            session_id = uuid.UUID(str(session_id))
        except (ValueError, TypeError):
            session_id = None
    try:
        StudyEmailContact.objects.create(
            study=study,
            email=email,
            session_id=session_id,
        )
    except Exception as e:
        logger.exception('submit_infographic_email: failed to save for study %s', study_id)
        return JsonResponse(
            {'error': 'Unable to save email. Please try again later.'},
            status=503
        )
    return JsonResponse({'success': True})


def _validate_infographic_email(email):
    """Return None if valid, else (error_message, status_code)."""
    email = (email or '').strip()
    if not email:
        return ('Email is required.', 400)
    if len(email) > 254:
        return ('Email is too long.', 400)
    if '@' not in email or '.' not in email.split('@')[-1]:
        return ('Please enter a valid email address.', 400)
    return None


@require_http_methods(["GET", "POST"])
def hr_sjt_infographic_signup(request):
    """
    Public page for HR SJT participants to sign up to receive the lab-branded
    aggregated report infographic. Same-origin form POST avoids CORS/connection issues.
    """
    study = get_object_or_404(Study, slug='hr-sjt')
    if not study.collect_emails_for_infographics:
        raise Http404('This study does not collect emails for infographics.')
    submitted = request.GET.get('submitted') == '1'
    error = None
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        err = _validate_infographic_email(email)
        if err:
            error = err[0] if isinstance(err, tuple) else err
        else:
            try:
                StudyEmailContact.objects.create(study=study, email=email.strip(), session_id=None)
            except Exception:
                logger.exception('hr_sjt_infographic_signup: failed to save for study hr-sjt')
                error = 'Unable to save. Please try again later.'
            else:
                return redirect(request.path + '?submitted=1')
    return render(request, 'studies/hr_sjt_infographic_signup.html', {
        'study': study,
        'submitted': submitted,
        'error': error,
        'lab_name': 'People Analytics Lab of the Bayou',
    })


def hr_sjt_infographic_image(request):
    """
    Serve the WFH ridges infographic PNG so it loads reliably (no dependency on static/CDN).
    Public; no login.
    """
    from pathlib import Path
    static_dirs = getattr(settings, 'STATICFILES_DIRS', [Path(settings.BASE_DIR) / 'static'])
    ridge_name = Path('images/infographics/wfh_productivity_ridges.png')
    for base in static_dirs:
        path = Path(base) / ridge_name
        if path.is_file():
            with open(path, 'rb') as f:
                body = f.read()
            response = HttpResponse(body, content_type='image/png')
            response['Cache-Control'] = 'public, max-age=3600'
            return response
    raise Http404('Infographic image not found. Run: python3 scripts/infographic_wfh_ridges.py')


def hr_sjt_infographic_preview(request):
    """
    View the lab-branded infographic: hypothetical WFH productivity by position.
    Uses economist-style ridge plot (R: ggridges + viridis) from Teaching/MNGT425.
    Public; no login.
    """
    study = get_object_or_404(Study, slug='hr-sjt')
    # Hypothetical summary: 4 perspectives (match Python script — students & professionals more positive, MBA & execs more pessimistic)
    positions_summary = [
        {'name': 'Undergraduate Students', 'mean': 3.8, 'n': 42},
        {'name': 'MBA Students', 'mean': 3.0, 'n': 28},
        {'name': 'Working Professionals', 'mean': 4.0, 'n': 45},
        {'name': 'Executives', 'mean': 2.9, 'n': 12},
    ]
    # Ridge plot: generated by Teaching/MNGT425/infographic_wfh_ridges.py (or R script)
    from pathlib import Path
    static_dirs = getattr(settings, 'STATICFILES_DIRS', [Path(settings.BASE_DIR) / 'static'])
    ridge_name = Path('images/infographics/wfh_productivity_ridges.png')
    has_ridge_image = any((Path(d) / ridge_name).is_file() for d in static_dirs)
    has_logo = any((Path(d) / Path('images/lab_emblem.png')).is_file() for d in static_dirs)
    infographic_image_url = request.build_absolute_uri(reverse('studies:hr_sjt_infographic_image')) if has_ridge_image else ''
    return render(request, 'studies/hr_sjt_infographic_preview.html', {
        'study': study,
        'lab_name': 'People Analytics Lab of the Bayou',
        'lab_website_url': 'https://bayoupal.nicholls.edu',
        'positions_summary': positions_summary,
        'has_ridge_image': has_ridge_image,
        'has_logo': has_logo,
        'infographic_image_url': infographic_image_url,
    })


def study_status(request, slug):
    """
    Show study status: N, BF, threshold, monitoring status, IRB/OSF indicators.
    """
    study = get_object_or_404(Study, slug=slug)
    
    # Check permission (researchers can view their own studies, admins can view all)
    if not user_can_access_study(request.user, study):
        if request.user.is_authenticated:
            messages.error(request, 'Access denied.')
            return redirect('studies:list')
        messages.error(request, 'Please log in.')
        return redirect('accounts:login')
    
    can_post_update = (
        request.user.is_authenticated and (
            (getattr(request.user, 'is_researcher', False) and study.researcher_id == request.user.id) or
            getattr(request.user, 'is_admin', False)
        )
    )
    update_form_error = None
    update_draft_message = ''
    update_draft_visibility = 'irb'
    
    if request.method == 'POST':
        if not can_post_update:
            messages.error(request, 'Only the study owner can post updates.')
            return redirect('studies:status', slug=slug)
        
        message_text = (request.POST.get('message') or '').strip()
        visibility = request.POST.get('visibility', 'irb')
        update_draft_message = message_text
        update_draft_visibility = visibility
        visibility_keys = {choice[0] for choice in StudyUpdate.VISIBILITY_CHOICES}
        if visibility not in visibility_keys:
            visibility = 'irb'
        attachment = request.FILES.get('attachment')
        
        if not message_text and not attachment:
            update_form_error = 'Please provide a message or upload a file.'
        else:
            try:
                update = StudyUpdate.objects.create(
                    study=study,
                    author=request.user,
                    visibility=visibility,
                    message=message_text,
                    attachment=attachment
                )
                if update.visibility == 'irb':
                    notify_result = notify_irb_members_about_update(update)
                    messages.success(
                        request,
                        f'IRB update posted. {notify_result}'.strip()
                    )
                else:
                    messages.success(request, 'Internal research team update posted.')
                return redirect('studies:status', slug=slug)
            except Exception:
                logger.exception('study_status: failed to create StudyUpdate for study %s', slug)
                update_form_error = 'The update could not be saved. Please try again or contact support.'
    
    # Determine which updates are visible to the current user
    if can_post_update or getattr(request.user, 'is_admin', False) or getattr(request.user, 'is_staff', False):
        allowed_visibilities = [choice[0] for choice in StudyUpdate.VISIBILITY_CHOICES]
    elif study.is_assigned_reviewer(request.user):
        allowed_visibilities = ['irb']
    else:
        allowed_visibilities = ['irb']
    
    study_updates = (
        study.updates.filter(visibility__in=allowed_visibilities)
        .select_related('author')
        .order_by('-created_at')[:10]
    )
    viewing_as_irb = study.is_assigned_reviewer(request.user) and not can_post_update
    
    # Get recent responses for display
    recent_responses = study.responses.order_by('-created_at')[:10]
    
    return render(request, 'studies/status.html', {
        'study': study,
        'recent_responses': recent_responses,
        'study_updates': study_updates,
        'can_post_update': can_post_update,
        'update_form_error': update_form_error,
        'update_visibility_choices': StudyUpdate.VISIBILITY_CHOICES,
        'viewing_as_irb': viewing_as_irb,
        'update_draft_message': update_draft_message,
        'update_draft_visibility': update_draft_visibility,
    })


# ========== IRB AI REVIEW VIEWS ==========

@login_required
def irb_review_create(request, study_id):
    """Create a new AI-assisted IRB review. Researchers can review their studies; staff/committee can review any study."""
    study = get_object_or_404(Study, id=study_id)
    # Access: study owner, staff, admin, or IRB member assigned to this study
    can_create = (
        study.researcher == request.user or
        request.user.is_staff or
        getattr(request.user, 'is_admin', False) or
        (getattr(request.user, 'is_irb_member', False) and study.reviewer_assignments.filter(reviewer=request.user).exists())
    )
    if not can_create:
        messages.error(request, 'Access denied: only the study owner or IRB committee can initiate AI review.')
        return redirect('home')
    
    if request.method == 'POST':
        try:
            # Create new review
            review = IRBReview.objects.create(
                study=study,
                initiated_by=request.user,
                osf_repo_url=request.POST.get('osf_url', '')
            )
            
            # Handle uploaded files
            uploaded_count = 0
            for file_key in request.FILES:
                uploaded_file = request.FILES[file_key]
                file_type = request.POST.get(f'{file_key}_type', 'other')
                
                doc = ReviewDocument.objects.create(
                    review=review,
                    file=uploaded_file,
                    filename=uploaded_file.name,
                    file_type=file_type
                )
                uploaded_count += 1
            
            # Record uploaded files metadata
            review.uploaded_files = [
                {
                    'filename': doc.filename,
                    'type': doc.file_type,
                    'size': doc.file_size_bytes,
                    'hash': doc.file_hash
                }
                for doc in review.documents.all()
            ]
            review.save(update_fields=['uploaded_files'])
            
            # Trigger background review
            run_irb_ai_review.delay(str(review.id))
            
            messages.success(
                request,
                f'IRB review initiated (version {review.version}). You will be notified when analysis is complete.'
            )
            return redirect('studies:irb_review_detail', study_id=study.id, version=review.version)
        except Exception:
            logger.exception('irb_review_create: failed to create review for study %s', study_id)
            messages.error(
                request,
                'The review could not be started. Please check your files and try again, or contact support.'
            )
            return render(request, 'studies/irb_review_create.html', {
                'study': study,
            })
    
    # GET: Show upload form
    return render(request, 'studies/irb_review_create.html', {
        'study': study,
    })


@login_required
def irb_review_detail(request, study_id, version):
    """View detailed IRB review results."""
    study = get_object_or_404(Study, id=study_id)
    
    if not user_can_access_study(request.user, study):
        messages.error(request, 'Access denied: you are not assigned to this study.')
        return redirect('home')
    
    review = get_object_or_404(IRBReview, study=study, version=version)
    
    # Handle researcher response submission
    if request.method == 'POST':
        if not (request.user.is_researcher and study.researcher == request.user):
            messages.error(request, 'Only the study owner can respond to AI review findings.')
            return redirect('studies:irb_review_detail', study_id=study.id, version=version)
        
        review.researcher_notes = request.POST.get('notes', '')
        
        # Record which issues were addressed
        addressed = []
        for key in request.POST:
            if key.startswith('issue_'):
                issue_id = key.replace('issue_', '')
                addressed.append(issue_id)
        
        review.issues_addressed = addressed
        review.save(update_fields=['researcher_notes', 'issues_addressed'])
        
        messages.success(request, 'Response saved.')
        return redirect('studies:irb_review_detail', study_id=study.id, version=version)
    
    # Normalize issue fields to lists of dicts so template and **issue never see None or non-dict
    def _normalize_issue(issue, default_id=''):
        if isinstance(issue, dict):
            return {
                'issue_id': issue.get('issue_id', default_id),
                'description': issue.get('description', ''),
                'recommendation': issue.get('recommendation', ''),
                'category': issue.get('category', 'general'),
                'affected_section': issue.get('affected_section', ''),
                'agent': issue.get('agent', ''),
            }
        return {'issue_id': default_id, 'description': str(issue), 'recommendation': '', 'category': 'general', 'affected_section': '', 'agent': ''}

    critical_raw = review.critical_issues if isinstance(review.critical_issues, list) else []
    moderate_raw = review.moderate_issues if isinstance(review.moderate_issues, list) else []
    minor_raw = review.minor_issues if isinstance(review.minor_issues, list) else []

    critical_safe = [_normalize_issue(issue, f'critical_{i}') for i, issue in enumerate(critical_raw)]
    moderate_safe = [_normalize_issue(issue, f'moderate_{i}') for i, issue in enumerate(moderate_raw)]
    minor_safe = [_normalize_issue(issue, f'minor_{i}') for i, issue in enumerate(minor_raw)]

    review.critical_issues = critical_safe
    review.moderate_issues = moderate_safe
    review.minor_issues = minor_safe

    all_issues = (
        [{'severity': 'critical', **issue} for issue in critical_safe]
        + [{'severity': 'moderate', **issue} for issue in moderate_safe]
        + [{'severity': 'minor', **issue} for issue in minor_safe]
    )

    # Per-agent transparency: what each agent does and what it found
    AGENT_DISPLAY = {
        'ethics': ('Ethics', 'Research ethics and Belmont Report principles (respect for persons, beneficence, justice).'),
        'privacy': ('Privacy', 'Privacy protection, confidentiality, and data anonymization.'),
        'vulnerability': ('Vulnerable Populations', 'Protections for vulnerable populations (e.g., children, prisoners).'),
        'data_security': ('Data Security', 'Data handling, storage, transmission, and security measures.'),
        'consent': ('Consent', 'Informed consent adequacy, documentation, and process.'),
    }
    agent_sections = []
    for key, (name, focus) in AGENT_DISPLAY.items():
        analysis = getattr(review, f'{key}_analysis', None) or {}
        if not isinstance(analysis, dict):
            analysis = {}
        model_used = (review.ai_model_versions or {}).get(key) or analysis.get('model') or '—'
        agent_sections.append({
            'key': key,
            'name': name,
            'focus': focus,
            'analysis': analysis,
            'model_used': model_used,
            'summary': analysis.get('summary') or '',
            'risk_assessment': analysis.get('risk_assessment') or '',
            'findings': analysis.get('findings') or [],
        })

    return render(request, 'studies/irb_review_report.html', {
        'study': study,
        'review': review,
        'all_issues': all_issues,
        'can_edit_review': request.user.is_researcher and study.researcher == request.user,
        'agent_sections': agent_sections,
    })


@login_required
def irb_review_history(request, study_id):
    """View all IRB reviews for a study."""
    study = get_object_or_404(Study, id=study_id)
    
    if not user_can_access_study(request.user, study):
        messages.error(request, 'Access denied: you are not assigned to this study.')
        return redirect('home')
    
    reviews = IRBReview.objects.filter(study=study).order_by('-version')
    
    return render(request, 'studies/irb_review_history.html', {
        'study': study,
        'reviews': reviews,
        'can_initiate_review': request.user.is_researcher and study.researcher == request.user,
        'viewing_as_irb': study.is_assigned_reviewer(request.user) and not (request.user.is_researcher and study.researcher == request.user),
    })


@login_required
def committee_dashboard(request):
    """IRB committee dashboard for reviewing AI reports."""
    # Restrict access to admins, staff, or assigned IRB members
    if request.user.is_staff or getattr(request.user, 'is_admin', False):
        studies = Study.objects.all()
    elif getattr(request.user, 'is_irb_member', False):
        studies = Study.objects.filter(reviewer_assignments__reviewer=request.user)
    else:
        messages.error(request, 'Access denied: Committee members only.')
        return redirect('home')
    
    # Get studies with reviews, filtered by IRB status
    irb_status_filter = request.GET.get('irb_status', '')
    
    if irb_status_filter:
        studies = studies.filter(irb_status=irb_status_filter)
    
    studies = studies.prefetch_related('irb_reviews').select_related('researcher').distinct()
    
    assignments_map = {}
    if getattr(request.user, 'is_irb_member', False):
        assignment_qs = IRBReviewerAssignment.objects.filter(
            reviewer=request.user,
            study_id__in=studies.values_list('id', flat=True)
        )
        assignments_map = {assignment.study_id: assignment for assignment in assignment_qs}
    
    # Annotate with latest review info
    studies_with_reviews = []
    for study in studies:
        latest_review = study.latest_irb_review
        studies_with_reviews.append({
            'study': study,
            'latest_review': latest_review,
            'has_critical': latest_review and len(latest_review.critical_issues) > 0 if latest_review else False,
            'assignment': assignments_map.get(study.id),
        })
    
    return render(request, 'studies/committee_dashboard.html', {
        'studies_with_reviews': studies_with_reviews,
        'irb_status_choices': Study.IRB_STATUS_CHOICES,
        'selected_status': irb_status_filter,
        'show_admin_links': request.user.is_staff or getattr(request.user, 'is_admin', False),
        'ai_review_enabled': getattr(settings, 'AI_REVIEW_ENABLED', False),
    })


@login_required
@require_http_methods(["POST"])
def toggle_irb_email_updates(request, assignment_id):
    """Allow IRB members (or staff) to toggle email notifications."""
    if not (getattr(request.user, 'is_irb_member', False) or request.user.is_staff or getattr(request.user, 'is_admin', False)):
        messages.error(request, 'Access denied: IRB members only.')
        return redirect('home')
    
    assignment = get_object_or_404(
        IRBReviewerAssignment,
        id=assignment_id
    )
    
    if assignment.reviewer != request.user and not (request.user.is_staff or getattr(request.user, 'is_admin', False)):
        messages.error(request, 'You cannot modify another reviewer’s preferences.')
        return redirect('studies:irb_member_dashboard')
    
    assignment.receive_email_updates = not assignment.receive_email_updates
    assignment.save(update_fields=['receive_email_updates'])
    
    state = 'enabled' if assignment.receive_email_updates else 'disabled'
    messages.success(
        request,
        f'Email notifications {state} for "{assignment.study.title}".'
    )
    
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
    if next_url:
        return redirect(next_url)
    if getattr(request.user, 'is_irb_member', False):
        return redirect('studies:irb_member_dashboard')
    return redirect('studies:committee_dashboard')


@login_required
def irb_member_dashboard(request):
    """Dashboard for individual IRB members to track assigned studies."""
    if not (getattr(request.user, 'is_irb_member', False) or request.user.is_staff or getattr(request.user, 'is_admin', False)):
        messages.error(request, 'Access denied: IRB members only.')
        return redirect('home')
    
    assignments = (
        IRBReviewerAssignment.objects.filter(reviewer=request.user)
        .select_related('study', 'study__researcher')
        .prefetch_related(
            Prefetch(
                'study__irb_reviews',
                queryset=IRBReview.objects.order_by('-version'),
                to_attr='prefetched_irb_reviews'
            ),
            Prefetch(
                'study__updates',
                queryset=StudyUpdate.objects.filter(visibility='irb').select_related('author').order_by('-created_at'),
                to_attr='prefetched_irb_updates'
            ),
        )
        .order_by('-created_at')
    )
    
    assigned_items = []
    for assignment in assignments:
        study = assignment.study
        prefetched_reviews = getattr(study, 'prefetched_irb_reviews', list(study.irb_reviews.order_by('-version')[:3]))
        latest_review = prefetched_reviews[0] if prefetched_reviews else None
        prefetched_updates = getattr(study, 'prefetched_irb_updates', list(
            study.updates.filter(visibility='irb').select_related('author').order_by('-created_at')[:5]
        ))
        assigned_items.append({
            'assignment': assignment,
            'study': study,
            'latest_review': latest_review,
            'recent_reviews': prefetched_reviews[:3],
            'updates': prefetched_updates[:5],
        })
    
    return render(request, 'studies/irb_member_dashboard.html', {
        'assigned_items': assigned_items,
    })


# ========== PROTOCOL SUBMISSION VIEWS ==========

@login_required
def protocol_enter(request, study_id):
    """Enter or edit protocol information (draft mode)."""
    from .forms import ProtocolSubmissionForm
    
    study = get_object_or_404(Study, id=study_id)
    
    # Only study owner can enter/edit protocol info (or admin/staff)
    if not (request.user.is_researcher and study.researcher == request.user) and not (request.user.is_admin or request.user.is_staff):
        messages.error(request, 'Only the study owner can enter protocol information.')
        return redirect('studies:detail', pk=study.id)
    
    # Get or create draft submission
    draft_submission = ProtocolSubmission.objects.filter(
        study=study,
        status='draft'
    ).order_by('-version').first()
    
    # Use latest submitted/approved protocol to pre-fill when no draft or draft is empty
    existing_submitted = ProtocolSubmission.objects.filter(
        study=study,
        status='submitted'
    ).order_by('-submitted_at', '-version').first()
    if not existing_submitted:
        # Fallback: any non-draft submission with a protocol or submission number
        existing_submitted = ProtocolSubmission.objects.filter(
            study=study
        ).exclude(status='draft').filter(
            Q(protocol_number__gt='') | Q(submission_number__gt='')
        ).order_by('-submitted_at', '-version').first()
    # If draft exists but has no content, prefer showing the approved protocol
    draft_has_content = (
        draft_submission
        and (
            (getattr(draft_submission, 'protocol_description', None) or '').strip()
            or (getattr(draft_submission, 'population_description', None) or '').strip()
        )
    )
    if draft_submission and not draft_has_content and existing_submitted:
        # Show approved protocol in form; don't bind to empty draft so initial data displays
        draft_submission = None
    
    if request.method == 'POST':
        form = ProtocolSubmissionForm(request.POST, request.FILES, instance=draft_submission)
        if form.is_valid():
            # Save as draft
            submission = form.save(commit=False)
            submission.study = study
            submission.status = 'draft'  # Always save as draft
            submission.submitted_by = request.user
            if not submission.review_type:
                submission.review_type = submission.pi_suggested_review_type  # Initial, may change
            
            # Handle selected IRB reviewers - format into suggested_reviewers
            selected_reviewers = form.cleaned_data.get('selected_irb_reviewers', [])
            if selected_reviewers:
                reviewer_names = [f"{r.get_full_name()} ({r.email})" for r in selected_reviewers]
                reviewer_text = "Selected IRB Reviewers:\n" + "\n".join(f"- {name}" for name in reviewer_names)
                # Append to existing suggested_reviewers if it exists
                if submission.suggested_reviewers:
                    submission.suggested_reviewers = f"{submission.suggested_reviewers}\n\n{reviewer_text}"
                else:
                    submission.suggested_reviewers = reviewer_text
            
            submission.save()
            form.save_m2m()  # Save co_investigator_users M2M
            
            # Rebuild co_investigators text from PRAMS users + extra (for display and dashboard __icontains)
            selected_co_i = form.cleaned_data.get('co_investigator_users') or []
            lines = [f"{u.get_full_name()}, {u.email}" for u in selected_co_i]
            extra = (form.cleaned_data.get('co_investigators_extra') or "").strip()
            if extra:
                lines.append(extra)
            submission.co_investigators = "\n".join(lines)
            submission.save(update_fields=['co_investigators'])
            
            # Update study deception flag
            study.involves_deception = submission.involves_deception
            study.save(update_fields=['involves_deception'])
            
            submit_url = request.build_absolute_uri(reverse('studies:protocol_submit', args=[study.id]))
            messages.success(
                request,
                f'Protocol information saved as draft! You can continue editing or submit for IRB review when ready: {submit_url}'
            )
            return redirect('studies:protocol_enter', study_id=study.id)
    else:
        # Pre-fill form with existing draft data, or from latest submitted protocol if no draft
        initial_data = {}
        source_submission = draft_submission or existing_submitted
        if source_submission:
            for field in ProtocolSubmissionForm.Meta.fields:
                if hasattr(source_submission, field):
                    value = getattr(source_submission, field)
                    if value is not None and value != '':  # Only include non-empty values
                        initial_data[field] = value
        
        # Auto-fill PI information from logged-in user profile when nothing loaded
        if not initial_data.get('pi_name'):
            initial_data['pi_name'] = request.user.get_full_name()
        if not initial_data.get('pi_email'):
            initial_data['pi_email'] = request.user.email
        if not initial_data.get('pi_department'):
            # Try to get department from user profile
            if hasattr(request.user, 'profile') and request.user.profile.department:
                initial_data['pi_department'] = request.user.profile.department
        
        form = ProtocolSubmissionForm(initial=initial_data, instance=draft_submission)
    
    return render(request, 'studies/protocol_enter.html', {
        'study': study,
        'form': form,
        'draft_submission': draft_submission,
        'existing_submitted': existing_submitted,
    })


@login_required
def protocol_submit(request, study_id):
    """Submit protocol for IRB review (final submission)."""
    from .forms import ProtocolSubmissionForm
    from django.conf import settings
    from apps.accounts.citi_utils import researcher_can_submit_protocol

    study = get_object_or_404(Study, id=study_id)

    # Only study owner can submit (or admin/staff)
    if not (request.user.is_researcher and study.researcher == request.user) and not (request.user.is_admin or request.user.is_staff):
        messages.error(request, 'Only the study owner can submit protocols.')
        return redirect('studies:detail', pk=study.id)

    # CITI check: PI must have valid (non-expired) CITI certificate to submit
    if getattr(settings, 'CITI_REQUIRED_FOR_SUBMISSION', False):
        pi = study.researcher
        if pi:
            can_submit, msg = researcher_can_submit_protocol(pi)
            if not can_submit:
                messages.error(
                    request,
                    f'Protocol submission blocked: {msg} '
                    'Please add or renew your CITI certificate in your profile.'
                )
                return redirect('studies:protocol_enter', study_id=study.id)

    # Get draft submission
    draft_submission = ProtocolSubmission.objects.filter(
        study=study,
        status='draft'
    ).order_by('-version').first()
    
    if not draft_submission:
        enter_url = request.build_absolute_uri(reverse('studies:protocol_enter', args=[study.id]))
        messages.warning(
            request,
            f'No protocol information found. Please enter protocol information first: {enter_url}'
        )
        return redirect('studies:protocol_enter', study_id=study.id)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Save full protocol PDF if uploaded
                full_pdf = request.FILES.get('full_protocol_pdf')
                if full_pdf and full_pdf.name.lower().endswith('.pdf'):
                    draft_submission.full_protocol_pdf = full_pdf
                # Mark draft as submitted (ensure review_type is set; fallback to exempt)
                draft_submission.status = 'submitted'
                draft_submission.submitted_by = request.user
                suggested = (draft_submission.pi_suggested_review_type or '').strip() or 'exempt'
                if suggested not in ('exempt', 'expedited', 'full'):
                    suggested = 'exempt'
                draft_submission.review_type = suggested
                draft_submission.save()  # This will generate submission_number and set submitted_at

                # Refresh from database to get the generated submission_number
                draft_submission.refresh_from_db()

                # Update study deception flag
                study.involves_deception = draft_submission.involves_deception
                study.save(update_fields=['involves_deception'])

                # Assign college rep
                assign_college_rep(draft_submission)

                # Route submission
                route_submission(draft_submission)

                # Send email notification to college rep
                from .tasks import notify_college_rep_about_submission
                try:
                    notify_result = notify_college_rep_about_submission(draft_submission)
                    if notify_result and 'Failed' not in notify_result:
                        messages.info(request, 'College representative has been notified via email.')
                except Exception:
                    pass

                # Check if AI review was requested (from form if present)
                use_ai_review = request.POST.get('use_ai_review', False)
                if use_ai_review:
                    if getattr(settings, 'AI_REVIEW_ENABLED', False):
                        ai_review = IRBReview.objects.create(
                            study=study,
                            initiated_by=request.user,
                        )
                        draft_submission.ai_review = ai_review
                        draft_submission.save(update_fields=['ai_review'])
                        run_irb_ai_review.delay(str(ai_review.id))
                        messages.info(request, 'AI review initiated. You will be notified when complete.')
                    else:
                        messages.warning(request, 'AI review is not currently enabled. Protocol submitted without AI review.')

                submission_detail_url = request.build_absolute_uri(
                    reverse('studies:protocol_submission_detail', args=[draft_submission.id])
                )
                dashboard_url = request.build_absolute_uri(reverse('studies:researcher_dashboard'))
                submission_number = draft_submission.submission_number or 'Pending'
                messages.success(
                    request,
                    f'Protocol submitted successfully! Submission #{submission_number}. '
                    f'Your college representative will review it within 5-7 business days. '
                    f'View submission details: {submission_detail_url} or return to dashboard: {dashboard_url}'
                )
                return redirect('studies:protocol_submission_detail', submission_id=draft_submission.id)
        except Exception as e:
            import logging
            logging.getLogger(__name__).exception('Protocol submit failed for study %s: %s', study_id, e)
            messages.error(
                request,
                'Submission could not be completed. The error has been logged. '
                'Please try again or contact support if the problem persists.'
            )
            return redirect('studies:protocol_submit', study_id=study.id)
    else:
        # Show confirmation page before submitting
        return render(request, 'studies/protocol_submit_confirm.html', {
            'study': study,
            'draft_submission': draft_submission,
            'ai_review_enabled': getattr(settings, 'AI_REVIEW_ENABLED', False),
        })


def _get_informed_consent_display(submission, study):
    """
    Build consent text for display on protocol submission detail.
    Uses Study.consent_text when set; otherwise inferred from submission
    (consent_procedures, risk_statement, confidentiality_procedures, risk_mitigation).
    Returns None if nothing to show.
    """
    if study and getattr(study, 'consent_text', None) and (study.consent_text or '').strip():
        return (study.consent_text or '').strip()
    parts = []
    for title, attr in [
        ('Consent procedures', 'consent_procedures'),
        ('Risks', 'risk_statement'),
        ('Confidentiality', 'confidentiality_procedures'),
        ('Risk mitigation', 'risk_mitigation'),
    ]:
        value = (getattr(submission, attr, None) or '').strip()
        if value:
            parts.append(f"### {title}\n\n{value}")
    if not parts:
        return None
    return '\n\n'.join(parts)


@login_required
def protocol_submission_detail(request, submission_id):
    """View protocol submission details."""
    submission = get_object_or_404(ProtocolSubmission, id=submission_id)
    # Backfill submission_number if this is submitted but never got one (e.g. created via bulk update)
    if submission.status == 'submitted' and not submission.submission_number:
        submission.save()  # Model.save() generates submission_number
        submission.refresh_from_db()
    try:
        study = submission.study if submission.study_id else None
    except Exception:
        study = None  # Study was deleted; protocol may still be viewable
    
    # Check access (include co-investigators: text list or PRAMS users)
    is_co_i = bool(
        (request.user.email and submission.co_investigators and request.user.email.lower() in submission.co_investigators.lower())
        or submission.co_investigator_users.filter(pk=request.user.pk).exists()
    )
    can_view = (
        request.user.is_staff or
        getattr(request.user, 'is_admin', False) or
        (request.user.is_researcher and study and study.researcher == request.user) or
        is_co_i or
        submission.college_rep == request.user or
        submission.chair_reviewer == request.user or
        submission.reviewers.filter(id=request.user.id).exists()
    )
    
    if not can_view:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Get IRB members for reviewer assignment
    from apps.accounts.models import User
    irb_members = User.objects.filter(role='irb_member')
    if submission.college_rep:
        irb_members = irb_members.exclude(id=submission.college_rep.id)
    
    informed_consent_display = _get_informed_consent_display(submission, study) if submission and study else None

    return render(request, 'studies/protocol_submission_detail.html', {
        'submission': submission,
        'study': study,
        'is_pi': request.user.is_researcher and study and study.researcher == request.user,
        'is_co_i': is_co_i,
        'is_college_rep': submission.college_rep == request.user,
        'is_chair': submission.chair_reviewer == request.user,
        'is_reviewer': submission.reviewers.filter(id=request.user.id).exists(),
        'irb_members': irb_members,
        'informed_consent_display': informed_consent_display,
    })


@login_required
@require_http_methods(["POST"])
def protocol_college_rep_review(request, submission_id):
    """College rep makes initial determination."""
    submission = get_object_or_404(ProtocolSubmission, id=submission_id)
    
    # Only college rep can review
    if submission.college_rep != request.user:
        messages.error(request, 'Only the assigned college representative can make this determination.')
        return redirect('studies:protocol_submission_detail', submission_id=submission.id)
    
    if submission.decision != 'pending':
        messages.error(request, 'This submission has already been decided.')
        return redirect('studies:protocol_submission_detail', submission_id=submission.id)
    
    determination = request.POST.get('determination')
    notes = request.POST.get('notes', '').strip()
    
    if determination not in ['exempt', 'expedited', 'full']:
        messages.error(request, 'Invalid determination.')
        return redirect('studies:protocol_submission_detail', submission_id=submission.id)
    
    submission.college_rep_determination = determination
    submission.college_rep_notes = notes
    submission.review_type = determination
    submission.reviewed_at = timezone.now()
    
    # If exempt, college rep can approve immediately
    if determination == 'exempt':
        # College rep can approve exempt protocols
        pass  # Will be handled by decision view
    
    # If expedited, need to assign 2 reviewers
    elif determination == 'expedited':
        # Reviewers will be assigned separately
        pass
    
    # If full, route to chair
    elif determination == 'full':
        chair = get_irb_chair()
        if chair:
            submission.chair_reviewer = chair
        else:
            messages.warning(request, 'IRB Chair not found. Please assign manually.')
    
    submission.save()
    
    messages.success(request, f'Determination recorded: {determination.title()}.')
    return redirect('studies:protocol_submission_detail', submission_id=submission.id)


@login_required
@require_http_methods(["POST"])
def protocol_assign_reviewers(request, submission_id):
    """Assign reviewers for expedited review."""
    submission = get_object_or_404(ProtocolSubmission, id=submission_id)
    
    # Only college rep or chair can assign reviewers
    can_assign = (
        submission.college_rep == request.user or
        submission.chair_reviewer == request.user or
        request.user.is_staff or
        getattr(request.user, 'is_admin', False)
    )
    
    if not can_assign:
        messages.error(request, 'You do not have permission to assign reviewers.')
        return redirect('studies:protocol_submission_detail', submission_id=submission.id)
    
    reviewer_ids = request.POST.getlist('reviewers')
    
    if len(reviewer_ids) < 2:
        messages.error(request, 'Expedited reviews require at least 2 reviewers.')
        return redirect('studies:protocol_submission_detail', submission_id=submission.id)
    
    from apps.accounts.models import User
    reviewers = User.objects.filter(
        id__in=reviewer_ids,
        role='irb_member'
    )
    
    submission.reviewers.set(reviewers)
    
    # Send email notifications to assigned reviewers
    from .tasks import notify_reviewers_about_assignment
    try:
        notify_result = notify_reviewers_about_assignment(submission)
        if notify_result and 'Failed' not in notify_result:
            messages.info(request, f'Reviewers have been notified via email.')
    except Exception as e:
        # Don't fail assignment if email fails
        pass
    
    messages.success(request, f'Assigned {reviewers.count()} reviewers.')
    
    return redirect('studies:protocol_submission_detail', submission_id=submission.id)


@login_required
@require_http_methods(["POST"])
def protocol_make_decision(request, submission_id):
    """Make decision on protocol (approve/R&R/reject)."""
    submission = get_object_or_404(ProtocolSubmission, id=submission_id)
    
    # Check permissions
    can_decide = False
    if submission.review_type == 'exempt':
        can_decide = submission.college_rep == request.user
    elif submission.review_type == 'expedited':
        can_decide = (
            submission.college_rep == request.user or
            submission.reviewers.filter(id=request.user.id).exists()
        )
    elif submission.review_type == 'full':
        can_decide = submission.chair_reviewer == request.user
    
    can_decide = can_decide or request.user.is_staff or getattr(request.user, 'is_admin', False)
    
    if not can_decide:
        messages.error(request, 'You do not have permission to make decisions on this submission.')
        return redirect('studies:protocol_submission_detail', submission_id=submission.id)
    
    if submission.decision != 'pending':
        messages.error(request, 'This submission has already been decided.')
        return redirect('studies:protocol_submission_detail', submission_id=submission.id)
    
    decision = request.POST.get('decision')
    notes = request.POST.get('notes', '')
    
    if decision not in ['approved', 'revise_resubmit', 'rejected']:
        messages.error(request, 'Invalid decision.')
        return redirect('studies:protocol_submission_detail', submission_id=submission.id)
    
    submission.decision = decision
    submission.decided_by = request.user
    submission.decided_at = timezone.now()
    
    if decision == 'approved':
        # Use custom protocol number if provided, otherwise auto-generate
        custom_protocol_number = request.POST.get('protocol_number', '').strip()
        if custom_protocol_number:
            # Validate that it doesn't already exist
            existing = ProtocolSubmission.objects.filter(
                protocol_number=custom_protocol_number
            ).exclude(id=submission.id).exists()
            if existing:
                messages.error(request, f'Protocol number {custom_protocol_number} already exists. Please use a different number.')
                return redirect('studies:protocol_submission_detail', submission_id=submission.id)
            protocol_number = custom_protocol_number
            submission.protocol_number = protocol_number
        else:
            # Auto-generate protocol number
            protocol_number = submission.generate_protocol_number()
        submission.approval_notes = notes
        
        # Update study
        submission.study.irb_status = 'approved'
        submission.study.irb_number = protocol_number
        submission.study.irb_approved_by = request.user
        submission.study.irb_approved_at = timezone.now()
        submission.study.irb_approval_notes = notes
        submission.study.save()
        
        messages.success(request, f'Protocol approved! Protocol number: {protocol_number}')
    
    elif decision == 'revise_resubmit':
        submission.rnr_notes = notes
        messages.info(request, 'Protocol marked for revision and resubmission.')
    
    elif decision == 'rejected':
        submission.rejection_grounds = notes
        messages.warning(request, 'Protocol rejected.')
    
    submission.save()
    
    # Send email notification to PI about decision
    from .tasks import notify_pi_about_decision
    import logging
    logger = logging.getLogger(__name__)
    try:
        notify_result = notify_pi_about_decision(submission)
        if notify_result and notify_result.startswith('Notified PI:'):
            messages.info(request, 'Principal Investigator has been notified via email.')
        elif notify_result:
            # Email not sent (not configured, no PI email, or send failed) – log for debugging
            logger.warning('PI decision notification skipped: %s', notify_result)
            if 'not configured' in notify_result.lower():
                messages.warning(request, 'Decision saved. PI was not emailed (outgoing email is not configured on this server).')
            elif 'No PI email' in notify_result:
                messages.warning(request, 'Decision saved. PI could not be notified (no email address on file).')
            else:
                messages.warning(request, 'Decision saved. PI notification could not be sent.')
    except Exception as e:
        logger.exception('PI decision notification failed')
        pass
    
    return redirect('studies:protocol_submission_detail', submission_id=submission.id)


@login_required
@require_http_methods(["POST"])
def protocol_archive(request, submission_id):
    """Archive a protocol submission (hide from default lists, preserve history)."""
    submission = get_object_or_404(ProtocolSubmission, id=submission_id)
    study = submission.study
    
    # Only PI, co-investigator, or admin/staff can archive
    is_co_i = bool(
        (request.user.email and submission.co_investigators and request.user.email.lower() in submission.co_investigators.lower())
        or submission.co_investigator_users.filter(pk=request.user.pk).exists()
    )
    can_archive = (
        request.user.is_staff or
        getattr(request.user, 'is_admin', False) or
        (request.user.is_researcher and study.researcher == request.user) or
        is_co_i
    )
    
    if not can_archive:
        messages.error(request, 'You do not have permission to archive this submission.')
        return redirect('studies:protocol_submission_detail', submission_id=submission.id)
    
    submission.is_archived = True
    submission.save(update_fields=['is_archived'])
    
    messages.success(request, f'Submission {submission.submission_number or "Draft"} archived. It will be hidden from default lists but preserved for history.')
    return redirect('studies:protocol_submission_detail', submission_id=submission.id)


@login_required
@require_http_methods(["POST"])
def protocol_unarchive(request, submission_id):
    """Unarchive a protocol submission."""
    submission = get_object_or_404(ProtocolSubmission, id=submission_id)
    study = submission.study
    
    # Only PI, co-investigator, or admin/staff can unarchive
    is_co_i = bool(
        (request.user.email and submission.co_investigators and request.user.email.lower() in submission.co_investigators.lower())
        or submission.co_investigator_users.filter(pk=request.user.pk).exists()
    )
    can_unarchive = (
        request.user.is_staff or
        getattr(request.user, 'is_admin', False) or
        (request.user.is_researcher and study.researcher == request.user) or
        is_co_i
    )
    
    if not can_unarchive:
        messages.error(request, 'You do not have permission to unarchive this submission.')
        return redirect('studies:protocol_submission_detail', submission_id=submission.id)
    
    submission.is_archived = False
    submission.save(update_fields=['is_archived'])
    
    messages.success(request, f'Submission {submission.submission_number or "Draft"} unarchived.')
    return redirect('studies:protocol_submission_detail', submission_id=submission.id)


@login_required
def protocol_submission_list(request):
    """List protocol submissions (for IRB members)."""
    if not (getattr(request.user, 'is_irb_member', False) or request.user.is_staff or getattr(request.user, 'is_admin', False)):
        messages.error(request, 'Access denied: IRB members only.')
        return redirect('home')
    
    # Get submissions user is involved with
    if request.user.is_staff or getattr(request.user, 'is_admin', False):
        submissions = ProtocolSubmission.objects.all()
    else:
        submissions = ProtocolSubmission.objects.filter(
            Q(college_rep=request.user) |
            Q(chair_reviewer=request.user) |
            Q(reviewers=request.user)
        ).distinct()
    
    # By default hide archived (duplicates); allow ?show_archived=1 to include them
    show_archived = request.GET.get('show_archived') == '1'
    if not show_archived:
        submissions = submissions.filter(is_archived=False)
    
    # Filter by status
    decision_filter = request.GET.get('decision', '')
    if decision_filter:
        submissions = submissions.filter(decision=decision_filter)
    
    # Don't select_related('study') - protocols with deleted studies would be excluded by INNER JOIN.
    # Use submission.safe_study_title in template for protocols with missing studies.
    submissions = submissions.select_related('college_rep', 'chair_reviewer').prefetch_related('reviewers').order_by('-submitted_at')

    # Backfill submission_number for any submitted protocols that never got one (e.g. created via bulk update)
    for sub_id in submissions.filter(status='submitted', submission_number__isnull=True).values_list('id', flat=True):
        try:
            obj = ProtocolSubmission.objects.get(id=sub_id)
            obj.save()
        except ProtocolSubmission.DoesNotExist:
            pass  # Deleted between filter and get; skip
    
    # Get pending amendments for the user
    if request.user.is_staff or getattr(request.user, 'is_admin', False):
        pending_amendments = ProtocolAmendment.objects.filter(decision='pending')
    else:
        pending_amendments = ProtocolAmendment.objects.filter(
            reviewer=request.user, decision='pending'
        )
    pending_amendments = pending_amendments.select_related(
        'protocol_submission', 'protocol_submission__study', 'submitted_by'
    ).order_by('-submitted_at')

    return render(request, 'studies/protocol_submission_list.html', {
        'submissions': submissions,
        'decision_choices': ProtocolSubmission.DECISION_CHOICES,
        'selected_decision': decision_filter,
        'show_archived': show_archived,
        'pending_amendments': pending_amendments,
    })


# ========== PROTOCOL AMENDMENT VIEWS ==========

@login_required
def amendment_create(request, submission_id):
    """Create an amendment for an approved protocol submission."""
    submission = get_object_or_404(ProtocolSubmission, id=submission_id)
    study = submission.study

    # Only PI, co-investigator, or admin/staff can create amendments
    is_pi = request.user.is_researcher and study.researcher == request.user
    is_co_i = bool(
        (request.user.email and submission.co_investigators and request.user.email.lower() in submission.co_investigators.lower())
        or submission.co_investigator_users.filter(pk=request.user.pk).exists()
    )
    if not (is_pi or is_co_i or request.user.is_staff or getattr(request.user, 'is_admin', False)):
        messages.error(request, 'Only the study PI or co-investigators can create amendments.')
        return redirect('studies:protocol_submission_detail', submission_id=submission.id)

    if submission.decision != 'approved':
        messages.error(request, 'Amendments can only be created for approved protocols.')
        return redirect('studies:protocol_submission_detail', submission_id=submission.id)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        justification = request.POST.get('justification', '').strip()
        amendment_type = request.POST.get('amendment_type', 'minor')
        impact_on_risk = request.POST.get('impact_on_risk', '').strip()
        impact_on_consent = request.POST.get('impact_on_consent', '').strip()
        new_instruments = request.POST.get('new_instruments', '').strip()
        instrument_url = request.POST.get('instrument_url', '').strip()
        supporting_document = request.FILES.get('supporting_document')

        if not title or not description or not justification:
            messages.error(request, 'Title, description, and justification are required.')
        else:
            amendment = ProtocolAmendment.objects.create(
                protocol_submission=submission,
                title=title,
                description=description,
                justification=justification,
                amendment_type=amendment_type,
                impact_on_risk=impact_on_risk,
                impact_on_consent=impact_on_consent,
                new_instruments=new_instruments,
                instrument_url=instrument_url,
                supporting_document=supporting_document,
                submitted_by=request.user,
                reviewer=submission.college_rep,  # Auto-assign to same college rep
            )
            # Audit log for addendum tracking (audit trail for IRB compliance)
            try:
                ip = request.META.get('REMOTE_ADDR')
                AuditLog.objects.create(
                    actor=request.user,
                    action='amendment_submitted',
                    entity='amendment',
                    entity_id=amendment.id,
                    ip_address=ip if ip and len(str(ip)) < 45 else None,
                    user_agent=(request.META.get('HTTP_USER_AGENT') or '')[:500],
                    metadata={
                        'amendment_number': amendment.amendment_number,
                        'title': amendment.title,
                        'protocol_number': submission.protocol_number,
                        'study_id': str(study.id),
                    },
                )
            except Exception:
                pass  # Don't fail amendment submission if audit log fails
            messages.success(request, f'Amendment {amendment.amendment_number} created and submitted for review.')

            # Send email notification to reviewer
            if amendment.reviewer:
                from django.core.mail import send_mail
                try:
                    send_mail(
                        subject=f'Protocol Amendment Submitted: {amendment.title}',
                        message=(
                            f'A protocol amendment has been submitted for your review.\n\n'
                            f'Protocol: {submission.protocol_number}\n'
                            f'Study: {study.title}\n'
                            f'Amendment: {amendment.amendment_number}\n'
                            f'Title: {amendment.title}\n'
                            f'Submitted by: {request.user.get_full_name()}\n\n'
                            f'Please log in to review this amendment.'
                        ),
                        from_email=None,
                        recipient_list=[amendment.reviewer.email],
                        fail_silently=True,
                    )
                except Exception:
                    pass

            return redirect('studies:amendment_detail', amendment_id=amendment.id)

    return render(request, 'studies/amendment_create.html', {
        'submission': submission,
        'study': study,
    })


@login_required
def amendment_detail(request, amendment_id):
    """View amendment details."""
    amendment = get_object_or_404(
        ProtocolAmendment.objects.select_related(
            'protocol_submission', 'protocol_submission__study',
            'protocol_submission__study__researcher',
            'submitted_by', 'reviewer',
        ),
        id=amendment_id,
    )
    submission = amendment.protocol_submission
    study = submission.study

    is_co_i = bool(
        (request.user.email and submission.co_investigators and request.user.email.lower() in submission.co_investigators.lower())
        or submission.co_investigator_users.filter(pk=request.user.pk).exists()
    )
    can_view = (
        request.user.is_staff or
        getattr(request.user, 'is_admin', False) or
        (request.user.is_researcher and study.researcher == request.user) or
        amendment.reviewer == request.user or
        submission.college_rep == request.user or
        is_co_i
    )

    if not can_view:
        messages.error(request, 'Access denied.')
        return redirect('home')

    # Only the assigned reviewer can approve/revise/reject (not PI, co-I, or other staff)
    is_reviewer = amendment.reviewer and amendment.reviewer == request.user

    return render(request, 'studies/amendment_detail.html', {
        'amendment': amendment,
        'submission': submission,
        'study': study,
        'is_reviewer': is_reviewer,
        'is_pi': request.user.is_researcher and study.researcher == request.user,
    })


@login_required
@require_http_methods(["POST"])
def amendment_review(request, amendment_id):
    """Review and make decision on an amendment. Only the assigned reviewer may submit."""
    amendment = get_object_or_404(ProtocolAmendment, id=amendment_id)

    # Only the assigned reviewer can submit a decision (not PI, co-I, or other staff)
    can_review = amendment.reviewer and amendment.reviewer == request.user

    if not can_review:
        messages.error(request, 'You do not have permission to review this amendment.')
        return redirect('studies:amendment_detail', amendment_id=amendment.id)

    if amendment.decision != 'pending':
        messages.error(request, 'This amendment has already been reviewed.')
        return redirect('studies:amendment_detail', amendment_id=amendment.id)

    decision = request.POST.get('decision')
    notes = request.POST.get('notes', '').strip()

    if decision not in ['approved', 'revise_resubmit', 'rejected']:
        messages.error(request, 'Invalid decision.')
        return redirect('studies:amendment_detail', amendment_id=amendment.id)

    amendment.decision = decision
    amendment.review_notes = notes
    amendment.reviewed_at = timezone.now()
    amendment.save()

    # Audit log for addendum review (audit trail for IRB compliance)
    try:
        ip = request.META.get('REMOTE_ADDR')
        AuditLog.objects.create(
            actor=request.user,
            action='amendment_reviewed',
            entity='amendment',
            entity_id=amendment.id,
            ip_address=ip if ip and len(str(ip)) < 45 else None,
            user_agent=(request.META.get('HTTP_USER_AGENT') or '')[:500],
            metadata={
                'amendment_number': amendment.amendment_number,
                'title': amendment.title,
                'decision': decision,
                'protocol_number': amendment.protocol_submission.protocol_number,
                'study_id': str(amendment.protocol_submission.study_id),
            },
        )
    except Exception:
        pass  # Don't fail amendment review if audit log fails

    if decision == 'approved':
        messages.success(request, f'Amendment {amendment.amendment_number} approved.')
    elif decision == 'revise_resubmit':
        messages.info(request, 'Amendment marked for revision and resubmission.')
    elif decision == 'rejected':
        messages.warning(request, 'Amendment rejected.')

    # Notify PI
    if amendment.submitted_by:
        from django.core.mail import send_mail
        try:
            send_mail(
                subject=f'Amendment {amendment.amendment_number}: {amendment.get_decision_display()}',
                message=(
                    f'Your amendment has been reviewed.\n\n'
                    f'Amendment: {amendment.amendment_number}\n'
                    f'Title: {amendment.title}\n'
                    f'Decision: {amendment.get_decision_display()}\n'
                    f'Notes: {notes or "None"}\n'
                ),
                from_email=None,
                recipient_list=[amendment.submitted_by.email],
                fail_silently=True,
            )
        except Exception:
            pass

    return redirect('studies:amendment_detail', amendment_id=amendment.id)


@login_required
def amendment_list(request, submission_id):
    """List all amendments for a protocol submission."""
    submission = get_object_or_404(ProtocolSubmission, id=submission_id)
    study = submission.study

    is_co_i = bool(
        (request.user.email and submission.co_investigators and request.user.email.lower() in submission.co_investigators.lower())
        or submission.co_investigator_users.filter(pk=request.user.pk).exists()
    )
    can_view = (
        request.user.is_staff or
        getattr(request.user, 'is_admin', False) or
        (request.user.is_researcher and study.researcher == request.user) or
        submission.college_rep == request.user or
        is_co_i
    )

    if not can_view:
        messages.error(request, 'Access denied.')
        return redirect('home')

    amendments = submission.amendments.select_related('submitted_by', 'reviewer').order_by('-submitted_at')

    return render(request, 'studies/amendment_list.html', {
        'submission': submission,
        'study': study,
        'amendments': amendments,
    })

