"""Management command to mark a user's email as verified by email address."""
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.accounts.models import User


class Command(BaseCommand):
    help = "Mark a user's email as verified by their email address."

    def add_arguments(self, parser):
        parser.add_argument('email', help='Email address of the user to verify.')

    def handle(self, *args, **options):
        email = options['email'].strip().lower()
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            raise CommandError(f'No user found with email: {email}')
        if user.email_verified_at:
            self.stdout.write(self.style.WARNING(f'User {email} is already verified.'))
            return
        user.email_verified_at = timezone.now()
        user.save(update_fields=['email_verified_at'])
        self.stdout.write(self.style.SUCCESS(f'Email verified for {email}.'))
