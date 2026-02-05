"""
Add Dr. Juliann Allen as an IRB member so she can be selected as a reviewer.
Profile: https://www.nicholls.edu/business/faculty/dr-juliann-allen/
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import User
from apps.accounts.models import Profile


class Command(BaseCommand):
    help = 'Add Dr. Juliann Allen as an IRB member (selectable as reviewer)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            default=None,
            help='Password for the account (default: set unusable until first login/reset)',
        )

    def handle(self, *args, **options):
        email = 'juliann.allen@nicholls.edu'
        password = options.get('password')

        self.stdout.write('Adding Dr. Juliann Allen as IRB member...\n')

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': 'Juliann',
                'last_name': 'Allen',
                'role': 'irb_member',
                'is_active': True,
            },
        )
        if created:
            if password:
                user.set_password(password)
            else:
                user.set_password(User.objects.make_random_password())
                user.set_unusable_password()
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created: {user.get_full_name()} ({user.email})'))
        else:
            user.role = 'irb_member'
            user.is_active = True
            user.first_name = 'Juliann'
            user.last_name = 'Allen'
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Updated existing user: {user.get_full_name()}'))

        profile, _ = Profile.objects.get_or_create(user=user)
        profile.department = 'Management and Marketing'
        profile.save()

        self.stdout.write(self.style.SUCCESS(
            '\nDr. Juliann Allen is now an IRB member and will appear in "Select IRB Reviewers" on protocol forms.'
        ))
        self.stdout.write(f'  Email: {user.email}')
        self.stdout.write(f'  Role: {user.role}')
        if not user.has_usable_password() and created:
            self.stdout.write(self.style.WARNING(
                '  Password: not set. Use Django admin or password reset to set a login password.'
            ))
