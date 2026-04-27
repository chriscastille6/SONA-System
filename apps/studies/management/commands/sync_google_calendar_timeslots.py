"""
Bulk sync study timeslots to Google Calendar.
"""
from django.core.management.base import BaseCommand

from apps.studies.calendar_sync import google_calendar_sync_enabled, sync_timeslot_to_google_calendar
from apps.studies.models import Timeslot


class Command(BaseCommand):
    help = "Create or update Google Calendar events for study timeslots."

    def add_arguments(self, parser):
        parser.add_argument(
            "--study",
            dest="study_id",
            default=None,
            help="Limit sync to one study UUID.",
        )
        parser.add_argument(
            "--include-cancelled",
            action="store_true",
            help="Also process cancelled timeslots so linked events are removed.",
        )

    def handle(self, *args, **options):
        if not google_calendar_sync_enabled():
            self.stdout.write(
                self.style.WARNING(
                    "Google Calendar sync is disabled. Set GOOGLE_CALENDAR_SYNC_ENABLED and GOOGLE_CALENDAR_ID."
                )
            )
            return

        queryset = Timeslot.objects.select_related("study").order_by("starts_at")
        if options["study_id"]:
            queryset = queryset.filter(study_id=options["study_id"])
        if not options["include_cancelled"]:
            queryset = queryset.filter(is_cancelled=False)

        created = 0
        updated = 0
        deleted = 0
        skipped = 0

        for timeslot in queryset:
            try:
                result = sync_timeslot_to_google_calendar(timeslot)
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f"{timeslot.pk}: {exc}"))
                continue

            action = result.get("action")
            if action == "created":
                created += 1
            elif action == "updated":
                updated += 1
            elif action == "deleted":
                deleted += 1
            else:
                skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Calendar sync complete. Created: {created}, updated: {updated}, deleted: {deleted}, skipped: {skipped}."
            )
        )
