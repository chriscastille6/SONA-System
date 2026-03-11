"""
Pretend smoke test for Decision Making and Unethical Behavior (goals-refs).
Generates example PI notification emails for (1) sample-size threshold and
(2) evidence-threshold retirement suggestion. Does not send email or modify data.
"""
from django.core.management.base import BaseCommand

from apps.studies.models import Study


def _email_1_sample_size_threshold(study):
    to_line = study.researcher.email if study.researcher else "(PI email not set)"
    subject = f"[Goals-refs] Sample size threshold reached — vignette R1 (N=10)"
    body = f"""To: {to_line}
Subject: {subject}

The sample size threshold has been reached for the Decision Making and Unethical Behavior study (goals-refs).

Vignette: R1
Valid N: 10 (minimum N for analysis is 10 per vignette).

Analysis has been triggered for this vignette. You will receive a follow-up email if the evidence threshold (BF ≥ 10) is reached for the hypothesis being tested.

This is a smoke-test example. No data was modified.
"""
    return subject, body


def _email_2_evidence_threshold_retirement_suggestion(study):
    to_line = study.researcher.email if study.researcher else "(PI email not set)"
    subject = f"[Goals-refs] Evidence threshold reached — retirement suggestion for vignette R1"
    body = f"""To: {to_line}
Subject: {subject}

The evidence threshold has been reached for the Decision Making and Unethical Behavior study (goals-refs).

Vignette: R1
Hypothesis tested: Goal-frame effect (below vs. above goal)
BF (alternative): 12.3
Interpretation: Evidence supports the alternative hypothesis (goal-frame effect). BF ≥ 10 per decision rules.

Suggestion: We suggest retiring vignette R1 (stop data collection for this vignette).

Your decision: Reply to this email with one of the following:
  • Retire R1 — to retire the vignette (stop collection).
  • Keep R1 — to continue collection for this vignette.

Your reply determines whether this vignette is retired. No automatic retirement is applied.

(When implemented: participants who saw this vignette and opted in will be contactable for sharing findings.)

This is a smoke-test example. No data was modified.
"""
    return subject, body


class Command(BaseCommand):
    help = (
        "Generate example PI notification emails for goals-refs smoke test "
        "(sample-size threshold and evidence-threshold retirement suggestion). Does not send email or modify data."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--study-slug",
            type=str,
            default="goals-refs",
            help="Study slug (default: goals-refs).",
        )
        parser.add_argument(
            "--output",
            type=str,
            default=None,
            metavar="PATH",
            help="Write example emails to this file (e.g. docs/smoke_test_goals_refs_emails.txt). If omitted, print to stdout.",
        )

    def handle(self, *args, **options):
        slug = options["study_slug"]
        output_path = options.get("output")

        try:
            study = Study.objects.get(slug=slug)
        except Study.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Study not found: {slug}"))
            return

        subject1, body1 = _email_1_sample_size_threshold(study)
        subject2, body2 = _email_2_evidence_threshold_retirement_suggestion(study)

        sep = "\n" + "-" * 60 + "\n"
        content = (
            "EXAMPLE EMAIL 1 — Sample size threshold reached\n"
            + "=" * 60 + "\n\n"
            + body1
            + sep
            + "EXAMPLE EMAIL 2 — Evidence threshold / retirement suggestion\n"
            + "=" * 60 + "\n\n"
            + body2
        )

        if output_path:
            with open(output_path, "w") as f:
                f.write(content)
            self.stdout.write(self.style.SUCCESS(f"Wrote example emails to {output_path}"))
        else:
            self.stdout.write(content)
