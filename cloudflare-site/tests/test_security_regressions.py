"""ECM security regression tests for Cloudflare Pages static assets.

This suite is intentionally read-only and never calls external services.
It should run in GitHub Actions before any deployment or merge.
"""
from pathlib import Path
from html.parser import HTMLParser
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
TEXT_EXTENSIONS = {".html", ".css", ".js", ".json", ".xml", ".txt", ".py"}
BLOCKED_CROSS_ECOSYSTEM = (
    re.compile(r"best[\s_-]*price[\s_-]*car", re.IGNORECASE),
    re.compile(r"bestpricecarmdg", re.IGNORECASE),
    re.compile(r"(?<![a-z])ebp(?![a-z])", re.IGNORECASE),
)


class AssetParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.external_scripts = []
        self.unsafe_links = []
        self.forms = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script" and attrs.get("src", "").startswith(("http://", "https://")):
            self.external_scripts.append(attrs["src"])
        if tag == "a" and attrs.get("target") == "_blank":
            rel = set(attrs.get("rel", "").split())
            if not {"noopener", "noreferrer"}.issubset(rel):
                self.unsafe_links.append(attrs.get("href"))
        if tag == "form":
            self.forms.append(attrs)


class SecurityRegressionTests(unittest.TestCase):
    def test_ecm_files_never_reference_ebp(self):
        for path in ROOT.rglob("*"):
            if (not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS
                    or path.name.startswith("test_") or path.name.endswith(".md")):
                continue
            contents = path.read_text(encoding="utf-8")
            for pattern in BLOCKED_CROSS_ECOSYSTEM:
                with self.subTest(file=str(path.relative_to(ROOT)), pattern=pattern.pattern):
                    self.assertIsNone(pattern.search(contents))

    def test_csp_rejects_unsafe_execution_and_embedding(self):
        headers = (ROOT / "_headers").read_text(encoding="utf-8")
        self.assertIn("Content-Security-Policy:", headers)
        self.assertIn("default-src 'self'", headers)
        self.assertIn("object-src 'none'", headers)
        self.assertIn("frame-ancestors 'none'", headers)
        self.assertIn("form-action 'self'", headers)
        self.assertIn("X-Content-Type-Options: nosniff", headers)
        self.assertIn("X-Frame-Options: DENY", headers)
        self.assertNotIn("'unsafe-inline'", headers)
        self.assertNotIn("'unsafe-eval'", headers)

    def test_no_remote_scripts_or_unsafe_new_tabs(self):
        p = AssetParser()
        p.feed((ROOT / "index.html").read_text(encoding="utf-8"))
        self.assertEqual([], p.external_scripts)
        self.assertEqual([], p.unsafe_links)
        for form in p.forms:
            action = form.get("action", "")
            self.assertFalse(action.startswith(("http://", "https://", "//")))

    def test_no_dynamic_js_execution(self):
        js = (ROOT / "app.js").read_text(encoding="utf-8")
        self.assertNotRegex(js, r"\beval\s*\(")
        self.assertNotRegex(js, r"\bnew\s+Function\s*\(")
        self.assertNotIn("document.write(", js)
        self.assertNotIn(".innerHTML", js)

    def test_static_site_has_safe_transport_links(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertNotRegex(html, r"(?i)(?:href|src)\s*=\s*['\"]http://")
        self.assertIn('rel="canonical" href="https://carokazmada.com/"', html)

    def test_public_catalogue_does_not_fabricate_stock(self):
        import json
        inventory = json.loads((ROOT / "catalogue.json").read_text(encoding="utf-8"))
        if not inventory.get("vehicules"):
            self.assertEqual("stock_non_confirme", inventory.get("statut"))
            html = (ROOT / "index.html").read_text(encoding="utf-8")
            self.assertIn("Disponibilités et prix à confirmer", html)
        self.assertEqual("MGA", inventory.get("devise"))


if __name__ == "__main__":
    unittest.main()
