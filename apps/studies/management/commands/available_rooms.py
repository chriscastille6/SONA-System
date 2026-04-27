"""
Find available rooms from the Advising schedule workbooks.
"""
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.studies.room_schedule import find_available_rooms, RoomScheduleError


class Command(BaseCommand):
    help = "List available Powell/White rooms for a requested date and time window."

    def add_arguments(self, parser):
        parser.add_argument("--date", required=True, help="Date in YYYY-MM-DD format")
        parser.add_argument("--start", required=True, help="Start time in HH:MM or HHMM format")
        parser.add_argument("--end", required=True, help="End time in HH:MM or HHMM format")
        parser.add_argument(
            "--term",
            default=None,
            help='Optional term filter such as "Spring 2026"',
        )
        parser.add_argument(
            "--min-capacity",
            type=int,
            default=getattr(settings, "ROOM_AVAILABILITY_MIN_CAPACITY", 20),
            help="Minimum room capacity (default: ROOM_AVAILABILITY_MIN_CAPACITY)",
        )
        parser.add_argument(
            "--buildings",
            default=",".join(getattr(settings, "ROOM_AVAILABILITY_BUILDINGS", [])),
            help='Comma-separated buildings (default: "Powell Hall,White Hall")',
        )

    def handle(self, *args, **options):
        try:
            requested_date = datetime.strptime(options["date"], "%Y-%m-%d").date()
            start_time = self._parse_time(options["start"])
            end_time = self._parse_time(options["end"])
            buildings = [
                building.strip()
                for building in (options.get("buildings") or "").split(",")
                if building.strip()
            ]
            rooms = find_available_rooms(
                requested_date=requested_date,
                start_time=start_time,
                end_time=end_time,
                term=options.get("term"),
                buildings=buildings,
                min_capacity=options.get("min_capacity"),
            )
        except ValueError as exc:
            raise CommandError(str(exc)) from exc
        except RoomScheduleError as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(
            self.style.SUCCESS(
                f"Available rooms for {requested_date} {start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}:"
            )
        )
        if not rooms:
            self.stdout.write("  No rooms matched the requested window.")
            return

        for room in rooms:
            self.stdout.write(
                f"  - {room['room_key']} (capacity {room['capacity']}, source {room['source']})"
            )

    @staticmethod
    def _parse_time(raw_value):
        normalized = raw_value.strip()
        if ":" not in normalized and len(normalized) in {3, 4}:
            normalized = f"{normalized[:-2]}:{normalized[-2:]}"
        return datetime.strptime(normalized, "%H:%M").time()
