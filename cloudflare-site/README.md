# Carokaz Mada — site statique

## Construire

Depuis la racine du dépôt :

```sh
python3 cloudflare-site/scripts/verify.py
```

Les fichiers générés se trouvent dans `cloudflare-output/`. Le script copie toutes les ressources nécessaires ; ne pas ajouter de copie manuelle après son exécution.

## Vérifier

```sh
python3 -m unittest discover -s cloudflare-site/tests -p 'test_*.py'
node --check cloudflare-site/app.js
```

`CF_PAGES_BRANCH=main` construit explicitement le candidat de production. Toute autre branche **ainsi qu'une exécution locale sans `CF_PAGES_BRANCH`** construisent une prévisualisation non indexable (`noindex,nofollow`, `X-Robots-Tag` et `robots.txt`). Sur Cloudflare, une identité de branche absente provoque un échec volontaire pour éviter toute ambiguïté. Les paramètres de l'hébergement doivent correspondre à cette convention.

Le thème et les photos sont conservés. Les règles CSS pour tablette et petits écrans empêchent les boutons de dépasser la largeur disponible.

Le site sert de vitrine institutionnelle et de sélection de modèles. Les données proviennent de `catalogue.json`, construit depuis les archives Shopify approuvées (19 fiches historiques, `ECM_IMPORT_ARCHIVES/`). Aucun prix ni disponibilité n'est certifié : chaque fiche affiche « Prix sur demande » et renvoie vers le contact Carokaz Mada. Aucune donnée client, commande ou prix n'est reprise des archives.

### Sécurité et référencement intégrés

- `_headers` : CSP à empreinte, HSTS, `nosniff`, `X-Frame-Options: DENY`, COOP/CORP, `Permissions-Policy`, cache immutable des assets.
- `_redirects` : anciennes URL Shopify (`/products/*`, `/collections/*`, …) redirigées en 301 vers l'accueil.
- `favicon.svg`, `site.webmanifest`, `assets/og-image.png` : icône, manifeste et image de partage.
- `sitemap.xml`, `robots.txt`, canonical et JSON-LD (`Organization`, `WebSite`, `AutoDealer`).

## Contrôle avant publication

- La branche `main` ne doit pas être modifiée ou déployée sans validation de la PR et des tests.
- Vérifier que le projet Pages est relié à la branche attendue, que la compilation réussit et que les prévisualisations restent `noindex`.
- Vérifier le stock réel, les photos, les droits de diffusion et les redirections des anciennes URLs. Le catalogue vide ne représente pas une migration achevée.
- Vérifier séparément les domaines Cloudflare Pages, les DNS Shopify/Hostinger, la réception des e-mails et le certificat TLS.
- Prévoir une sauvegarde et un chemin de retour arrière avant d'activer la publication de production.
- Conserver l'écosystème ECM indépendant de tout autre projet.
