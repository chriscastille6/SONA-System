"""
Send a verification email to a user (by email address). Use this to test that
verification emails are delivered when EMAIL_HOST etc. are configured in .env.
"""
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from apps.accounts.models import User, EmailVerificationToken


class Command(BaseCommand):
    help = (
        "Send a verification email to the user with the given email address. "
        "Requires EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD in .env. "
        "Use to test that verification emails are delivered."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'email',
            help='Email address of the user to send a verification email to (user must exist).'
        )

    def handle(self, *args, **options):
        email = options['email'].strip().lower()
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            raise CommandError(f'No user found with email: {email}')

        if not getattr(settings, 'EMAIL_HOST', ''):
            raise CommandError(
                'Outgoing email is not configured. Set EMAIL_HOST, EMAIL_HOST_USER, and '
                'EMAIL_HOST_PASSWORD in .env. Run: python manage.py check_email_config'
            )

        token = EmailVerificationToken.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(days=7)
        )
        base_url = (getattr(settings, 'SITE_URL', '') or 'http://localhost:8000').rstrip('/')
        path = reverse('accounts:verify_email', kwargs={'token': token.token})
        verify_url = base_url + path

        subject = 'Verify your email - ' + getattr(settings, 'SITE_NAME', 'PRAMS')
        message = (
            f'Hi {user.get_full_name()},\n\n'
            f'Please verify your email by clicking the link below:\n\n'
            f'{verify_url}\n\n'
            f'This link expires in 7 days. If you did not request this, you can ignore this email.\n'
        )
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None) or None,
                recipient_list=[user.email],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(
                f'Verification email sent to {email}. Check your inbox (and spam). '
                f'Click the link to verify.'
            ))
        except Exception as e:
            raise CommandError(f'Failed to send email: {e}')
