"""
SMS helpers for study reminder tasks.
"""
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def sms_reminders_enabled():
    return bool(getattr(settings, "STUDY_SMS_REMINDERS_ENABLED", False))


def get_signup_phone_number(signup):
    profile = getattr(signup.participant, "profile", None)
    phone = getattr(profile, "phone", "") if profile else ""
    return (phone or "").strip()


def build_signup_sms_message(signup, reminder_type):
    study_title = signup.timeslot.study.title
    location = signup.timeslot.location or "See study details"
    cancel_url = f"{settings.SITE_URL}/studies/signup/{signup.id}/cancel/"
    participant_name = signup.participant.first_name or "there"

    if reminder_type == "24h":
        when_text = signup.timeslot.starts_at.strftime("%a %b %d at %I:%M %p")
        return (
            f"Hi {participant_name}, reminder: your study \"{study_title}\" is tomorrow at "
            f"{when_text}. Location: {location}. Cancel if needed: {cancel_url}"
        )

    when_text = signup.timeslot.starts_at.strftime("%I:%M %p")
    return (
        f"Hi {participant_name}, reminder: your study \"{study_title}\" starts in 2 hours at "
        f"{when_text}. Location: {location}. If you cannot attend, contact the researcher right away."
    )


def send_signup_sms(signup, reminder_type):
    """Send a study reminder text message."""
    if not sms_reminders_enabled():
        return {"sent": False, "reason": "disabled"}

    phone_number = get_signup_phone_number(signup)
    if not phone_number:
        return {"sent": False, "reason": "missing_phone"}

    provider = (getattr(settings, "STUDY_SMS_PROVIDER", "twilio") or "twilio").lower()
    if provider != "twilio":
        raise RuntimeError(f"Unsupported SMS provider: {provider}")

    account_sid = getattr(settings, "TWILIO_ACCOUNT_SID", "")
    auth_token = getattr(settings, "TWILIO_AUTH_TOKEN", "")
    from_number = getattr(settings, "TWILIO_FROM_NUMBER", "")
    if not account_sid or not auth_token or not from_number:
        raise RuntimeError("Twilio SMS reminders require SID, auth token, and from number.")

    try:
        from twilio.rest import Client
    except ImportError as exc:
        raise RuntimeError("SMS reminders require the twilio package.") from exc

    body = build_signup_sms_message(signup, reminder_type)
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=body,
        from_=from_number,
        to=phone_number,
    )
    logger.info("Sent %s SMS reminder for signup %s", reminder_type, signup.pk)
    return {"sent": True, "sid": getattr(message, "sid", ""), "to": phone_number}
