# Spec 0001 — Uygulama iskeleti + iş günü hesabı

- Status: In progress
- Mode: lite
- Plan: `specs/plans/0001-plan.md`

## Intent
İK ve çalışanlar, bir izin aralığının kaç iş günü tuttuğunu tutarlı ve yasaya uygun biçimde bilmek
istiyor; bu sayı ileride bakiyeden düşülecek miktarın temelidir. Bu feature iki şey getirir: sonraki
tüm özelliklerin üzerine oturacağı çalışan bir uygulama iskeleti (uygulama ayağa kalkar, sağlık
kontrolü verir, otomatik kontroller `scripts/check` ve CI gerçekten çalışır) ve iki tarih arasındaki
iş günü sayısını hafta sonlarını ve resmi tatilleri (yarım gün tatiller dahil) düşerek hesaplayan
kural (BR-3, BR-4). Başarı: aynı aralık için hesap her zaman aynı sonucu verir ve bir İK uzmanının
elle yaptığı hesapla örtüşür. Bilerek yapılmayanlar: izin talebi, bakiye, giriş/roller, tatil
yönetim ekranı ve hesabın HTTP/ekran üzerinden kullanıma açılması (F6 ile gelir).

Clarify kararları (2026-10-19): tek spec, auth yok · çalışma haftası herkes için Pazartesi–Cuma ·
tatiller sürüm kontrolündeki yıl bazlı veri dosyasından · arifeler ve 28 Ekim 0,5 iş günü · hesap
yalnızca uygulama içi · tanımsız yıl → açık hata.

## Requirements

### Uygulama iskeleti
- R-1 Uygulama tek komutla yerel ortamda başlatılabilir; boş bir ortamda veritabanı altyapısını
  tekrarlanabilir biçimde (migration ile) kendisi hazırlar.
- R-2 Uygulama, kimlik doğrulama istemeyen bir sağlık kontrolü sunar; bu, bilinçli olarak herkese açık
  tek uç noktadır (ana sayfa dışında). Başka her şey ileride default-deny kuralına tabidir.
  Sağlık kontrolü veritabanına erişimi de yoklar; erişilemiyorsa "hazır değil" bildirir.
- R-3 Uygulama, ürün adını gösteren boş bir ana sayfa sunar.
- R-4 Bilinmeyen bir adres ya da beklenmeyen bir hata, `docs/conventions.md` "Error handling"
  biçiminde Türkçe bir hata yanıtı döner; iç ayrıntı (stack trace, dosya yolu, SQL) sızmaz.
- R-5 Otomatik kontroller gerçek adımlarla çalışır: lint, biçim, tip kontrolü, modül sınırları ve
  birim testleri (fast profil); entegrasyon testleri ve bağımlılık açığı taraması (yalnızca full).
  CI aynı kontrolü çalıştırır. Bir modül sınırı ihlali kontrolü kırmızıya çevirir.

