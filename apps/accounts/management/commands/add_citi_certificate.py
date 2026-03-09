"""
Add a CITI certificate for a researcher.
Usage: python manage.py add_citi_certificate user@email.com --completion 2025-01-11 --expiration 2027-01-11 [--record-id 66618363]
"""
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from apps.accounts.models import CITICertificate

User = get_user_model()


class Command(BaseCommand):
    help = 'Add CITI certificate for a researcher'

    def add_arguments(self, parser):
        parser.add_argument('email', help='Researcher email')
        parser.add_argument('--completion', required=True, help='Completion date (YYYY-MM-DD)')
        parser.add_argument('--expiration', required=True, help='Expiration date (YYYY-MM-DD)')
        parser.add_argument('--record-id', default='', help='CITI Record ID')
        parser.add_argument('--course', default='', help='Course name (e.g. Human Subjects Research - Student Researchers)')

    def handle(self, *args, **options):
        user = User.objects.filter(email__iexact=options['email']).first()
        if not user:
            self.stdout.write(self.style.ERROR(f'User not found: {options["email"]}'))
            return

        completion = datetime.strptime(options['completion'], '%Y-%m-%d').date()
        expiration = datetime.strptime(options['expiration'], '%Y-%m-%d').date()

        cert = CITICertificate.objects.create(
            user=user,
            completion_date=completion,
            expiration_date=expiration,
            record_id=options.get('record_id', ''),
            course_name=options.get('course', ''),
        )

        status = 'created'
        self.stdout.write(self.style.SUCCESS(f'✓ CITI certificate {status} for {user.get_full_name()} ({user.email})'))
        self.stdout.write(f'  Expires: {cert.expiration_date}  Valid: {cert.is_valid}')
