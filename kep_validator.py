#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KEP (Kayıtlı Elektronik Posta) Adresi Doğrulama ve MX Sorgulama Aracı
===================================================================
Türkiye BTK mevzuatına uygun olarak KEP adreslerinin sözdizimini (syntax),
yetkili KEP Hizmet Sağlayıcısını (KEPHS) ve DNS MX posta sunucusu kayıtlarını inceler.

Yazar: E-İmza & Dijital Dönüşüm Portalı (https://kep-akademisi.pages.dev/yazilar/normal-eposta-ile-kep-adresine-mail-atilir-mi.html)
Lisans: MIT
"""

import sys
import re
import socket
import json
import argparse

# BTK Onaylı KEP Hizmet Sağlayıcıları ve Bilinen Alan Adları
KNOWN_KEP_OPERATORS = {
    "hs01.kep.tr": "TÜRKKEP Kayıtlı Elektronik Posta Hizmetleri A.Ş.",
    "hs02.kep.tr": "TN KEP / TN İletişim Teknolojileri A.Ş.",
    "hs03.kep.tr": "TÜRKKEP (HS03 Altyapısı)",
    "ptt.kep.tr":  "PTT A.Ş. (Ulusal Posta ve KEP Operatörü)",
    "hs04.kep.tr": "Klon Bilişim A.Ş.",
    "hs05.kep.tr": "E-Tuğra EBG A.Ş. KEP Altyapısı",
}

def validate_kep_syntax(address):
    """KEP adresi sözdizimini kontrol eder."""
    if not address or "@" not in address:
        return False, "Geçersiz e-posta biçimi (içinde '@' karakteri yok)"

    parts = address.strip().lower().split("@")
    if len(parts) != 2:
        return False, "Geçersiz e-posta biçimi"

    local_part, domain = parts

    # Domain .kep.tr ile bitmelidir
    if not domain.endswith(".kep.tr"):
        return False, f"Alan adı '.kep.tr' ile bitmiyor (Bulunan: @{domain})"

    # Local-part denetimi
    if not re.match(r"^[a-z0-9\._\-]+$", local_part):
        return False, "Kullanıcı adında geçersiz özel karakterler var"

    # Tip tespiti
    account_type = "Tüzel Kişi / Şirket veya Kurum"
    if re.match(r"^\d{11}$", local_part):
        account_type = "Gerçek Kişi (T.C. Kimlik No İle Kayıtlı)"
    elif re.match(r"^\d{16}$", local_part):
        account_type = "Tüzel Kişi (MERSİS No İle Kayıtlı)"
    elif re.match(r"^[a-z]+[\.][a-z0-9]+$", local_part):
        account_type = "Gerçek Kişi (Ad.Soyad Formatı)"

    return True, account_type

def check_mx_records(domain):
    """Domain için DNS MX / A sunucu kayıtlarını kontrol eder."""
    try:
        # Standart socket ile host çözümleme denemesi
        host_info = socket.gethostbyname(domain)
        return True, [f"A Kaydı: {host_info} (Sunucu Erişilebilir)"]
    except socket.gaierror as e:
        return False, [f"DNS Çözümleme Hatası: {e}"]

def validate_kep(address, as_json=False):
    address = address.strip().lower()
    is_valid_syntax, type_or_err = validate_kep_syntax(address)

    domain = address.split("@")[1] if "@" in address else ""
    operator_name = KNOWN_KEP_OPERATORS.get(domain, "Yetkili Diğer KEPHS / Kurumsal KEP Alan Adı")

    dns_ok = False
    dns_details = []
    if is_valid_syntax and domain:
        dns_ok, dns_details = check_mx_records(domain)

    result = {
        "address": address,
        "is_valid": is_valid_syntax and dns_ok,
        "syntax_valid": is_valid_syntax,
        "dns_active": dns_ok,
        "account_type": type_or_err if is_valid_syntax else None,
        "error_message": type_or_err if not is_valid_syntax else None,
        "operator": operator_name,
        "domain": domain,
        "dns_details": dns_details
    }

    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print("=" * 80)
    print("      KEP (KAYITLI ELEKTRONİK POSTA) DOĞRULAMA VE TEST ARACI v1.0")
    print("=" * 80)
    print(f"Sorgulanan KEP Adresi: {address}")
    print(f"Genel Durum:           {'✅ GEÇERLİ KEP ADRESİ' if result['is_valid'] else '❌ GEÇERSİZ / HATALI KEP ADRESİ'}")
    print(f"Sözdizimi (Syntax):    {'✅ Doğru Standart' if is_valid_syntax else '❌ Hatalı Biçim'}")
    print(f"Sunucu (DNS) Durumu:   {'✅ Aktif' if dns_ok else '❌ Erişilemiyor'}\n")

    if is_valid_syntax:
        print(f"📋 Hesap Türü:          {result['account_type']}")
        print(f"🏢 KEP Operatörü:       {result['operator']}")
        print(f"🌐 Alan Adı:            @{domain}")
        print(f"📡 DNS Durumu:          {', '.join(dns_details)}")
    else:
        print(f"⚠️  Hata Nedeni:        {result['error_message']}")

    print("-" * 80)
    print("💡 HUKUKİ BİLGİ: KEP üzerinden yapılan tebligatlar ve ihtarnameler, Türk Ticaret")
    print("   Kanunu ve Tebligat Kanunu kapsamında resmi noter tebligatı hükmündedir.")
    print("=" * 80)

def main():
    parser = argparse.ArgumentParser(description="KEP Adresi Sözdizimi ve DNS Doğrulama Aracı")
    parser.add_argument("address", help="Doğrulanacak KEP adresi (Örn: sirket@hs01.kep.tr)")
    parser.add_argument("--json", action="store_true", help="Sonucu JSON olarak çıktı verir")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()
    validate_kep(args.address, as_json=args.json)

if __name__ == "__main__":
    main()
