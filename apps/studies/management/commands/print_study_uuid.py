"""
Print the database UUID for a study slug (e.g. hr-sjt for HR SJT ?study= links).
"""
from django.core.management.base import BaseCommand

from apps.studies.models import Study


class Command(BaseCommand):
    help = 'Print Study.id (UUID) for a slug — not stored in git; created at deploy.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--slug',
            default='hr-sjt',
            help='Study slug (default: hr-sjt)',
        )

    def handle(self, *args, **options):
        slug = options['slug']
        study = Study.objects.filter(slug=slug).first()
        if not study:
            self.stderr.write(self.style.ERROR(f'No study with slug={slug!r}'))
            return
        self.stdout.write(str(study.id))
