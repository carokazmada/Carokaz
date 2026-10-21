"""ECM: immutable approved theme proof and preview safety regressions."""
import hashlib
import importlib.util
import os
from pathlib import Path
from unittest.mock import patch
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
VERIFY_PATH = ROOT / "scripts" / "verify.py"
SPEC = importlib.util.spec_from_file_location("ecm_theme_verify", VERIFY_PATH)
verify = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify)
ORIGINAL_SHA256 = "cd4260b291cb3696b7d1624427b209e5e3eb5e554f579e0cbb19072e3548a0e4"
THEME_FILENAME = "ECM_THEME_REFERENCE_ORIGINALE_2026-10-21.jpg"


class ThemeExactTests(unittest.TestCase):
    def test_approved_reference_is_byte_identical(self):
        screenshot = ROOT / "assets" / THEME_FILENAME
        self.assertTrue(screenshot.is_file())
        self.assertEqual(hashlib.sha256(screenshot.read_bytes()).hexdigest(), ORIGINAL_SHA256)

    def test_reference_page_is_not_an_advertisement(self):
        html = (ROOT / "theme-exact.html").read_text(encoding="utf-8")
        self.assertIn('meta name="robots" content="noindex,nofollow"', html)
        self.assertIn(THEME_FILENAME, html)
        self.assertIn("ne sont pas des offres vérifiées", html)
        self.assertIn("le formulaire illustré n'est pas interactif", html)
        self.assertNotIn("<form", html.lower())
        css = (ROOT / "theme-exact.css").read_text(encoding="utf-8")
        self.assertIn("object-fit:contain", css)

    def test_visual_branch_cannot_become_indexed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(verify, "OUT", Path(tmpdir) / "built"):
                with patch.dict(os.environ, {"CF_PAGES_BRANCH": "design/ecm-theme-exact-20261021"}, clear=True):
                    verify.main()
                out = Path(tmpdir) / "built"
                self.assertIn('content="noindex,nofollow"', (out / "index.html").read_text())
                self.assertIn("X-Robots-Tag: noindex, nofollow", (out / "_headers").read_text())
                self.assertIn("Disallow: /", (out / "robots.txt").read_text())
                self.assertEqual(
                    hashlib.sha256((out / "assets" / THEME_FILENAME).read_bytes()).hexdigest(),
                    ORIGINAL_SHA256,
                )


if __name__ == "__main__":
    unittest.main()
