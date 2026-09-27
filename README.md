# KEP (Kayıtlı Elektronik Posta) Adresi Doğrulayıcı 📬⚖️

[![Python CI](https://github.com/eimza-kep/kep-adresi-dogrulayici/actions/workflows/ci.yml/badge.svg)](https://github.com/eimza-kep/kep-adresi-dogrulayici/actions)
[![Lisans: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Standart: RFC 5322 & BTK](https://img.shields.io/badge/Standart-BTK%20KEP-success.svg)](https://btk.gov.tr)
[![Blog](https://img.shields.io/badge/Rehber-KEP%20Akademisi-blue.svg)](https://kep-akademisi.pages.dev/)

Türkiye'de **BTK mevzuatı, 6102 Sayılı Türk Ticaret Kanunu (Madde 18/3)** ve **7201 Sayılı Tebligat Kanunu** kapsamında kullanılan KEP (Kayıtlı Elektronik Posta) ve UETS adreslerinin sözdizimini (syntax), kurumsal alt alan adlarını (subdomain), yetkili KEP Hizmet Sağlayıcısını (KEPHS) ve DNS posta sunucusu durumunu denetleyen açık kaynaklı CLI aracıdır.

---

## ✨ Öne Çıkan Özellikler

* ⚡ **Sıfır Bağımlılık (Zero-Dependency):** Harici kütüphane gerektirmeyen saf Python standart kütüphanesi mimarisi.
* 🏢 **Tüm BTK KEPHS Sağlayıcıları:** TÜRKKEP (`hs01`, `hs03`), TN KEP (`hs02`), PTT KEP (`ptt.kep.tr`), E-Tuğra (`hs05`), TÜBİTAK BİLGEM (`hs07`), EDM (`hs09`) ve Klon Bilişim eşleşmesi.
* 🌐 **Kurumsal Subdomain Desteği:** `banka.hs02.kep.tr`, `sirket.hs01.kep.tr` gibi kurumsal alt alan adlarını otomatik algılar.
* ⚖️ **Hesap Tipi Sınıflandırması:** TCKN, MERSİS, Ad.Soyad ve UETS formatlarını ayırt eder.
* 📊 **Esnek Raporlama:** Terminal renkli çıktı, JSON, CSV ve Markdown tablo desteği.
* 📁 **Toplu Tarama:** `--file` parametresi ile binlerce adresi saniyeler içinde doğrulayabilme.

---

## 🚀 Hızlı Başlangıç

### 1. Tekil Adres Sorgulama
```bash
python kep_validator.py sirket@hs01.kep.tr
```

### 2. Kurumsal Alt Alan Adı ve UETS Sorgusu
```bash
python kep_validator.py finans@garanti.hs02.kep.tr
python kep_validator.py 15421-98741-23654@hs01.kep.tr
```

### 3. Toplu Doğrulama ve Raporlama
```bash
# Markdown formatında rapor oluşturma
python kep_validator.py adres1@hs01.kep.tr adres2@ptt.kep.tr --markdown

# Dosyadan okuyup CSV çıktısı alma
python kep_validator.py --file sirket_kep_listesi.txt --output rapor.csv
```

---

## 🐍 Python Projelerinde Kullanım

```python
from kep_validator import validate_kep_single

sonuc = validate_kep_single("muhasebe@hs01.kep.tr")

if sonuc["is_valid"]:
    print(f"✅ Geçerli KEP: {sonuc['address']}")
    print(f"Operatör: {sonuc['operator']} | Hesap Türü: {sonuc['account_type']}")
else:
    print(f"❌ Hatalı Adres! Sebep: {sonuc['error_message']}")
```

---

## 🔗 E-Dönüşüm Açık Kaynak Ekosistemi

Bu araç [eimza-kep](https://github.com/eimza-kep) organizasyonunun açık kaynak e-dönüşüm araçları ekosisteminin bir parçasıdır:

* 🇹🇷 **[awesome-turkiye-e-donusum](https://github.com/eimza-kep/awesome-turkiye-e-donusum):** Türkiye E-Dönüşüm kütüphane, mevzuat ve araçlar listesi.
* 📑 **[e-fatura-itiraz-ve-iade-scripti](https://github.com/eimza-kep/e-fatura-itiraz-ve-iade-scripti):** TTK Md. 18/3 uyarınca KEP üzerinden 8 günlük fatura itiraz scripti.
* 🏠 **[kira-tahliye-ve-sozlesme-scripti](https://github.com/eimza-kep/kira-tahliye-ve-sozlesme-scripti):** KEP üzerinden tahliye ihtarı ve kira sözleşmesi yönetim scripti.
* 📄 **[python-pdf-eimza-dogrulayici](https://github.com/eimza-kep/python-pdf-eimza-dogrulayici):** PDF belgelerindeki PAdES e-imzaları doğrulama aracı.

---

## 📚 İlgili Teknik Rehberler
* 📄 [Normal E-Posta ile KEP Adresine Mail Gönderilir mi?](https://kep-akademisi.pages.dev/yazilar/normal-eposta-ile-kep-adresine-mail-atilir-mi.html)
* 📄 [KEP Delil Kutusu Nedir? Delil İletilerinin Hukuki Saklama Süresi](https://kep-akademisi.pages.dev/yazilar/kep-delil-kutusu-saklama-sureleri.html)
* 📄 [Şirketlerde KEP Adresi Zorunlu mu? Hangi Firmalar KEP Almak Zorunda?](https://kep-akademisi.pages.dev/yazilar/sirketlerde-kep-adresi-zorunlulugu.html)

---

## ⚖️ Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır.
