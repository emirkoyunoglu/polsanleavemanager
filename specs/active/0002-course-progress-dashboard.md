# Spec 0002 — Eğitim ilerleme paneli

- Status: In progress
- Mode: lite
- Plan: `specs/plans/0002-plan.md`

## Intent
LearnHouse kurs ilerleme dışa aktarımı Türkçe tek sayfalık bir panelde gösterilir: kaç öğrenci ve
kurs kaydı var, ortalama ilerleme ne, hangi kurs ne kadar ilerledi, departman bazında durum nasıl. Başarı: demo dosyası değişip sayfa yenilendiğinde panelin tüm değerleri
dosyayla birebir örtüşür. Panel izin uygulamasından bağımsızdır ve onun davranışını değiştirmez.
Bilerek yapılmayanlar: dosya yükleme, XLSX desteği, veritabanı, giriş/roller, grafik kütüphanesi.

Önceki sürümdeki dosya yükleme formu (CSV/XLSX) kaldırıldı; panel `ornek-veri/learnhouse-demo.csv`
dosyasından beslenir (plan, adım 3).

## Requirements
- R-1 Panel, izin uygulamasından ayrı, tek komutla yerel olarak başlatılır; izin uygulamasının
  davranışını değiştirmez.
- R-2 Veri, her sayfa açılışında `ornek-veri/learnhouse-demo.csv` dosyasından (UTF-8, BOM'lu olabilir)
  yeniden okunur. Dosya değişip sayfa yenilendiğinde tüm değerler güncellenir; sayılar, adlar ve
  çubuk verileri sayfaya sabit yazılmaz.
- R-3 Dosya, LearnHouse dışa aktarımının dokuz sütununa (Sıra, Öğrenci, Departman, Kurs,
  Tamamlanan / Toplam, İlerleme, Durum, Kapsam, Filtreler) sahip olmalıdır; başka biçim desteklenmez.
- R-4 Üstte "Eğitim İlerleme Paneli" başlığı ve üç kart: Öğrenci (benzersiz öğrenci sayısı),
  Kurs Kaydı (kayıt sayısı), Ortalama İlerleme (İlerleme sütunundaki 0–1 oranlarının ortalaması,
  yüzde olarak, bir ondalık, Türkçe ondalık virgülüyle).
- R-5 "Kurslara Göre Ortalama İlerleme": her kurs kendi satırında; solda kurs adı, sağda ortalama
  yüzde, altında ince bir ilerleme çubuğu. En yüksek ortalama başta; eşitlikte kurs adına göre.
- R-6 Tablo: öğrenci, departman, kurs, tamamlanan/toplam ders, ilerleme (yüzde) ve durum sütunları.
  Durum etiketleri: "Tamamlandı" yeşil, "Devam ediyor" mavi, "Başlamadı" (ve diğerleri) gri.
- R-7 Tablo başlığında departman filtresi: "Tümü" ve dosyadaki departmanlar. Seçim değişince kartlar,
  kurs ortalamaları ve tablo yalnızca seçili departmanın kayıtlarıyla birlikte güncellenir.
  Dosyada olmayan bir departman istenirse "Tümü" gösterilir.
- R-8 Dosya bulunamaz, okunamaz, sütunları uyuşmaz ya da bir satırın ilerleme değerleri okunamazsa
  sayfada kısa bir Türkçe hata gösterilir; iç ayrıntı (stack trace, tam dosya yolu) sızmaz.

## User experience
- Flow: kullanıcı yerel adresi açar → paneli tüm kayıtlarla görür → tablo başlığından bir departman
  seçer → sayfa o departmanın değerleriyle yenilenir. CSV'yi değiştirip sayfayı yenileyince yeni
  değerleri görür.
- States:
  - **success** — kartlar, kurs ortalamaları, tablo (filtre "Tümü" ya da seçili departman).
  - **empty** — yalnızca başlık satırı olan dosya: kartlar 0 / 0 / %0,0, kurs bölümünde "Kayıt yok.",
    tablo boş.
  - **error** — R-8'deki durumlar: başlık ve kısa hata mesajı; panel gösterilmez.
  - **loading** — yok: sayfa sunucuda tek istekte hazırlanır.
  - **no permission** — yok: yerel çalışır, giriş/rol yoktur.
- Design reference: none — the flow above is the design. Görsel: açık gri zemin, beyaz kartlar,
  lacivert başlıklar, tek mavi vurgu rengi; telefonda kartlar alt alta, tablo kendi alanında yatay kayar.
- Accessibility: sayfa dili `tr`; filtre etiketli (`label`); ilerleme çubuklarında `aria-label` ve
  `aria-value*`; JavaScript kapalıyken filtre "Uygula" düğmesiyle çalışır.

## Constraints & out of scope
- Bootstrap 5 (CDN) ve az miktarda CSS; grafik kütüphanesi ve frontend build adımı yok.
- Yalnızca örnek LearnHouse CSV biçimi; veritabanı yok.
- OUT OF SCOPE: dosya yükleme, XLSX, kalıcı depolama, giriş/roller, izin uygulamasıyla entegrasyon,
  otomatik testler.

## Acceptance criteria
Kutular VERIFY'da (ayrı rol) işaretlenir.
- [ ] AC-1 — Demo dosyayla sayfa açılınca kartlar: Öğrenci = benzersiz öğrenci sayısı, Kurs Kaydı = veri satırı sayısı, Ortalama İlerleme = İlerleme oranlarının ortalaması × 100, bir ondalık, virgüllü (ör. %56,4).
- [ ] AC-2 — CSV'de bir değer değiştirilip sayfa yenilendiğinde kartlar, kurs ortalamaları ve tablo yeni değeri gösterir; uygulama yeniden başlatılmaz.
- [ ] AC-3 — Kurs ortalamaları: her kurs bir satırda, ad solda, yüzde sağda, altında ince çubuk; yüksekten düşüğe sıralı.
- [ ] AC-4 — Tablo, filtreye uyan her kayıt için öğrenci, departman, kurs, tamamlanan/toplam, ilerleme (%) ve durum gösterir.
- [ ] AC-5 — Durum etiketleri: "Tamamlandı" yeşil, "Devam ediyor" mavi, "Başlamadı" gri.
- [ ] AC-6 — Departman filtresi "Tümü" ve dosyadaki departmanları listeler; "Finans" seçilince kartlar, kurs ortalamaları ve tablo yalnızca Finans kayıtlarıyla hesaplanır (demo dosyada 7 / 14 / %62,5 ve 14 satır).
- [ ] AC-7 — Dosyada olmayan bir departman parametresi "Tümü" gibi davranır.
- [ ] AC-8 — Dosya yok, sütunlar uyumsuz ya da bir satırın ilerleme değeri bozuk → sayfada kısa Türkçe hata; stack trace ve tam dosya yolu yok.
- [ ] AC-9 — Yalnızca başlık satırı olan dosya → 0 / 0 / %0,0, "Kayıt yok." ve boş tablo.
- [ ] AC-10 — Telefon genişliğinde (≈375 px) kartlar alt alta; tablo kendi alanında yatay kayar, sayfa yatay kaymaz.
- [ ] AC-11 — Açık gri zemin, beyaz kartlar, lacivert başlıklar ve tek mavi vurgu rengi kullanılır.
- [ ] AC-12 — Sayılar, adlar ve çubuk verileri şablonda sabit yazılı değildir (şablon incelemesi).
- [ ] AC-13 — Panel tek komutla başlar; izin uygulamasının (`app/`, `static/`, `migrations/`) dosyalarına dokunulmamıştır.

## Definition of Done
- [ ] Every acceptance criterion mapped to proof (test or reproducible observation) — eşleme planda; kanıt yok, VERIFY çalıştırılmadı
- [ ] `scripts/check` green — çalıştırılmadı
- [ ] Independent review done; real findings fixed, noise rejected with written rationale — çalıştırılmadı
- [ ] Docs / ADRs updated if behavior or architecture changed — açık soru (plan, risk 2)
- [ ] Spec moved to `specs/done/` (it becomes immutable there)

## Scorecard (fill at ship — honest numbers make the process improvable)
| Metric | Value |
|---|---|
| Spec revisions | |
| Fix rounds | |
| Review findings: real / noise | |
| Regressions introduced | |
| Bugs escaped to production | |
