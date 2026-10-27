"""ECM showcase regression tests: safe rendering, SEO assets, redirects.

Read-only, offline. Guarantees that the transferred Shopify model data stays a
non-fabricated showcase (no prices, availability on request) and that the
static site keeps its security and SEO configuration.
"""
import json
import re
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ShowcaseTests(unittest.TestCase):
    def setUp(self):
        self.catalogue = json.loads((ROOT / "catalogue.json").read_text(encoding="utf-8"))
        self.html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.js = (ROOT / "app.js").read_text(encoding="utf-8")
        self.headers = (ROOT / "_headers").read_text(encoding="utf-8")

    def test_models_carry_identity_and_no_price(self):
        vehicles = self.catalogue["vehicules"]
        self.assertGreaterEqual(len(vehicles), 1)
        ids = set()
        for car in vehicles:
            self.assertTrue(car["id"] and car["marque"] and car["modele"] and car["categorie"])
            self.assertEqual("sur_demande", car["disponibilite"])
            self.assertEqual([], car["photos"])
            self.assertNotIn("prix", car)
            ids.add(car["id"])
        self.assertEqual(len(ids), len(vehicles), "Duplicate vehicle ids")

    def test_renderer_uses_dom_api_not_html_injection(self):
        self.assertNotIn(".innerHTML", self.js)
        self.assertNotIn("document.write(", self.js)
        self.assertNotRegex(self.js, r"\beval\s*\(")
        self.assertNotRegex(self.js, r"\bnew\s+Function\s*\(")
        self.assertIn("textContent", self.js)
        self.assertIn("replaceChildren", self.js)

    def test_head_declares_icons_manifest_and_social(self):
        for needle in ("rel=\"icon\" href=\"/favicon.svg\"",
                       "rel=\"manifest\" href=\"/site.webmanifest\"",
                       "property=\"og:image\" content=\"https://carokazmada.com/assets/og-image.png\"",
                       "name=\"twitter:card\" content=\"summary_large_image\""):
            self.assertIn(needle, self.html)
        manifest = json.loads((ROOT / "site.webmanifest").read_text(encoding="utf-8"))
        self.assertEqual("fr", manifest["lang"])
        self.assertEqual("/", manifest["start_url"])

    def test_security_headers_hardened(self):
        self.assertIn("Strict-Transport-Security: max-age=", self.headers)
        self.assertIn("Cross-Origin-Opener-Policy: same-origin", self.headers)
        self.assertIn("Cross-Origin-Resource-Policy: same-origin", self.headers)
        self.assertIn("Permissions-Policy:", self.headers)
        self.assertIn("manifest-src 'self'", self.headers)

    def test_redirects_are_internal_301(self):
        rules = [l.split() for l in (ROOT / "_redirects").read_text(encoding="utf-8").splitlines()
                 if l.strip() and not l.lstrip().startswith("#")]
        self.assertTrue(rules)
        for rule in rules:
            self.assertGreaterEqual(len(rule), 3)
            self.assertTrue(rule[0].startswith("/"))
            self.assertTrue(rule[1].startswith("/"))
            self.assertIn(rule[2], ("301", "308"))

    def test_no_cross_ecosystem_reference_in_catalogue(self):
        raw = json.dumps(self.catalogue, ensure_ascii=False)
        self.assertIsNone(re.search(r"best[\s_-]*price[\s_-]*car", raw, re.IGNORECASE))
        self.assertIsNone(re.search(r"(?<![a-z])ebp(?![a-z])", raw, re.IGNORECASE))


if __name__ == "__main__":
    unittest.main()
