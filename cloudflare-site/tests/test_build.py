import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import shutil

SITE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('ecm_verify', SITE / 'scripts/verify.py')
verify = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify)


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'source'
        shutil.copytree(SITE, self.root)
        self.out = Path(self.temp.name) / 'output'
        self.scope = patch.multiple(verify, ROOT=self.root, OUT=self.out)
        self.scope.start()
        self.addCleanup(self.scope.stop)

    def build(self, branch):
        with patch.dict(os.environ, {'CF_PAGES_BRANCH': branch}, clear=True):
            verify.main()

    def test_production_canonical_and_resources(self):
        self.build('main')
        self.assertIn('content="index,follow"', (self.out / 'index.html').read_text())
        self.assertNotIn('Disallow: /', (self.out / 'robots.txt').read_text())
        self.assertNotIn('X-Robots-Tag', (self.out / '_headers').read_text().split('/404.html')[0])
        self.assertEqual(set(p.relative_to(self.out).as_posix() for p in self.out.rglob('*') if p.is_file()), set(verify.FILES))

    def test_preview_remains_blocked_and_rebuild_is_clean(self):
        self.build('fix/ecm-audit-20261021')
        self.assertIn('content="noindex,nofollow"', (self.out / 'index.html').read_text())
        self.assertIn('X-Robots-Tag: noindex, nofollow', (self.out / '_headers').read_text().split('/404.html')[0])
        self.assertIn('Disallow: /', (self.out / 'robots.txt').read_text())
        self.build('main')
        self.assertNotIn('content="noindex,nofollow"', (self.out / 'index.html').read_text())

    def test_wrong_canonical_is_rejected(self):
        p = self.root / 'index.html'
        p.write_text(p.read_text().replace('rel="canonical" href="https://carokazmada.com/"', 'rel="canonical" href="https://carokazmada.pages.dev/"'))
        with self.assertRaisesRegex(ValueError, 'Canonical'):
            self.build('main')

    def test_missing_asset_is_rejected(self):
        (self.root / 'assets/hero-audi.webp').unlink()
        with self.assertRaisesRegex(ValueError, 'Missing asset'):
            self.build('main')

    def test_jsonld_hash_drift_is_rejected(self):
        p = self.root / '_headers'
        p.write_text(p.read_text().replace('sha256-', 'broken-'))
        with self.assertRaisesRegex(ValueError, 'CSP hash'):
            self.build('main')

    def test_local_without_branch_is_noindex(self):
        # Local builds must never generate accidentally indexable output.
        with patch.dict(os.environ, {}, clear=True):
            verify.main()
        self.assertIn('content="noindex,nofollow"', (self.out / 'index.html').read_text())
        self.assertIn('X-Robots-Tag: noindex, nofollow', (self.out / '_headers').read_text().split('/404.html')[0])
        self.assertIn('Disallow: /', (self.out / 'robots.txt').read_text())

    def test_ambiguous_cloudflare_branch_is_rejected(self):
        with patch.dict(os.environ, {'CF_PAGES': '1'}, clear=True):
            with self.assertRaisesRegex(ValueError, 'branch identity'):
                verify.main()


if __name__ == '__main__':
    unittest.main()