### İş günü hesabı (calendar modülü)
- R-6 Verilen başlangıç ve bitiş tarihi (ikisi dahil) için iş günü sayısını 0,5 hassasiyetle verir.
  Yalnızca hafta sonu ve tatilden oluşan bir aralık için sonuç 0'dır ve bu bir hata değildir
  (sıfır günlük talebin reddi F6'nın kararıdır). Hafta sonuna denk gelen tatil ayrıca düşülmez.
- R-7 Çalışma haftası Pazartesi–Cuma'dır; Cumartesi ve Pazar 0 sayılır.
- R-8 Tam gün resmi tatil 0 sayılır. Yarım gün resmi tatil (bayram arifeleri ve 28 Ekim — 13:00'ten
  itibaren tatil) 0,5 sayılır.
- R-9 Tek günlük hesapta yarım gün seçilebilir: sabah ya da öğleden sonra. Normal iş gününde her
  ikisi 0,5'tir; yarım gün tatilde sabah 0,5, öğleden sonra 0'dır; tam tatilde ve hafta sonunda 0'dır.
  Birden çok günlük aralıkta yarım gün seçimi yoktur.
- R-10 Resmi tatiller, sürüm kontrolündeki yıl bazlı bir veri dosyasından okunur; her tatil tarihi,
  adı ve türü (tam / yarım) ile kayıtlıdır. 2026 ve 2027 yılları bu feature ile gelir ve resmi
  kaynakla (Resmî Gazete / Diyanet takvimi) karşılaştırılarak doğrulanır.
- R-11 Aralığın dokunduğu yıllardan biri için tatil verisi yoksa hesap yapılmaz; hata, eksik yılı adıyla belirtir.
- R-12 Tatil verisi geçersizse (okunamayan biçim, bilinmeyen tür, aynı tarihin iki kez geçmesi,
  dosyanın yılı dışında bir tarih) uygulama açılışta hatayla durur; hatalı veriyle çalışmaz.
- R-13 Başlangıç tarihi bitiş tarihinden sonraysa hesap yapılmaz, açık bir hata döner.
- R-14 Hesap yalnızca calendar modülünün public arayüzünden kullanılır; bu feature'da HTTP üzerinden açılmaz.

## User experience
- Flow: kullanıcı tarayıcıda uygulamanın ana adresini açar → ürün adını ve "hazırlanıyor"
  bilgisini gösteren ana sayfayı görür. Başka ekran yoktur; iş günü hesabının arayüzü yoktur (F6).
- States: yalnızca **success** (statik sayfa). Veri yüklenmediği için empty / loading / error /
  no permission durumları bu sayfada oluşmaz; sayfa sunulamazsa tarayıcının bağlantı hatası görünür.
- Design reference: none — the flow above is the design.
- Accessibility: sayfa dili `tr` olarak işaretlidir, anlamlı bir başlığı ve ana başlığı (h1) vardır;
  metin, arka planla WCAG AA kontrastını sağlar.

## Constraints & out of scope
- Stack ve sınırlar: `docs/architecture.md`, ADR 0001–0003. Tarih ve miktar kuralları:
  `docs/conventions.md` "Data rules" (saat içermeyen tarih, `Decimal`, float yok).
- Hesap; "bugün"e, saat dilimine ya da çalıştığı makineye bağlı olmaz.
- Aralık uzunluğuna yapay bir üst sınır konmaz; tatil verisi tanımlı yıllar içindeki her aralık hesaplanır (sınırı R-11 koyar).
- Performans: tek bir hesap, bir yıllık aralık için insan fark edemeyeceği kadar hızlıdır (< 50 ms).
- `docs/domain.md` BR-3, yarım gün tatilleri (R-8) içerecek şekilde güncellenir.
- OUT OF SCOPE: giriş/roller (F4), çalışan ve organizasyon (F3), izin talebi ve bakiye (F6),
  tatil yönetim ekranı, hesabın HTTP/ekran üzerinden açılması, çalışana özel çalışma takvimi,
  kamu sektörüne özgü idari izin / köprü günleri, birden çok günlük aralıkta yarım gün başlangıç/bitiş,
  e2e testleri (bu feature'da test edilecek kullanıcı akışı yok; ilk e2e F8 ile).

## Acceptance criteria
Örnek tarihlerin haftanın günleri hesaplanarak doğrulandı.

### Uygulama iskeleti
- [ ] AC-1 — Uygulama başlatıldığında sağlık kontrolü, kimlik bilgisi olmadan başarılı (çalışıyor) yanıtı döner; veritabanına erişilemediğinde 503 (hazır değil) döner.
- [ ] AC-2 — Ana adres, dili `tr` olan, ürün adını başlık ve h1 olarak gösteren bir HTML sayfası döner.
- [ ] AC-3 — Bilinmeyen bir adres 404 ve Türkçe `problem+json` yanıtı döner.
- [ ] AC-4 — Beklenmeyen bir hata 500 ve genel bir Türkçe mesaj döner; yanıtta stack trace, dosya yolu ya da istisna metni bulunmaz.
- [ ] AC-5 — Boş bir ortamda migration'lar sıfırdan sona kadar hatasız uygulanır ve ikinci kez uygulamak bir şey değiştirmez.
- [ ] AC-6 — `./scripts/check` ve `./scripts/check --fast` gerçek adımlarla yeşildir (`CHECK GREEN (full, …)` ve `(fast, …)`); her iki profilde residue testi temizdir (boşta bir makinede).
- [ ] AC-7 — Bir modülün başka bir modülün `api.py` dışındaki koduna import eklemesi `./scripts/check`'i kırmızıya çevirir (ihlal edilmiş bir örnekle gösterilir, sonra geri alınır).
- [ ] AC-8 — CI'da `check` işi aynı adımlarla yeşil çalışır.

### İş günü hesabı
- [ ] AC-9 — Normal hafta: 2026-10-19 (Pzt) – 2026-10-23 (Cum) → 5.
- [ ] AC-10 — Hafta sonu: 2026-10-24 (Cmt) – 2026-10-25 (Paz) → 0.
- [ ] AC-11 — Tam ve yarım tatil: 2026-10-26 (Pzt) – 2026-10-30 (Cum) → 3,5 (28 Ekim 0,5; 29 Ekim 0).
- [ ] AC-12 — Bayram ve arife: 2026-03-16 (Pzt) – 2026-03-23 (Pzt) → 4,5 (19 Mart arife 0,5; 20 Mart Ramazan Bayramı 0; 21–22 hafta sonu).
- [ ] AC-13 — Tek gün = başlangıç ve bitiş aynı: normal iş günü → 1; tam tatil (2026-10-29) → 0; arife (2026-10-28) → 0,5.
- [ ] AC-14 — Yarım gün seçimi: normal iş gününde sabah 0,5 ve öğleden sonra 0,5; 2026-10-28'de sabah 0,5 ve öğleden sonra 0; 2026-10-29'da ve bir Cumartesi'de 0.
- [ ] AC-15 — Birden çok günlük aralıkta yarım gün seçimi reddedilir.
- [ ] AC-16 — Yıl sınırı: 2026-12-31 (Per) – 2027-01-01 (Cum, yılbaşı) → 1.
- [ ] AC-17 — Tanımsız yıl: 2027-12-31 – 2028-01-03 hesabı, 2028'i adıyla belirten bir hatayla reddedilir.
- [ ] AC-18 — Başlangıç > bitiş (2026-10-23 – 2026-10-19) açık bir hatayla reddedilir.
- [ ] AC-19 — Geçersiz tatil verisi (bozuk biçim, bilinmeyen tür, tekrar eden tarih, yıl dışı tarih — her biri ayrı) uygulamanın açılışını hatayla durdurur.
- [ ] AC-20 — Sonuç her zaman `Decimal` türündedir ve 0,5'in katıdır; aynı girdiyle tekrar çağrı aynı sonucu verir.
- [ ] AC-21 — 2026 ve 2027 tatil dosyaları resmi kaynakla karşılaştırılmıştır (karşılaştırma kaynağı ve sonucu PR'da).
- [ ] AC-22 — `docs/domain.md` BR-3, yarım gün tatilleri içerecek şekilde güncellenmiştir.
- [ ] AC-23 — Hafta sonuna denk gelen tatil çift düşülmez: 2026-08-24 (Pzt) – 2026-08-30 (Paz, Zafer Bayramı) → 5.

## Definition of Done
- [ ] Every acceptance criterion mapped to proof (test or reproducible observation)
- [ ] `scripts/check` green
- [ ] Independent review done; real findings fixed, noise rejected with written rationale
- [ ] Docs / ADRs updated if behavior or architecture changed
- [ ] Spec moved to `specs/done/` (it becomes immutable there)

## Scorecard (fill at ship — honest numbers make the process improvable)
| Metric | Value |
|---|---|
| Spec revisions | |
| Fix rounds | |
| Review findings: real / noise | |
| Regressions introduced | |
| Bugs escaped to production | |
