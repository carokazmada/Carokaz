# ECM — mise à niveau de la vitrine (2026-10-27)

Branche : `fix/ecm-audit-20261021` (PR #15). Aucune fusion, aucun déploiement,
aucune modification DNS réalisée par l'agent.

## Ce qui a été corrigé / optimisé

### Sécurité (en-têtes Cloudflare `_headers`)
- `Strict-Transport-Security: max-age=31536000; includeSubDomains` (HSTS).
- `Cross-Origin-Opener-Policy: same-origin` et `Cross-Origin-Resource-Policy: same-origin`.
- `X-Permitted-Cross-Domain-Policies: none`, `Permissions-Policy` élargie
  (`payment=()`, `usb=()` en plus de caméra/micro/géolocalisation).
- CSP conservée (empreinte du JSON-LD recalculée après enrichissement), `manifest-src 'self'`.
- Cache immutable des assets, `X-Robots-Tag: noindex` sur la page 404.

### Référencement et partage
- JSON-LD enrichi : `Organization` (+ adresse, zone desservie, logo, image),
  `WebSite`, et nouveau `AutoDealer` (prix `$$`, devise `MGA`).
- `og:image` PNG 1200×630 (`assets/og-image.png`), balises Twitter Card.
- `favicon.svg`, `site.webmanifest` (icône, `start_url`, `theme_color`).
- `robots.txt` en `Allow: /`, `sitemap.xml` sur `https://carokazmada.com/`.
- Canonical unique `https://carokazmada.com/`.

### Transfert des données Shopify (vitrine, sans prix)
- `catalogue.json` construit depuis les **19 fiches historiques** de
  `ECM_IMPORT_ARCHIVES/INVENTAIRE_19_BROUILLONS.csv` (PR #17) : identité du
  véhicule (marque, modèle, année, catégorie) uniquement.
- **Aucun prix, aucune disponibilité certifiée, aucune photo, aucune donnée
  client/commande.** Chaque fiche affiche « Prix sur demande » et renvoie vers le
  contact Carokaz Mada.
- `app.js` réécrit : rendu par API DOM (`textContent`, `replaceChildren`, aucune
  injection HTML), filtres dynamiques marque/modèle/année/catégorie.
- Section catalogue renommée « Notre sélection », repli `<noscript>`.

### Redirections des anciennes URL Shopify
- `_redirects` : `/products/*`, `/collections/*`, `/pages/*`, `/blogs/*`,
  `/cart`, `/account/*` → `/` en **301**, cibles internes uniquement.

### Garde-fous et tests
- `verify.py` valide les nouveaux fichiers, refuse tout prix publié, toute
  disponibilité certifiée et toute photo, et contrôle les règles de redirection.
- `publication_gate.py` : mode vitrine (prix non affichés) sans bloquer, tout en
  interdisant un prix inventé.
- Nouvelle suite `tests/test_showcase.py` (rendu DOM, SEO, en-têtes, redirections).
- **24/24 tests** OK, `node --check app.js` OK, scan de secrets : 0.

## Reste à faire (action humaine obligatoire)

1. **Fusionner la PR #15** — la protection de branche exige un second réviseur.
2. Vérifier côté Cloudflare (Workers & Pages → `carokazmada` → Déploiements) que
   la compilation de `main` réussit après fusion.
3. Diagnostic de la panne `carokazmada.com` (HTTP 402, Shopify) — hors périmètre agent.
4. Basculer le DNS de `carokazmada.com` vers Pages : impact MX Hostinger à valider.
5. Valider les prix réels, les photos (droits de diffusion) et les anciennes URL
   indexées avant d'enrichir le catalogue.
