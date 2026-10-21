"""Regression tests for ECM public-site auditing (offline only)."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'ecm_live_audit', ROOT / 'scripts' / 'live_audit.py'
)
audit_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit_module)


class LiveAuditTests(unittest.TestCase):
    def test_missing_url_must_return_http_404(self):
        requested = []

        def fake_fetch(path):
            requested.append(path)
            if path == '/':
                return {
                    'status': 200, 'body': '<title>ECM</title><meta name="robots" content="noindex">',
                    'x_robots_tag': 'noindex', 'csp': "default-src 'self'; frame-ancestors 'none'",
                    'nosniff': 'nosniff', 'frame_options': 'DENY',
                }
            if path == '/robots.txt':
                return {
                    'status': 200, 'body': 'User-agent: *\\nDisallow: /\\n',
                    'content_type': 'text/plain',
                }
            # A pretty 404 document served with HTTP 200 is a broken error response.
            return {'status': 200, 'body': 'Cette page n’existe pas sur ce site.'}

        with patch.object(audit_module, 'fetch', side_effect=fake_fetch):
            report = audit_module.audit()

        self.assertIn('/__ecm_audit_nonexistent_404__', requested)
        facts = {item['id']: item for item in report['facts']}
        self.assertEqual('ANOMALIE', facts['404']['status'])


if __name__ == '__main__':
    unittest.main()
