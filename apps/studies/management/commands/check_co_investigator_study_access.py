"""
Check whether a user (by email) would see a given study on My Studies.
Uses only co_investigators text and researcher; safe to run on production
with or without the co_investigator_users migration.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Q

from apps.studies.models import Study

User = get_user_model()


class Command(BaseCommand):
    help = "Check if a user (by email) would see a study on My Studies (co-investigator or PI)."

    def add_arguments(self, parser):
        parser.add_argument("email", help="User email (e.g. jbennett15@nicholls.edu)")
        parser.add_argument(
            "--slug",
            default="goals-refs",
            help="Study slug to check (default: goals-refs)",
        )

    def handle(self, *args, **options):
        email = options["email"].strip().lower()
        slug = options["slug"].strip()
        u = User.objects.filter(email__iexact=email).first()
        if not u:
            self.stdout.write(self.style.ERROR(f"No user with email: {email}"))
            return
        # Match researcher_dashboard: researcher or email in co_investigators (text)
        # Uses only fields that exist before co_investigator_users migration
        studies = Study.objects.filter(
            Q(researcher=u) | Q(protocol_submissions__co_investigators__icontains=u.email)
        ).distinct()
        goals = studies.filter(slug=slug)
        self.stdout.write(f"User: {u.get_full_name()} ({u.email})")
        self.stdout.write(f"Sees study '{slug}'? {goals.exists()}")
        if goals.exists():
            self.stdout.write(self.style.SUCCESS(f"  Title: {goals.first().title}"))
        else:
            titles = list(studies.values_list("title", flat=True))
            self.stdout.write(f"  Studies this user sees: {titles or '(none)'}")
