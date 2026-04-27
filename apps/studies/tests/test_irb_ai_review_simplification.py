"""
Tests for SONA AI Review Simplification: submitted protocol + consent to AI without file upload.
"""
from django.test import TestCase
from django.urls import reverse

from django.contrib.auth import get_user_model

from apps.studies.models import (
    Study,
    IRBReview,
    ProtocolSubmission,
)
from apps.studies.irb_ai.analyzer import IRBAnalyzer
from apps.studies.views import _get_informed_consent_display


User = get_user_model()


class IRBReviewSimplificationTests(TestCase):
    """Validate submitted protocol and consent are gathered for AI without file upload."""

    def setUp(self):
        self.researcher = User.objects.create_user(
            email='pi@test.com',
            password='testpass123',
            first_name='PI',
            last_name='Test',
            role='researcher',
        )
        self.study = Study.objects.create(
            title='Validation Study',
            slug='validation-study',
            description='Study for AI review simplification tests.',
            mode='online',
            researcher=self.researcher,
            credit_value=1.0,
            consent_text='',  # empty; we use inferred consent from submission
        )

    def test_get_submitted_protocol_and_consent_with_linked_submission(self):
        """When a submission is linked to the review via ai_review, it is used."""
        review = IRBReview.objects.create(
            study=self.study,
            initiated_by=self.researcher,
        )
        submission = ProtocolSubmission.objects.create(
            study=self.study,
            status='submitted',
            pi_suggested_review_type='exempt',
            review_type='exempt',
            protocol_description='We will survey students.',
            research_procedures='Online survey.',
            consent_procedures='Participants read and click agree.',
            risk_statement='Minimal risk.',
            confidentiality_procedures='Data anonymized.',
            submitted_by=self.researcher,
            ai_review=review,
        )
        submission.submitted_at = submission.submitted_at or __import__('django.utils.timezone', fromlist=['timezone']).timezone.now()
        submission.save()

        result = IRBAnalyzer._get_submitted_protocol_and_consent(review)

        self.assertIn('submitted_protocol', result)
        self.assertIn('## Protocol description', result['submitted_protocol'])
        self.assertIn('We will survey students', result['submitted_protocol'])
        self.assertIn('## Consent procedures', result['submitted_protocol'])
        self.assertIn('consent_page', result)
        self.assertIn('Consent procedures', result['consent_page'])
        self.assertIn('Risks', result['consent_page'])

    def test_get_submitted_protocol_fallback_to_latest_submitted(self):
        """When no submission is linked to the review, latest submitted for study is used."""
        review = IRBReview.objects.create(
            study=self.study,
            initiated_by=self.researcher,
        )
        submission = ProtocolSubmission.objects.create(
            study=self.study,
            status='submitted',
            pi_suggested_review_type='expedited',
            review_type='expedited',
            protocol_description='Fallback protocol text.',
            consent_procedures='Inferred consent.',
            submitted_by=self.researcher,
            # ai_review left null
        )
        from django.utils import timezone
        submission.submitted_at = timezone.now()
        submission.save()

        result = IRBAnalyzer._get_submitted_protocol_and_consent(review)

        self.assertIn('submitted_protocol', result)
        self.assertIn('Fallback protocol text', result['submitted_protocol'])
        self.assertIn('consent_page', result)

    def test_participant_consent_text_from_study(self):
        """Study.consent_text is added as participant_consent_text when set."""
        self.study.consent_text = 'I agree to participate in this study.'
        self.study.save()
        review = IRBReview.objects.create(
            study=self.study,
            initiated_by=self.researcher,
        )
        submission = ProtocolSubmission.objects.create(
            study=self.study,
            status='submitted',
            pi_suggested_review_type='exempt',
            review_type='exempt',
            submitted_by=self.researcher,
            ai_review=review,
        )

        result = IRBAnalyzer._get_submitted_protocol_and_consent(review)

        self.assertIn('participant_consent_text', result)
        self.assertEqual(result['participant_consent_text'], 'I agree to participate in this study.')

    def test_gather_materials_input_includes_submitted_protocol_and_consent(self):
        """Data from _get_submitted_protocol_and_consent (merged into materials by gather_materials) is correct."""
        review = IRBReview.objects.create(
            study=self.study,
            initiated_by=self.researcher,
        )
        ProtocolSubmission.objects.create(
            study=self.study,
            status='submitted',
            pi_suggested_review_type='exempt',
            review_type='exempt',
            protocol_description='Gather test protocol.',
            consent_procedures='Consent obtained.',
            submitted_by=self.researcher,
            ai_review=review,
        )

        # This is the same dict that gather_materials() merges into materials via materials.update(submitted)
        submitted = IRBAnalyzer._get_submitted_protocol_and_consent(review)

        self.assertIn('submitted_protocol', submitted)
        self.assertIn('Gather test protocol', submitted['submitted_protocol'])
        self.assertIn('consent_page', submitted)
        self.assertIn('Consent obtained', submitted['consent_page'])
        # Agents receive these keys in materials; no file upload required
        self.assertIn('## Protocol description', submitted['submitted_protocol'])
        self.assertIn('## Consent procedures', submitted['submitted_protocol'])

    def test_informed_consent_display_uses_study_consent_when_set(self):
        """_get_informed_consent_display returns study.consent_text when set."""
        self.study.consent_text = 'Participant consent form text.'
        self.study.save()
        submission = ProtocolSubmission.objects.create(
            study=self.study,
            status='submitted',
            pi_suggested_review_type='exempt',
            review_type='exempt',
            consent_procedures='From protocol.',
            submitted_by=self.researcher,
        )

        display = _get_informed_consent_display(submission, self.study)

        self.assertEqual(display, 'Participant consent form text.')

    def test_informed_consent_display_inferred_when_no_study_consent(self):
        """_get_informed_consent_display returns inferred consent from submission when study has no consent_text."""
        submission = ProtocolSubmission.objects.create(
            study=self.study,
            status='submitted',
            pi_suggested_review_type='exempt',
            review_type='exempt',
            consent_procedures='We will obtain written consent.',
            risk_statement='No physical risk.',
            submitted_by=self.researcher,
        )

        display = _get_informed_consent_display(submission, self.study)

        self.assertIsNotNone(display)
        self.assertIn('Consent procedures', display)
        self.assertIn('We will obtain written consent', display)
        self.assertIn('Risks', display)
        self.assertIn('No physical risk', display)

    def test_informed_consent_display_none_when_empty(self):
        """_get_informed_consent_display returns None when submission and study have no consent content."""
        submission = ProtocolSubmission.objects.create(
            study=self.study,
            status='draft',
            pi_suggested_review_type='exempt',
            review_type='exempt',
            submitted_by=self.researcher,
        )

        display = _get_informed_consent_display(submission, self.study)

        self.assertIsNone(display)

    def test_protocol_submission_detail_shows_informed_consent_section(self):
        """Protocol submission detail page shows 'Informed consent (from protocol)' when content exists."""
        submission = ProtocolSubmission.objects.create(
            study=self.study,
            status='submitted',
            pi_suggested_review_type='exempt',
            review_type='exempt',
            consent_procedures='Participants will read and agree to the consent form.',
            risk_statement='Minimal risk only.',
            submitted_by=self.researcher,
        )
        self.client.login(email=self.researcher.email, password='testpass123')
        url = reverse('studies:protocol_submission_detail', args=[submission.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Informed consent (from protocol)', response.content)
        self.assertIn(b'Participants will read and agree', response.content)
