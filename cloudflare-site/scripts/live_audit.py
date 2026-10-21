#!/usr/bin/env python3
"""Carokaz Mada : audit public Cloudflare en lecture seule.

GET uniquement sur le sous-domaine de préparation. Jamais de jeton, cookies,
modification, publication, formulaire, appel à un service payant ou DNS.
Le rapport différencie un résultat observé d'un accès réseau impossible.
"""
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import json
import os

BASE = "https://fix-ecm-audit-20261021.carokazmada.pages.dev"
USER_AGENT = "CarokazMada-SiteAudit/1.0 (read-only)"
PHONE_LINK = "tel:+261388424138"
FB_URL = "https://www.facebook.com/carokazmada/"


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.h1 = ""
        self.robots = []
        self.hrefs = []
        self._tag = ""
    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        self._tag = tag if tag in ("title", "h1") else ""
        if tag == "meta" and data.get("name", "").lower() == "robots":
            self.robots.append(data.get("content", "").lower())
        if tag == "a":
            self.hrefs.append(data.get("href", ""))
    def handle_endtag(self, tag):
        if tag in ("title", "h1"):
            self._tag = ""
    def handle_data(self, data):
        if self._tag == "title":
            self.title += data
        if self._tag == "h1":
            self.h1 += data


def fetch(path):
    req = Request(BASE + path, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(req, timeout=15) as res:
            raw = res.read(250_000)
            return {"status": res.status, "body": raw.decode("utf-8", errors="replace"),
                    "content_type": res.headers.get("Content-Type", ""),
                    "x_robots_tag": res.headers.get("X-Robots-Tag", ""),
                    "csp": res.headers.get("Content-Security-Policy", ""),
                    "nosniff": res.headers.get("X-Content-Type-Options", ""),
                    "frame_options": res.headers.get("X-Frame-Options", "")}
    except HTTPError as exc:
        return {"status": exc.code,
                "body": exc.read(20_000).decode("utf-8", errors="replace"),
                "content_type": exc.headers.get("Content-Type", ""),
                "x_robots_tag": exc.headers.get("X-Robots-Tag", ""),
                "csp": exc.headers.get("Content-Security-Policy", ""),
                "nosniff": exc.headers.get("X-Content-Type-Options", ""),
                "frame_options": exc.headers.get("X-Frame-Options", "")}
    except (URLError, OSError, TimeoutError) as exc:
        return {"error": type(exc).__name__ + ": " + str(exc)[:180]}


def audit():
    results = {path: fetch(path) for path in ("/", "/robots.txt", "/404.html")}
    facts = []
    home = results["/"]
    if "error" in home:
        facts.append({"id": "homepage", "status": "BLOQUÉ", "detail": "Accès au site impossible depuis ce runner, sans preuve de panne publique"})
    else:
        parser = Page()
        parser.feed(home["body"])
        facts.append({"id": "homepage", "status": "OK" if home["status"] == 200 else "ANOMALIE",
                      "detail": "HTTP " + str(home["status"]) + "; titre: " + parser.title[:120]})
        facts.append({"id": "contact", "status": "OK" if PHONE_LINK in parser.hrefs else "ANOMALIE",
                      "detail": "Lien téléphone principal " + ("présent" if PHONE_LINK in parser.hrefs else "absent")})
        facts.append({"id": "facebook", "status": "OK" if FB_URL in parser.hrefs else "ANOMALIE",
                      "detail": "Lien Facebook officiel " + ("présent" if FB_URL in parser.hrefs else "absent")})
        has_noindex = any("noindex" in x for x in parser.robots) or "noindex" in home["x_robots_tag"].lower()
        facts.append({"id": "noindex", "status": "OK" if has_noindex else "ANOMALIE",
                      "detail": "Directive noindex " + ("observée" if has_noindex else "non observée dans les éléments contrôlés")})
    if "error" not in home:
        csp = home.get("csp", "")
        checks = {
            "csp": "default-src 'self'" in csp and "frame-ancestors 'none'" in csp,
            "nosniff": home.get("nosniff", "").lower() == "nosniff",
            "anti_clickjacking": home.get("frame_options", "").upper() == "DENY",
        }
        for check, passed in checks.items():
            facts.append({"id": check, "status": "OK" if passed else "ANOMALIE",
                          "detail": "En-tête HTTP " + ("présent" if passed else "absent ou incorrect")})
    robots = results["/robots.txt"]
    if "error" in robots:
        facts.append({"id": "robots_txt", "status": "BLOQUÉ", "detail": robots["error"]})
    else:
        is_robot_txt = ("text/plain" in robots["content_type"].lower()
                        or robots["body"].lstrip().lower().startswith(("user-agent:", "#")))
        html_fallback = "<html" in robots["body"][:500].lower() or "<!doctype html" in robots["body"][:500].lower()
        facts.append({"id": "robots_txt",
                      "status": "ANOMALIE" if html_fallback or not is_robot_txt else "OK",
                      "detail": "HTTP " + str(robots["status"]) + ", type " + robots["content_type"] +
                      "; " + ("page HTML renvoyée" if html_fallback else "texte robots reconnu" if is_robot_txt else "texte robots non reconnu")})
    missing = results["/404.html"]
    if "error" in missing:
        facts.append({"id": "404", "status": "BLOQUÉ", "detail": missing["error"]})
    else:
        distinct_404 = ("Cette page est introuvable" in missing["body"]
                        or "Cette page n’existe pas sur ce site." in missing["body"]
                        or "ERREUR 404" in missing["body"])
        facts.append({"id": "404", "status": "OK" if distinct_404 else "À VÉRIFIER",
                      "detail": "Une page 404 personnalisée " + ("a été observée" if distinct_404 else "n'a pas été observée")})
    return {"generated_at": datetime.now(timezone.utc).isoformat(), "target": BASE,
            "scope": "lecture seule sur site public", "facts": facts,
            "http_status": {k: v.get("status") for k, v in results.items()}}


def main():
    report = audit()
    out = Path(os.environ.get("CAROKAZ_AUDIT_DIR", "rapports-publics"))
    out.mkdir(parents=True, exist_ok=True)
    (out / "cloudflare-public.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# Carokaz Mada — état public de Cloudflare Pages",
             "", "Cible : " + report["target"], "", "Lecture seule ; aucun déploiement.", ""]
    for f in report["facts"]:
        lines.append("- **" + f["id"] + "** [" + f["status"] + "] : " + f["detail"])
    lines.extend(["", "Les anomalies ci-dessus concernent la version publique, pas les fichiers GitHub de préparation.",
                  "L'absence de liaison Git n'est pas démontrable depuis la page publique.", ""])
    (out / "cloudflare-public.md").write_text("\n".join(lines), encoding="utf-8")
    for f in report["facts"]:
        print("[" + f["status"] + "] " + f["id"] + " - " + f["detail"])
    print("Rapport :", str(out))


if __name__ == "__main__":
    main()
