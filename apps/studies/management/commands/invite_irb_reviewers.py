"""
Prepare Jon Murphy and Juliann Allen for IRB access.
- Fix Jon Murphy email: jon.murphy@nicholls.edu → jonathan.murphy@nicholls.edu (via fix_jon_murphy_accounts)
- Ensure Juliann Allen has an account
- Set temporary passwords and output credentials for the invite email
"""
import secrets
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounts.models import Profile
from apps.studies.models import CollegeRepresentative

User = get_user_model()


def generate_password():
    """Generate a secure temporary password (12 chars, alphanumeric)."""
    return secrets.token_urlsafe(9)[:12]


class Command(BaseCommand):
    help = 'Fix Jon Murphy email, ensure Juliann Allen exists, set passwords, output credentials for invite'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-password',
            action='store_true',
            help='Do not set new passwords (only fix email and ensure accounts exist)',
        )

    def handle(self, *args, **options):
        set_passwords = not options.get('no_password', False)
        jon_password = generate_password() if set_passwords else None
        juliann_password = generate_password() if set_passwords else None

        self.stdout.write('🔧 Preparing IRB reviewers for invite...\n')

        # 1. Fix Jon Murphy (merge duplicates, correct email)
        call_command('fix_jon_murphy_accounts', verbosity=1)

        jon = User.objects.filter(email='jonathan.murphy@nicholls.edu').first()
        if jon and jon_password:
            jon.set_password(jon_password)
            jon.save()
            self.stdout.write(self.style.SUCCESS('✓ Set Jon Murphy temporary password'))

        # 2. Ensure Juliann Allen exists
        juliann, created = User.objects.get_or_create(
            email='juliann.allen@nicholls.edu',
            defaults={
                'first_name': 'Juliann',
                'last_name': 'Allen',
                'role': 'irb_member',
                'is_active': True,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created Juliann Allen account'))
        else:
            juliann.role = 'irb_member'
            juliann.is_active = True
            juliann.first_name = juliann.first_name or 'Juliann'
            juliann.last_name = juliann.last_name or 'Allen'
            juliann.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Juliann Allen account exists'))

        profile, _ = Profile.objects.get_or_create(user=juliann)
        profile.department = profile.department or 'Management and Marketing'
        profile.save()

        if juliann_password:
            juliann.set_password(juliann_password)
            juliann.save()

        # Output credentials
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('LOGIN CREDENTIALS FOR INVITE EMAIL')
        self.stdout.write('=' * 60)
        self.stdout.write('\n**Dr. Jonathan Murphy (College of Business Rep)**')
        self.stdout.write(f'  Email: jonathan.murphy@nicholls.edu')
        self.stdout.write(f'  Password: {jon_password or "(unchanged - use password reset)"}')
        self.stdout.write('\n**Dr. Juliann Allen (IRB Reviewer)**')
        self.stdout.write(f'  Email: juliann.allen@nicholls.edu')
        self.stdout.write(f'  Password: {juliann_password or "(unchanged - use password reset)"}')
        self.stdout.write('\n**Login URL:** https://bayoupal.nicholls.edu/hsirb/accounts/login/')
        self.stdout.write('=' * 60)
        self.stdout.write(self.style.SUCCESS('\n✅ Ready to send invite email.'))
