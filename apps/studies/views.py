"""
Views for studies app.
"""
from django.db.models import Prefetch, Q
from django.db import models
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.conf import settings
import json
import uuid
from .models import (
    Study,
    Timeslot,
    Signup,
    Response,
    IRBReview,
    ReviewDocument,
    IRBReviewerAssignment,
    StudyUpdate,
    ProtocolSubmission,
    CollegeRepresentative,
)
from .irb_utils import assign_college_rep, route_submission, get_irb_chair
from .tasks import (
    run_sequential_bayes_monitoring,
    run_irb_ai_review,
    notify_irb_members_about_update,
)


def user_can_access_study(user, study):
    """Determine if the given user can view protected study information."""
    if not getattr(user, 'is_authenticated', False):
        return False
    if getattr(user, 'is_admin', False) or getattr(user, 'is_staff', False):
        return True
    if getattr(user, 'is_researcher', False) and study.researcher_id == getattr(user, 'id', None):
        return True
    return study.is_assigned_reviewer(user)


def study_list(request):
    """Browse available studies."""
    studies = Study.objects.filter(is_active=True, is_approved=True)
    
    # Exclude classroom-based studies from general signup
    studies = studies.filter(is_classroom_based=False)
    
    # Filter by mode if specified
    mode = request.GET.get('mode')
    if mode in ['lab', 'online']:
        studies = studies.filter(mode=mode)
    
    # TODO: Apply eligibility filtering based on user's prescreen
    
    return render(request, 'studies/list.html', {'studies': studies})


