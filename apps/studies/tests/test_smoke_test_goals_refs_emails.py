"""
Tests for the goals-refs pretend smoke test (smoke_test_goals_refs_emails command).
"""
import os
import tempfile
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from apps.accounts.models import User
from apps.studies.models import Study


class SmokeTestGoalsRefsEmailsTests(TestCase):
    """Test smoke_test_goals_refs_emails management command."""

    @classmethod
    def setUpTestData(cls):
        cls.researcher = User.objects.create_user(
            email="pi@example.com",
            password="testpass123",
            first_name="PI",
            last_name="Researcher",
            role="researcher",
        )
        cls.study = Study.objects.create(
            title="Goals as Reference Points and Risk Taking",
            slug="goals-refs",
            description="Decision Making and Unethical Behavior study.",
            mode="online",
            researcher=cls.researcher,
            credit_value=0,
            consent_text="Sample consent.",
        )

    def test_command_prints_both_emails_with_expected_content(self):
        """Running the command prints both example emails with key content."""
        out = StringIO()
        call_command("smoke_test_goals_refs_emails", stdout=out)
        content = out.getvalue()
        self.assertIn("EXAMPLE EMAIL 1 — Sample size threshold reached", content)
        self.assertIn("EXAMPLE EMAIL 2 — Evidence threshold / retirement suggestion", content)
        self.assertIn("Sample size threshold", content)
        self.assertIn("Evidence threshold", content)
        self.assertIn("Retire R1", content)
        self.assertIn("Keep R1", content)
        self.assertIn("Valid N: 10", content)
        self.assertIn("BF (alternative): 12.3", content)
        self.assertIn("pi@example.com", content)
        self.assertIn("Your reply determines whether this vignette is retired", content)

    def test_command_study_not_found(self):
        """Running with a non-existent study slug prints an error and no emails."""
        out = StringIO()
        call_command("smoke_test_goals_refs_emails", "--study-slug=nonexistent-slug-xyz", stdout=out)
        content = out.getvalue()
        self.assertIn("Study not found", content)
        self.assertIn("nonexistent-slug-xyz", content)
        self.assertNotIn("EXAMPLE EMAIL 1", content)

    def test_command_writes_to_output_file(self):
        """With --output, the command writes both emails to the file."""
        fd, path = tempfile.mkstemp(suffix=".txt")
        os.close(fd)
        try:
            out = StringIO()
            call_command("smoke_test_goals_refs_emails", f"--output={path}", stdout=out)
            self.assertIn("Wrote example emails to", out.getvalue())
            with open(path) as f:
                content = f.read()
            self.assertIn("EXAMPLE EMAIL 1 — Sample size threshold reached", content)
            self.assertIn("EXAMPLE EMAIL 2 — Evidence threshold / retirement suggestion", content)
        finally:
            os.unlink(path)

    def test_command_pi_email_not_set_when_researcher_missing(self):
        """When study has no researcher, output shows (PI email not set)."""
        study_no_pi = Study.objects.create(
            title="Goals refs no PI",
            slug="goals-refs-no-pi",
            description="Test.",
            mode="online",
            researcher=None,
            credit_value=0,
            consent_text="Consent.",
        )
        out = StringIO()
        call_command("smoke_test_goals_refs_emails", "--study-slug=goals-refs-no-pi", stdout=out)
        content = out.getvalue()
        self.assertIn("(PI email not set)", content)
        self.assertIn("EXAMPLE EMAIL 1", content)
