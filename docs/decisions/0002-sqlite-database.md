# ADR 0002 — Veritabanı: SQLite (SQLAlchemy 2 + Alembic)

- Status: Accepted
- Date: 2026-10-19

## Context
İlk sürüm şirket içi, tek sunucuda çalışacak; kullanıcı sayısı küçük ve yazma yükü düşük (izin
talepleri ve onaylar). Önerilen PostgreSQL yerine ekip, kurulum ve işletim kolaylığı için SQLite seçti.

## Decision
Veritabanı SQLite'tır; erişim yalnızca SQLAlchemy 2 (ORM/Core) üzerinden, şema değişiklikleri Alembic ile yapılır.
Dialect'e özel SQL yazılmaz, böylece PostgreSQL'e geçiş bir bağlantı adresi ve migration testi işi olarak kalır.

## Consequences
- Kazanç: ayrı veritabanı sunucusu yok; testler geçici dosyayla hızlı ve izole çalışır; yedek = dosya kopyası.
- Maliyet: eşzamanlı yazımlar serileşir (tek yazar). WAL modu açılır ve kısa transaction kuralı uygulanır.
- Maliyet: `Numeric` SQLite'ta gerçek decimal değildir — `Decimal` dönüşümü SQLAlchemy tip katmanında yapılır ve testle korunur.
- Maliyet: Alembic'te SQLite `ALTER TABLE` kısıtları nedeniyle batch mode kullanılır.

## Alternatives considered
- PostgreSQL — eşzamanlılık ve tarih/aralık tipleri daha güçlü; kurulum/işletim yükü nedeniyle ilk sürümde tercih edilmedi.
- SQL Server — şirkette MSSQL altyapısı zorunluluğu yok.

## Revisit triggers
- "database is locked" hataları ya da yazma gecikmesi kullanıcıya yansır.
- Birden fazla uygulama sunucusu (yatay ölçek) gerekir.
- Yedekleme/KVKK denetimi sunucu tarafı şifreleme ya da erişim denetimi ister.
