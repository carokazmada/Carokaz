import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import carokaz_setup as setup


class FakeResponse:
    def __init__(self, status_code=200, text="", url="https://example.test/"):
        self.status_code = status_code
        self.text = text
        self.url = url
        self.headers = {"content-type": "text/html; charset=utf-8"}


class FakeSession:
    def __init__(self, page):
        self.page = page
        self.headers = {}

    def get(self, url, timeout=30, allow_redirects=True):
        if url.endswith("/robots.txt"):
            response = FakeResponse(200, "User-agent: *\nAllow: /\n", url)
            response.headers = {"content-type": "text/plain"}
            return response
        if url.endswith("/sitemap.xml"):
            response = FakeResponse(200, "<urlset><url><loc>https://example.test/</loc></url></urlset>", url)
            response.headers = {"content-type": "application/xml"}
            return response
        return FakeResponse(200, self.page, url)


class PublicCrawlTests(unittest.TestCase):
    def setUp(self):
        setup.RESULTS.clear()

    def test_missing_canonical_is_reported(self):
        page = """
        <html><head><title>Test</title>
        <meta name='description' content='Description'></head>
        <body><h1>Accueil</h1><img src='car.jpg' alt='Voiture'></body></html>
        """
        with patch.object(setup.requests, "Session", return_value=FakeSession(page)):
            setup.task_T11({"SITE_URL": "https://example.test", "SEO_AUDIT_PATHS": "/"}, True)

        issues = setup.RESULTS[-1]["data"]["issues"]
        self.assertIn({"path": "/", "issue": "canonical manquante"}, issues)

    def test_healthy_page_has_no_issue(self):
        page = """
        <html><head><title>Test</title>
        <meta name='description' content='Description'>
        <link rel='canonical' href='https://example.test/'>
        </head><body><h1>Accueil</h1><img src='car.jpg' alt='Voiture'></body></html>
        """
        with patch.object(setup.requests, "Session", return_value=FakeSession(page)):
            setup.task_T11({"SITE_URL": "https://example.test", "SEO_AUDIT_PATHS": "/"}, True)

        self.assertEqual(setup.RESULTS[-1]["data"]["issues"], [])


if __name__ == "__main__":
    unittest.main()
