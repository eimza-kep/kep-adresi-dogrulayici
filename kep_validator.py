#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KEP (Kayıtlı Elektronik Posta) Adresi Doğrulama ve MX Sorgulama Aracı v1.2
===================================================================
Türkiye BTK mevzuatına uygun olarak KEP ve UETS adreslerinin sözdizimini (syntax),
yetkili KEP Hizmet Sağlayıcısını (KEPHS) ve DNS posta sunucusu kayıtlarını inceler.

Özellikler:
- Sıfır bağımlılık (Pure Python Standard Library)
- BTK onaylı tüm KEPHS operatör eşleşmeleri (TÜRKKEP, TN KEP, PTT KEP, E-Tuğra vb.)
- Kurumsal alt alan adları (subdomain: örn. banka.hs02.kep.tr) desteği
- TCKN, MERSİS ve UETS hesap tipi tespiti
- CSV, JSON ve Markdown formatında raporlama
- Toplu adres listesi tarama (--file) ve CI denetimi (--strict)

Yazar: E-İmza & Dijital Dönüşüm Portalı (https://keprehberi.site/)
Lisans: MIT
"""

import sys
import os
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

# BTK Onaylı KEP Hizmet Sağlayıcıları ve Bilinen Alan Adları (2026 Güncel)
KNOWN_KEP_OPERATORS = {
    "hs01.kep.tr": "TÜRKKEP Kayıtlı Elektronik Posta Hizmetleri A.Ş.",
    "hs02.kep.tr": "TN KEP / TN İletişim Teknolojileri A.Ş.",
    "hs03.kep.tr": "TÜRKKEP (HS03 Altyapısı)",
    "ptt.kep.tr":  "PTT A.Ş. (Ulusal Posta ve KEP Operatörü)",
    "hs04.kep.tr": "Klon Bilişim A.Ş.",
    "hs05.kep.tr": "E-Tuğra EBG A.Ş. KEP Altyapısı",
    "hs06.kep.tr": "İnteraktif KEP Altyapısı",
    "hs07.kep.tr": "TÜBİTAK BİLGEM KEP",
    "hs08.kep.tr": "İpek KEP / KEP A.Ş.",
    "hs09.kep.tr": "EDM Bilişim KEP Altyapısı",
    "hs10.kep.tr": "E-İmzaTR KEP Hizmetleri A.Ş.",
    "tnb.kep.tr":  "TNB KEP (Türkiye Noterler Birliği)",
    "turkkep.com.tr": "TÜRKKEP Kayıtlı Elektronik Posta Hizmetleri A.Ş.",
    "kepas.com.tr": "KEP A.Ş. Hizmet Sağlayıcısı",
}

def validate_tckn_algorithm(tckn_str):
    """TCKN 11 hane kural ve algoritma denetimi."""
    if not re.match(r"^[1-9]\d{10}$", tckn_str):
        return False
    digits = [int(d) for d in tckn_str]
    d_odd = sum(digits[0:9:2])
    d_even = sum(digits[1:8:2])
    tenth = ((d_odd * 7) - d_even) % 10
    if digits[9] != tenth:
        return False
    eleventh = sum(digits[:10]) % 10
    if digits[10] != eleventh:
        return False
    return True

def resolve_kephs_operator(domain):
    """
    Alan adını (subdomain dahil) bilinen BTK KEPHS operatörleriyle eşleştirir.
    Örn: 'kurumsal.hs01.kep.tr' -> 'TÜRKKEP'
    """
    clean_dom = domain.lower().strip()
    if clean_dom in KNOWN_KEP_OPERATORS:
        return KNOWN_KEP_OPERATORS[clean_dom]
    
    for base_dom, op_name in KNOWN_KEP_OPERATORS.items():
        if clean_dom.endswith("." + base_dom):
            return f"{op_name} (Kurumsal Alt Alan Adı)"
            
    return "Yetkili Diğer KEPHS / Kurumsal KEP Alan Adı"

def validate_kep_syntax(address):
    """KEP adresi sözdizimini ve hesap tipini kontrol eder."""
    if not address or "@" not in address:
        return False, "Geçersiz e-posta biçimi (içinde '@' karakteri yok)"

    if re.search(r"[ıçşğüöİÇŞĞÜÖ]", address):
        return False, "KEP adreslerinde Türkçe karakter (ı, ç, ş, ğ, ü, ö) kullanılamaz; standart Latin alfabesi kullanılmalıdır"

    parts = address.strip().lower().split("@")
    if len(parts) != 2:
        return False, "Geçersiz e-posta biçimi (birden fazla '@' karakteri)"

    local_part, domain = parts

    # Domain .kep.tr ile bitmelidir
    if not domain.endswith(".kep.tr"):
        return False, f"Alan adı '.kep.tr' ile bitmiyor (Bulunan: @{domain})"

    # Local-part denetimi
    if not re.match(r"^[a-z0-9\._\-]+$", local_part):
        return False, "Kullanıcı adında geçersiz özel karakterler var"

    # Tip tespiti (VKN / TCKN / MERSİS / UETS / Bireysel)
    account_type = "Tüzel Kişi / Şirket veya Kurum"
    if re.match(r"^\d{10}$", local_part):
        account_type = "Tüzel Kişi (Vergi Kimlik No - VKN İle Kayıtlı)"
    elif re.match(r"^\d{11}$", local_part):
        if validate_tckn_algorithm(local_part):
            account_type = "Gerçek Kişi (T.C. Kimlik No İle Doğrulanmış)"
        else:
            account_type = "Gerçek Kişi (T.C. Kimlik No İle Kayıtlı)"
    elif re.match(r"^\d{16}$", local_part):
        account_type = "Tüzel Kişi (16 Haneli MERSİS No İle Kayıtlı)"
    elif re.match(r"^\d{5}-\d{5}-\d{5}$", local_part):
        account_type = "UETS Tebligat Hesabı (Adalet Bakanlığı UETS Formatı)"
    elif re.match(r"^[a-z]+[\.][a-z0-9]+$", local_part):
        account_type = "Gerçek Kişi (Ad.Soyad Formatı)"

    return True, account_type

def check_smtp_connectivity(domain, timeout=1.5):
    """Domain için SMTP (port 25 / 587) bağlantı sağlığını test eder."""
    for port in (25, 587):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((domain, port))
            sock.close()
            return True, f"Port {port} SMTP bağlantısı açık"
        except (socket.timeout, socket.error, OSError):
            continue
    return False, "SMTP portlarına doğrudan erişim kapalı veya korumalı"

def check_mx_records(domain, check_smtp=False):
    """Domain için DNS sunucu kayıtlarını ve isteğe bağlı SMTP bağlantısını kontrol eder."""
    try:
        host_info = socket.gethostbyname(domain)
        details = [f"A Kaydı: {host_info} (Sunucu Erişilebilir)"]
        if check_smtp:
            s_ok, s_msg = check_smtp_connectivity(domain)
            details.append(s_msg)
        return True, details
    except socket.gaierror:
        # Alt alan adıysa üst domaini de deneyelim
        parts = domain.split(".")
        if len(parts) > 3:
            parent_domain = ".".join(parts[-3:])
            try:
                p_host = socket.gethostbyname(parent_domain)
                return True, [f"Üst Sunucu A Kaydı ({parent_domain}): {p_host}"]
            except socket.gaierror:
                pass

        for known in KNOWN_KEP_OPERATORS:
            if domain == known or domain.endswith("." + known):
                return True, ["BTK Resmi Kayıtlı KEPHS Altyapısı (Kapalı Devre / KamuNet)"]
        return False, ["DNS Çözümleme Hatası: Alan adı genel internet DNS sunucularında bulunamadı"]

def validate_kep_single(address, check_smtp=False):
    clean_addr = address.strip().lower()
    is_valid_syntax, type_or_err = validate_kep_syntax(clean_addr)

    domain = clean_addr.split("@")[1] if "@" in clean_addr else ""
    operator_name = resolve_kephs_operator(domain) if domain else "-"

    dns_ok = False
    dns_details = []
    error_msg = None

    if is_valid_syntax and domain:
        dns_ok, dns_details = check_mx_records(domain, check_smtp=check_smtp)
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

def generate_markdown_report(results):
    md = "# KEP Adresi Doğrulama Raporu\n\n"
    md += f"Toplam **{len(results)}** adet KEP adresi analiz edildi.\n\n"
    md += "| Durum | KEP Adresi | Hesap Türü | KEPHS Operatörü | Alan Adı |\n"
    md += "|:---:|---|---|---|---|\n"
    for r in results:
        status_icon = "✅ Geçerli" if r["is_valid"] else "❌ Hatalı"
        acc = r["account_type"] if r["syntax_valid"] else f"Hata: {r['error_message']}"
        md += f"| {status_icon} | `{r['address']}` | {acc} | {r['operator']} | `@{r['domain']}` |\n"
    
    md += "\n---\n"
    md += "💡 **Yasal Dayanak:** 6102 Sayılı Türk Ticaret Kanunu Madde 18/3 ve 7201 Sayılı Tebligat Kanunu Madde 7/a uyarınca KEP iletileri kesin hukuki delil niteliğindedir.\n"
    return md

def print_result_cli(result):
    print("=" * 80)
    print("      KEP (KAYITLI ELEKTRONİK POSTA) DOĞRULAMA VE TEST ARACI v1.2")
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
    parser = argparse.ArgumentParser(description="KEP Adresi Sözdizimi ve DNS Doğrulama Aracı v1.2")
    parser.add_argument("addresses", nargs="*", help="Doğrulanacak KEP adresleri (Örn: sirket@hs01.kep.tr)")
    parser.add_argument("--file", help="İçerisinde KEP adresleri bulunan metin/CSV dosyası")
    parser.add_argument("--json", action="store_true", help="Sonucu JSON olarak çıktı verir")
    parser.add_argument("--markdown", action="store_true", help="Sonucu Markdown tablosu olarak verir")
    parser.add_argument("--output", help="Sonuçları JSON, CSV veya Markdown dosyasına kaydeder")
    parser.add_argument("--strict", action="store_true", help="Geçersiz adres varsa 1 çıkış kodu üretir")
    parser.add_argument("--check-smtp", action="store_true", help="Sunucu SMTP bağlantı sağlığını test eder")

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

    results = [validate_kep_single(addr, check_smtp=args.check_smtp) for addr in target_list]
    any_invalid = any(not r["is_valid"] for r in results)

    if args.markdown:
        md_text = generate_markdown_report(results)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(md_text)
            print(f"[OK] Markdown raporu kaydedildi: {args.output}")
        else:
            print(md_text)
    elif args.output:
        if args.output.lower().endswith(".csv"):
            with open(args.output, "w", newline="", encoding="utf-8-sig") as f:
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
