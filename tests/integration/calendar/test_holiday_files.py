"""Spec 0001 examples against the real 2026/2027 holiday files (AC-11, AC-12, AC-16, AC-23)."""

from datetime import date
from decimal import Decimal

import pytest

from app.calendar.api import DEFAULT_DATA_DIR, init_calendar, working_days

pytestmark = pytest.mark.integration


@pytest.fixture(autouse=True)
def _real_calendar() -> None:
    init_calendar(DEFAULT_DATA_DIR)


def test_spec_example_october_2026() -> None:
    assert working_days(date(2026, 10, 26), date(2026, 10, 30)) == Decimal("3.5")


def test_spec_example_ramazan_2026() -> None:
    assert working_days(date(2026, 3, 16), date(2026, 3, 23)) == Decimal("4.5")


def test_spec_example_new_year_2027() -> None:
    assert working_days(date(2026, 12, 31), date(2027, 1, 1)) == Decimal("1")


def test_spec_example_zafer_bayrami_2026() -> None:
    assert working_days(date(2026, 8, 24), date(2026, 8, 30)) == Decimal("5")
