"""
Excel-backed room availability utilities.

These helpers read the Advising schedule workbooks and answer:
"Which Powell/White rooms are free for this date/time window?"
"""
from __future__ import annotations

import json
import re
from datetime import date, datetime, time, timedelta
from functools import lru_cache
from pathlib import Path

from django.conf import settings

try:
    import pandas as pd
except ImportError:  # pragma: no cover - handled at runtime with a clear error
    pd = None


DAY_CODE_TO_WEEKDAY = {
    "M": 0,
    "T": 1,
    "W": 2,
    "R": 3,
    "F": 4,
    "S": 5,
    "U": 6,
}

TERM_PATTERN = re.compile(r"(Spring|Summer|Fall|Winter)\s+\d{4}", re.IGNORECASE)


class RoomScheduleError(Exception):
    """Base error for room schedule planning."""


class ScheduleConfigurationError(RoomScheduleError):
    """Raised when the schedule directory or files are unavailable."""


class ScheduleParsingError(RoomScheduleError):
    """Raised when a schedule workbook cannot be parsed."""


def _require_excel_dependencies():
    if pd is None:
        raise ScheduleConfigurationError(
            "Excel support is not installed. Add pandas and openpyxl to the Python environment."
        )


def get_schedule_dir() -> Path:
    schedule_dir = getattr(settings, "ROOM_SCHEDULE_DIR", "")
    if not schedule_dir:
        raise ScheduleConfigurationError(
            "ROOM_SCHEDULE_DIR is not configured. Point it at the Advising schedule folder."
        )
    path = Path(schedule_dir).expanduser()
    if not path.exists():
        raise ScheduleConfigurationError(
            f"ROOM_SCHEDULE_DIR does not exist: {path}"
        )
    return path


def extract_term_from_filename(file_name: str) -> str:
    match = TERM_PATTERN.search(file_name)
    if match:
        return match.group(0).title()
    return Path(file_name).stem


def get_schedule_files(term: str | None = None) -> list[Path]:
    schedule_dir = get_schedule_dir()
    files = sorted(schedule_dir.glob("*.xlsx"))
    if term:
        term_lower = term.lower()
        files = [path for path in files if term_lower in path.name.lower()]
    if not files:
        if term:
            raise ScheduleConfigurationError(
                f"No schedule files found in {schedule_dir} for term '{term}'."
            )
        raise ScheduleConfigurationError(f"No .xlsx schedule files found in {schedule_dir}.")
    return files


def get_available_terms() -> list[str]:
    try:
        files = get_schedule_files()
    except ScheduleConfigurationError:
        return []
    terms = {extract_term_from_filename(path.name) for path in files}
    return sorted(terms)


def _clean_text(value) -> str:
    if value is None:
        return ""
    if pd is not None and pd.isna(value):
        return ""
    text = str(value).strip()
    if text.lower() == "nan":
        return ""
    return text


def _parse_date(value) -> date | None:
    if value is None or _clean_text(value) == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if pd is not None and isinstance(value, pd.Timestamp):
        return value.date()
    if isinstance(value, (int, float)):
        base = date(1899, 12, 30)
        return base + timedelta(days=float(value))
    try:
        return datetime.fromisoformat(str(value)).date()
    except ValueError:
        pass
    parsed = pd.to_datetime(value, errors="coerce") if pd is not None else None
    if parsed is None or pd.isna(parsed):
        return None
    return parsed.date()


def _parse_time(value) -> time | None:
    if value is None or _clean_text(value) == "":
        return None
    if isinstance(value, datetime):
        return value.time().replace(second=0, microsecond=0)
    if isinstance(value, time):
        return value.replace(second=0, microsecond=0)
    if pd is not None and isinstance(value, pd.Timestamp):
        return value.time().replace(second=0, microsecond=0)
    if isinstance(value, (int, float)):
        if 0 <= float(value) < 1:
            total_minutes = round(float(value) * 24 * 60)
            hours = total_minutes // 60
            minutes = total_minutes % 60
            return time(hour=hours % 24, minute=minutes)
        digits = str(int(value)).zfill(4)
    else:
        raw = _clean_text(value)
        if ":" in raw:
            parsed = datetime.strptime(raw, "%H:%M")
            return parsed.time()
        digits = re.sub(r"\D", "", raw)
    if not digits:
        return None
    if len(digits) == 3:
        digits = f"0{digits}"
    if len(digits) != 4:
        return None
    return time(hour=int(digits[:2]), minute=int(digits[2:]))


def _parse_int(value) -> int:
    text = _clean_text(value)
    if not text:
        return 0
    try:
        return int(float(text))
    except ValueError:
        return 0


def canonical_room_key(building: str, room: str) -> str:
    return f"{_clean_text(building)} {_clean_text(room)}".strip()


def _default_room_catalog_path() -> Path:
    return Path(__file__).resolve().parent / "data" / "cob_rooms.json"


@lru_cache(maxsize=1)
def load_room_catalog() -> list[dict]:
    path = _default_room_catalog_path()
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _get_column_map() -> dict[str, str]:
    return getattr(settings, "ROOM_SCHEDULE_COLUMN_MAP", {})


