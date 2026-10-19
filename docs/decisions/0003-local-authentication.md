# ADR 0003 — İlk sürümde yerel kimlik doğrulama, SSO sonra

- Status: Accepted
- Date: 2026-10-19

## Context
Uygulama çalışan, yönetici ve İK verisi ile sağlık verisi (rapor nedeni; KVKK özel nitelikli veri)
taşır. Şirket hesabıyla SSO (Entra ID/LDAP) tenant erişimi ve uygulama kaydı gerektirir; ilk sürümü buna bağlamak istenmedi.

## Decision
İlk sürüm kendi kimlik doğrulamasını kullanır: argon2id ile hash'lenmiş parola ve `HttpOnly`,
`Secure`, `SameSite=Strict` oturum çerezi; yetkilendirme default-deny ve rol bazlıdır (`docs/security.md`).

## Consequences
- Kazanç: harici bağımlılık yok, hemen başlanabilir.
- Maliyet: parola saklama, sıfırlama ve brute-force koruması bizim sorumluluğumuzda.
- Maliyet: işten ayrılan çalışanın hesabı şirket dizininden otomatik kapanmaz — İK/Admin manuel kapatır.

## Alternatives considered
- Baştan SSO (Microsoft Entra ID) — parola tutulmaz ve hesap kapatma otomatik olur; tenant erişimi ve kayıt süreci ilk sürümü geciktirdiği için ertelendi.

## Revisit triggers
- Şirket dizini erişimi sağlanır ya da BT politikası SSO'yu zorunlu kılar.
- Bir güvenlik olayı ya da denetim bulgusu parola tabanlı girişi işaret eder.
