import uuid

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.accounts.models import User
from apps.studies.models import IRBReviewerAssignment, Study


class Command(BaseCommand):
    help = "Create or update an IRB member account and assign them to a study."

    def add_arguments(self, parser):
        parser.add_argument('email', help='Email address for the IRB member.')
        parser.add_argument('--first-name', default='', help='First name for the IRB member.')
        parser.add_argument('--last-name', default='', help='Last name for the IRB member.')
        parser.add_argument('--password', default=None, help='Optional password to set (default: auto-generate).')
        parser.add_argument(
            '--study',
            help='Study slug or UUID to assign this IRB member to.'
        )
        parser.add_argument(
            '--disable-email-updates',
            action='store_true',
            help='Create the assignment with email updates disabled.'
        )
        parser.add_argument(
            '--staff',
            action='store_true',
            help='Grant Django admin access (is_staff=True).'
        )

    def handle(self, *args, **options):
        email = options['email'].strip().lower()
        if not email:
            raise CommandError('Email is required.')
        
        first_name = options['first_name'] or 'IRB'
        last_name = options['last_name'] or 'Reviewer'
        password = options['password']
        receive_email_updates = not options['disable_email_updates']
        study_identifier = options.get('study')
        make_staff = options['staff']
        
        generated_password = None
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'role': 'irb_member',
                'is_active': True,
            }
        )
        
        if created and not password:
            generated_password = User.objects.make_random_password()
            user.set_password(generated_password)
        elif password:
            user.set_password(password)
        
        # Ensure role and profile details are up to date
        user.role = 'irb_member'
        user.first_name = first_name
        user.last_name = last_name
        user.is_staff = True
        if not user.email_verified_at:
            user.email_verified_at = timezone.now()
        user.save()
        
        assignments_summary = []
        if study_identifier:
            study = self._get_study(study_identifier)
            assignment, assignment_created = IRBReviewerAssignment.objects.get_or_create(
                study=study,
                reviewer=user,
                defaults={'receive_email_updates': receive_email_updates}
            )
            if not assignment_created and assignment.receive_email_updates != receive_email_updates:
                assignment.receive_email_updates = receive_email_updates
                assignment.save(update_fields=['receive_email_updates'])
            assignments_summary.append(
                f"- {study.title} (email updates {'on' if assignment.receive_email_updates else 'off'})"
            )
        
        self.stdout.write(self.style.SUCCESS(f"IRB member account ready for {user.get_full_name()} <{user.email}>."))
        if generated_password:
            self.stdout.write(self.style.WARNING(f"Generated password: {generated_password}"))
        elif password:
            self.stdout.write("Password updated from command arguments.")
        else:
            self.stdout.write("Password unchanged.")
        
        if assignments_summary:
            self.stdout.write("Assignments:")
            for line in assignments_summary:
                self.stdout.write(f"  {line}")
        elif study_identifier:
            self.stdout.write("No study assignment was created (study not found).")
        else:
            self.stdout.write("No study assignment requested.")

    def _get_study(self, identifier: str) -> Study:
        try:
            return Study.objects.get(slug=identifier)
        except Study.DoesNotExist:
            pass
        
        try:
            study_uuid = uuid.UUID(identifier)
        except ValueError as exc:
            raise CommandError(f'Could not find study with slug or UUID "{identifier}".') from exc
        
        try:
            return Study.objects.get(id=study_uuid)
        except Study.DoesNotExist as exc:
            raise CommandError(f'Could not find study with slug or UUID "{identifier}".') from exc

