"""
Ensure Christopher Castille (co-I) can log in. Use this if your credentials
don't work or you suspect the system confused your account with another user.

Login is strictly by email; no code merges or confuses you with Jon Murphy.
This command only ensures your account exists, is active, and has a known password.
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import User


class Command(BaseCommand):
    help = 'Ensure Christopher Castille account exists, is active, and can log in'

    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            default='ChangeMe123!',
            help='Password to set (default: ChangeMe123! — change after logging in)',
        )
        parser.add_argument(
            '--email',
            default='christopher.castille@nicholls.edu',
            help='Email for the account (default: christopher.castille@nicholls.edu)',
        )

    def handle(self, *args, **options):
        email = options['email'].strip().lower()
        password = options['password']

        self.stdout.write('🔐 Ensuring researcher account can log in...\n')

        user = User.objects.filter(email=email).first()
        if not user:
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name='Christopher',
                last_name='Castille',
                role='researcher',
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Created account: {user.email}'))
        else:
            self.stdout.write(f'✓ Found account: {user.get_full_name()} ({user.email})')
            self.stdout.write(f'  Role: {user.role}, Active: {user.is_active}')

        # Ensure they can log in
        user.is_active = True
        user.role = 'researcher'  # in case it was changed
        user.set_password(password)
        user.save()

        self.stdout.write(self.style.SUCCESS('\n✅ Account updated. You can log in with:'))
        self.stdout.write(f'   Email: {email}')
        self.stdout.write(f'   Password: {password}')
        self.stdout.write(self.style.WARNING('\n⚠ Change your password after logging in (Profile or Forgot password).'))
