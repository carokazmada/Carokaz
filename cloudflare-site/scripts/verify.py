#!/usr/bin/env python3
from pathlib import Path
from html.parser import HTMLParser
import json, shutil, os, re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parent / "cloudflare-output"
FILES = ("index.html","404.html","style.css","app.js","robots.txt","_headers","catalogue.json","sitemap.xml","assets/hero-audi.webp","assets/catalogue-maquette.webp")
class Tags(HTMLParser):
    def __init__(self):
        super().__init__(); self.tags=[]
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag,dict(attrs)))
def main():
    for name in FILES:
        assert (ROOT/name).is_file(), name
    html=(ROOT/"index.html").read_text()
    js=(ROOT/"app.js").read_text()
    css=(ROOT/"style.css").read_text()
    p=Tags();p.feed(html)
    assert sum(t=="h1" for t,a in p.tags)==1
    assert 'tel:+261388424138' in html and '038 84 241 38' in html
    assert 'https://www.facebook.com/carokazmada/' in html
    assert 'const vehicles = [];' in js and 'demo-' not in js
    assert json.loads((ROOT/"catalogue.json").read_text())["vehicules"]==[]
    assert 'noindex' not in html and 'PRÉVISUALISATION' not in html
    assert 'https://carokazmada.pages.dev/' in html
    assert 'Disallow: /' not in (ROOT/"robots.txt").read_text()
    assert 'X-Content-Type-Options: nosniff' in (ROOT/"_headers").read_text()
    assert css.count('{')==css.count('}')
    for tag,a in p.tags:
        target=a.get("src","") or (a.get("href","") if tag=="link" else "")
        if target.startswith("/"):
            assert (ROOT/target.lstrip("/")).is_file(),target
    for name in ("assets/hero-audi.webp","assets/catalogue-maquette.webp"):
        b=(ROOT/name).read_bytes()
        assert b[:4]==b"RIFF" and b[8:12]==b"WEBP"
    if OUT.exists(): shutil.rmtree(OUT)
    for name in FILES:
        dest=OUT/name;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/name,dest)
    if os.environ.get("CF_PAGES_BRANCH","main")!="main":
        h=OUT/"index.html";h.write_text(h.read_text().replace('content="index,follow"','content="noindex,nofollow"'))
        h=OUT/"_headers";h.write_text(h.read_text().replace("/*\n","/*\n  X-Robots-Tag: noindex, nofollow\n",1))
        (OUT/"robots.txt").write_text("User-agent: *\nDisallow: /\n")
    print("OK: contacts, catalogue confirmé vide, ressources locales, sécurité, SEO et paquet complet.")
if __name__=="__main__": main()
