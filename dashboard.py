"""Eğitim İlerleme Paneli (spec 0002) — izin uygulamasından bağımsız, ayrı çalışan Flask uygulaması.

Çalıştırma: .venv/Scripts/python dashboard.py  →  http://127.0.0.1:5000/
Veri her istekte ornek-veri/learnhouse-demo.csv dosyasından okunur; CSV değişip sayfa yenilenince
tüm değerler güncellenir. Veritabanı yoktur.
"""

from __future__ import annotations

import csv
from pathlib import Path

from flask import Flask, render_template, request

DATA_FILE = Path(__file__).resolve().parent / "ornek-veri" / "learnhouse-demo.csv"
EXPECTED_COLUMNS = [
    "Sıra",
    "Öğrenci",
    "Departman",
    "Kurs",
    "Tamamlanan / Toplam",
    "İlerleme",
    "Durum",
    "Kapsam",
    "Filtreler",
]
STATUS_BADGES = {"Tamamlandı": "text-bg-success", "Devam ediyor": "text-bg-primary"}
TR_ALPHABET = "0123456789abcçdefgğhıijklmnoöprsştuüvyz"

app = Flask(__name__)


class DataFileError(Exception):
    """Veri dosyası okunamadı ya da beklenen biçimde değil; mesaj kullanıcıya gösterilir."""


def tr_sort_key(text: str) -> list[int]:
    lowered = text.replace("I", "ı").replace("İ", "i").lower()
    return [
        TR_ALPHABET.find(ch) if ch in TR_ALPHABET else len(TR_ALPHABET) + ord(ch) for ch in lowered
    ]


def percent(ratio: float) -> str:
    return f"%{ratio * 100:.1f}".replace(".", ",")


def load_records(path: Path = DATA_FILE) -> list[dict[str, object]]:
    """CSV'yi utf-8-sig ile okur, sütunları doğrular ve satırları kayıtlara çevirir."""
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            table = [row for row in csv.reader(handle) if any(cell.strip() for cell in row)]
    except FileNotFoundError:
        raise DataFileError(f"Veri dosyası bulunamadı: {path.name}") from None
    except OSError, UnicodeDecodeError, csv.Error:
        raise DataFileError(f"Veri dosyası okunamadı: {path.name}") from None

    if not table or [h.strip() for h in table[0]] != EXPECTED_COLUMNS:
        raise DataFileError("Veri dosyasının sütunları LearnHouse ilerleme biçimiyle eşleşmiyor.")

    records = []
    for line_no, row in enumerate(table[1:], start=2):
        if len(row) != len(EXPECTED_COLUMNS):
            raise DataFileError(f"{line_no}. satırda sütun sayısı hatalı.")
        cells = dict(zip(EXPECTED_COLUMNS, (cell.strip() for cell in row), strict=True))
        try:
            done, total = (int(part) for part in cells["Tamamlanan / Toplam"].split("/"))
            ratio = float(cells["İlerleme"].replace(",", "."))
        except ValueError:
            raise DataFileError(f"{line_no}. satırda ilerleme değerleri okunamadı.") from None
        records.append(
            {
                "student": cells["Öğrenci"],
                "department": cells["Departman"],
                "course": cells["Kurs"],
                "lessons": f"{done} / {total}",
                "ratio": ratio,
                "progress": percent(ratio),
                "status": cells["Durum"],
                "badge": STATUS_BADGES.get(cells["Durum"], "text-bg-secondary"),
            }
        )
    return records


def summarize(records: list[dict[str, object]]) -> dict[str, object]:
    """Kartlar ve kurs ortalamaları; seçili departmanın kayıtları üzerinden hesaplanır."""
    count = len(records)
    by_course: dict[str, list[float]] = {}
    for rec in records:
        by_course.setdefault(str(rec["course"]), []).append(float(rec["ratio"]))  # type: ignore[arg-type]
    courses = [
        {"name": name, "width": round(sum(r) / len(r) * 100, 1), "label": percent(sum(r) / len(r))}
        for name, r in by_course.items()
    ]
    courses.sort(key=lambda c: (-c["width"], tr_sort_key(c["name"])))  # type: ignore[arg-type,operator]
    avg = sum(float(rec["ratio"]) for rec in records) / count if count else 0.0  # type: ignore[arg-type]
    return {
        "students": len({rec["student"] for rec in records}),
        "enrollments": count,
        "avg_progress": percent(avg),
        "courses": courses,
    }


@app.get("/")
def index() -> str:
    try:
        records = load_records()
    except DataFileError as exc:
        return render_template("dashboard.html", error=str(exc))

    departments = sorted({str(rec["department"]) for rec in records}, key=tr_sort_key)
    selected = request.args.get("departman", "")
    if selected not in departments:
        selected = ""
    visible = [rec for rec in records if not selected or rec["department"] == selected]
    return render_template(
        "dashboard.html",
        error=None,
        source=DATA_FILE.name,
        departments=departments,
        selected=selected,
        summary=summarize(visible),
        records=visible,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
