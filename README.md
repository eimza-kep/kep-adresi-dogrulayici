# KEP (Kayıtlı Elektronik Posta) Adresi Doğrulama Aracı 📬⚖️

[![Lisans: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Standart: BTK KEP](https://img.shields.io/badge/Standart-BTK%20KEP%20Mevzuat%C4%B1-green.svg)](https://btk.gov.tr)

Türkiye'de **BTK (Bilgi Teknolojileri ve İletişim Kurumu)** mevzuatına uygun olarak; şirketler, avukatlar, kamu kurumları ve vatandaşlar arasındaki resmi tebligatlarda kullanılan **KEP (Kayıtlı Elektronik Posta)** adreslerinin sözdizimini (formatını), hesap türünü ve sunucu (DNS) erişilebilirliğini doğrulayan açık kaynaklı test aracıdır.

---

## 🔍 Neleri Denetler?

1. **Format Doğruluğu:** Adresin zorunlu `.kep.tr` uzantısına sahip olup olmadığını ve geçerli karakterler içerip içermediğini kontrol eder.
2. **Hesap Türü Tespiti:**
   * 👤 **Gerçek Kişi (T.C. Kimlik No):** `12345678901@hs01.kep.tr`
   * 👤 **Gerçek Kişi (Ad Soyad):** `ahmet.yilmaz@hs01.kep.tr`
   * 🏢 **Tüzel Kişi / Şirket (MERSİS No):** `0123456789000001@hs02.kep.tr`
   * 🏢 **Tüzel Kişi (Şirket Unvanı):** `abcteknoloji@hs01.kep.tr`
3. **Operatör Tespiti:** Alan adına göre (TÜRKKEP, PTT KEP, TN KEP vb.) yetkili operatörü belirler.
4. **DNS & Sunucu Erişimi:** KEP sunucusunun internette aktif ve yayında olup olmadığını test eder.

---

## 🚀 Hızlı Kullanım

### Komut Satırından Çalıştırma
```bash
python kep_validator.py abcsirket@hs01.kep.tr
```

**Örnek Çıktı:**
```text
================================================================================
      KEP (KAYITLI ELEKTRONİK POSTA) DOĞRULAMA VE TEST ARACI v1.0
================================================================================
Sorgulanan KEP Adresi: abcsirket@hs01.kep.tr
Genel Durum:           ✅ GEÇERLİ KEP ADRESİ
Sözdizimi (Syntax):    ✅ Doğru Standart
Sunucu (DNS) Durumu:   ✅ Aktif

📋 Hesap Türü:          Tüzel Kişi / Şirket veya Kurum
🏢 KEP Operatörü:       TÜRKKEP Kayıtlı Elektronik Posta Hizmetleri A.Ş.
🌐 Alan Adı:            @hs01.kep.tr
📡 DNS Durumu:          A Kaydı: 185.122.200.15 (Sunucu Erişilebilir)
```

### JSON Formatında Çıktı Alma (Yazılım Entegrasyonları İçin)
```bash
python kep_validator.py 12345678901@ptt.kep.tr --json
```

```json
{
  "address": "12345678901@ptt.kep.tr",
  "is_valid": true,
  "syntax_valid": true,
  "dns_active": true,
  "account_type": "Gerçek Kişi (T.C. Kimlik No İle Kayıtlı)",
  "operator": "PTT A.Ş. (Ulusal Posta ve KEP Operatörü)",
  "domain": "ptt.kep.tr"
}
```

---

## 🏢 Yetkili KEP Operatörleri ve Alan Adları

* **TÜRKKEP:** `@hs01.kep.tr` / `@hs03.kep.tr`
* **TN KEP:** `@hs02.kep.tr`
* **PTT KEP:** `@ptt.kep.tr`
* **Klon Bilişim:** `@hs04.kep.tr`
* **E-Tuğra:** `@hs05.kep.tr`

---

## ⚖️ Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır.


### 📚 İlgili Rehber ve Çözümler
* 📄 [Normal E-Posta (Gmail, Hotmail) ile KEP Adresine Mail Gönderilebilir mi?](https://kep-akademisi.pages.dev/yazilar/normal-eposta-ile-kep-adresine-mail-atilir-mi.html)
* 📄 [İşten Ayrılma ve İstifa Bildirimi KEP ile Nasıl Gönderilir?](https://kep-akademisi.pages.dev/yazilar/isten-ayrilma-istifa-kep-ile-gonderilir-mi.html)
* 📄 [Şirketler İçin KEP Adresi Almak Zorunlu mu? Hangi Şirketleri Kapsar?](https://kep-akademisi.pages.dev/yazilar/sirketler-icin-kep-adresi-zorunlu-mu.html)
* 📄 [E-İmza ile KEP Arasındaki İlişki: Biri Olmadan Diğeri Kullanılır mı?](https://eimza-kep.github.io/eimza-blog/posts/e-imza-ile-kep-arasindaki-fark-ve-iliskiler.html)
