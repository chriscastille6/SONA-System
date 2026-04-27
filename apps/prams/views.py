"""
PRAMS API and catalog SPA — FERPA compliant. No PII in request/response.
"""
import json
import os
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import PRAMSStudy, PRAMSSignup


def _study_to_json(study):
    """Serialize a PRAMSStudy with dynamic available_slots (no PII)."""
    return {
        'id': str(study.id),
        'title': study.title,
        'description': study.description or '',
        'datetime': study.datetime.isoformat() if study.datetime else None,
        'max_capacity': study.max_capacity,
        'available_slots': study.available_slots,
        'bookings_service_id': study.bookings_service_id or None,
    }


@require_http_methods(['GET'])
def study_list(request):
    """
    GET /api/studies
    Returns all studies with available_slots = max_capacity - current signup count.
    """
    now = timezone.now()
    studies = PRAMSStudy.objects.filter(datetime__gte=now).order_by('datetime')
    payload = [_study_to_json(s) for s in studies]
    return JsonResponse({'studies': payload})


@method_decorator(csrf_exempt, name='dispatch')
class SignupView(View):
    """
    POST: create signup. Body: { "study_id": "uuid", "participant_secure_id": "string" }.
    Returns success with cancellation_pin and study details.
    DELETE: cancel signup. Body: { "study_id": "uuid", "participant_secure_id": "string", "cancellation_pin": "1234" }.
    """

    def post(self, request):
        try:
            body = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        study_id = body.get('study_id')
        participant_secure_id = (body.get('participant_secure_id') or '').strip()
        if not study_id or not participant_secure_id:
            return JsonResponse(
                {'error': 'study_id and participant_secure_id are required'},
                status=400
            )
        with transaction.atomic():
            study = PRAMSStudy.objects.select_for_update().filter(id=study_id).first()
            if not study:
                return JsonResponse({'error': 'Study not found'}, status=404)
            if study.available_slots <= 0:
                return JsonResponse({'error': 'No slots available'}, status=409)
            if PRAMSSignup.objects.filter(study=study, participant_secure_id=participant_secure_id).exists():
                return JsonResponse({'error': 'Already signed up for this study'}, status=409)
            signup = PRAMSSignup(
                study=study,
                participant_secure_id=participant_secure_id,
            )
            signup.save()
            return JsonResponse({
                'success': True,
                'message': 'Booking confirmed.',
                'cancellation_pin': signup.cancellation_pin,
                'study': _study_to_json(study),
            }, status=201)

    def delete(self, request):
        try:
            body = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        study_id = body.get('study_id')
        participant_secure_id = (body.get('participant_secure_id') or '').strip()
        cancellation_pin = (body.get('cancellation_pin') or '').strip()
        if not study_id or not participant_secure_id or not cancellation_pin:
            return JsonResponse(
                {'error': 'study_id, participant_secure_id, and cancellation_pin are required'},
                status=400
            )
        signup = PRAMSSignup.objects.filter(
            study_id=study_id,
            participant_secure_id=participant_secure_id,
            cancellation_pin=cancellation_pin,
        ).first()
        if not signup:
            return JsonResponse({'error': 'Signup not found or PIN invalid'}, status=404)
        signup.delete()
        return JsonResponse({'success': True, 'message': 'Signup cancelled.'})


def _format_ical_datetime(dt):
    """Format datetime for iCal (UTC)."""
    return dt.strftime('%Y%m%dT%H%M%SZ') if dt else ''


@require_http_methods(['GET'])
def study_ical(request, study_id):
    """
    GET /api/studies/<id>/ical/
    Returns a .ics calendar file for the study (title, datetime). No PII.
    """
    study = get_object_or_404(PRAMSStudy, id=study_id)
    dt = study.datetime
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt)
    dt_utc = dt.astimezone(timezone.utc)
    end_utc = dt_utc + timezone.timedelta(hours=1)  # 1-hour default duration
    title_esc = (study.title or 'Study').replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,')
    ics = (
        'BEGIN:VCALENDAR\r\n'
        'VERSION:2.0\r\n'
        'PRODID:-//PRAMS//Study Calendar//EN\r\n'
        'BEGIN:VEVENT\r\n'
        f'UID:prams-study-{study.id}@prams\r\n'
        f'DTSTAMP:{_format_ical_datetime(timezone.now())}\r\n'
        f'DTSTART:{_format_ical_datetime(dt_utc)}\r\n'
        f'DTEND:{_format_ical_datetime(end_utc)}\r\n'
        f'SUMMARY:{title_esc}\r\n'
        f'DESCRIPTION:PRAMS study - {title_esc}\r\n'
        'END:VEVENT\r\n'
        'END:VCALENDAR\r\n'
    )
    response = HttpResponse(ics, content_type='text/calendar; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="prams-study-{study.id}.ics"'
    return response


def catalog_spa(request):
    """
    Serve the PRAMS catalog SPA (React app).
    Build the frontend first: cd prams_frontend && npm run build
    """
    index_path = os.path.join(
        settings.BASE_DIR, 'apps', 'prams', 'static', 'prams', 'index.html'
    )
    if not os.path.isfile(index_path):
        return HttpResponseNotFound(
            '<p>PRAMS catalog not built. Run: <code>cd prams_frontend && npm install && npm run build</code></p>'
        )
    with open(index_path, 'r') as f:
        return HttpResponse(f.read(), content_type='text/html')
