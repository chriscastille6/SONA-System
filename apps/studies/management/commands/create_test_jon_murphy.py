"""
Management command to create a test user with Jon Murphy's permissions
for local testing of the IRB review workflow.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.accounts.models import User, Profile
from apps.studies.models import CollegeRepresentative


class Command(BaseCommand):
    help = 'Create a test user with Jon Murphy\'s permissions (IRB member + College Rep)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='jon.murphy@test.local',
            help='Email address for the test user (default: jon.murphy@test.local)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='testpass123',
            help='Password for the test user (default: testpass123)'
        )
        parser.add_argument(
            '--college',
            type=str,
            default='business',
            choices=['business', 'education', 'liberal_arts', 'sciences', 'nursing'],
            help='College to assign as representative (default: business)'
        )

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        college = options['college']
        
        # Create or get user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': 'Jon',
                'last_name': 'Murphy',
                'role': 'irb_member',
                'is_active': True,
                'email_verified_at': timezone.now(),
            }
        )
        
        if created:
            user.set_password(password)
            self.stdout.write(
                self.style.SUCCESS(f'✅ Created user: {user.get_full_name()} ({email})')
            )
        else:
            # Update existing user
            user.first_name = 'Jon'
            user.last_name = 'Murphy'
            user.role = 'irb_member'
            user.is_active = True
            if not user.email_verified_at:
                user.email_verified_at = timezone.now()
            if password:
                user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.WARNING(f'⚠️  Updated existing user: {user.get_full_name()} ({email})')
            )
        
        # Create or update profile
        profile, profile_created = Profile.objects.get_or_create(
            user=user,
            defaults={}
        )
        
        # Set up as college representative
        college_rep, rep_created = CollegeRepresentative.objects.get_or_create(
            college=college,
            defaults={
                'representative': user,
                'active': True,
                'is_chair': False,
            }
        )
        
        if rep_created:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Created college representative assignment: '
                    f'{college_rep.get_college_display()}'
                )
            )
        elif college_rep.representative != user:
            college_rep.representative = user
            college_rep.active = True
            college_rep.save()
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  Updated college representative: {college_rep.get_college_display()}'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Already assigned as college representative: {college_rep.get_college_display()}'
                )
            )
        
        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('✅ Test User Setup Complete!'))
        self.stdout.write('='*60)
        self.stdout.write(f'Email: {email}')
        self.stdout.write(f'Password: {password}')
        self.stdout.write(f'Role: IRB Member')
        self.stdout.write(f'College Representative: {college_rep.get_college_display()}')
        self.stdout.write('\nYou can now log in at: http://localhost:8000/accounts/login/')
        self.stdout.write('='*60 + '\n')
