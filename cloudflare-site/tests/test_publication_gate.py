"""Offline unit tests for the ECM publication gate."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "scripts" / "publication_gate.py"
SPEC = importlib.util.spec_from_file_location("ecm_publication_gate", MODULE)
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class PublicationGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "index.html").write_text(
            '<meta content="index,follow" name="robots"/>'
            '<link rel="canonical" href="https://carokazmada.com/"/>',
            encoding="utf-8"
        )
        (self.root / "sitemap.xml").write_text(
            "<urlset><url><loc>https://carokazmada.com/</loc></url></urlset>",
            encoding="utf-8"
        )

    def write_catalogue(self, vehicles):
        (self.root / "catalogue.json").write_text(json.dumps({
            "devise": "MGA", "vehicules": vehicles
        }), encoding="utf-8")

    def test_empty_catalogue_is_not_publishable(self):
        self.write_catalogue([])
        result = gate.check(self.root)
        self.assertFalse(result["machine_ready"])
        self.assertFalse(result["production_approved"])
        blocked = {x["id"] for x in result["checks"] if x["status"] == "BLOCK"}
        self.assertIn("approved_vehicle_stock", blocked)
        self.assertIn("legacy_url_redirects", blocked)

    def test_incomplete_vehicle_is_rejected(self):
        self.write_catalogue([{"id": "example", "marque": "Toyota"}])
        (self.root / "_redirects").write_text(
            "/products/old-example /vehicules/example 301\n", encoding="utf-8"
        )
        result = gate.check(self.root)
        self.assertIn("vehicle_0", {x["id"] for x in result["checks"] if x["status"] == "BLOCK"})

    def test_draft_can_be_machine_ready_without_production_approval(self):
        self.write_catalogue([{
            "id": "example", "marque": "Toyota", "modele": "Exemple",
            "annee": 2020, "prix_mga": 123456789,
            "disponibilite": "sur_demande", "photos": ["example.webp"]
        }])
        (self.root / "_redirects").write_text(
            "/products/old-example /vehicules/example 301\n", encoding="utf-8"
        )
        result = gate.check(self.root)
        self.assertTrue(result["machine_ready"])
        self.assertFalse(result["production_approved"])
        self.assertTrue(result["external_signoffs_required"])

    def test_invalid_redirects_are_rejected(self):
        self.write_catalogue([])
        (self.root / "_redirects").write_text(
            "/products/old-example https://some-other-domain.test/ 302\n",
            encoding="utf-8"
        )
        self.assertIn("legacy_url_redirects", {
            x["id"] for x in gate.check(self.root)["checks"] if x["status"] == "BLOCK"
        })


if __name__ == "__main__":
    unittest.main()
