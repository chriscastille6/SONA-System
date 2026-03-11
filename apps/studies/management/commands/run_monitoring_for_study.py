"""
Trigger sequential Bayesian monitoring for a study (for smoke testing post-decision analysis).
Optionally add fake responses so the placeholder plugin reaches the BF threshold.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.studies.models import Study, Response
from apps.studies.tasks import run_sequential_bayes_monitoring


class Command(BaseCommand):
    help = (
        "Run sequential Bayesian monitoring for a study by slug or id. "
        "Use for smoke testing: verify status page shows 'Post-decision analysis ran' when threshold is reached."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "slug",
            nargs="?",
            type=str,
            help="Study slug (e.g. ei-pilot). Optional if --id is set.",
        )
        parser.add_argument(
            "--id",
            type=str,
            help="Study UUID (alternative to slug).",
        )
        parser.add_argument(
            "--add-responses",
            type=int,
            metavar="N",
            help="Add N fake protocol responses before running monitoring (e.g. 25 for placeholder to reach BF >= 3).",
        )

    def handle(self, *args, **options):
        slug = options.get("slug")
        study_id = options.get("id")
        add_responses = options.get("add_responses")

        if not slug and not study_id:
            self.stdout.write(
                self.style.ERROR("Provide either a study slug or --id <uuid>.")
            )
            return

        if slug and study_id:
            self.stdout.write(self.style.ERROR("Provide only one of slug or --id."))
            return

        try:
            if study_id:
                study = Study.objects.get(id=study_id)
            else:
                study = Study.objects.get(slug=slug)
        except Study.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"Study not found: {slug or study_id}")
            )
            return

        if add_responses and add_responses > 0:
            for i in range(add_responses):
                Response.objects.create(
                    study=study,
                    payload={"smoke_test": True, "batch_index": i},
                )
            self.stdout.write(
                self.style.SUCCESS(f"Added {add_responses} responses. N={study.responses.count()}.")
            )

        run_sequential_bayes_monitoring.delay(str(study.id))
        self.stdout.write(
            self.style.SUCCESS(
                f"Enqueued run_sequential_bayes_monitoring for study {study.slug} ({study.id})."
            )
        )
        self.stdout.write(
            "Check the study status page and admin for 'Post-decision analysis ran' "
            "(ensure monitoring_enabled, run_analysis_on_threshold=True, and N >= min_sample_size with BF >= threshold)."
        )
