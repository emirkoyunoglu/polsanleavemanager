"""Working-day count — BR-3, BR-4 (spec 0001, AC-9..AC-18, AC-20, AC-23).

The calendar here is built in memory from the 2026/2027 entries the examples touch, so these
tests pin the rule itself; tests/integration/calendar/test_holiday_files.py runs the same
examples against the real data files.
"""

from datetime import date
from decimal import Decimal

import pytest

from app.calendar.domain.working_days import (
    HalfDay,
    HalfDayNotAllowed,
    Holiday,
    HolidayCalendar,
    HolidayDataMissing,
    HolidayKind,
    InvalidDateRange,
    count_working_days,
)

FULL = HolidayKind.FULL
AFTERNOON = HolidayKind.AFTERNOON


@pytest.fixture
def calendar() -> HolidayCalendar:
    return HolidayCalendar(
        {
            2026: [
                Holiday(date(2026, 3, 19), "Ramazan Bayramı arifesi", AFTERNOON),
                Holiday(date(2026, 3, 20), "Ramazan Bayramı 1. gün", FULL),
                Holiday(date(2026, 3, 21), "Ramazan Bayramı 2. gün", FULL),
                Holiday(date(2026, 3, 22), "Ramazan Bayramı 3. gün", FULL),
                Holiday(date(2026, 8, 30), "Zafer Bayramı", FULL),
                Holiday(date(2026, 10, 28), "Cumhuriyet Bayramı arifesi", AFTERNOON),
                Holiday(date(2026, 10, 29), "Cumhuriyet Bayramı", FULL),
            ],
            2027: [Holiday(date(2027, 1, 1), "Yılbaşı", FULL)],
        }
    )


def test_br3_full_week_is_five(calendar: HolidayCalendar) -> None:
    assert count_working_days(calendar, date(2026, 10, 19), date(2026, 10, 23)) == Decimal("5")


def test_br3_weekend_is_zero(calendar: HolidayCalendar) -> None:
    assert count_working_days(calendar, date(2026, 10, 24), date(2026, 10, 25)) == Decimal("0")


def test_br3_full_and_half_holiday_in_week(calendar: HolidayCalendar) -> None:
    assert count_working_days(calendar, date(2026, 10, 26), date(2026, 10, 30)) == Decimal("3.5")


def test_br3_bayram_with_eve(calendar: HolidayCalendar) -> None:
    assert count_working_days(calendar, date(2026, 3, 16), date(2026, 3, 23)) == Decimal("4.5")


@pytest.mark.parametrize(
    ("day", "expected"),
    [
        (date(2026, 10, 27), Decimal("1")),  # ordinary working day
        (date(2026, 10, 29), Decimal("0")),  # full holiday
        (date(2026, 10, 28), Decimal("0.5")),  # afternoon holiday (eve)
    ],
)
def test_br3_single_day_cases(calendar: HolidayCalendar, day: date, expected: Decimal) -> None:
    assert count_working_days(calendar, day, day) == expected


@pytest.mark.parametrize(
    ("day", "half", "expected"),
    [
        (date(2026, 10, 27), HalfDay.MORNING, Decimal("0.5")),
        (date(2026, 10, 27), HalfDay.AFTERNOON, Decimal("0.5")),
        (date(2026, 10, 28), HalfDay.MORNING, Decimal("0.5")),
        (date(2026, 10, 28), HalfDay.AFTERNOON, Decimal("0")),
        (date(2026, 10, 29), HalfDay.MORNING, Decimal("0")),
        (date(2026, 10, 29), HalfDay.AFTERNOON, Decimal("0")),
        (date(2026, 10, 24), HalfDay.MORNING, Decimal("0")),  # Saturday
        (date(2026, 10, 24), HalfDay.AFTERNOON, Decimal("0")),
    ],
)
def test_br4_half_day_selection(
    calendar: HolidayCalendar, day: date, half: HalfDay, expected: Decimal
) -> None:
    assert count_working_days(calendar, day, day, half) == expected


def test_br4_half_day_on_multi_day_range_rejected(calendar: HolidayCalendar) -> None:
    with pytest.raises(HalfDayNotAllowed):
        count_working_days(calendar, date(2026, 10, 19), date(2026, 10, 20), HalfDay.MORNING)


def test_br3_year_boundary(calendar: HolidayCalendar) -> None:
    assert count_working_days(calendar, date(2026, 12, 31), date(2027, 1, 1)) == Decimal("1")


def test_br3_missing_year_names_the_year(calendar: HolidayCalendar) -> None:
    with pytest.raises(HolidayDataMissing) as raised:
        count_working_days(calendar, date(2027, 12, 31), date(2028, 1, 3))
    assert raised.value.years == (2028,)
    assert "2028" in raised.value.detail


def test_br3_start_after_end_rejected(calendar: HolidayCalendar) -> None:
    with pytest.raises(InvalidDateRange):
        count_working_days(calendar, date(2026, 10, 23), date(2026, 10, 19))


@pytest.mark.parametrize(
    ("start", "end", "half"),
    [
        (date(2026, 10, 26), date(2026, 10, 30), None),
        (date(2026, 3, 16), date(2026, 3, 23), None),
        (date(2026, 1, 1), date(2026, 12, 31), None),
        (date(2026, 10, 28), date(2026, 10, 28), HalfDay.MORNING),
    ],
)
def test_br4_result_is_decimal_multiple_of_half_and_deterministic(
    calendar: HolidayCalendar, start: date, end: date, half: HalfDay | None
) -> None:
    first = count_working_days(calendar, start, end, half)
    assert type(first) is Decimal
    assert (first * 2) % 1 == 0
    assert count_working_days(calendar, start, end, half) == first


def test_br3_holiday_on_weekend_not_double_counted(calendar: HolidayCalendar) -> None:
    assert count_working_days(calendar, date(2026, 8, 24), date(2026, 8, 30)) == Decimal("5")
