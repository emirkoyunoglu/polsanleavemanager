# Spec 0002 — Kurs ilerleme dashboard'u

- Status: In progress
- Mode: lite
- Plan: `specs/plans/0002-plan.md`
- Source: `ornek-veri/learnhouse-demo.csv`

## Intent
LearnHouse kurs ilerleme dışa aktarımını (CSV / XLSX) yükleyip Türkçe tek sayfalık bir özet görmek.
İzin uygulamasından bağımsız, ayrı çalışan küçük bir Flask uygulaması (`dashboard.py`); veritabanı yok,
yüklenen dosya diske yazılmaz.

## Tasks
- [x] T-1 — LearnHouse ilerleme dosyasını (CSV: `csv` modülü, XLSX: `openpyxl`) bellekte yükle, sütunları doğrula.
- [ ] T-2 — Özeti hesapla: kayıt, öğrenci, kurs sayısı, ders tamamlama ve ortalama ilerleme, en sık 5 kurs.
- [ ] T-3 — Bootstrap 5 dashboard'u göster: yükleme formu, özet kartı, en sık 5 kurs çubuğu, ilk 20 satır, hata mesajı.