def _normalized_dataframe(file_path: Path):
    _require_excel_dependencies()
    header_row = getattr(settings, "ROOM_SCHEDULE_HEADER_ROW", 1)
    df = pd.read_excel(file_path, sheet_name=0, header=header_row, engine="openpyxl")
    df.columns = [str(column).strip() for column in df.columns]

    column_map = _get_column_map()
    rename_map = {}
    for normalized_name, raw_name in column_map.items():
        if raw_name in df.columns:
            rename_map[raw_name] = normalized_name
    df = df.rename(columns=rename_map)

    required_columns = [
        "building",
        "room",
        "days",
        "begin",
        "end",
        "max_capacity",
        "begin_date",
        "end_date",
    ]
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise ScheduleParsingError(
            f"{file_path.name} is missing expected columns: {', '.join(missing)}"
        )

    df["building"] = df["building"].map(_clean_text)
    df["room"] = df["room"].map(_clean_text)
    df["days"] = df["days"].map(lambda value: _clean_text(value).upper())
    df["begin_date"] = df["begin_date"].map(_parse_date)
    df["end_date"] = df["end_date"].map(_parse_date)
    df["begin"] = df["begin"].map(_parse_time)
    df["end"] = df["end"].map(_parse_time)
    df["max_capacity"] = df["max_capacity"].map(_parse_int)
    df["room_key"] = df.apply(
        lambda row: canonical_room_key(row["building"], row["room"]),
        axis=1,
    )

    return df[
        (df["building"] != "")
        & (df["room"] != "")
        & (df["days"] != "")
        & df["begin"].notna()
        & df["end"].notna()
        & df["begin_date"].notna()
        & df["end_date"].notna()
    ]


def inspect_schedule_file(
    file_path: str | Path,
    *,
    sheet_name: int = 0,
    preview_rows: int = 5,
) -> dict:
    _require_excel_dependencies()
    path = Path(file_path)
    workbook = pd.ExcelFile(path, engine="openpyxl")
    preview = pd.read_excel(
        path,
        sheet_name=sheet_name,
        header=None,
        nrows=preview_rows,
        engine="openpyxl",
    ).fillna("")
    return {
        "file_name": path.name,
        "sheet_names": workbook.sheet_names,
        "selected_sheet": workbook.sheet_names[sheet_name],
        "header_row": getattr(settings, "ROOM_SCHEDULE_HEADER_ROW", 1) + 1,
        "column_map": _get_column_map(),
        "preview_rows": preview.values.tolist(),
    }


def collect_room_inventory(term: str | None = None) -> list[dict]:
    room_inventory: dict[str, dict] = {}

    for room in load_room_catalog():
        room_inventory[room["room_key"]] = {
            "building": room["building"],
            "room": room["room"],
            "room_key": room["room_key"],
            "capacity": int(room["estimated_capacity"]),
            "source": "catalog",
        }

    for file_path in get_schedule_files(term):
        df = _normalized_dataframe(file_path)
        for row in df.itertuples(index=False):
            room_key = row.room_key
            observed_capacity = int(row.max_capacity or 0)
            existing = room_inventory.get(room_key)
            if existing is None or observed_capacity > existing["capacity"]:
                room_inventory[room_key] = {
                    "building": row.building,
                    "room": row.room,
                    "room_key": room_key,
                    "capacity": observed_capacity,
                    "source": "schedule",
                }

    return sorted(
        room_inventory.values(),
        key=lambda room: (room["building"], room["room"]),
    )


def _room_occurs_on_date(row, requested_date: date) -> bool:
    if requested_date < row.begin_date or requested_date > row.end_date:
        return False
    valid_day_codes = {code for code in row.days if code in DAY_CODE_TO_WEEKDAY}
    target_codes = {
        code
        for code, weekday in DAY_CODE_TO_WEEKDAY.items()
        if weekday == requested_date.weekday()
    }
    return bool(valid_day_codes & target_codes)


def _overlaps(start_a: time, end_a: time, start_b: time, end_b: time) -> bool:
    return (start_a < end_b) and (end_a > start_b)


def find_busy_rooms(
    *,
    requested_date: date,
    start_time: time,
    end_time: time,
    term: str | None = None,
    buildings: list[str] | None = None,
) -> set[str]:
    buildings = buildings or list(getattr(settings, "ROOM_AVAILABILITY_BUILDINGS", []))
    busy_rooms: set[str] = set()

    for file_path in get_schedule_files(term):
        df = _normalized_dataframe(file_path)
        filtered = df[df["building"].isin(buildings)] if buildings else df
        for row in filtered.itertuples(index=False):
            if not _room_occurs_on_date(row, requested_date):
                continue
            if _overlaps(row.begin, row.end, start_time, end_time):
                busy_rooms.add(row.room_key)

    return busy_rooms


def find_available_rooms(
    *,
    requested_date: date,
    start_time: time,
    end_time: time,
    term: str | None = None,
    buildings: list[str] | None = None,
    min_capacity: int | None = None,
) -> list[dict]:
    if end_time <= start_time:
        raise RoomScheduleError("End time must be after start time.")

    buildings = buildings or list(getattr(settings, "ROOM_AVAILABILITY_BUILDINGS", []))
    min_capacity = (
        min_capacity
        if min_capacity is not None
        else int(getattr(settings, "ROOM_AVAILABILITY_MIN_CAPACITY", 20))
    )

    room_inventory = collect_room_inventory(term)
    busy_rooms = find_busy_rooms(
        requested_date=requested_date,
        start_time=start_time,
        end_time=end_time,
        term=term,
        buildings=buildings,
    )

    available_rooms = []
    for room in room_inventory:
        if buildings and room["building"] not in buildings:
            continue
        if room["capacity"] < min_capacity:
            continue
        if room["room_key"] in busy_rooms:
            continue
        available_rooms.append(room)

    return available_rooms
