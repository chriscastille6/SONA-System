import uuid

from django.core.management.base import BaseCommand, CommandError

from apps.studies.models import Study
from apps.studies.tasks import send_irb_test_email


class Command(BaseCommand):
    help = "Send a test email to IRB reviewers assigned to a study to verify SMTP configuration."

    def add_arguments(self, parser):
        parser.add_argument(
            'study',
            help='Study slug or UUID whose IRB reviewers should receive the test email.'
        )
        parser.add_argument(
            '--subject',
            help='Optional email subject override.'
        )
        parser.add_argument(
            '--message',
            help='Optional plain-text body override.'
        )

    def handle(self, *args, **options):
        study = self._get_study(options['study'])
        subject = options.get('subject')
        message = options.get('message')

        count, response = send_irb_test_email(study, subject=subject, message=message)
        if not count:
            self.stdout.write(self.style.WARNING(response))
        else:
            self.stdout.write(self.style.SUCCESS(response))

    def _get_study(self, identifier: str) -> Study:
        try:
            return Study.objects.get(slug=identifier)
        except Study.DoesNotExist:
            pass

        try:
            study_uuid = uuid.UUID(identifier)
        except ValueError as exc:
            raise CommandError(f'Could not find study with slug or UUID "{identifier}".') from exc

        try:
            return Study.objects.get(id=study_uuid)
        except Study.DoesNotExist as exc:
            raise CommandError(f'Could not find study with slug or UUID "{identifier}".') from exc



