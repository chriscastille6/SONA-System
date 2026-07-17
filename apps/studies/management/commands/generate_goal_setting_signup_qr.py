"""
Generate QR code PNG for goal-setting anonymous sign-up (marketing materials).

Usage:
    python manage.py generate_goal_setting_signup_qr
    python manage.py generate_goal_setting_signup_qr --url https://bayoupal.nicholls.edu/hsirb/studies/signup/decision-making/
"""
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.urls import reverse

from apps.studies.goal_setting_study import GOAL_SETTING_STUDY_SLUG, PUBLIC_SIGNUP_URL
from apps.studies.models import Study
from apps.studies.qr_utils import build_signup_qr_png


class Command(BaseCommand):
    help = 'Generate QR code PNG for goal-setting study anonymous sign-up'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            help='Override sign-up URL (default: production PUBLIC_SIGNUP_URL)',
        )
        parser.add_argument(
            '--output',
            help='Output PNG path (default: goal-setting materials folder)',
        )

    def handle(self, *args, **options):
        study = Study.objects.filter(slug=GOAL_SETTING_STUDY_SLUG).first()
        if not study:
            self.stderr.write(self.style.ERROR(f'Study with slug {GOAL_SETTING_STUDY_SLUG} not found.'))
            return

        if options['url']:
            signup_url = options['url'].rstrip('/') + '/'
        else:
            signup_url = PUBLIC_SIGNUP_URL

        default_out = (
            Path(settings.BASE_DIR)
            / 'apps'
            / 'studies'
            / 'assets'
            / 'irb'
            / 'goal-setting'
            / 'materials'
            / 'goal_setting_signup_qr.png'
        )
        output_path = Path(options['output']) if options['output'] else default_out
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(build_signup_qr_png(signup_url))

        self.stdout.write(self.style.SUCCESS(f'QR code saved: {output_path}'))
        self.stdout.write(f'Sign-up URL: {signup_url}')
        self.stdout.write(
            f'Embed in materials: <img src="/hsirb/studies/signup/{GOAL_SETTING_STUDY_SLUG}/qr.png" '
            'alt="Scan to sign up" width="200" height="200">'
        )
