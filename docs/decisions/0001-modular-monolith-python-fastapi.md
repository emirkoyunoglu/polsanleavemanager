# ADR 0001 — Python/FastAPI modular monolith, sade HTML/JS frontend

- Status: Accepted
- Date: 2026-10-19

## Context
Polsan için şirket içi bir izin yönetimi uygulaması gerekiyor: küçük ekip, tek ürün, tek şirket.
Bootstrap mülakatında önce .NET + React önerildi; ekip Python, FastAPI ve sade HTML/JS/CSS ile
çalışmayı tercih etti. İş kuralları (İş Kanunu md. 53, KVKK) ileride büyüyecek; sınırların erken korunması gerekiyor.

## Decision
Uygulama, Python 3.14 + FastAPI ile tek süreçte çalışan bir modular monolith olarak yazılır;
modüller (`organization`, `calendar`, `leave`, `identity`, `audit`) birbirine yalnızca `api.py` üzerinden
erişir ve bu kural import-linter ile `scripts/check` içinde denetlenir. Frontend, FastAPI'nin statik
olarak sunduğu build adımsız HTML/JS/CSS'tir.

## Consequences
- Kazanç: tek deploy, tek dil (backend), düşük operasyon yükü; sınırlar araçla korunduğu için ileride bir modülü ayırmak mümkün.
- Kazanç: frontend için npm/bundler zinciri yok; bağımlılık yüzeyi ve tedarik zinciri riski küçük.
- Maliyet: Python'da sınırları dil değil araç korur — import-linter kontratları bakımlı tutulmalı.
- Maliyet: framework'süz frontend'de bileşen yeniden kullanımı ve durum yönetimi elle yapılır; arayüz büyürse zorlaşır.

## Alternatives considered
- .NET 10 + React — güçlü tip sistemi ve decimal/tarih tipleri; ekip tercihi Python olduğu için elendi.
- Katmanlı tek paket (routers/services/models) — başlaması hızlı, ama modül sınırı olmadığı için büyüdükçe dağılır.
- Mikroservisler — tek ekip ve tek ürün için operasyon maliyeti karşılığını vermez.

## Revisit triggers
- Frontend ekran sayısı ~15'i geçer ya da karmaşık istemci durumu gerekir → bir frontend framework'ü için yeni ADR.
- Bir modülün bağımsız ölçeklenmesi ya da ayrı ekibe geçmesi gerekir.
