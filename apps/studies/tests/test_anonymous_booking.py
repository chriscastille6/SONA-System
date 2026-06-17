from datetime import timedelta
from unittest.mock import patch

from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.credits.models import AuditLog
from apps.studies.models import AnonymousSignup, Study, Timeslot


class AnonymousBookingTests(TestCase):
    def setUp(self):
        self.researcher = User.objects.create_user(
            email='researcher@example.com',
            password='password123',
            first_name='Res',
            last_name='Earcher',
            role='researcher',
        )
        self.study = Study.objects.create(
            title='Anonymous Lab Study',
            slug='anonymous-lab-study',
            description='Test study.',
            mode='lab',
            researcher=self.researcher,
            credit_value=0,
            consent_text='You agree to participate.',
            is_active=True,
            is_approved=True,
            irb_status='approved',
            allows_anonymous_booking=True,
        )
        self.other_study = Study.objects.create(
            title='Account Required Study',
            slug='account-required-study',
            description='Needs login.',
            mode='lab',
            researcher=self.researcher,
            credit_value=1,
            consent_text='Consent.',
            is_active=True,
            is_approved=True,
            irb_status='approved',
            allows_anonymous_booking=False,
        )
        starts = timezone.now() + timedelta(days=2)
        self.timeslot = Timeslot.objects.create(
            study=self.study,
            starts_at=starts,
            ends_at=starts + timedelta(hours=1),
            capacity=2,
            location='Room 101',
        )
        self.full_timeslot = Timeslot.objects.create(
            study=self.study,
            starts_at=starts + timedelta(hours=2),
            ends_at=starts + timedelta(hours=3),
            capacity=1,
            location='Room 102',
        )
        AnonymousSignup.objects.create(
            timeslot=self.full_timeslot,
            consent_text_version=self.study.consent_text,
            cancellation_pin='1234',
        )
        other_starts = timezone.now() + timedelta(days=2)
        self.other_timeslot = Timeslot.objects.create(
            study=self.other_study,
            starts_at=other_starts,
            ends_at=other_starts + timedelta(hours=1),
            capacity=1,
        )

    def test_detail_shows_anonymous_sign_up_buttons(self):
        response = self.client.get(reverse('studies:detail', args=[self.study.id]))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('Sign Up', content)
        self.assertIn('No account required', content)
        self.assertNotIn('Log in', content)

    @override_settings(CANCELLATION_WINDOW_HOURS=24)
    def test_anonymous_confirm_shows_cancellation_window_hours(self):
        url = reverse('studies:anonymous_book_timeslot', args=[self.timeslot.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('cancel up to 24 hours before', response.content.decode())
        self.assertNotIn('up to  hours before', response.content.decode())

    def test_detail_without_flag_requires_login(self):
        response = self.client.get(reverse('studies:detail', args=[self.other_study.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Log in', response.content.decode())

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        EMAIL_HOST='localhost',
        SITE_URL='http://testserver',
        SITE_NAME='Test PRAMS',
    )
    def test_anonymous_booking_creates_signup_and_notifies_researcher(self):
        mail.outbox.clear()
        url = reverse('studies:anonymous_book_timeslot', args=[self.timeslot.id])
        response = self.client.post(url, follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(AnonymousSignup.objects.filter(timeslot=self.timeslot, status='booked').count(), 1)
        self.assertEqual(self.timeslot.available_capacity, 1)
        anonymous_mails = [m for m in mail.outbox if 'Anonymous slot booked' in m.subject]
        self.assertEqual(len(anonymous_mails), 1)
        self.assertIn('Room 101', anonymous_mails[0].body)
        self.assertNotIn('@example.com', anonymous_mails[0].body)

    def test_full_timeslot_rejects_booking(self):
        url = reverse('studies:anonymous_book_timeslot', args=[self.full_timeslot.id])
        response = self.client.post(url, follow=True)
        self.assertEqual(AnonymousSignup.objects.filter(timeslot=self.full_timeslot).count(), 1)
        messages = [m.message for m in response.context['messages']]
        self.assertTrue(any('full' in m.lower() for m in messages))

    def test_timeslot_ical_download(self):
        url = reverse('studies:timeslot_ical', args=[self.timeslot.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/calendar; charset=utf-8')
        body = response.content.decode()
        self.assertIn('BEGIN:VCALENDAR', body)
        self.assertIn('Anonymous Lab Study', body)

    def test_cancel_with_valid_reference_and_pin(self):
        signup = AnonymousSignup.objects.create(
            timeslot=self.timeslot,
            consent_text_version=self.study.consent_text,
            cancellation_pin='5678',
        )
        url = reverse('studies:anonymous_cancel_signup')
        response = self.client.post(url, {
            'booking_reference': str(signup.booking_reference),
            'cancellation_pin': '5678',
        }, follow=True)
        signup.refresh_from_db()
        self.assertEqual(signup.status, 'cancelled')
        self.assertEqual(self.timeslot.available_capacity, 2)

    def test_cancel_with_invalid_pin_fails(self):
        signup = AnonymousSignup.objects.create(
            timeslot=self.timeslot,
            consent_text_version=self.study.consent_text,
            cancellation_pin='5678',
        )
        url = reverse('studies:anonymous_cancel_signup')
        self.client.post(url, {
            'booking_reference': str(signup.booking_reference),
            'cancellation_pin': '0000',
        })
        signup.refresh_from_db()
        self.assertEqual(signup.status, 'booked')

    @patch('apps.studies.tasks.send_mail')
    def test_notification_skipped_when_email_not_configured(self, mock_send_mail):
        with self.settings(EMAIL_HOST=''):
            url = reverse('studies:anonymous_book_timeslot', args=[self.timeslot.id])
            self.client.post(url)
        mock_send_mail.assert_not_called()

    def test_booking_writes_audit_log_with_ip(self):
        url = reverse('studies:anonymous_book_timeslot', args=[self.timeslot.id])
        self.client.post(url, REMOTE_ADDR='203.0.113.10')
        log = AuditLog.objects.filter(action='anonymous_signup').latest('created_at')
        self.assertEqual(log.ip_address, '203.0.113.10')
        self.assertNotIn('participant', str(log.metadata).lower())

    @override_settings(
        ANONYMOUS_BOOKING_RATE_LIMIT_BOOK=1,
        ANONYMOUS_BOOKING_RATE_LIMIT_BOOK_WINDOW=3600,
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            }
        },
    )
    def test_booking_rate_limit_returns_403(self):
        cache.clear()
        url = reverse('studies:anonymous_book_timeslot', args=[self.timeslot.id])
        self.assertEqual(self.client.post(url).status_code, 302)
        starts = timezone.now() + timedelta(days=3)
        second_slot = Timeslot.objects.create(
            study=self.study,
            starts_at=starts,
            ends_at=starts + timedelta(hours=1),
            capacity=1,
        )
        url2 = reverse('studies:anonymous_book_timeslot', args=[second_slot.id])
        self.assertEqual(self.client.post(url2).status_code, 403)

    def test_booking_success_page_shows_reference_and_pin(self):
        url = reverse('studies:anonymous_book_timeslot', args=[self.timeslot.id])
        self.client.post(url)
        success_url = reverse('studies:anonymous_booking_success')
        response = self.client.get(success_url, follow=True)
        self.assertEqual(response.status_code, 200)
        signup = AnonymousSignup.objects.get(timeslot=self.timeslot)
        content = response.content.decode()
        self.assertIn(str(signup.booking_reference), content)
        self.assertIn(signup.cancellation_pin, content)
