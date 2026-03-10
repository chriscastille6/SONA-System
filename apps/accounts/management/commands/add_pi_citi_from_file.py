"""
Add PI CITI certificate from docs/citi_pi_dates.txt.
Edit the file with your real completion/expiration, then run:
  python manage.py add_pi_citi_from_file
"""
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model

from apps.accounts.models import CITICertificate

User = get_user_model()


def parse_citi_file(path):
    out = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                k, v = line.split('=', 1)
                out[k.strip().lower()] = v.strip()
    return out


class Command(BaseCommand):
    help = 'Add PI CITI certificate from docs/citi_pi_dates.txt'

    def add_arguments(self, parser):
        parser.add_argument('--file', default=None, help='Path to citi dates file')

    def handle(self, *args, **options):
        base = Path(settings.BASE_DIR)
        path = Path(options['file']) if options.get('file') else base / 'docs' / 'citi_pi_dates.txt'
        if not path.exists():
            self.stdout.write(self.style.ERROR(f'File not found: {path}'))
            return
        data = parse_citi_file(path)
        email = data.get('email', '').strip()
        completion_str = data.get('completion', '').strip()
        expiration_str = data.get('expiration', '').strip()
        record_id = data.get('record_id', '').strip()
        course_name = data.get('course', '').strip()
        if not email or not completion_str or not expiration_str:
            self.stdout.write(self.style.ERROR('File must set email=, completion=YYYY-MM-DD, expiration=YYYY-MM-DD'))
            return
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            self.stdout.write(self.style.ERROR(f'User not found: {email}'))
            return
        try:
            completion = datetime.strptime(completion_str, '%Y-%m-%d').date()
            expiration = datetime.strptime(expiration_str, '%Y-%m-%d').date()
        except ValueError:
            self.stdout.write(self.style.ERROR('Dates must be YYYY-MM-DD'))
            return
        existing = CITICertificate.objects.filter(user=user).order_by('-expiration_date').first()
        if existing:
            existing.completion_date = completion
            existing.expiration_date = expiration
            existing.record_id = record_id
            existing.course_name = course_name
            existing.save()
            cert, created = existing, False
        else:
            cert = CITICertificate.objects.create(
                user=user,
                completion_date=completion,
                expiration_date=expiration,
                record_id=record_id,
                course_name=course_name,
            )
            created = True
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ CITI certificate added for {user.get_full_name()}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✓ CITI certificate updated for {user.get_full_name()}'))
        self.stdout.write(f'  Expires: {cert.expiration_date}')
