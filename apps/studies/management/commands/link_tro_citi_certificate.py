"""
Link an existing CITI certificate file to the TRO study protocol submission.
Searches common locations; you can also upload via the protocol form.
"""
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from apps.studies.models import ProtocolSubmission


class Command(BaseCommand):
    help = 'Link existing CITI certificate to TRO study protocol submission'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            default=None,
            help='Full path to CITI certificate PDF (optional; otherwise searches standard locations)',
        )

    def handle(self, *args, **options):
        submission = ProtocolSubmission.objects.filter(
            protocol_number='IRBE20251031-005CBA'
        ).first()

        if not submission:
            self.stdout.write(self.style.ERROR('TRO protocol submission not found'))
            return

        if submission.citi_training_certificate:
            self.stdout.write(self.style.SUCCESS(
                f'✓ CITI certificate already linked: {submission.citi_training_certificate.name}'
            ))
            return

        custom_path = options.get('path')
        if custom_path:
            search_paths = [Path(custom_path)]
        else:
            now = timezone.now()
            yyyy, mm = now.strftime('%Y'), now.strftime('%m')
            media = Path(settings.MEDIA_ROOT)
            base = Path(settings.BASE_DIR)
            search_paths = [
                media / 'protocol_submissions' / 'citi_certificates' / yyyy / mm / 'citiCompletionCertificate_4689946_59381539.pdf',
                media / 'protocol_submissions' / 'citi_certificates' / '2026' / '01' / 'citiCompletionCertificate_4689946_59381539.pdf',
                media / 'protocol_submissions' / 'citi_certificates' / yyyy / mm,
                base / 'apps' / 'studies' / 'assets' / 'irb' / 'conjoint-analysis',
            ]

        citi_file = None
        for p in search_paths:
            if p.is_file() and p.suffix.lower() in ('.pdf', '.png', '.jpg', '.jpeg'):
                citi_file = p
                break
            if p.is_dir():
                for f in p.glob('*citi*.pdf') or p.glob('*.pdf'):
                    citi_file = f
                    break
            if citi_file:
                break

        if not citi_file or not citi_file.exists():
            self.stdout.write(self.style.WARNING(
                'No CITI certificate file found. Options:\n'
                '  1. Place a PDF in media/protocol_submissions/citi_certificates/YYYY/MM/ and run this command again.\n'
                '  2. Run: python manage.py link_tro_citi_certificate --path /full/path/to/your/citi.pdf\n'
                '  3. Upload via the protocol form (Enter Protocol Information → Section 9).'
            ))
            return

        try:
            rel = citi_file.relative_to(media)
            relative_path = str(rel).replace('\\', '/')
        except ValueError:
            import shutil
            now = timezone.now()
            yyyy, mm = now.strftime('%Y'), now.strftime('%m')
            relative_path = f'protocol_submissions/citi_certificates/{yyyy}/{mm}/{citi_file.name}'
            dest = media / relative_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(citi_file, dest)

        submission.citi_training_certificate.name = relative_path
        submission.save()

        self.stdout.write(self.style.SUCCESS('✓ Linked CITI certificate to TRO protocol submission'))
        self.stdout.write(f'  File: {relative_path}')
