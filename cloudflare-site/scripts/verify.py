#!/usr/bin/env python3
"""Prévalidation locale, sans réseau et sans effet sur les sites existants."""
from pathlib import Path
import json
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
PHONE = "tel:+261388424138"
FACEBOOK = "https://www.facebook.com/carokazmada/"


class LinksAndMeta(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []
        self.meta_robots = []
        self.lang = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if tag in ("a", "link"):
            self.hrefs.append(a.get("href"))
        if tag == "meta" and a.get("name") == "robots":
            self.meta_robots.append(a.get("content", "").lower())


def main():
    for name in ("index.html", "404.html", "style.css", "robots.txt", "_headers", "catalogue.json"):
        assert (ROOT / name).is_file(), f"Fichier obligatoire absent : {name}"

    homepage = (ROOT / "index.html").read_text(encoding="utf-8")
    parser = LinksAndMeta()
    parser.feed(homepage)
    assert parser.lang == "fr", "Langue française absente"
    assert PHONE in parser.hrefs, "Lien téléphone absent"
    assert FACEBOOK in parser.hrefs, "Lien Facebook officiel absent"
    assert any("noindex" in r for r in parser.meta_robots), "noindex absent"
    assert "/style.css" in parser.hrefs, "Feuille de style absente"
    assert '<h1>' in homepage and '</h1>' in homepage, "Titre H1 absent"
    assert '038 84 241 38' in homepage, "Téléphone affiché non conforme"
    assert '032 78 214 42' not in homepage, "Numéro secondaire non confirmé"
    assert 'Catalogue en préparation' in homepage, "Catalogue ne doit pas être présenté comme publié"

    headers = (ROOT / "_headers").read_text(encoding="utf-8")
    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    assert "X-Robots-Tag: noindex" in headers, "En-tête robots manquant"
    assert "Disallow: /" in robots, "robots.txt doit bloquer les robots"
    assert 'noindex' in (ROOT / "404.html").read_text(encoding="utf-8")

    data = json.loads((ROOT / "catalogue.json").read_text(encoding="utf-8"))
    assert data["vehicules"] == [], "Le catalogue provisoire doit rester vide"
    assert data["statut"] == "preparation"

    print("OK : contacts, 404, indexation bloquée et catalogue provisoire vérifiés.")


if __name__ == "__main__":
    main()
