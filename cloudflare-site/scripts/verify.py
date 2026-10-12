#!/usr/bin/env python3
"""Vérification statique sans connexion réseau ni déploiement."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import json

ROOT = Path(__file__).resolve().parents[1]
PHONE = "tel:+261388424138"
FACEBOOK = "https://www.facebook.com/carokazmada/"
REQUIRED = ("index.html", "404.html", "style.css", "robots.txt", "_headers", "catalogue.json")

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.robots, self.headings = [], [], []
        self.lang = ""
        self.form_count = self.script_count = 0
        self.images_without_alt = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang", "")
        if tag in ("a", "link"):
            self.links.append(a.get("href", ""))
        if tag == "meta" and a.get("name") == "robots":
            self.robots.append(a.get("content", "").lower())
        if tag == "form":
            self.form_count += 1
        if tag == "script":
            self.script_count += 1
        if tag == "img" and not a.get("alt"):
            self.images_without_alt.append(a.get("src", ""))
        if tag in ("h1", "h2", "h3"):
            self.headings.append(tag)

def page(filename):
    p = Page()
    p.feed((ROOT / filename).read_text(encoding="utf-8"))
    return p

def main():
    for filename in REQUIRED:
        assert (ROOT / filename).is_file(), "Missing: " + filename
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    error_html = (ROOT / "404.html").read_text(encoding="utf-8")
    home, missing = page("index.html"), page("404.html")
    for p in (home, missing):
        assert p.lang == "fr", "Langue du site"
        assert "h1" in p.headings and p.headings[0] == "h1", "Titre H1"
        assert any("noindex" in x for x in p.robots), "Noindex"
        assert p.form_count == 0 and p.script_count == 0, "Aucune collecte ni script"
        assert not p.images_without_alt, "Image sans alt"
        assert "/style.css" in p.links, "CSS"
        for href in p.links:
            assert href, "Lien vide"
            if href.startswith(("tel:", "mailto:", "#")):
                continue
            url = urlsplit(href)
            if url.scheme:
                assert href == FACEBOOK, "Lien externe non valide: " + href
            elif href.startswith("/"):
                path = url.path.lstrip("/")
                assert not path or (ROOT / path).is_file(), "Lien interne cassé: " + href
            else:
                raise AssertionError("Lien relatif non validé: " + href)
    assert PHONE in home.links, "Bouton Appeler"
    assert FACEBOOK in home.links, "Bouton Facebook"
    assert "038 84 241 38" in index, "Téléphone confirmé"
    assert "032 78 214 42" not in index, "Téléphone secondaire non confirmé"
    assert "Catalogue en préparation" in index, "Statut catalogue"
    assert "ERREUR 404" in error_html and "/" in missing.links, "404 personnalisée"
    assert "X-Robots-Tag: noindex, nofollow" in (ROOT / "_headers").read_text(encoding="utf-8")
    assert "Disallow: /" in (ROOT / "robots.txt").read_text(encoding="utf-8")
    data = json.loads((ROOT / "catalogue.json").read_text(encoding="utf-8"))
    assert data["statut"] == "preparation" and data["devise"] == "MGA" and data["vehicules"] == [], "Catalogue en préparation"
    css = (ROOT / "style.css").read_text(encoding="utf-8")
    assert css.count("{") == css.count("}"), "Accolades CSS"
    print("OK : liens, contacts, indexation, 404, catalogue et HTML statique.")

if __name__ == "__main__":
    main()
