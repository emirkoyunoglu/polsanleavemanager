# Security

> Her plan ve review bu kurallara uyar. Ürünün en büyük hukuki riski KVKK'dır (sağlık verisi).

## Secrets
- Secrets never enter the repo, specs, prompts, or chat. `.env` is gitignored; provide `.env.example`.
- Agents never print secret values, even when debugging.
- Oturum imzalama anahtarı ve benzerleri yalnızca ortam değişkeninden okunur; kodda varsayılan değer yoktur.

## Input & output
- Tüm HTTP girdileri Pydantic modelleriyle sınırda doğrulanır; doğrulanmamış veri servis katmanına girmez.
- SQL yalnızca SQLAlchemy ile, parametreli; string birleştirme ile SQL yasak.
- Frontend'de kullanıcı verisi DOM'a yalnızca `textContent` ile yazılır; `innerHTML` ile kullanıcı verisi yasak (XSS).
- Hata yanıtları `docs/conventions.md` "Error handling" kuralına uyar; iç ayrıntı sızmaz.
- Güvenlik başlıkları: `Content-Security-Policy` (yalnızca `'self'`, inline script yok), `X-Content-Type-Options: nosniff`.

## AuthN / AuthZ
- Kimlik doğrulama: yerel hesap, parola **argon2id** ile hash'lenir; oturum çerezi `HttpOnly`,
  `Secure`, `SameSite=Strict`. Başarısız giriş denemeleri sınırlandırılır (ADR 0003).
- **Default-deny:** her endpoint gereken rolü açıkça beyan eder; beyan etmeyen endpoint'e erişim
  reddedilir. Yetki kontrolü servis katmanında yapılır, yalnızca UI'da gizlemek yetki değildir.
- Roller: Çalışan, Yönetici, İK, Sistem Yöneticisi (`docs/domain.md`).
- Kendi verisi: çalışan yalnızca kendi talep ve bakiyesini, yönetici yalnızca kendi doğrudan
  ekibininkileri görür; İK hepsini görür. Bir başkasının kaydına erişim 404 döner (varlık sızdırılmaz).
- **KVKK — özel nitelikli veri:** rapor/hastalık izninin nedeni ve belgesi yalnızca İK'ya görünür;
  yöneticiye yalnızca tarih aralığı ve "izinli" bilgisi gider. Bu alanlar API yanıt modellerinde rol
  bazlı ayrı şemalarla verilir ve loglanmaz.
- Onay, override, iptal ve düzeltme işlemleri denetim kaydına yazılır (`audit`).

## Dependencies
- Yeni bağımlılığı bir insan onaylar (plan içinde gerekçesiyle): lisans (MIT/BSD/Apache uyumlu),
  bakım durumu (son 12 ay içinde sürüm) ve bilinen açıklar kontrol edilir.
- `pip-audit` bilinen CVE'leri tarar; full `scripts/check` profilinde çalışır.

## Review lens
Security is a mandatory dimension of every independent review (see `prompts/review.md`), not a
separate afterthought phase.