def study_detail(request, pk):
    """Study detail view."""
    study = get_object_or_404(Study, pk=pk)
    
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
    """Book a timeslot."""
    timeslot = get_object_or_404(Timeslot, pk=pk)
    
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
    studies = Study.objects.filter(
        researcher=request.user
    ).order_by('-created_at')
    
    return render(request, 'studies/researcher_dashboard.html', {'studies': studies})


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
            messages.success(request, f'Study "{study.title}" created successfully! You can now submit it for IRB review.')
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
    
    # Check permission
    if signup.timeslot.study.researcher != request.user and not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('studies:researcher_dashboard')
    
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
    
    Tries to load templates/projects/{slug}/protocol/index.html if present,
    otherwise shows the generic placeholder.
    """
    study = get_object_or_404(Study, slug=slug)
    
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


@csrf_exempt
@require_http_methods(["POST"])
def submit_response(request, study_id):
    """
    Accept JSON protocol response submission.
    
    Expected POST body: JSON with response data
    Optional query param: session_id (otherwise generated)
    """
    try:
        study = Study.objects.get(id=study_id)
    except Study.DoesNotExist:
        return JsonResponse({'error': 'Study not found'}, status=404)
    
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
    
    # Save response
    response = Response.objects.create(
        study=study,
        session_id=session_id,
        payload=payload,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    # Trigger monitoring if enabled
    if study.monitoring_enabled:
        run_sequential_bayes_monitoring.delay(str(study.id))
    
    return JsonResponse({
        'success': True,
        'response_id': str(response.id),
        'session_id': str(response.session_id)
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
    """Create a new AI-assisted IRB review."""
    study = get_object_or_404(Study, id=study_id, researcher=request.user)
    
    if request.method == 'POST':
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
    
    # Prepare issues for display
    all_issues = [
        {'severity': 'critical', **issue} for issue in review.critical_issues
    ] + [
        {'severity': 'moderate', **issue} for issue in review.moderate_issues
    ] + [
        {'severity': 'minor', **issue} for issue in review.minor_issues
    ]
    
    return render(request, 'studies/irb_review_report.html', {
        'study': study,
        'review': review,
        'all_issues': all_issues,
        'can_edit_review': request.user.is_researcher and study.researcher == request.user,
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
def protocol_submit(request, study_id):
    """PI submits protocol for IRB review."""
    from .forms import ProtocolSubmissionForm
    
    study = get_object_or_404(Study, id=study_id)
    
    # Only study owner can submit (or admin/staff)
    if not (request.user.is_researcher and study.researcher == request.user) and not (request.user.is_admin or request.user.is_staff):
        messages.error(request, 'Only the study owner can submit protocols.')
        return redirect('studies:detail', pk=study.id)
    
    existing_submission = ProtocolSubmission.objects.filter(study=study).order_by('-version').first()
    
    if request.method == 'POST':
        form = ProtocolSubmissionForm(request.POST)
        if form.is_valid():
            # Get AI review preference before saving
            use_ai_review = form.cleaned_data.pop('use_ai_review', False)
            
            # Create submission with all form data
            submission = form.save(commit=False)
            submission.study = study
            submission.submitted_by = request.user
            submission.review_type = submission.pi_suggested_review_type  # Initial, may change
            submission.save()
            
            # Update study deception flag
            study.involves_deception = submission.involves_deception
            study.save(update_fields=['involves_deception'])
            
            # Assign college rep
            assign_college_rep(submission)
            
            # Route submission
            route_submission(submission)
            
            # Optionally trigger AI review
            if use_ai_review:
                if getattr(settings, 'AI_REVIEW_ENABLED', False):
                    # Create AI review
                    ai_review = IRBReview.objects.create(
                        study=study,
                        initiated_by=request.user,
                    )
                    submission.ai_review = ai_review
                    submission.save(update_fields=['ai_review'])
                    run_irb_ai_review.delay(str(ai_review.id))
                    messages.info(request, 'AI review initiated. You will be notified when complete.')
                else:
                    messages.warning(request, 'AI review is not currently enabled. Protocol submitted without AI review.')
            
            messages.success(
                request,
                f'Protocol submitted successfully (Submission #{submission.submission_number}). '
                f'Your college representative will review it shortly.'
            )
            return redirect('studies:protocol_submission_detail', submission_id=submission.id)
    else:
        # Pre-fill form with existing submission data if available
        initial_data = {}
        if existing_submission:
            for field in ProtocolSubmissionForm.Meta.fields:
                if hasattr(existing_submission, field):
                    value = getattr(existing_submission, field)
                    if value:  # Only include non-empty values
                        initial_data[field] = value
        form = ProtocolSubmissionForm(initial=initial_data)
    
    return render(request, 'studies/protocol_submit.html', {
        'study': study,
        'form': form,
        'existing_submission': existing_submission,
        'ai_review_enabled': getattr(settings, 'AI_REVIEW_ENABLED', False),
    })


@login_required
def protocol_submission_detail(request, submission_id):
    """View protocol submission details."""
    submission = get_object_or_404(ProtocolSubmission, id=submission_id)
    study = submission.study
    
    # Check access
    can_view = (
        request.user.is_staff or
        getattr(request.user, 'is_admin', False) or
        (request.user.is_researcher and study.researcher == request.user) or
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
    
    return render(request, 'studies/protocol_submission_detail.html', {
        'submission': submission,
        'study': study,
        'is_pi': request.user.is_researcher and study.researcher == request.user,
        'is_college_rep': submission.college_rep == request.user,
        'is_chair': submission.chair_reviewer == request.user,
        'is_reviewer': submission.reviewers.filter(id=request.user.id).exists(),
        'irb_members': irb_members,
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
    notes = request.POST.get('notes', '')
    
    if determination not in ['exempt', 'expedited', 'full']:
        messages.error(request, 'Invalid determination.')
        return redirect('studies:protocol_submission_detail', submission_id=submission.id)
    
    submission.college_rep_determination = determination
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
        # Generate protocol number
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
    
    # Filter by status
    decision_filter = request.GET.get('decision', '')
    if decision_filter:
        submissions = submissions.filter(decision=decision_filter)
    
    submissions = submissions.select_related('study', 'study__researcher', 'college_rep', 'chair_reviewer').prefetch_related('reviewers').order_by('-submitted_at')
    
    return render(request, 'studies/protocol_submission_list.html', {
        'submissions': submissions,
        'decision_choices': ProtocolSubmission.DECISION_CHOICES,
        'selected_decision': decision_filter,
    })



