# -*- coding: utf-8 -*-
"""Unit tests for KEP Address Validator v1.2"""
import unittest
from kep_validator import (
    validate_kep_syntax,
    validate_kep_single,
    resolve_kephs_operator,
    generate_markdown_report,
    validate_tckn_algorithm,
    check_smtp_connectivity
)

class TestKEPValidator(unittest.TestCase):
    def test_syntax_validation(self):
        valid, account_type = validate_kep_syntax("acmeholding@hs01.kep.tr")
        self.assertTrue(valid)
        self.assertIn("Tüzel Kişi", account_type)

        valid_adsoyad, adsoyad_type = validate_kep_syntax("ahmet.yilmaz@hs01.kep.tr")
        self.assertTrue(valid_adsoyad)
        self.assertIn("Ad.Soyad", adsoyad_type)

        # 11-digit TCKN
        valid_ptt, ptt_type = validate_kep_syntax("12345678901@ptt.kep.tr")
        self.assertTrue(valid_ptt)
        self.assertIn("T.C. Kimlik No", ptt_type)

        # 10-digit VKN
        valid_vkn, vkn_type = validate_kep_syntax("1234567890@hs01.kep.tr")
        self.assertTrue(valid_vkn)
        self.assertIn("Vergi Kimlik No", vkn_type)

        # 16-digit MERSIS
        valid_mersis, mersis_type = validate_kep_syntax("0123456789012345@hs02.kep.tr")
        self.assertTrue(valid_mersis)
        self.assertIn("MERSİS", mersis_type)

        # UETS format test
        valid_uets, uets_type = validate_kep_syntax("15421-98741-23654@hs01.kep.tr")
        self.assertTrue(valid_uets)
        self.assertIn("UETS", uets_type)

        invalid_domain, err = validate_kep_syntax("deneme@gmail.com")
        self.assertFalse(invalid_domain)
        self.assertIn(".kep.tr", err)

        invalid_syntax, err2 = validate_kep_syntax("gecersiz-adres-kep.tr")
        self.assertFalse(invalid_syntax)
        self.assertIn("@", err2)

        # Turkish character test
        invalid_tr, err_tr = validate_kep_syntax("şirket@hs01.kep.tr")
        self.assertFalse(invalid_tr)
        self.assertIn("Türkçe karakter", err_tr)

    def test_tckn_algorithm(self):
        # 10000000146 satisfies TCKN checksum algorithm
        self.assertTrue(validate_tckn_algorithm("10000000146"))
        # Invalid checksum
        self.assertFalse(validate_tckn_algorithm("10000000147"))
        # Leading zero is invalid
        self.assertFalse(validate_tckn_algorithm("01234567890"))
        # Non-11 digit
        self.assertFalse(validate_tckn_algorithm("12345"))

        valid_algo, algo_type = validate_kep_syntax("10000000146@hs01.kep.tr")
        self.assertTrue(valid_algo)
        self.assertIn("Doğrulanmış", algo_type)

    def test_subdomain_operator_resolution(self):
        op1 = resolve_kephs_operator("hs01.kep.tr")
        self.assertIn("TÜRKKEP", op1)

        op2 = resolve_kephs_operator("kurumsal.hs02.kep.tr")
        self.assertIn("TN KEP", op2)
        self.assertIn("Alt Alan Adı", op2)

        op3 = resolve_kephs_operator("posta.ptt.kep.tr")
        self.assertIn("PTT", op3)

        op4 = resolve_kephs_operator("portal.kepas.com.tr")
        self.assertIn("KEP A.Ş.", op4)

    def test_single_full_validation(self):
        res = validate_kep_single("acmeholding@hs01.kep.tr")
        self.assertTrue(res["syntax_valid"])
        self.assertEqual(res["domain"], "hs01.kep.tr")
        self.assertIn("TÜRKKEP", res["operator"])

        res_ptt = validate_kep_single("12345678901@ptt.kep.tr")
        self.assertTrue(res_ptt["syntax_valid"])
        self.assertEqual(res_ptt["domain"], "ptt.kep.tr")
        self.assertIn("PTT", res_ptt["operator"])

    def test_markdown_report_generation(self):
        res_list = [validate_kep_single("test@hs01.kep.tr")]
        md = generate_markdown_report(res_list)
        self.assertIn("KEP Adresi Doğrulama Raporu", md)
        self.assertIn("hs01.kep.tr", md)

if __name__ == "__main__":
    unittest.main()
