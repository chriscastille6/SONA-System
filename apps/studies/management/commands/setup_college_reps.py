"""
Management command to set up college representatives.
Based on Nicholls State University HSIRB board members.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.studies.models import CollegeRepresentative

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up college representatives for IRB review workflow'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-users',
            action='store_true',
            help='Create user accounts for college reps if they do not exist',
        )

    def handle(self, *args, **options):
        # College representatives from Nicholls HSIRB website
        reps = [
            {
                'college': 'business',
                'name': 'Dr. Jonathan Murphy',
                'email': 'jonathan.murphy@nicholls.edu',
                'is_chair': False,
            },
            {
                'college': 'education',
                'name': 'Dr. Grant Gautreaux',
                'email': 'grant.gautreaux@nicholls.edu',
                'is_chair': False,
            },
            {
                'college': 'liberal_arts',
                'name': 'Dr. Linda Martin',
                'email': 'linda.martin@nicholls.edu',
                'is_chair': False,
            },
            {
                'college': 'sciences',
                'name': 'Dr. Sherry Foret',
                'email': 'sherry.foret@nicholls.edu',
                'is_chair': False,
            },
            {
                'college': 'nursing',
                'name': 'Dr. Alaina Daigle',
                'email': 'alaina.daigle@nicholls.edu',
                'is_chair': True,  # Chair of the Committee
            },
        ]

        created_count = 0
        updated_count = 0

        for rep_data in reps:
            college = rep_data['college']
            email = rep_data['email']
            name_parts = rep_data['name'].replace('Dr. ', '').split(' ', 1)
            first_name = name_parts[0] if len(name_parts) > 0 else ''
            last_name = name_parts[1] if len(name_parts) > 1 else ''

            # Get or create user
            user, user_created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': 'irb_member',
                    'is_active': True,
                }
            )

            if user_created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created user: {user.get_full_name()} ({email})')
                )
            elif user.role != 'irb_member':
                user.role = 'irb_member'
                user.save()
                self.stdout.write(
                    self.style.WARNING(f'Updated user role to irb_member: {user.get_full_name()}')
                )

            # Get or create college representative
            college_rep, created = CollegeRepresentative.objects.get_or_create(
                college=college,
                defaults={
                    'representative': user,
                    'is_chair': rep_data['is_chair'],
                    'active': True,
                }
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created college rep: {college_rep.get_college_display()} → {user.get_full_name()}'
                    )
                )
            else:
                # Update existing
                if college_rep.representative != user:
                    college_rep.representative = user
                if college_rep.is_chair != rep_data['is_chair']:
                    college_rep.is_chair = rep_data['is_chair']
                if not college_rep.active:
                    college_rep.active = True
                college_rep.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'Updated college rep: {college_rep.get_college_display()} → {user.get_full_name()}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted! Created {created_count} college reps, updated {updated_count}.'
            )
        )
        self.stdout.write(
            self.style.WARNING(
                '\nNote: You may need to set passwords for these users if they were just created.'
            )
        )
