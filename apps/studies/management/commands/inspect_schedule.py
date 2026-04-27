"""
Inspect an Advising schedule workbook so column mapping can be verified.
"""
from django.core.management.base import BaseCommand, CommandError

from apps.studies.room_schedule import inspect_schedule_file, RoomScheduleError


class Command(BaseCommand):
    help = "Inspect a schedule .xlsx file and print sheet names plus preview rows."

    def add_arguments(self, parser):
        parser.add_argument("file_path", help="Absolute path to the schedule .xlsx file")
        parser.add_argument(
            "--sheet",
            type=int,
            default=0,
            help="Zero-based sheet index to inspect (default: 0)",
        )
        parser.add_argument(
            "--preview-rows",
            type=int,
            default=5,
            help="Number of preview rows to print (default: 5)",
        )

    def handle(self, *args, **options):
        try:
            result = inspect_schedule_file(
                options["file_path"],
                sheet_name=options["sheet"],
                preview_rows=options["preview_rows"],
            )
        except RoomScheduleError as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(self.style.SUCCESS(f"File: {result['file_name']}"))
        self.stdout.write(f"Selected sheet: {result['selected_sheet']}")
        self.stdout.write(f"All sheets: {', '.join(result['sheet_names'])}")
        self.stdout.write(f"Configured header row: {result['header_row']}")
        self.stdout.write("Configured column mapping:")
        for normalized, raw in result["column_map"].items():
            self.stdout.write(f"  {normalized}: {raw}")

        self.stdout.write("\nPreview:")
        for index, row in enumerate(result["preview_rows"], start=1):
            rendered = " | ".join(str(value) for value in row)
            self.stdout.write(f"  Row {index}: {rendered}")
