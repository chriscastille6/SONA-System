from django.core import mail
from django.urls import reverse
from django.core.management import call_command
from io import StringIO
from django.test import TestCase, override_settings
from django.utils import timezone

from apps.accounts.models import User
from apps.studies.models import (
    IRBReview,
    IRBReviewerAssignment,
    Study,
    StudyUpdate,
)
from apps.studies.tasks import notify_irb_members_about_update, notify_irb_members_about_review


class IRBNotificationTests(TestCase):
    def setUp(self):
        self.researcher = User.objects.create_user(
            email='researcher@example.com',
            password='password123',
            first_name='Res',
            last_name='Earcher',
            role='researcher',
        )
        self.irb_member = User.objects.create_user(
            email='irb@example.com',
            password='password123',
            first_name='Irb',
            last_name='Member',
            role='irb_member',
        )
        self.study = Study.objects.create(
            title='Conjoint Analysis Pilot',
            slug='conjoint-analysis-pilot',
            description='Test study for IRB notifications.',
            mode='online',
            researcher=self.researcher,
            credit_value=1.0,
            consent_text='Sample consent text.',
        )
        IRBReviewerAssignment.objects.create(
            study=self.study,
            reviewer=self.irb_member,
        )

    def test_is_assigned_reviewer_helper(self):
        """Study helper should recognize assigned IRB members."""
        self.assertTrue(self.study.is_assigned_reviewer(self.irb_member))
        another_member = User.objects.create_user(
            email='other-irb@example.com',
            password='password123',
            first_name='Other',
            last_name='Reviewer',
            role='irb_member',
        )
        self.assertFalse(self.study.is_assigned_reviewer(another_member))

    def test_irb_member_can_toggle_email_preferences(self):
        assignment = self.study.reviewer_assignments.get(reviewer=self.irb_member)
        self.assertTrue(assignment.receive_email_updates)
        self.client.login(email=self.irb_member.email, password='password123')
        toggle_url = reverse('studies:irb_toggle_email', args=[assignment.id])
        response = self.client.post(toggle_url, follow=True)
        self.assertEqual(response.status_code, 200)
        assignment.refresh_from_db()
        self.assertFalse(assignment.receive_email_updates)
        # Toggle back on
        response = self.client.post(toggle_url, follow=True)
        self.assertEqual(response.status_code, 200)
        assignment.refresh_from_db()
        self.assertTrue(assignment.receive_email_updates)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', EMAIL_HOST='localhost')
    def test_update_notification_emails_irb_members(self):
        """Posting a study update should notify subscribed IRB reviewers."""
        update = StudyUpdate.objects.create(
            study=self.study,
            author=self.researcher,
            visibility='irb',
            message='Protocol draft uploaded for review.',
        )
        response = notify_irb_members_about_update(update)
        self.assertIn('Notified 1 IRB reviewers', response)
        update.refresh_from_db()
        self.assertIsNotNone(update.notified_at)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['irb@example.com'])

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', EMAIL_HOST='localhost')
    def test_ai_review_completion_notifies_irb_members(self):
        """Completed AI reviews should send summary emails to IRB reviewers."""
        review = IRBReview.objects.create(
            study=self.study,
            initiated_by=self.researcher,
            status='completed',
            version=1,
            overall_risk_level='low',
            critical_issues=[],
            moderate_issues=[],
            minor_issues=[],
        )
        # Manually set timestamps expected by notify helper
        review.initiated_at = timezone.now()
        review.save(update_fields=['initiated_at'])
        response = notify_irb_members_about_review(review)
        self.assertIn('IRB reviewers', response)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['irb@example.com'])

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', EMAIL_HOST='localhost')
    def test_send_irb_test_email_command(self):
        """Management command should trigger a test email to reviewers."""
        out = StringIO()
        call_command('send_irb_test_email', self.study.slug, stdout=out)
        self.assertIn('Notified 1 IRB reviewers', out.getvalue())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['irb@example.com'])

