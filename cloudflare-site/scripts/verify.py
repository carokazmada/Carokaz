#!/usr/bin/env python3
"""Validate and assemble ECM assets; non-main branches always stay noindex."""
from pathlib import Path
from html.parser import HTMLParser
import base64
import hashlib
import json
import os
import shutil
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parent / 'cloudflare-output'
CANONICAL = 'https://carokazmada.com/'
FILES = ('index.html', '404.html', 'style.css', 'app.js', 'robots.txt', '_headers',
         'catalogue.json', 'sitemap.xml', 'assets/hero-audi.webp', 'assets/catalogue-maquette.webp',
         'assets/ECM_THEME_REFERENCE_ORIGINALE_2026-10-21.jpg', 'theme-exact.html', 'theme-exact.css')


class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.jsonld = []
        self.in_jsonld = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if tag == 'script':
            self.in_jsonld = attrs.get('type') == 'application/ld+json'

    def handle_data(self, data):
        if self.in_jsonld:
            self.jsonld.append(data)

    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_jsonld = False


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    for name in FILES:
        require((ROOT / name).is_file(), 'Missing asset: ' + name)
    html = (ROOT / 'index.html').read_text()
    headers = (ROOT / '_headers').read_text()
    robots = (ROOT / 'robots.txt').read_text()
    p = Tags()
    p.feed(html)
    require(sum(t == 'h1' for t, a in p.tags) == 1, 'Exactly one h1 required')
    require('tel:+261388424138' in html and '038 84 241 38' in html, 'ECM phone mismatch')
    require('https://www.facebook.com/carokazmada/' in html, 'ECM Facebook missing')
    require([a.get('href') for t, a in p.tags if t == 'link' and a.get('rel') == 'canonical'] == [CANONICAL], 'Canonical mismatch')
    require([a.get('content') for t, a in p.tags if t == 'meta' and a.get('name') == 'robots'] == ['index,follow'], 'Source must be indexable')
    require('Disallow: /' not in robots and CANONICAL + 'sitemap.xml' in robots, 'Production robots mismatch')
    locations = [e.text for e in ET.fromstring((ROOT / 'sitemap.xml').read_text()).iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    require(locations == [CANONICAL], 'Sitemap must match published pages')
    require('X-Content-Type-Options: nosniff' in headers, 'Security header missing')
    require(p.jsonld, 'Structured data missing')
    for raw in p.jsonld:
        data = json.loads(raw)
        require(data.get('@context') == 'https://schema.org', 'JSON-LD context mismatch')
        digest = base64.b64encode(hashlib.sha256(raw.encode()).digest()).decode()
        require("'sha256-" + digest + "'" in headers, 'JSON-LD CSP hash mismatch')
    catalogue = json.loads((ROOT / 'catalogue.json').read_text())
    require(catalogue.get('devise') == 'MGA' and isinstance(catalogue.get('vehicules'), list), 'Invalid catalogue')
    # No stock is certified yet. Supporting real listings requires a separate reviewed change.
    require(catalogue['vehicules'] == [] and catalogue.get('statut') == 'stock_non_confirme', 'Stock needs reviewed integration')
    css = (ROOT / 'style.css').read_text()
    require(css.count('{') == css.count('}'), 'Unbalanced CSS')
    for tag, attrs in p.tags:
        target = attrs.get('src', '') or (attrs.get('href', '') if tag == 'link' else '')
        if target.startswith('/'):
            require((ROOT / target.lstrip('/')).is_file(), 'Missing resource: ' + target)
    for name in ('assets/hero-audi.webp', 'assets/catalogue-maquette.webp'):
        content = (ROOT / name).read_bytes()
        require(content[:4] == b'RIFF' and content[8:12] == b'WEBP', 'Invalid WebP: ' + name)
    branch = os.environ.get('CF_PAGES_BRANCH', 'main')
    if os.environ.get('CF_PAGES') and not os.environ.get('CF_PAGES_BRANCH'):
        raise ValueError('Cloudflare branch identity missing; refusing ambiguous build')
    preview = branch != 'main'
    if OUT.exists():
        shutil.rmtree(OUT)
    for name in FILES:
        dest = OUT / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, dest)
    if preview:
        target = OUT / 'index.html'
        target.write_text(target.read_text().replace('content="index,follow"', 'content="noindex,nofollow"'))
        target = OUT / '_headers'
        target.write_text(target.read_text().replace('/*\n', '/*\n  X-Robots-Tag: noindex, nofollow\n', 1))
        (OUT / 'robots.txt').write_text('User-agent: *\nDisallow: /\n')
    if branch == 'design/ecm-theme-exact-20261021':
        # This is ONLY a noindex preview. Never replace a production build with the picture.
        require(preview, 'Reference mockup must not be deployed as production')
        (OUT / 'index.html').write_text((ROOT / 'theme-exact.html').read_text())
        require('content="noindex,nofollow"' in (OUT / 'index.html').read_text(), 'Theme preview must be noindex')
    print('OK: ECM assets, canonical, JSON-LD, CSP; mode=' + ('preview' if preview else 'production-candidate'))
    print('Publication readiness NOT certified: current stock, domain mapping, redirects and analytics still require verification.')


if __name__ == '__main__':
    main()
