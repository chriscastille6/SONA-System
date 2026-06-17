from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from apps.accounts.models import User
from apps.studies.goal_setting_study import GOAL_SETTING_STUDY_SLUG, GOAL_SETTING_STUDY_SLUG_LEGACY
from apps.studies.models import AnonymousSignup, Study, Timeslot


class GoalSettingSignupQrTests(TestCase):
    def setUp(self):
        self.researcher = User.objects.create_user(
            email='researcher@example.com',
            password='password123',
            first_name='Res',
            last_name='Earcher',
            role='researcher',
        )
        self.study = Study.objects.create(
            title='A Study in Decision Making',
            slug=GOAL_SETTING_STUDY_SLUG,
            description='Goal setting study.',
            mode='lab',
            researcher=self.researcher,
            credit_value=0,
            consent_text='Consent.',
            is_active=True,
            is_approved=True,
            irb_status='approved',
            allows_anonymous_booking=True,
        )
        starts = timezone.now() + timedelta(days=2)
        self.timeslot = Timeslot.objects.create(
            study=self.study,
            starts_at=starts,
            ends_at=starts + timedelta(hours=1),
            capacity=5,
        )

    def test_public_signup_landing_no_login(self):
        url = reverse('studies:public_study_signup', kwargs={'slug': GOAL_SETTING_STUDY_SLUG})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No account required')
        self.assertContains(response, 'Sign Up')
        self.assertNotContains(response, 'Log in')

    def test_signup_count_json(self):
        AnonymousSignup.objects.create(
            timeslot=self.timeslot,
            consent_text_version=self.study.consent_text,
        )
        url = reverse('studies:public_study_signup_count', kwargs={'slug': GOAL_SETTING_STUDY_SLUG})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['total_signups'], 1)
        self.assertEqual(data['anonymous_signups'], 1)

    def test_qr_png_endpoint(self):
        url = reverse('studies:public_study_signup_qr', kwargs={'slug': GOAL_SETTING_STUDY_SLUG})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')
        self.assertTrue(response.content.startswith(b'\x89PNG'))

    def test_legacy_goal_setting_slug_redirects(self):
        url = '/studies/signup/goal-setting/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 301)
        self.assertIn(GOAL_SETTING_STUDY_SLUG, response['Location'])

    def test_study_total_signups_includes_anonymous(self):
        AnonymousSignup.objects.create(
            timeslot=self.timeslot,
            consent_text_version=self.study.consent_text,
        )
        self.assertEqual(self.study.total_signups, 1)
