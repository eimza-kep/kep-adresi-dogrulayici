# -*- coding: utf-8 -*-
"""Unit tests for KEP Address Validator v1.2"""
import unittest
from kep_validator import validate_kep_syntax, validate_kep_single, resolve_kephs_operator, generate_markdown_report

class TestKEPValidator(unittest.TestCase):
    def test_syntax_validation(self):
        valid, account_type = validate_kep_syntax("acmeholding@hs01.kep.tr")
        self.assertTrue(valid)
        self.assertIn("Tüzel Kişi", account_type)

        valid_adsoyad, adsoyad_type = validate_kep_syntax("ahmet.yilmaz@hs01.kep.tr")
        self.assertTrue(valid_adsoyad)
        self.assertIn("Ad.Soyad", adsoyad_type)

        valid_ptt, ptt_type = validate_kep_syntax("12345678901@ptt.kep.tr")
        self.assertTrue(valid_ptt)
        self.assertIn("T.C. Kimlik No", ptt_type)

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

    def test_subdomain_operator_resolution(self):
        op1 = resolve_kephs_operator("hs01.kep.tr")
        self.assertIn("TÜRKKEP", op1)

        op2 = resolve_kephs_operator("kurumsal.hs02.kep.tr")
        self.assertIn("TN KEP", op2)
        self.assertIn("Alt Alan Adı", op2)

        op3 = resolve_kephs_operator("posta.ptt.kep.tr")
        self.assertIn("PTT", op3)

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
