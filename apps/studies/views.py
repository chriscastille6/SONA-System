"""
Views for studies app.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
import json
import uuid
from .models import Study, Timeslot, Signup, Response
from .tasks import run_sequential_bayes_monitoring


def study_list(request):
    """Browse available studies."""
    studies = Study.objects.filter(is_active=True, is_approved=True)
    
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
    """Researcher dashboard."""
    if not request.user.is_researcher:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    studies = Study.objects.filter(researcher=request.user).order_by('-created_at')
    
    return render(request, 'studies/researcher_dashboard.html', {'studies': studies})


@login_required
def create_study(request):
    """Create new study."""
    if not request.user.is_researcher:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        # TODO: Implement study creation form
        messages.success(request, 'Study created successfully!')
        return redirect('studies:researcher_dashboard')
    
    return render(request, 'studies/create.html')


@login_required
def edit_study(request, pk):
    """Edit study."""
    study = get_object_or_404(Study, pk=pk, researcher=request.user)
    
    if request.method == 'POST':
        # TODO: Implement study editing
        messages.success(request, 'Study updated successfully!')
        return redirect('studies:researcher_dashboard')
    
    return render(request, 'studies/edit.html', {'study': study})


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
    if request.user.is_authenticated:
        if request.user.is_researcher and study.researcher == request.user:
            pass  # Authorized
        elif request.user.is_admin:
            pass  # Authorized
        else:
            messages.error(request, 'Access denied.')
            return redirect('studies:list')
    else:
        messages.error(request, 'Please log in.')
        return redirect('accounts:login')
    
    # Get recent responses for display
    recent_responses = study.responses.order_by('-created_at')[:10]
    
    return render(request, 'studies/status.html', {
        'study': study,
        'recent_responses': recent_responses,
    })




