# Architecture

## System overview
Polsan izin yönetimi, tek süreçte çalışan bir **modular monolith**tir: Python 3.14 + FastAPI
backend, SQLAlchemy 2 + Alembic ile SQLite veritabanı, FastAPI'nin statik olarak sunduğu sade
HTML/JavaScript/CSS frontend (build adımı yok). Tek ekip ve tek ürün için mikroservis maliyeti
karşılığını vermez; modül sınırları ise import-linter ile testle korunur, böylece monolit dağılmaz
(ADR 0001). Veritabanı seçimi ADR 0002, kimlik doğrulama ADR 0003.

```
app/
  main.py               # FastAPI uygulaması, router kayıtları, hata handler'ı
  shared/               # yalnızca teknik ortaklar (db oturumu, hata tipleri, saat) — domain kuralı yok
  <module>/
    api.py              # modülün PUBLIC arayüzü — diğer modüller yalnızca bunu import eder
    domain/             # saf Python: varlıklar, kurallar (BR-n), domain exception'ları
    service.py          # use case'ler, yetki kontrolü, transaction sınırı
    persistence.py      # SQLAlchemy modelleri ve repository'ler (modülün kendi tabloları)
    routes.py           # HTTP endpoint'leri (FastAPI router)
static/                 # HTML/JS/CSS — yalnızca HTTP API'yi çağırır
migrations/             # Alembic
tests/                  # unit/, integration/, e2e/ (docs/testing.md)
```

## Modules / components and ownership

| Module | Single responsibility | Owns |
|---|---|---|
| `organization` | Çalışanlar, işe giriş/doğum tarihleri, yönetici hiyerarşisi | Çalışan kayıtları, raporlama ilişkisi |
| `calendar` | Resmi tatiller ve iş günü hesabı | Tatil takvimi |
| `leave` | İzin talebi, onay akışı, hak ediş (BR-1), bakiye ve hareketleri | Talepler, bakiye hareketleri |
| `identity` | Kullanıcı hesabı, parola, oturum, rol | Kullanıcılar, oturumlar, rol atamaları |
| `audit` | Değiştirilemez denetim kaydı | Denetim kayıtları |

Her modülün tabloları kendi önekini taşır (`leave_*`, `org_*`, …); başka modül o tablolara SQL ile erişmez.

## Communication rules
- Modüller arası iletişim **senkron fonksiyon çağrısıdır** ve yalnızca hedef modülün `api.py`
  dosyasındaki fonksiyonlar/DTO'lar üzerinden yapılır. ORM nesneleri modül dışına çıkmaz; DTO döner.
- Denetim kaydı, değişikliği yapan servis tarafından `audit.api` çağrılarak **aynı transaction içinde** yazılır.
- Mesaj kuyruğu, arka plan işçisi ve harici servis çağrısı yoktur (bkz. Deliberately out of scope).
- Frontend yalnızca `/api/...` HTTP uç noktalarını çağırır.

## Forbidden dependencies (make them testable)
Hepsi `pyproject.toml` içindeki import-linter kontratları ile `scripts/check` adımında denetlenir.
1. Bir modül, başka bir modülün `api.py` dışındaki hiçbir alt modülünü import edemez
   (`app.leave.service` → `app.organization.persistence` yasak; `app.organization.api` serbest).
2. `app.<module>.domain` paketleri `fastapi`, `starlette`, `sqlalchemy` ve diğer modülleri import edemez.
3. `app.shared` hiçbir domain modülünü import edemez.
4. `static/` JavaScript'i yalnızca `fetch('/api/...')` ile veri alır; sunucu tarafı şablon ile veritabanı verisi gömülmez (review'da denetlenir).

## Deliberately out of scope
- Bordro, SGK/e-Devlet ve muhasebe entegrasyonları.
- SSO (Entra ID / LDAP) — ilk sürüm yerel kimlik doğrulama kullanır (ADR 0003).
- Çok şirketli (multi-tenant) yapı; sistem tek şirket (Polsan) içindir.
- Doğum izni, süt izni ve diğer özel izin türleri; vekil atama; ekip izin takvimi.
- E-posta/anlık bildirim.
- Mobil uygulama ve frontend framework'ü (React vb.).
