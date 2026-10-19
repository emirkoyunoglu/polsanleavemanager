# Conventions

> Buradaki her kural ya araçla (tercih edilen) ya da review'da denetlenir.

## Language
- Chat language (interviews, sessions): Türkçe
- Document language (docs/, specs, plans, ADRs, review and verify reports): Türkçe
- Always English (protocol, not prose): ANEW core files, template headings and field labels,
  `Status:` values (Draft / Approved / In progress / Shipped), `Approved by / on:`, `Source:`.
- Code identifiers, branch names, commit messages: İngilizce. Kullanıcıya görünen metinler (arayüz,
  hata mesajlarının `title`/`detail` alanları) Türkçe.
- Agent messages (handoff summaries, refusals, `Next:` lines): chat language; command names, file
  paths and protocol fields verbatim.

## Language & framework versions
- Python 3.14 · FastAPI · SQLAlchemy 2.x (2.0 stili, typed `Mapped[...]`) · Alembic · Pydantic v2.
- Veritabanı: SQLite (ADR 0002). Dialect'e özel SQL yazılmaz; her şey SQLAlchemy Core/ORM üzerinden.
- Frontend: sade HTML + ES modülleri (JavaScript) + CSS; npm, bundler ve framework yok.
- Bağımlılıklar `pyproject.toml` içinde sürüm aralığıyla, kilitli sürümler `requirements*.txt` ile tutulur.

## Naming
- Python: modül/fonksiyon/değişken `snake_case`, sınıf `PascalCase`, sabit `UPPER_SNAKE`.
- Domain terimleri kodda `docs/domain.md` tablosundaki İngilizce karşılığıyla yazılır (`LeaveRequest`, `Entitlement`).
- Testler: `tests/<unit|integration|e2e>/<module>/test_<konu>.py`; test adı davranışı söyler:
  `test_br5_request_exceeding_balance_is_rejected`. İş kuralı testleri adında `brN` taşır.
- HTTP: `/api/<module>/<kaynak-çoğul>` (`/api/leave/requests`), JSON alanları `snake_case`.
- Frontend dosyaları: `static/<sayfa>.html`, `static/js/<sayfa>.js`, `static/css/`.

## Error handling
- Domain kodu yalnızca `app.shared.errors.DomainError` alt sınıflarını fırlatır (ör. `InsufficientBalance`, `NotAllowed`).
- Tek bir FastAPI exception handler bunları **RFC 9457 `application/problem+json`** yanıtına çevirir
  (`type`, `title`, `status`, `detail`; Türkçe metin). Doğrulama hataları 422, yetki 403, bulunamadı 404, kural ihlali 409/422.
- Beklenmeyen hata: 500 + genel bir mesaj ve korelasyon kimliği; stack trace, SQL, dosya yolu ve
  istisna metni kullanıcıya **asla** dönmez, yalnızca sunucu loguna yazılır.
- Hata yutulmaz: `except Exception: pass` yasak.

## Data rules
- İzin günleri saat içermeyen `datetime.date`; zaman damgaları timezone-aware UTC `datetime`.
  Kullanıcıya gösterim `Europe/Istanbul`. Naive `datetime` yasak.
- İzin süresi ve bakiye `decimal.Decimal` (0,5 adım); `float` yasak. Veritabanında `Numeric(5, 1)`.
- Kimlikler UUID (v4); otomatik artan integer ID dışarı açılmaz.
- "Bugün" ve "şimdi" yalnızca enjekte edilen bir saat (`Clock`) üzerinden alınır; testler sabit saat kullanır.
- Kişisel veri (doğum tarihi, rapor nedeni) loglara yazılmaz.

## Enforced by tooling
- `ruff check` (lint, import sırası) ve `ruff format --check` (biçim).
- `mypy --strict` (tip kontrolü; `float` izin alanları da tiplerden yakalanır).
- `lint-imports` (import-linter): `docs/architecture.md` "Forbidden dependencies" 1–3.
- `pytest --strict-markers`: tanımsız marker kullanımı hata verir.
Hepsi `scripts/check.conf` adımlarıdır.
