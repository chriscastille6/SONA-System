from datetime import timedelta
from unittest.mock import patch

from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone

from apps.accounts.models import User
from apps.studies.calendar_sync import sync_timeslot_to_google_calendar
from apps.studies.models import Signup, Study, Timeslot
from apps.studies.tasks import send_24h_reminders, send_2h_reminders


class StudySchedulingIntegrationTests(TestCase):
    def setUp(self):
        self.researcher = User.objects.create_user(
            email="researcher@example.com",
            password="password123",
            first_name="Res",
            last_name="Earcher",
            role="researcher",
        )
        self.participant = User.objects.create_user(
            email="participant@example.com",
            password="password123",
            first_name="Pat",
            last_name="Icipant",
            role="participant",
        )
        self.participant.profile.phone = "+19855550123"
        self.participant.profile.save(update_fields=["phone"])

        self.study = Study.objects.create(
            title="Reminder Study",
            slug="reminder-study",
            description="Test study for scheduling integrations.",
            mode="in_person",
            researcher=self.researcher,
            credit_value=1.0,
            duration_minutes=30,
            consent_text="Sample consent text.",
        )

    def create_signup(self, starts_at, **signup_kwargs):
        timeslot = Timeslot.objects.create(
            study=self.study,
            starts_at=starts_at,
            ends_at=starts_at + timedelta(minutes=30),
            capacity=3,
            location="Powell Hall 101",
        )
        return Signup.objects.create(
            timeslot=timeslot,
            participant=self.participant,
            consent_text_version=self.study.consent_text,
            **signup_kwargs,
        )

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        STUDY_SMS_REMINDERS_ENABLED=True,
    )
    @patch("apps.studies.tasks.send_signup_sms")
    def test_send_24h_reminders_sends_email_and_sms(self, mock_send_sms):
        mock_send_sms.return_value = {"sent": True, "to": "+19855550123"}
        signup = self.create_signup(timezone.now() + timedelta(hours=24))

        result = send_24h_reminders()

        signup.refresh_from_db()
        self.assertIn("24-hour email reminders", result)
        self.assertTrue(signup.reminder_24h_sent)
        self.assertTrue(signup.reminder_24h_sms_sent)
        self.assertEqual(len(mail.outbox), 1)
        mock_send_sms.assert_called_once_with(signup, "24h")

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        STUDY_SMS_REMINDERS_ENABLED=True,
    )
    @patch("apps.studies.tasks.send_signup_sms")
    def test_send_24h_reminders_can_finish_pending_sms_after_email(self, mock_send_sms):
        mock_send_sms.return_value = {"sent": True, "to": "+19855550123"}
        signup = self.create_signup(
            timezone.now() + timedelta(hours=24),
            reminder_24h_sent=True,
        )

        send_24h_reminders()

        signup.refresh_from_db()
        self.assertTrue(signup.reminder_24h_sent)
        self.assertTrue(signup.reminder_24h_sms_sent)
        self.assertEqual(len(mail.outbox), 0)
        mock_send_sms.assert_called_once_with(signup, "24h")

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        STUDY_SMS_REMINDERS_ENABLED=True,
    )
    @patch("apps.studies.tasks.send_signup_sms")
    def test_send_2h_reminders_sends_email_and_sms(self, mock_send_sms):
        mock_send_sms.return_value = {"sent": True, "to": "+19855550123"}
        signup = self.create_signup(timezone.now() + timedelta(hours=2))

        result = send_2h_reminders()

        signup.refresh_from_db()
        self.assertIn("2-hour email reminders", result)
        self.assertTrue(signup.reminder_2h_sent)
        self.assertTrue(signup.reminder_2h_sms_sent)
        self.assertEqual(len(mail.outbox), 1)
        mock_send_sms.assert_called_once_with(signup, "2h")

    @override_settings(
        GOOGLE_CALENDAR_SYNC_ENABLED=True,
        GOOGLE_CALENDAR_ID="research-studies@example.com",
    )
    @patch("apps.studies.calendar_sync.get_google_calendar_service")
    def test_calendar_sync_creates_event_and_stores_event_id(self, mock_get_service):
        timeslot = Timeslot.objects.create(
            study=self.study,
            starts_at=timezone.now() + timedelta(days=1),
            ends_at=timezone.now() + timedelta(days=1, minutes=30),
            capacity=4,
            location="White Hall 201",
        )

        events_api = mock_get_service.return_value.events.return_value
        events_api.insert.return_value.execute.return_value = {"id": "evt-123"}

        result = sync_timeslot_to_google_calendar(timeslot)

        timeslot.refresh_from_db()
        self.assertEqual(result["action"], "created")
        self.assertEqual(timeslot.google_calendar_event_id, "evt-123")
        self.assertIsNotNone(timeslot.google_calendar_last_synced_at)
        self.assertEqual(timeslot.google_calendar_sync_error, "")

    @override_settings(
        GOOGLE_CALENDAR_SYNC_ENABLED=True,
        GOOGLE_CALENDAR_ID="research-studies@example.com",
    )
    @patch("apps.studies.calendar_sync.get_google_calendar_service")
    def test_calendar_sync_deletes_event_for_cancelled_timeslot(self, mock_get_service):
        timeslot = Timeslot.objects.create(
            study=self.study,
            starts_at=timezone.now() + timedelta(days=1),
            ends_at=timezone.now() + timedelta(days=1, minutes=30),
            capacity=4,
            location="White Hall 201",
            google_calendar_event_id="evt-123",
        )
        Timeslot.objects.filter(pk=timeslot.pk).update(is_cancelled=True)
        timeslot.refresh_from_db()

        events_api = mock_get_service.return_value.events.return_value
        events_api.delete.return_value.execute.return_value = {}

        result = sync_timeslot_to_google_calendar(timeslot)

        timeslot.refresh_from_db()
        self.assertEqual(result["action"], "deleted")
        self.assertEqual(timeslot.google_calendar_event_id, "")
        self.assertEqual(timeslot.google_calendar_sync_error, "")
