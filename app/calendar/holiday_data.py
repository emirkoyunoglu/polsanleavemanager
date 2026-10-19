"""Versioned public-holiday data (spec 0001 R-10, R-12): one TOML file per year in data/.

Any defect stops loading with InvalidHolidayData naming the file — the app never runs on
half-valid holiday data.
"""

import tomllib
from collections.abc import Callable
from datetime import date, datetime
from pathlib import Path
from typing import Any

from app.calendar.domain.working_days import (
    Holiday,
    HolidayCalendar,
    HolidayKind,
    InvalidHolidayData,
)


def parse_year(text: str, source: str) -> tuple[int, list[Holiday]]:
    def invalid(reason: str) -> InvalidHolidayData:
        return InvalidHolidayData(f"{source}: {reason}")

    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise invalid(f"dosya okunamadı ({exc}).") from exc

    year = data.get("year")
    if not isinstance(year, int) or isinstance(year, bool):
        raise invalid("'year' alanı eksik ya da tam sayı değil.")

    entries = data.get("holiday")
    if not isinstance(entries, list) or not entries:
        raise invalid("hiç tatil kaydı yok.")

    holidays: list[Holiday] = []
    seen: set[date] = set()
    for index, entry in enumerate(entries, start=1):
        holiday = _parse_entry(entry, index, invalid)
        if holiday.day.year != year:
            raise invalid(f"{holiday.day.isoformat()} tarihi {year} yılına ait değil.")
        if holiday.day in seen:
            raise invalid(f"{holiday.day.isoformat()} tarihi birden çok kez tanımlı.")
        seen.add(holiday.day)
        holidays.append(holiday)
    return year, holidays


def _parse_entry(entry: Any, index: int, invalid: Callable[[str], InvalidHolidayData]) -> Holiday:
    if not isinstance(entry, dict):
        raise invalid(f"{index}. kayıt geçersiz.")
    day = entry.get("date")
    # tomllib returns datetime for date-times; datetime is a date subclass, so exclude it.
    if not isinstance(day, date) or isinstance(day, datetime):
        raise invalid(f"{index}. kaydın 'date' alanı bir tarih (YYYY-AA-GG) değil.")
    name = entry.get("name")
    if not isinstance(name, str) or not name.strip():
        raise invalid(f"{index}. kaydın 'name' alanı boş.")
    kind = entry.get("kind")
    if not isinstance(kind, str) or kind not in {k.value for k in HolidayKind}:
        raise invalid(f"{index}. kaydın 'kind' alanı 'full' ya da 'afternoon' olmalı.")
    return Holiday(day, name.strip(), HolidayKind(kind))


def load_calendar(data_dir: Path) -> HolidayCalendar:
    years: dict[int, list[Holiday]] = {}
    for path in sorted(data_dir.glob("*.toml")):
        year, holidays = parse_year(path.read_text(encoding="utf-8"), path.name)
        if path.stem != str(year):
            raise InvalidHolidayData(f"{path.name}: dosya adı yılla ({year}) uyuşmuyor.")
        years[year] = holidays
    if not years:
        raise InvalidHolidayData(f"{data_dir}: hiç tatil verisi bulunamadı.")
    return HolidayCalendar(years)
