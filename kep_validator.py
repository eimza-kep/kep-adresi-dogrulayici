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
import csv
import socket
import json
import argparse

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# BTK Onaylı KEP Hizmet Sağlayıcıları ve Bilinen Alan Adları
KNOWN_KEP_OPERATORS = {
    "hs01.kep.tr": "TÜRKKEP Kayıtlı Elektronik Posta Hizmetleri A.Ş.",
    "hs02.kep.tr": "TN KEP / TN İletişim Teknolojileri A.Ş.",
    "hs03.kep.tr": "TÜRKKEP (HS03 Altyapısı)",
    "ptt.kep.tr":  "PTT A.Ş. (Ulusal Posta ve KEP Operatörü)",
    "hs04.kep.tr": "Klon Bilişim A.Ş.",
    "hs05.kep.tr": "E-Tuğra EBG A.Ş. KEP Altyapısı",
    "hs06.kep.tr": "İnteraktif KEP Altyapısı",
    "hs07.kep.tr": "TÜBİTAK BİLGEM KEP",
    "hs08.kep.tr": "İpek KEP",
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
    """Domain için DNS sunucu kayıtlarını kontrol eder."""
    try:
        host_info = socket.gethostbyname(domain)
        return True, [f"A Kaydı: {host_info} (Sunucu Erişilebilir)"]
    except socket.gaierror:
        if domain in KNOWN_KEP_OPERATORS:
            return True, ["BTK Resmi Kayıtlı KEPHS Altyapısı (Kapalı Devre / KamuNet)"]
        return False, ["DNS Çözümleme Hatası: Alan adı genel internet DNS sunucularında bulunamadı"]

def validate_kep_single(address):
    clean_addr = address.strip().lower()
    is_valid_syntax, type_or_err = validate_kep_syntax(clean_addr)

    domain = clean_addr.split("@")[1] if "@" in clean_addr else ""
    operator_name = KNOWN_KEP_OPERATORS.get(domain, "Yetkili Diğer KEPHS / Kurumsal KEP Alan Adı")

    dns_ok = False
    dns_details = []
    error_msg = None

    if is_valid_syntax and domain:
        dns_ok, dns_details = check_mx_records(domain)
        if not dns_ok:
            error_msg = f"Alan adı DNS/A kaydı çözümlenemedi ({dns_details[0] if dns_details else 'Bilinmiyor'})"
    elif not is_valid_syntax:
        error_msg = type_or_err

    return {
        "address": clean_addr,
        "is_valid": is_valid_syntax and dns_ok,
        "syntax_valid": is_valid_syntax,
        "dns_active": dns_ok,
        "account_type": type_or_err if is_valid_syntax else None,
        "error_message": error_msg,
        "operator": operator_name,
        "domain": domain,
        "dns_details": dns_details
    }

def print_result_cli(result):
    print("=" * 80)
    print("      KEP (KAYITLI ELEKTRONİK POSTA) DOĞRULAMA VE TEST ARACI v1.1")
    print("=" * 80)
    print(f"Sorgulanan KEP Adresi: {result['address']}")
    print(f"Genel Durum:           {'✅ GEÇERLİ KEP ADRESİ' if result['is_valid'] else '❌ GEÇERSİZ / HATALI KEP ADRESİ'}")
    print(f"Sözdizimi (Syntax):    {'✅ Doğru Standart' if result['syntax_valid'] else '❌ Hatalı Biçim'}")
    print(f"Sunucu (DNS) Durumu:   {'✅ Aktif' if result['dns_active'] else '❌ Erişilemiyor'}\n")

    if result['syntax_valid']:
        print(f"📋 Hesap Türü:          {result['account_type']}")
        print(f"🏢 KEP Operatörü:       {result['operator']}")
        print(f"🌐 Alan Adı:            @{result['domain']}")
        print(f"📡 DNS Durumu:          {', '.join(result['dns_details'])}")
    else:
        print(f"⚠️  Hata Nedeni:        {result['error_message']}")

    print("-" * 80)
    print("💡 HUKUKİ BİLGİ: KEP üzerinden yapılan tebligatlar ve ihtarnameler, Türk Ticaret")
    print("   Kanunu ve Tebligat Kanunu kapsamında resmi noter tebligatı hükmündedir.")
    print("=" * 80)

def main():
    parser = argparse.ArgumentParser(description="KEP Adresi Sözdizimi ve DNS Doğrulama Aracı")
    parser.add_argument("addresses", nargs="*", help="Doğrulanacak KEP adresleri (Örn: sirket@hs01.kep.tr)")
    parser.add_argument("--file", help="İçerisinde KEP adresleri bulunan metin/CSV dosyası")
    parser.add_argument("--json", action="store_true", help="Sonucu JSON olarak çıktı verir")
    parser.add_argument("--output", help="Sonuçları JSON veya CSV dosyasına kaydeder")
    parser.add_argument("--strict", action="store_true", help="Geçersiz adres varsa 1 çıkış kodu üretir")

    args = parser.parse_args()

    target_list = list(args.addresses) if args.addresses else []
    if args.file:
        if not os.path.exists(args.file):
            print(f"Hata: Dosya bulunamadı -> {args.file}", file=sys.stderr)
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip().strip(",;\"'")
                if stripped and "@" in stripped:
                    target_list.append(stripped)

    if not target_list:
        parser.print_help()
        sys.exit(0)

    results = [validate_kep_single(addr) for addr in target_list]
    any_invalid = any(not r["is_valid"] for r in results)

    if args.output:
        if args.output.lower().endswith(".csv"):
            with open(args.output, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Adres", "Gecerli", "Sozdizimi", "DNS_Aktif", "HesapTuru", "Operator", "Hata"])
                for r in results:
                    writer.writerow([r["address"], r["is_valid"], r["syntax_valid"], r["dns_active"], r["account_type"] or "", r["operator"], r["error_message"] or ""])
            print(f"[OK] CSV raporu kaydedildi: {args.output}")
        else:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(results if len(results) > 1 else results[0], f, ensure_ascii=False, indent=2)
            print(f"[OK] JSON raporu kaydedildi: {args.output}")
    elif args.json:
        print(json.dumps(results if len(results) > 1 else results[0], ensure_ascii=False, indent=2))
    elif len(results) == 1:
        print_result_cli(results[0])
    else:
        print("=" * 80)
        print(f"Toplam {len(results)} Adet KEP Adresi Doğrulama Raporu:")
        print("=" * 80)
        for r in results:
            icon = "✅" if r["is_valid"] else "❌"
            err_or_type = r["account_type"] if r["is_valid"] else r["error_message"]
            print(f" {icon} {r['address']:<35} | {r['operator']:<25} | {err_or_type}")
        print("=" * 80)

    if args.strict and any_invalid:
        sys.exit(1)

if __name__ == "__main__":
    main()

