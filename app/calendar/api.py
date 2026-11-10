"""Public interface of the calendar module — other modules import only this file
(docs/architecture.md, Forbidden dependencies 1).
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

from app.calendar.domain.working_days import (
    HalfDay,
    HalfDayNotAllowed,
    HolidayCalendar,
    HolidayDataMissing,
    InvalidDateRange,
    InvalidHolidayData,
    count_working_days,
)
from app.calendar.holiday_data import load_calendar

__all__ = [
    "DEFAULT_DATA_DIR",
    "HalfDay",
    "HalfDayNotAllowed",
    "HolidayDataMissing",
    "InvalidDateRange",
    "InvalidHolidayData",
    "init_calendar",
    "working_days",
]

DEFAULT_DATA_DIR = Path(__file__).parent / "data"

_calendar: HolidayCalendar | None = None


def init_calendar(data_dir: Path = DEFAULT_DATA_DIR) -> None:
    """Load and validate holiday data; called once at application startup (R-12)."""
    global _calendar
    _calendar = load_calendar(data_dir)


def working_days(start: date, end: date, half: HalfDay | None = None) -> Decimal:
    """Working days from start to end, both inclusive (BR-3, BR-4)."""
    if _calendar is None:
        raise RuntimeError("calendar not initialised: call init_calendar() at startup")
    return count_working_days(_calendar, start, end, half)
