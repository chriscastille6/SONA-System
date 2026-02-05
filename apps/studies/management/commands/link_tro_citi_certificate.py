"""
Link the existing CITI certificate to the TRO study protocol submission.
"""
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.studies.models import Study, ProtocolSubmission


class Command(BaseCommand):
    help = 'Link existing CITI certificate to TRO study protocol submission'

    def handle(self, *args, **options):
        # Get the protocol submission
        submission = ProtocolSubmission.objects.filter(
            protocol_number='IRBE20251031-005CBA'
        ).first()
        
        if not submission:
            self.stdout.write(self.style.ERROR('Protocol submission not found'))
            return
        
        # Check if CITI certificate already exists
        if submission.citi_training_certificate:
            self.stdout.write(self.style.SUCCESS(
                f'✓ CITI certificate already linked: {submission.citi_training_certificate.name}'
            ))
            return
        
        # Find the CITI certificate file
        citi_file = Path(settings.MEDIA_ROOT) / 'protocol_submissions' / 'citi_certificates' / '2026' / '01' / 'citiCompletionCertificate_4689946_59381539.pdf'
        
        if not citi_file.exists():
            self.stdout.write(self.style.ERROR(
                f'✗ CITI certificate not found at: {citi_file}'
            ))
            return
        
        # Link the file to the protocol submission
        # The file path relative to MEDIA_ROOT
        relative_path = 'protocol_submissions/citi_certificates/2026/01/citiCompletionCertificate_4689946_59381539.pdf'
        submission.citi_training_certificate.name = relative_path
        submission.save()
        
        self.stdout.write(self.style.SUCCESS(
            f'✓ Linked CITI certificate to protocol submission'
        ))
        self.stdout.write(f'  File: {relative_path}')
        self.stdout.write(f'  URL: {submission.citi_training_certificate.url}')
