"""Working-day count (docs/domain.md BR-3, BR-4). Pure Python: no I/O, no framework.

The working week is Monday–Friday. A full-day public holiday counts 0, an afternoon holiday
(bayram eves and 28 October, off from 13:00) counts 0.5. Results are Decimal in 0.5 steps.
"""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from enum import StrEnum

from app.shared.errors import DomainError

ZERO = Decimal("0")
HALF_DAY = Decimal("0.5")
FULL_DAY = Decimal("1")

_SATURDAY = 5


class HolidayKind(StrEnum):
    FULL = "full"
    AFTERNOON = "afternoon"


class HalfDay(StrEnum):
    MORNING = "morning"
    AFTERNOON = "afternoon"


@dataclass(frozen=True)
class Holiday:
    day: date
    name: str
    kind: HolidayKind


class InvalidHolidayData(DomainError):
    title = "Geçersiz tatil verisi"


class HolidayDataMissing(DomainError):
    title = "Tatil takvimi eksik"

    def __init__(self, years: tuple[int, ...]) -> None:
        listed = ", ".join(str(year) for year in years)
        super().__init__(f"{listed} yılı için resmi tatil takvimi tanımlı değil.")
        self.years = years


class InvalidDateRange(DomainError):
    title = "Geçersiz tarih aralığı"

    def __init__(self) -> None:
        super().__init__("Başlangıç tarihi bitiş tarihinden sonra olamaz.")


class HalfDayNotAllowed(DomainError):
    title = "Yarım gün seçilemez"

    def __init__(self) -> None:
        super().__init__("Yarım gün yalnızca tek günlük aralıkta seçilebilir.")


class HolidayCalendar:
    """Public holidays per year. A year absent from the mapping is unknown, not holiday-free."""

    def __init__(self, years: Mapping[int, Iterable[Holiday]]) -> None:
        by_day: dict[date, Holiday] = {}
        for year, holidays in years.items():
            for holiday in holidays:
                if holiday.day.year != year:
                    raise InvalidHolidayData(
                        f"{holiday.day.isoformat()} tarihi {year} yılı verisinde yer alamaz."
                    )
                if holiday.day in by_day:
                    raise InvalidHolidayData(
                        f"{holiday.day.isoformat()} tarihi birden çok kez tanımlı."
                    )
                by_day[holiday.day] = holiday
        self._years = frozenset(years)
        self._by_day = by_day

    def require_years(self, start: date, end: date) -> None:
        missing = tuple(y for y in range(start.year, end.year + 1) if y not in self._years)
        if missing:
            raise HolidayDataMissing(missing)

    def day_value(self, day: date) -> Decimal:
        if day.weekday() >= _SATURDAY:
            return ZERO
        holiday = self._by_day.get(day)
        if holiday is None:
            return FULL_DAY
        return ZERO if holiday.kind is HolidayKind.FULL else HALF_DAY


def count_working_days(
    calendar: HolidayCalendar, start: date, end: date, half: HalfDay | None = None
) -> Decimal:
    """Working days from start to end, both inclusive (spec 0001, R-6..R-11, R-13)."""
    if start > end:
        raise InvalidDateRange()
    if half is not None and start != end:
        raise HalfDayNotAllowed()
    calendar.require_years(start, end)

    if half is not None:
        return _half_day_value(calendar.day_value(start), half)

    total = ZERO
    day = start
    while day <= end:
        total += calendar.day_value(day)
        day += timedelta(days=1)
    return total


def _half_day_value(day_value: Decimal, half: HalfDay) -> Decimal:
    if day_value == ZERO:
        return ZERO
    if day_value == HALF_DAY:
        # Afternoon holiday: only the morning is working time.
        return HALF_DAY if half is HalfDay.MORNING else ZERO
    return HALF_DAY
