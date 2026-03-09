"""
Update Goals as Reference Points protocol submission with Jaycee Bennett as co-investigator
and link her CITI certificate.
"""
import shutil
from pathlib import Path

from django.core.management.base import BaseCommand
from django.conf import settings

from apps.studies.models import Study, ProtocolSubmission


CO_INVESTIGATORS = (
    "Jaycee Bennett (Co-Investigator, Student Researcher)"
)
CITI_TRAINING = (
    "Principal Investigator (Dr. Christopher Castille): CITI training in Human Subjects Research "
    "(Social/Behavioral Research). Co-Investigator (Jaycee Bennett): Human Subjects Research - "
    "Student Researchers (Basic Course), completed 11-Jan-2025, expires 11-Jan-2027, Record ID 66618363."
)


class Command(BaseCommand):
    help = "Add Jaycee Bennett as co-investigator and link her CITI certificate to Goals-refs protocol"

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            default=None,
            help='Path to Jaycee Bennett CITI certificate PDF (optional)',
        )

    def handle(self, *args, **options):
        study = Study.objects.filter(slug='goals-refs').first()
        if not study:
            self.stdout.write(self.style.ERROR('Goals-refs study not found.'))
            return

        submission = ProtocolSubmission.objects.filter(
            study=study,
            status='submitted'
        ).order_by('-submitted_at').first()

        if not submission:
            submission = ProtocolSubmission.objects.filter(
                study=study,
                status='draft'
            ).order_by('-version').first()

        if not submission:
            self.stdout.write(self.style.ERROR('No protocol submission found for Goals-refs.'))
            return

        submission.co_investigators = CO_INVESTIGATORS
        submission.citi_training_completion = CITI_TRAINING

        # Link CITI certificate if path provided or default location exists
        custom_path = options.get('path')
        media = Path(settings.MEDIA_ROOT)
        cert_rel = f'protocol_submissions/citi_certificates/2026/03/jaycee_bennett_citi_2025.pdf'
        cert_full = media / cert_rel

        if custom_path:
            src = Path(custom_path)
            if src.exists():
                cert_full.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, cert_full)
                submission.citi_training_certificate.name = cert_rel
                self.stdout.write(self.style.SUCCESS(f'  ✓ Linked CITI certificate from {src}'))
        elif cert_full.exists():
            submission.citi_training_certificate.name = cert_rel
            self.stdout.write(self.style.SUCCESS(f'  ✓ Linked CITI certificate: {cert_rel}'))

        submission.save()

        self.stdout.write(self.style.SUCCESS('✓ Updated Goals as Reference Points protocol'))
        self.stdout.write(f'  Co-Investigators: {CO_INVESTIGATORS}')
        self.stdout.write(f'  CITI: Jaycee Bennett (11-Jan-2025, expires 11-Jan-2027)')
        if submission.citi_training_certificate:
            self.stdout.write(f'  Certificate file: {submission.citi_training_certificate.name}')
