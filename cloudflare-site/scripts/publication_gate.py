#!/usr/bin/env python3
"""ECM publication readiness check. Never deploys, changes DNS, or calls services.

Default exit 0 to keep validation/previews non-blocking. --strict exits nonzero
until all locally verifiable migration blockers have been resolved. Externally
verified conditions (DNS, mail, real HTTP, consent) ALWAYS require human signoff.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check(root=ROOT):
    findings = []
    def add(item, ok, detail):
        findings.append({"id": item, "status": "PASS" if ok else "BLOCK",
                         "detail": detail})

    catalogue_path = root / "catalogue.json"
    try:
        catalogue = json.loads(catalogue_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        catalogue = {}
    vehicles = catalogue.get("vehicules", [])
    valid_list = isinstance(vehicles, list)
    add("catalogue_structure", valid_list and catalogue.get("devise") == "MGA",
        "Stock structuré en liste et devise MGA exigés.")
    if not valid_list:
        vehicles = []
    add("approved_vehicle_stock", len(vehicles) > 0,
        "Ne pas annoncer des véhicules disponibles sans fiches vérifiées.")
    for i, car in enumerate(vehicles):
        if not isinstance(car, dict):
            add("vehicle_" + str(i), False, "Fiche invalide.")
            continue
        essential = ("id", "marque", "modele", "annee", "prix_mga",
                     "disponibilite", "photos")
        missing = [field for field in essential if field not in car or not car[field]]
        if car.get("disponibilite") not in ("disponible", "vendu", "sur_demande"):
            missing.append("disponibilite_non_certifiee")
        if car.get("prix_mga") and (
            isinstance(car["prix_mga"], bool) or
            not isinstance(car["prix_mga"], int) or car["prix_mga"] <= 0
        ):
            missing.append("prix_mga_invalide")
        add("vehicle_" + str(i), not missing,
            "Données manquantes/incorrectes: " + ", ".join(missing) if missing
            else "Données minimales présentes; validation humaine encore nécessaire.")
    redirects_file = root / "_redirects"
    redirects = redirects_file.read_text(encoding="utf-8") if redirects_file.is_file() else ""
    rules = [line for line in redirects.splitlines()
             if line.strip() and not line.lstrip().startswith("#")]
    valid_rules = bool(rules) and all(
        len(line.split()) >= 3 and line.split()[0].startswith("/")
        and line.split()[1].startswith("/") and line.split()[2] in ("301", "308")
        for line in rules
    )
    add("legacy_url_redirects", valid_rules,
        "Anciennes URL recensées, cibles vérifiées et règles 301/308 nécessaires.")
    sitemap = (root / "sitemap.xml").read_text(encoding="utf-8") if (root / "sitemap.xml").is_file() else ""
    add("sitemap", "<loc>https://carokazmada.com/</loc>" in sitemap,
        "Le sitemap doit lister les URL réellement servies, sans rediriger vers des pages vides.")
    html = (root / "index.html").read_text(encoding="utf-8") if (root / "index.html").is_file() else ""
    add("canonical", 'href="https://carokazmada.com/"' in html,
        "Le canonical public doit correspondre au domaine cible.")
    add("noindex_not_in_production_source", 'content="index,follow"' in html,
        "Les prévisualisations doivent rester noindex; la production ne doit pas l'être.")

    external = [
        "Validation du stock et droits sur les images par le responsable ECM.",
        "Validation des redirections à partir des URL Shopify réellement indexées.",
        "Contrôle de HTTPS, robots, CSP, formulaires et rendu sur la production.",
        "Contrôle des MX, SPF, DKIM, DMARC et réception/envoi mail après bascule DNS.",
        "Contrôle de la délégation DNS et du domaine Pages; plan de retour arrière.",
        "Approbation de la PR et des protections GitHub par un autre réviseur autorisé."
    ]
    blockers = [f for f in findings if f["status"] == "BLOCK"]
    return {"project": "ECM / Carokaz Mada", "mode": "read_only",
            "machine_ready": not blockers, "blockers_count": len(blockers),
            "checks": findings, "external_signoffs_required": external,
            "production_approved": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true",
                        help="Exit 1 on unresolved machine-checkable blockers.")
    args = parser.parse_args()
    result = check()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if args.strict and not result["machine_ready"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
