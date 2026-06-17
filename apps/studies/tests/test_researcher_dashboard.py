from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.studies.irb_utils import studies_for_researcher_dashboard
from apps.studies.models import ProtocolSubmission, Study


class ResearcherDashboardSortTests(TestCase):
    def setUp(self):
        self.researcher = User.objects.create_user(
            email='researcher@example.com',
            password='password123',
            first_name='Res',
            last_name='Earcher',
            role='researcher',
        )
        self.older_study = Study.objects.create(
            title='Older Study',
            slug='older-study',
            description='Created earlier.',
            mode='online',
            researcher=self.researcher,
            credit_value=1.0,
            consent_text='Consent.',
        )
        Study.objects.filter(pk=self.older_study.pk).update(
            created_at=timezone.now() - timedelta(days=30),
            updated_at=timezone.now() - timedelta(days=30),
        )
        self.newer_study = Study.objects.create(
            title='Newer Study',
            slug='newer-study',
            description='Created recently.',
            mode='online',
            researcher=self.researcher,
            credit_value=1.0,
            consent_text='Consent.',
        )

    def test_queryset_orders_by_study_updated_at_by_default(self):
        ordered = list(studies_for_researcher_dashboard(self.researcher))
        self.assertEqual(ordered[0], self.newer_study)
        self.assertEqual(ordered[1], self.older_study)

    def test_queryset_bumps_study_with_recent_protocol_activity(self):
        ProtocolSubmission.objects.create(
            study=self.older_study,
            status='submitted',
            submitted_at=timezone.now(),
            pi_suggested_review_type='exempt',
            review_type='exempt',
            submitted_by=self.researcher,
        )
        ordered = list(studies_for_researcher_dashboard(self.researcher))
        self.assertEqual(ordered[0], self.older_study)
        self.assertEqual(ordered[1], self.newer_study)

    def test_dashboard_renders_studies_in_last_worked_on_order(self):
        ProtocolSubmission.objects.create(
            study=self.older_study,
            status='submitted',
            submitted_at=timezone.now(),
            pi_suggested_review_type='exempt',
            review_type='exempt',
            submitted_by=self.researcher,
        )
        self.client.login(email=self.researcher.email, password='password123')
        response = self.client.get(reverse('studies:researcher_dashboard'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertLess(content.index('Older Study'), content.index('Newer Study'))
