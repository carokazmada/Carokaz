#!/usr/bin/env python3
"""Vérification sans réseau de la maquette Codex Cloudflare, et copies des assets prévisualisation.

Seul le dépôt sur branche de préparation doit exécuter ce code. Ne modifie aucune
configuration Cloudflare, base de données, token ni fichier de production.
"""
from html.parser import HTMLParser
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parent / "cloudflare-output"
REQUIRED = ("index.html", "404.html", "style.css", "robots.txt", "_headers", "catalogue.json", "app.js", "assets/hero-audi.webp", "assets/catalogue-maquette.webp")
PHONE = "tel:+261388424138"
FACEBOOK = "https://www.facebook.com/carokazmada/"

class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lang = None
        self.tags = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.tags.append((tag, a))
        if tag == "html":
            self.lang = a.get("lang")

def main():
    for f in REQUIRED:
        assert (ROOT / f).is_file(), f"Fichier requis absent : {f}"
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    missing = (ROOT / "404.html").read_text(encoding="utf-8")
    css = (ROOT / "style.css").read_text(encoding="utf-8")
    js = (ROOT / "app.js").read_text(encoding="utf-8")
    hp = Tags(); hp.feed(index)
    np = Tags(); np.feed(missing)
    assert hp.lang == "fr" and np.lang == "fr", "Pages doivent être en français"
    assert any(tag == "h1" for tag, _ in hp.tags), "H1 manquant"
    assert any(tag == "h1" for tag, _ in np.tags), "H1 404 manquant"
    for p in (hp, np):
        assert any(tag == "meta" and a.get("name") == "robots" and "noindex" in a.get("content","") for tag,a in p.tags), "noindex HTML manquant"
        assert any(tag == "link" and a.get("href") == "/style.css" for tag,a in p.tags), "style.css absent du HTML"
    hrefs = [a.get("href", "") for tag,a in hp.tags if tag == "a"]
    assert PHONE in hrefs and FACEBOOK in hrefs, "Téléphone ou Facebook manquant"
    assert "038 84 241 38" in index, "Numéro officiel manquant"
    assert any(tag == "script" and a.get("src") == "/app.js" for tag,a in hp.tags), "JavaScript local manquant"
    assert all(not a.get("src", "").startswith("http") for tag,a in hp.tags if tag == "script"), "Script tiers interdit"
    assert not any(tag == "form" and a.get("action") for tag,a in hp.tags), "Interdiction d'envoyer un formulaire"
    assert "PRÉVISUALISATION" in index and "démonstration" in index, "Avertissement maquette absent"
    assert "Prix à confirmer" in js and "demo-" in js, "Catalogue démonstratif non signalé"
    assert "'/assets/hero-audi.webp'" in css and "'/assets/catalogue-maquette.webp'" in css, "Images locales incorrectes"
    assert css.count("{") == css.count("}"), "CSS invalide"
    assert "ERREUR 404" in missing or "introuvable" in missing.lower(), "404 non conforme"
    assert "Disallow: /" in (ROOT / "robots.txt").read_text(), "robots.txt non bloquant"
    headers = (ROOT / "_headers").read_text()
    assert "X-Robots-Tag: noindex, nofollow" in headers, "noindex header manquant"
    d = json.loads((ROOT / "catalogue.json").read_text())
    assert d.get("vehicules") == [] and d.get("statut") == "preparation", "Annonce commerciale non autorisée"
    for filename in ("assets/hero-audi.webp", "assets/catalogue-maquette.webp"):
        b = (ROOT / filename).read_bytes()
        assert b[:4] == b"RIFF" and b[8:12] == b"WEBP", "Image WebP invalide : " + filename
    # Le build Cloudflare configuré copie six fichiers existants après ce script.
    # Copier seulement les trois ressources complémentaires non présentes dans cette commande.
    (OUT / "assets").mkdir(parents=True, exist_ok=True)
    (OUT / "app.js").write_bytes((ROOT / "app.js").read_bytes())
    for filename in ("hero-audi.webp", "catalogue-maquette.webp"):
        (OUT / "assets" / filename).write_bytes((ROOT / "assets" / filename).read_bytes())
    print("OK : maquette Codex, coordonnées, noindex, 404, JS local, WebP et catalogue vide. Prévisualisation uniquement.")

if __name__ == "__main__":
    main()
