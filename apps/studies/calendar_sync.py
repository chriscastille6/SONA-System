"""
Helpers for one-way Google Calendar sync for study timeslots.
"""
import json
import logging

from django.conf import settings
from django.utils import timezone

from .models import Timeslot

logger = logging.getLogger(__name__)

GOOGLE_CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar"]


def google_calendar_sync_enabled():
    """Return True when Calendar sync has the minimum required config."""
    return bool(
        getattr(settings, "GOOGLE_CALENDAR_SYNC_ENABLED", False)
        and getattr(settings, "GOOGLE_CALENDAR_ID", "")
    )


def get_google_calendar_service():
    """Build an authenticated Google Calendar API client."""
    if not google_calendar_sync_enabled():
        raise RuntimeError("Google Calendar sync is disabled.")

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError as exc:
        raise RuntimeError(
            "Google Calendar sync requires google-api-python-client and google-auth."
        ) from exc

    service_account_json = getattr(settings, "GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON", "")
    service_account_file = getattr(settings, "GOOGLE_CALENDAR_SERVICE_ACCOUNT_FILE", "")

    if service_account_json:
        credentials = service_account.Credentials.from_service_account_info(
            json.loads(service_account_json),
            scopes=GOOGLE_CALENDAR_SCOPES,
        )
    elif service_account_file:
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=GOOGLE_CALENDAR_SCOPES,
        )
    else:
        raise RuntimeError(
            "Set GOOGLE_CALENDAR_SERVICE_ACCOUNT_FILE or GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON."
        )

    return build("calendar", "v3", credentials=credentials, cache_discovery=False)


def build_timeslot_event_payload(timeslot: Timeslot):
    """Build the event payload sent to Google Calendar."""
    prefix = (getattr(settings, "GOOGLE_CALENDAR_EVENT_PREFIX", "Study") or "Study").strip()
    manage_url = f"{settings.SITE_URL}/studies/researcher/{timeslot.study_id}/timeslots/"

    description_lines = [
        f"Study: {timeslot.study.title}",
        f"Capacity: {timeslot.capacity}",
        f"Active signups: {timeslot.current_signups}",
        f"Manage in SONA: {manage_url}",
    ]
    if timeslot.notes:
        description_lines.extend(["", "Internal notes:", timeslot.notes.strip()])

    return {
        "summary": f"{prefix}: {timeslot.study.title}",
        "description": "\n".join(description_lines),
        "location": timeslot.location or "",
        "start": {
            "dateTime": timeslot.starts_at.isoformat(),
            "timeZone": settings.TIME_ZONE,
        },
        "end": {
            "dateTime": timeslot.ends_at.isoformat(),
            "timeZone": settings.TIME_ZONE,
        },
    }


def _mark_sync_success(timeslot_id, event_id):
    Timeslot.objects.filter(pk=timeslot_id).update(
        google_calendar_event_id=event_id or "",
        google_calendar_last_synced_at=timezone.now(),
        google_calendar_sync_error="",
    )


def _mark_sync_error(timeslot_id, message):
    Timeslot.objects.filter(pk=timeslot_id).update(
        google_calendar_sync_error=str(message).strip(),
    )


def _clear_sync_state(timeslot_id):
    Timeslot.objects.filter(pk=timeslot_id).update(
        google_calendar_event_id="",
        google_calendar_last_synced_at=timezone.now(),
        google_calendar_sync_error="",
    )


def delete_google_calendar_event(event_id):
    """Delete a Google Calendar event by id."""
    if not google_calendar_sync_enabled():
        return {"action": "disabled"}

    if not event_id:
        return {"action": "skipped", "reason": "missing_event_id"}

    service = get_google_calendar_service()
    service.events().delete(
        calendarId=settings.GOOGLE_CALENDAR_ID,
        eventId=event_id,
        sendUpdates="none",
    ).execute()
    return {"action": "deleted", "event_id": event_id}


def sync_timeslot_to_google_calendar(timeslot: Timeslot):
    """Create, update, or delete a Calendar event for a timeslot."""
    if not google_calendar_sync_enabled():
        return {"action": "disabled"}

    service = get_google_calendar_service()

    try:
        if timeslot.is_cancelled:
            if not timeslot.google_calendar_event_id:
                return {"action": "skipped", "reason": "cancelled_without_event"}

            delete_google_calendar_event(timeslot.google_calendar_event_id)
            _clear_sync_state(timeslot.pk)
            return {"action": "deleted", "event_id": timeslot.google_calendar_event_id}

        payload = build_timeslot_event_payload(timeslot)
        events = service.events()

        if timeslot.google_calendar_event_id:
            event = events.patch(
                calendarId=settings.GOOGLE_CALENDAR_ID,
                eventId=timeslot.google_calendar_event_id,
                body=payload,
                sendUpdates="none",
            ).execute()
            _mark_sync_success(timeslot.pk, event.get("id", timeslot.google_calendar_event_id))
            return {"action": "updated", "event_id": event.get("id", timeslot.google_calendar_event_id)}

        event = events.insert(
            calendarId=settings.GOOGLE_CALENDAR_ID,
            body=payload,
            sendUpdates="none",
        ).execute()
        _mark_sync_success(timeslot.pk, event.get("id", ""))
        return {"action": "created", "event_id": event.get("id", "")}
    except Exception as exc:
        _mark_sync_error(timeslot.pk, exc)
        logger.exception("Google Calendar sync failed for timeslot %s", timeslot.pk)
        raise
