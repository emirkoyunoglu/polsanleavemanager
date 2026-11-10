"""Real holiday files: spec 0001 examples (AC-11, -12, -16, -23) and directory loading (AC-19)."""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from app.calendar.api import DEFAULT_DATA_DIR, InvalidHolidayData, init_calendar, working_days
from app.calendar.holiday_data import load_calendar

pytestmark = pytest.mark.integration


@pytest.fixture(autouse=True)
def _real_calendar() -> None:
    init_calendar(DEFAULT_DATA_DIR)


def test_br3_spec_example_october_2026() -> None:
    assert working_days(date(2026, 10, 26), date(2026, 10, 30)) == Decimal("3.5")


def test_br3_spec_example_ramazan_2026() -> None:
    assert working_days(date(2026, 3, 16), date(2026, 3, 23)) == Decimal("4.5")


def test_br3_spec_example_new_year_2027() -> None:
    assert working_days(date(2026, 12, 31), date(2027, 1, 1)) == Decimal("1")


def test_br3_spec_example_zafer_bayrami_2026() -> None:
    assert working_days(date(2026, 8, 24), date(2026, 8, 30)) == Decimal("5")


def test_load_calendar_rejects_file_name_that_differs_from_year(tmp_path: Path) -> None:
    (tmp_path / "2025.toml").write_text(
        'year = 2026\n[[holiday]]\ndate = 2026-10-29\nname = "X"\nkind = "full"\n',
        encoding="utf-8",
    )
    with pytest.raises(InvalidHolidayData) as raised:
        load_calendar(tmp_path)
    assert "2025.toml" in raised.value.detail


def test_load_calendar_rejects_empty_directory(tmp_path: Path) -> None:
    with pytest.raises(InvalidHolidayData):
        load_calendar(tmp_path)
