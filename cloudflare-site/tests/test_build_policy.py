"""Offline regression tests for the ECM build gate."""
import importlib.util
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

SITE = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


verify = load("ecm_verify_for_policy", SITE / "scripts/verify.py")
gate = load("ecm_check_build_for_policy", SITE / "scripts/check_build.py")


class ECMBuildGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name) / "source"
        self.output = Path(self.temp.name) / "output"
        shutil.copytree(SITE, self.source)
        patched = patch.multiple(verify, ROOT=self.source, OUT=self.output)
        patched.start()
        self.addCleanup(patched.stop)

    def compile(self, branch):
        with patch.dict(os.environ, {"CF_PAGES_BRANCH": branch}, clear=True):
            verify.main()

    def test_preview_is_nonindexable_and_report_is_not_release_permission(self):
        self.compile("automation/ecm-build-gates-20261021")
        report = gate.inspect("preview", self.source, self.output)
        self.assertEqual("PASS", report["build"])
        self.assertEqual([], report["erreurs"])
        self.assertFalse(report["publication_autorisee"])
        self.assertEqual("NON_CERTIFIEE", report["publication"])

    def test_preview_missing_noindex_is_rejected(self):
        self.compile("automation/ecm-build-gates-20261021")
        index = self.output / "index.html"
        index.write_text(index.read_text().replace("noindex,nofollow", "index,follow"))
        self.assertIn("preview_indexable_html", gate.inspect("preview", self.source, self.output)["erreurs"])

    def test_preview_robots_txt_without_disallow_is_rejected(self):
        self.compile("automation/ecm-build-gates-20261021")
        (self.output / "robots.txt").write_text("User-agent: *\nAllow: /\n")
        self.assertIn("preview_robots_missing_disallow", gate.inspect("preview", self.source, self.output)["erreurs"])

    def test_production_candidate_does_not_certify_stock(self):
        self.compile("main")
        report = gate.inspect("production", self.source, self.output)
        self.assertEqual("PASS", report["build"])
        self.assertEqual("NON_CONFIRME", report["stock"])
        self.assertFalse(report["publication_autorisee"])
        self.assertIn("stock_et_photos_non_valides", report["blocages_publication"])

    def test_production_noindex_regression_is_rejected(self):
        self.compile("main")
        index = self.output / "index.html"
        index.write_text(index.read_text().replace('content="index,follow"', 'content="noindex,nofollow"'))
        self.assertIn("production_indexation_invalid", gate.inspect("production", self.source, self.output)["erreurs"])

    def test_missing_resource_is_rejected(self):
        self.compile("main")
        (self.output / "app.js").unlink()
        report = gate.inspect("production", self.source, self.output)
        self.assertEqual("FAIL", report["build"])
        self.assertIn("missing: app.js", report["erreurs"])

    def test_wrong_canonical_is_rejected(self):
        self.compile("main")
        index = self.output / "index.html"
        index.write_text(index.read_text().replace("https://carokazmada.com/", "https://example.org/"))
        self.assertIn("canonical_incorrect", gate.inspect("production", self.source, self.output)["erreurs"])


if __name__ == "__main__":
    unittest.main()
