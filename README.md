# KEP (Kayıtlı Elektronik Posta) Adresi Doğrulayıcı 📬⚖️

[![Python CI](https://github.com/eimza-kep/kep-adresi-dogrulayici/actions/workflows/ci.yml/badge.svg)](https://github.com/eimza-kep/kep-adresi-dogrulayici/actions)
[![Lisans: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Standart: RFC 5322 & BTK](https://img.shields.io/badge/Standart-BTK%20KEP-success.svg)](https://btk.gov.tr)
[![Blog](https://img.shields.io/badge/Rehber-KEP%20Akademisi-blue.svg)](https://keprehberi.site/)

Türkiye'de **BTK mevzuatı, 6102 Sayılı Türk Ticaret Kanunu (Madde 18/3)** ve **7201 Sayılı Tebligat Kanunu** kapsamında kullanılan KEP (Kayıtlı Elektronik Posta) ve UETS adreslerinin sözdizimini (syntax), kurumsal alt alan adlarını (subdomain), yetkili KEP Hizmet Sağlayıcısını (KEPHS), DNS / DoH (DNS over HTTPS) posta sunucusu durumunu ve toplu Excel (.xlsx) listelerini denetleyen açık kaynaklı CLI aracıdır.

---

## ✨ Öne Çıkan Özellikler (v1.3)

* ⚡ **Sıfır Bağımlılık (Zero-Dependency):** Harici kütüphane gerektirmeyen saf Python standart kütüphanesi mimarisi (isteğe bağlı zengin Excel stilleri için `openpyxl` entegrasyonu).
* 🛡️ **DNS over HTTPS (DoH) Desteği:** Port 53 UDP engelli veya kısıtlı kurumsal ağlarda Cloudflare ve Google DoH JSON API'leri üzerinden güvenli MX/A çözümlemesi (`--doh`).
* 📊 **Toplu Excel (.xlsx) Doğrulama & Raporlama:** İK ve Muhasebe listelerindeki yüzlerce KEP adresini doğrudan Excel'den okuma, doğrulama ve renklendirilmiş durum sütunlarıyla yeni bir rapora kaydetme (`--excel`, `--col`).
* 🏢 **Tüm BTK KEPHS Sağlayıcıları:** TÜRKKEP (`hs01`, `hs03`), TN KEP (`hs02`), PTT KEP (`ptt.kep.tr`), E-Tuğra (`hs05`), TÜBİTAK BİLGEM (`hs07`), EDM Bilişim (`hs09`) ve Klon Bilişim eşleşmesi.
* 🌐 **Kurumsal Subdomain Desteği:** `banka.hs02.kep.tr`, `sirket.hs01.kep.tr` gibi kurumsal alt alan adlarını otomatik algılama ve kök operatöre çözümleme.
* ⚖️ **Gelişmiş Hesap Tipi & Algoritma Kontrolü:** TCKN (Mod 10/11 doğrulama algoritması), VKN, MERSİS, Ad.Soyad ve UETS formatlarını ayırt eder.
* 📑 **Esnek Raporlama:** Renkli terminal çıktısı, JSON, CSV, Markdown tablosu ve Excel (.xlsx) raporları.
* 🚦 **CI/CD Entegrasyonu:** `--strict` parametresi ile pipeline ve test otomasyonlarında geçersiz adres durumunda `exit code 1` üretme.

---

## 🛠️ Kurulum ve Yerel Geliştirme (Local Setup)

### Gereksinimler
- Python 3.8 veya üzeri
- `git`
- (İsteğe bağlı) Excel dosyalarını biçimlendirilmiş hücrelerle işlemek için `openpyxl`

### 1. Depoyu Klonlama ve Çalışma Ortamı
```bash
# Depoyu klonlayın
git clone https://github.com/eimza-kep/kep-adresi-dogrulayici.git
cd kep-adresi-dogrulayici

# Sanal ortam (virtualenv) oluşturma ve aktifleştirme (Opsiyonel)
python -m venv venv
# Linux/macOS:
source venv/bin/activate
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
```

### 2. İsteğe Bağlı Bağımlılıkların Kurulumu
Çekirdek doğrulayıcı harici paket gerektirmez. Ancak gelişmiş Excel renklendirme özellikleri için:
```bash
pip install openpyxl
```

### 3. Birim Testleri Çalıştırma
```bash
python test_kep_validator.py
```
veya `unittest` keşif mekanizması ile:
```bash
python -m unittest discover -v
```

---

## 🚀 Hızlı Başlangıç ve Kullanım Örnekleri

### 1. Tekil Adres Sorgulama
```bash
python kep_validator.py sirket@hs01.kep.tr
```

### 2. Kurumsal Alt Alan Adı ve UETS Sorgusu
```bash
python kep_validator.py finans@garanti.hs02.kep.tr
python kep_validator.py 15421-98741-23654@hs01.kep.tr
```

### 3. DNS-over-HTTPS (DoH) ile Güvenli Çözümleme
Kurumsal güvenlik duvarlarında (firewall) UDP port 53 kapalıysa DoH sorgusu kullanılabilir:
```bash
python kep_validator.py muhasebe@hs01.kep.tr --doh
```

### 4. Toplu Excel (.xlsx) Doğrulama
Excel tablosundaki KEP adreslerini otomatik bulur veya `--col` parametresiyle belirtilen sütundan okur:
```bash
# Otomatik sütun tespiti ve raporlama
python kep_validator.py --excel personeller.xlsx

# Özel sütun adı ve çıktı dosyası belirleme
python kep_validator.py --excel cariler.xlsx --col KEP_ADRESI --output cariler_dogrulanmis.xlsx --doh
```

### 5. Metin / CSV Dosyasından Toplu Okuma ve Markdown / JSON Raporu
```bash
# Markdown formatında rapor oluşturma
python kep_validator.py adres1@hs01.kep.tr adres2@ptt.kep.tr --markdown

# Dosyadan okuyup CSV / JSON çıktısı alma
python kep_validator.py --file sirket_kep_listesi.txt --output rapor.csv
python kep_validator.py sirket@hs01.kep.tr --json
```

---

## 🐍 Python Projelerinde Kütüphane Olarak Kullanım

```python
from kep_validator import validate_kep_single, process_excel_file

# Tekil adres doğrulama (DoH destekli)
sonuc = validate_kep_single("muhasebe@hs01.kep.tr", use_doh=True)

if sonuc["is_valid"]:
    print(f"✅ Geçerli KEP: {sonuc['address']}")
    print(f"Operatör: {sonuc['operator']} | Hesap Türü: {sonuc['account_type']}")
else:
    print(f"❌ Hatalı Adres! Sebep: {sonuc['error_message']}")

# Excel tablosunu doğrudan işleme
excel_sonuc = process_excel_file("cari_listesi.xlsx", col_name="KEP_Adresi", output_path="rapor.xlsx")
print(f"İşlenen KEP Sayısı: {excel_sonuc['processed_keps']}")
```

---

## 🏛️ BTK Kayıtlı KEP Hizmet Sağlayıcıları (KEPHS) Tablosu

| Operatör Kodu / Alan Adı | Yetkili KEP Hizmet Sağlayıcısı (KEPHS) | Desteklenen Formatlar |
|:---|:---|:---|
| `hs01.kep.tr`, `hs03.kep.tr` | **TÜRKKEP** Kayıtlı Elektronik Posta Hizmetleri | TCKN, VKN, MERSİS, Ad.Soyad, Subdomain |
| `hs02.kep.tr` | **TN KEP** (Turkcell Teknoloji / TN İletişim) | TCKN, VKN, MERSİS, Kurumsal Subdomain |
| `ptt.kep.tr` | **PTT KEP** (PTT Genel Müdürlüğü) | TCKN, Kamu Kurumu, UETS Uyumlu |
| `hs05.kep.tr` | **E-Tuğra** EBG Bilişim Teknolojileri | TCKN, VKN, MERSİS |
| `hs07.kep.tr` | **TÜBİTAK BİLGEM** KEP Altyapısı | Kamu ve Araştırma Kurumları |
| `hs09.kep.tr` | **EDM Bilişim** KEP Hizmet Sağlayıcısı | TCKN, VKN, Subdomain |
| `kepas.com.tr` | **Klon Bilişim / KEP A.Ş.** | Özel Entegratör ve Kurumsal Portallar |

---

## 🔗 E-Dönüşüm Açık Kaynak Ekosistemi

Bu araç [eimza-kep](https://github.com/eimza-kep) organizasyonunun açık kaynak e-dönüşüm araçları ekosisteminin bir parçasıdır:

* 🇹🇷 **[awesome-turkiye-e-donusum](https://github.com/eimza-kep/awesome-turkiye-e-donusum):** Türkiye E-Dönüşüm kütüphane, mevzuat ve araçlar listesi.
* 📑 **[e-fatura-itiraz-ve-iade-scripti](https://github.com/eimza-kep/e-fatura-itiraz-ve-iade-scripti):** TTK Md. 18/3 uyarınca KEP üzerinden 8 günlük fatura itiraz scripti (KEP doğrulayıcı ile entegre).
* 🏠 **[kira-tahliye-ve-sozlesme-scripti](https://github.com/eimza-kep/kira-tahliye-ve-sozlesme-scripti):** KEP üzerinden tahliye ihtarı ve kira sözleşmesi yönetim scripti.
* 📄 **[python-pdf-eimza-dogrulayici](https://github.com/eimza-kep/python-pdf-eimza-dogrulayici):** PDF belgelerindeki PAdES e-imzaları doğrulama aracı.

---

## 📚 İlgili Teknik Rehberler
* 📄 [Normal E-Posta ile KEP Adresine Mail Gönderilir mi?](https://keprehberi.site/yazilar/normal-eposta-ile-kep-adresine-mail-atilir-mi.html)
* 📄 [KEP Delil Kutusu Nedir? Delil İletilerinin Hukuki Saklama Süresi](https://keprehberi.site/yazilar/kep-delil-kutusu-saklama-sureleri.html)
* 📄 [Şirketlerde KEP Adresi Zorunlu mu? Hangi Firmalar KEP Almak Zorunda?](https://keprehberi.site/yazilar/sirketlerde-kep-adresi-zorunlulugu.html)

---

## ⚖️ Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır.