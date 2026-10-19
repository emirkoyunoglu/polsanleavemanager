# Domain

> Polsan izin yönetimi: çalışanlar izin talep eder, doğrudan yöneticileri onaylar, İK bakiyeleri
> izler. Yıllık izin hakkı 4857 sayılı İş Kanunu md. 53'e göre hesaplanır. Bir terim burada yoksa
> anlamını uydurma — sor (`prompts/recovery/`).

## Ubiquitous language

| Term | Meaning | Notes / not to be confused with |
|---|---|---|
| Çalışan (`Employee`) | Sisteme kayıtlı, izin talep edebilen kişi. Bir doğrudan yöneticisi olur (en üst kademe hariç). | Kullanıcı hesabı (`User`, Identity) ile aynı şey değil; bir çalışanın bir hesabı olur. |
| Yönetici (`Manager`) | Bir çalışanın doğrudan bağlı olduğu çalışan. Onay yetkisi bu ilişkiden gelir. | "Sistem Yöneticisi" (Admin) değildir. |
| Üst yönetici | Yöneticinin yöneticisi. Yöneticinin kendi talebini onaylar. | |
| İK (`HR`) | Tüm talepleri görür, onay/reddi devralabilir (override), düzeltme yapar, rapor alır. | |
| Sistem Yöneticisi (`Admin`) | Kullanıcı, rol ve takvim (resmi tatil) yönetir. İzin onaylamaz. | |
| İzin talebi (`LeaveRequest`) | Bir çalışanın belirli tarih aralığı ve izin türü için açtığı kayıt. | |
| İzin türü (`LeaveType`) | `Annual` (yıllık), `Excuse` (mazeret), `Unpaid` (ücretsiz), `Sick` (rapor/hastalık). | |
| Talep durumu | `Pending` (beklemede), `Approved`, `Rejected`, `CancellationRequested`, `Cancelled`. | Durum adları kodda İngilizce, arayüzde Türkçe. |
| Yıllık izin hakkı (`Entitlement`) | Hizmet yılı dolduğunda çalışana tanımlanan yıllık izin günü (BR-1). | Bakiye değildir. |
| Bakiye (`Balance`) | Kullanılabilir yıllık izin günü = haklar − onaylı kullanımlar − bekleyen talepler (rezerv) ± İK düzeltmeleri. | Saklanan bir sayı değil; hareketlerden (ledger) türetilir. |
| Bakiye hareketi (`BalanceEntry`) | Bakiyeyi değiştiren her olayın değiştirilemez kaydı (hak ediş, kullanım, iade, düzeltme). | |
| İş günü | Hafta sonu ve resmi tatil olmayan gün. İzin süresi iş günü ile sayılır. | Takvim günü değil. |
| Yarım gün | 0,5 iş günü; izin süresinin en küçük birimi. | |
| Kıdem | İşe giriş tarihinden itibaren hizmet süresi (deneme süresi dahil). | |
| Override | İK'nın yönetici yerine onay/ret vermesi. Her zaman denetim kaydına yazılır. | |
| Denetim kaydı (`AuditEntry`) | Kim, ne zaman, neyi, hangi eski/yeni değerle değiştirdi. Silinmez, değiştirilmez. | Uygulama logu değildir. |

## Business rules

- **BR-1 Yıllık izin hakkı (md. 53).** Kıdem 1 yıl (dahil) – 5 yıl (hariç): 14 gün; 5 – 15 yıl
  (hariç): 20 gün; 15 yıl ve üstü: 26 gün. 18 yaş altı ve 50 yaş ve üstü çalışanlara en az 20 gün.
  Hak, her hizmet yılı dolduğunda (işe giriş yıldönümü) tanımlanır; ilk yıl dolmadan yıllık izin hakkı yoktur.
- **BR-2 Kullanılmayan yıllık izin yanmaz**, sonraki yıla devreder.
- **BR-3 İş günü sayımı.** İzin süresi yalnızca iş günleri sayılarak hesaplanır; çalışma haftası
  herkes için Pazartesi–Cuma'dır. Hafta sonu (Cumartesi, Pazar) ve tam gün resmi tatiller 0 sayılır
  (md. 56). Yarım gün resmi tatiller — bayram arifeleri ve 28 Ekim, 13:00'ten itibaren (2429 sayılı
  Kanun) — 0,5 iş günü sayılır. Hafta sonuna denk gelen tatil ayrıca düşülmez. Tatil takvimi
  tanımlı olmayan bir yıla dokunan hesap yapılmaz (spec 0001).
- **BR-4 Yarım gün.** Talepler 0,5 gün adımlarıyla açılabilir; tek günlük talep sabah ya da öğleden sonra yarım olabilir.
- **BR-5 Eksi bakiye yok.** Yıllık izin talebi, bakiyeyi 0'ın altına düşürecekse açılamaz.
  Bekleyen talepler bakiyeden rezerve edilir.
- **BR-6 Çakışma yok.** Bir çalışanın `Pending`, `Approved` veya `CancellationRequested` durumundaki
  talepleri tarih olarak çakışamaz.
- **BR-7 Mazeret izni (ek md. 2).** Evlilik, evlat edinme, birinci derece yakının ya da kardeşin
  ölümü: 3 gün; eşin doğum yapması (babalık): 5 gün. Ücretlidir, yıllık izin bakiyesinden düşmez.
- **BR-8 Ücretsiz izin** yönetici onayı gerektirir, bakiyeden düşmez, İK raporunda ayrıca görünür.
- **BR-9 Rapor/hastalık izni** onay akışına girmez; İK, rapora dayanarak kaydeder. Bakiyeden düşmez.
  Rapor nedeni yalnızca İK'ya görünür (KVKK — `docs/security.md`).
- **BR-10 Tek kademeli onay.** Talebi çalışanın doğrudan yöneticisi onaylar ya da reddeder.
  Kimse kendi talebini onaylayamaz: yöneticinin talebi üst yöneticisine, yöneticisi olmayanın talebi İK'ya gider.
- **BR-11 İK override.** İK herhangi bir bekleyen talebi onaylayabilir ya da reddedebilir; işlem denetim kaydına yazılır.
- **BR-12 İptal.** Onaylı bir izin, başlangıç gününden önce çalışan tarafından iptal talebine
  (`CancellationRequested`) alınabilir; bakiye yalnızca yönetici iptali onaylarsa iade edilir.
  Bekleyen talebi çalışan doğrudan geri çekebilir.
- **BR-13 Başlamış/geçmiş izin** yalnızca İK tarafından düzeltilebilir; düzeltme yeni bir bakiye
  hareketi ve denetim kaydı üretir, eski kayıt değişmez.

## Key domain invariants

- Yıllık izin bakiyesi hiçbir zaman 0'ın altında olamaz.
- Bakiye yalnızca bakiye hareketlerinden türetilir; hareketler eklenir, asla güncellenmez ya da silinmez.
- Kimse kendi izin talebini onaylayamaz — İK override dahil (İK çalışanının talebini başka bir İK ya da yöneticisi onaylar).
- Onaylı ya da geçmiş bir talep silinmez; değişiklik her zaman yeni bir kayıt ve denetim kaydıdır.
- Sağlık nedeni (rapor) İK dışında hiçbir role görünmez — API yanıtları ve loglar dahil.
