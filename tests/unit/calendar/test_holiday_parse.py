"""Holiday data validation — spec 0001 R-10, R-12 (AC-19). Parses text; no file I/O."""

from datetime import date

import pytest

from app.calendar.domain.working_days import HolidayKind, InvalidHolidayData
from app.calendar.holiday_data import parse_year

VALID = """
year = 2026

[[holiday]]
date = 2026-10-28
name = "Cumhuriyet Bayramı arifesi"
kind = "afternoon"

[[holiday]]
date = 2026-10-29
name = "Cumhuriyet Bayramı"
kind = "full"
"""


def test_valid_year_is_parsed() -> None:
    year, holidays = parse_year(VALID, "2026.toml")
    assert year == 2026
    assert [(h.day, h.kind) for h in holidays] == [
        (date(2026, 10, 28), HolidayKind.AFTERNOON),
        (date(2026, 10, 29), HolidayKind.FULL),
    ]


@pytest.mark.parametrize(
    "text",
    [
        pytest.param("year = 2026\n[[holiday]\n", id="unreadable-format"),
        pytest.param(
            'year = 2026\n[[holiday]]\ndate = 2026-10-29\nname = "X"\nkind = "evening"\n',
            id="unknown-kind",
        ),
        pytest.param(
            'year = 2026\n[[holiday]]\ndate = 2026-10-29\nname = "X"\nkind = ["full"]\n',
            id="kind-not-a-string",
        ),
        pytest.param(
            'year = 2026\n[[holiday]]\ndate = 2026-10-29\nname = "X"\nkind = "full"\n'
            '[[holiday]]\ndate = 2026-10-29\nname = "Y"\nkind = "full"\n',
            id="duplicate-date",
        ),
        pytest.param(
            'year = 2026\n[[holiday]]\ndate = 2027-01-01\nname = "X"\nkind = "full"\n',
            id="date-outside-year",
        ),
        pytest.param('[[holiday]]\ndate = 2026-10-29\nname = "X"\nkind = "full"\n', id="no-year"),
        pytest.param(
            'year = 2026\n[[holiday]]\ndate = "2026-10-29"\nname = "X"\nkind = "full"\n',
            id="date-as-string",
        ),
        pytest.param(
            'year = 2026\n[[holiday]]\ndate = 2026-10-29T00:00:00\nname = "X"\nkind = "full"\n',
            id="datetime-not-date",
        ),
        pytest.param(
            'year = 2026\n[[holiday]]\ndate = 2026-10-29\nname = ""\nkind = "full"\n',
            id="empty-name",
        ),
        pytest.param("year = 2026\n", id="no-holidays"),
    ],
)
def test_invalid_data_rejected(text: str) -> None:
    with pytest.raises(InvalidHolidayData) as raised:
        parse_year(text, "2026.toml")
    assert "2026.toml" in raised.value.detail
