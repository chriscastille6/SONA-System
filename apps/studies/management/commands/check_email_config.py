"""
Check whether outgoing email is configured (for PI approval notifications, etc.)
and optionally send a test email to verify delivery.
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.mail import send_mail


class Command(BaseCommand):
    help = (
        "Check email configuration and optionally send a test email. "
        "Use this on bayoupal after setting EMAIL_* in .env to verify PI approval emails will work."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'email',
            nargs='?',
            default=None,
            help='Send a test email to this address (e.g. your @nicholls.edu). Omit to only check config.'
        )

    def handle(self, *args, **options):
        email_host = getattr(settings, 'EMAIL_HOST', '') or ''
        backend = getattr(settings, 'EMAIL_BACKEND', '')
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', '')
        has_user = bool(getattr(settings, 'EMAIL_HOST_USER', ''))
        has_password = bool(getattr(settings, 'EMAIL_HOST_PASSWORD', ''))

        self.stdout.write('Email configuration:')
        self.stdout.write(f'  EMAIL_BACKEND = {backend}')
        self.stdout.write(f'  EMAIL_HOST = {email_host or "(not set)"}')
        self.stdout.write(f'  DEFAULT_FROM_EMAIL = {from_email or "(not set)"}')
        self.stdout.write(f'  EMAIL_HOST_USER = {"(set)" if has_user else "(not set)"}')
        self.stdout.write(f'  EMAIL_HOST_PASSWORD = {"(set)" if has_password else "(not set)"}')

        if not email_host:
            self.stdout.write(self.style.WARNING(
                '\nOutgoing email is NOT configured. PI approval notifications will not be sent.\n'
                'Add EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD (and optionally DEFAULT_FROM_EMAIL)\n'
                'to your .env on the server. See docs/EMAIL_SETUP_BAYOUPAL.md.'
            ))
            return

        if not has_user or not has_password:
            self.stdout.write(self.style.WARNING(
                '\nEMAIL_HOST is set but credentials are missing. Set EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in .env.'
            ))
            return

        self.stdout.write(self.style.SUCCESS('\nEmail appears configured. PI approval emails should be sent.'))

        test_to = (options.get('email') or '').strip()
        if not test_to:
            self.stdout.write('To verify delivery, run: python manage.py check_email_config your@nicholls.edu')
            return

        self.stdout.write(f'\nSending test email to {test_to}...')
        try:
            send_mail(
                subject='[HSIRB] Test email – PI notifications are working',
                message=(
                    'This is a test from the HSIRB Study Management System.\n\n'
                    'If you received this, outgoing email is configured correctly and you should '
                    'receive "Protocol Approved" emails when a college rep approves your submissions.\n\n'
                    f'Sent by check_email_config on {settings.SITE_NAME}.'
                ),
                from_email=from_email or None,
                recipient_list=[test_to],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f'Test email sent to {test_to}. Check your inbox (and spam).'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to send test email: {e}'))
