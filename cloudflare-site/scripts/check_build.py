#!/usr/bin/env python3
"""ECM: validate local Cloudflare Pages build outputs without deploying."""
import argparse
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

SITE = Path(__file__).resolve().parents[1]
OUTPUT = SITE.parent / "cloudflare-output"
CANONICAL = "https://carokazmada.com/"


class Metadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.robots = []
        self.canonicals = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta" and attrs.get("name", "").lower() == "robots":
            self.robots.append(attrs.get("content", "").lower())
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonicals.append(attrs.get("href"))


def inspect(mode, source=SITE, output=OUTPUT):
    """Check generated files. Passing static checks NEVER authorizes publication."""
    if mode not in ("preview", "production"):
        raise ValueError("mode must be preview or production")
    output = Path(output)
    errors = []
    required = ("index.html", "robots.txt", "_headers", "sitemap.xml",
                "style.css", "app.js", "catalogue.json", "404.html")
    for name in required:
        if not (output / name).is_file():
            errors.append("missing: " + name)
    if errors:
        return make_report(mode, errors, "INCONNU")
    html = (output / "index.html").read_text(encoding="utf-8")
    robots = (output / "robots.txt").read_text(encoding="utf-8")
    headers = (output / "_headers").read_text(encoding="utf-8")
    common_headers = headers.split("/404.html", 1)[0]
    parser = Metadata()
    parser.feed(html)
    if parser.canonicals != [CANONICAL]:
        errors.append("canonical_incorrect")
    if "X-Content-Type-Options: nosniff" not in common_headers:
        errors.append("nosniff_missing")
    if "Content-Security-Policy:" not in common_headers:
        errors.append("csp_missing")
    if "script-src" not in common_headers or "'unsafe-eval'" in common_headers:
        errors.append("csp_scripts_unsafe")
    if mode == "preview":
        if not any("noindex" in x and "nofollow" in x for x in parser.robots):
            errors.append("preview_indexable_html")
        if "X-Robots-Tag: noindex, nofollow" not in common_headers:
            errors.append("preview_indexable_header")
        if not re.search(r"(?im)^\s*Disallow:\s*/\s*$", robots):
            errors.append("preview_robots_missing_disallow")
    else:
        if parser.robots != ["index,follow"]:
            errors.append("production_indexation_invalid")
        if "X-Robots-Tag: noindex" in common_headers:
            errors.append("production_blocked_by_header")
        if re.search(r"(?im)^\s*Disallow:\s*/\s*$", robots):
            errors.append("production_blocked_by_robots")
        if "Sitemap: " + CANONICAL + "sitemap.xml" not in robots:
            errors.append("production_sitemap_missing")
    try:
        tree = ET.fromstring((output / "sitemap.xml").read_text(encoding="utf-8"))
        links = [x.text for x in tree.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        if links != [CANONICAL]:
            errors.append("sitemap_links_incorrect")
    except (ET.ParseError, OSError):
        errors.append("sitemap_invalid")
    try:
        catalog = json.loads((output / "catalogue.json").read_text(encoding="utf-8"))
        vehicles = catalog.get("vehicules")
        if catalog.get("devise") != "MGA" or not isinstance(vehicles, list):
            errors.append("catalogue_schema_invalid")
            stock = "INCONNU"
        elif not vehicles:
            stock = "NON_CONFIRME"
            if catalog.get("statut") != "stock_non_confirme":
                errors.append("catalogue_status_invalid")
        else:
            stock = "A_VERIFIER"
    except (OSError, ValueError, TypeError):
        errors.append("catalogue_invalid")
        stock = "INCONNU"
    return make_report(mode, errors, stock)


def make_report(mode, errors, stock):
    blockers = [
        "domaine_pages_a_tester_en_ligne",
        "redirections_anciennes_urls_a_valider",
        "emails_hostinger_a_tester",
        "approbation_humaine_et_rollback_requis",
    ]
    if stock != "CONFIRME":
        blockers.insert(0, "stock_et_photos_non_valides")
    return {
        "ecosysteme": "ECM — Carokaz Mada",
        "mode": mode,
        "build": "FAIL" if errors else "PASS",
        "erreurs": errors,
        "stock": stock,
        "publication_autorisee": False,
        "publication": "NON_CERTIFIEE",
        "blocages_publication": blockers,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("production", "preview"), required=True)
    ap.add_argument("--output", type=Path, default=OUTPUT)
    args = ap.parse_args()
    report = inspect(args.mode, output=args.output)
    report["horodatage_utc"] = datetime.now(timezone.utc).isoformat()
    dest = Path("rapports-build")
    dest.mkdir(exist_ok=True)
    (dest / ("ecm-" + args.mode + ".json")).write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    summary = (
        f"### ECM — Build {args.mode}\n"
        f"- Vérification locale : **{report['build']}**\n"
        f"- Catalogue : **{report['stock']}**\n"
        "- Publication : **NON CERTIFIÉE**\n"
        f"- Anomalies : {', '.join(report['erreurs']) or 'aucune'}\n"
        f"- Bloqueurs : {', '.join(report['blocages_publication'])}\n"
    )
    print(summary)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as fh:
            fh.write(summary + "\n")
    return 1 if report["erreurs"] else 0


if __name__ == "__main__":
    sys.exit(main())
