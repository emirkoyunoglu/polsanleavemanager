"""LearnHouse kurs ilerleme dashboard'u (spec 0002) — izin uygulamasından bağımsız, ayrı çalışır.

Çalıştırma: .venv/Scripts/python dashboard.py  →  http://127.0.0.1:5000/
Yüklenen dosya yalnızca bellekte okunur; diske yazılmaz, veritabanı yoktur.
"""

from __future__ import annotations

import csv
import io
import zipfile
from collections import Counter
from pathlib import Path

from flask import Flask, render_template, request
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

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
PREVIEW_ROWS = 20
MAX_UPLOAD_BYTES = 5 * 1024 * 1024

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES


class FileFormatError(Exception):
    """Dosya beklenen LearnHouse ilerleme biçiminde değil; mesaj kullanıcıya gösterilir."""


def _cell(value: object) -> str:
    return "" if value is None else str(value).strip()


def _read_csv(data: bytes) -> list[list[str]]:
    text = data.decode("utf-8-sig")
    return [[_cell(v) for v in row] for row in csv.reader(io.StringIO(text))]


def _read_xlsx(data: bytes) -> list[list[str]]:
    workbook = load_workbook(io.BytesIO(data), read_only=True, data_only=True)
    try:
        sheet = workbook.active
        return [[_cell(v) for v in row] for row in sheet.iter_rows(values_only=True)]
    finally:
        workbook.close()


def load_rows(filename: str, data: bytes) -> tuple[list[str], list[list[str]]]:
    """Dosyayı okur, başlıkları doğrular; (başlıklar, veri satırları) döner."""
    suffix = Path(filename).suffix.lower()
    try:
        if suffix == ".csv":
            table = _read_csv(data)
        elif suffix == ".xlsx":
            table = _read_xlsx(data)
        else:
            raise FileFormatError("Yalnızca .csv ve .xlsx dosyaları desteklenir.")
    except (UnicodeDecodeError, csv.Error, zipfile.BadZipFile, InvalidFileException, KeyError, OSError):
        raise FileFormatError("Dosya okunamadı; bozuk ya da beklenen biçimde değil.") from None

    table = [row for row in table if any(row)]
    if not table:
        raise FileFormatError("Dosya boş.")

    headers = table[0]
    while headers and not headers[-1]:
        headers = headers[:-1]
    if headers != EXPECTED_COLUMNS:
        raise FileFormatError("Sütunlar LearnHouse kurs ilerleme dışa aktarımıyla eşleşmiyor.")

    rows = []
    for line_no, row in enumerate(table[1:], start=2):
        row = row + [""] * (len(headers) - len(row))
        if any(row[len(headers):]):
            raise FileFormatError(f"{line_no}. satırda fazladan sütun var.")
        rows.append(row[: len(headers)])
    return headers, rows


def summarize(rows: list[list[str]]) -> dict[str, object]:
    """Gerçek sütunlardan özet: sayılar, ders tamamlama, ortalama ilerleme, durumlar, en sık 5 kurs."""
    col = {name: i for i, name in enumerate(EXPECTED_COLUMNS)}
    done_lessons = total_lessons = 0
    progress_sum = 0.0
    for line_no, row in enumerate(rows, start=2):
        try:
            done, total = (int(part) for part in row[col["Tamamlanan / Toplam"]].split("/"))
            progress_sum += float(row[col["İlerleme"]].replace(",", "."))
        except ValueError:
            raise FileFormatError(f"{line_no}. satırda ilerleme değerleri okunamadı.") from None
        done_lessons += done
        total_lessons += total

    count = len(rows)
    courses = Counter(row[col["Kurs"]] for row in rows)
    top_courses = [
        {"name": name, "count": n, "percent": round(100 * n / count, 1)} for name, n in courses.most_common(5)
    ]
    return {
        "students": len({row[col["Öğrenci"]] for row in rows}),
        "courses": len(courses),
        "done_lessons": done_lessons,
        "total_lessons": total_lessons,
        "avg_progress": round(100 * progress_sum / count, 1) if count else 0.0,
        "statuses": Counter(row[col["Durum"]] for row in rows).most_common(),
        "top_courses": top_courses,
    }


@app.route("/", methods=["GET", "POST"])
def index() -> str:
    context: dict[str, object] = {"error": None, "filename": None}
    if request.method == "POST":
        upload = request.files.get("file")
        if upload is None or not upload.filename:
            context["error"] = "Lütfen bir dosya seçin."
        else:
            try:
                headers, rows = load_rows(upload.filename, upload.read())
                summary = summarize(rows)
            except FileFormatError as exc:
                context["error"] = str(exc)
            else:
                context.update(
                    filename=upload.filename,
                    headers=headers,
                    total=len(rows),
                    summary=summary,
                    preview=rows[:PREVIEW_ROWS],
                )
    return render_template("dashboard.html", **context)


@app.errorhandler(413)
def too_large(_error: Exception) -> tuple[str, int]:
    message = f"Dosya çok büyük (en fazla {MAX_UPLOAD_BYTES // (1024 * 1024)} MB)."
    return render_template("dashboard.html", error=message, filename=None), 413


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
