"""
Remove a duplicate user by email (e.g. jbennett15@nicholls.edu after keeping jbennett@nicholls.edu).
Run on the environment where the duplicate exists (e.g. production).
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Remove a user by email (for duplicate accounts). Use with care."

    def add_arguments(self, parser):
        parser.add_argument(
            "email",
            help="Email of the user account to delete (e.g. jbennett15@nicholls.edu)",
        )
        parser.add_argument(
            "--no-input",
            action="store_true",
            help="Do not prompt for confirmation.",
        )

    def handle(self, *args, **options):
        email = options["email"].strip().lower()
        if not email:
            self.stdout.write(self.style.ERROR("Please provide an email address."))
            return

        user = User.objects.filter(email__iexact=email).first()
        if not user:
            self.stdout.write(self.style.WARNING(f"No user found with email: {email}"))
            return

        # Safety: do not delete if they are the researcher (PI) on any study
        from apps.studies.models import Study
        pi_studies = Study.objects.filter(researcher=user)
        if pi_studies.exists():
            self.stdout.write(self.style.ERROR(
                f"Cannot delete {email}: they are the researcher (PI) on {pi_studies.count()} study(ies). "
                "Reassign or remove that study's researcher first."
            ))
            return

        if not options["no_input"]:
            confirm = input(f"Delete user {user.get_full_name()} ({user.email})? [y/N]: ")
            if confirm.lower() != "y":
                self.stdout.write("Aborted.")
                return

        name = user.get_full_name()
        user.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted user: {name} ({email})"))
