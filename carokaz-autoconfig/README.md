# Carokaz Mada — Auto-configuration

Script d'exécution automatique des tâches restantes **automatisables par API**.

## Installation (5 min)

```bash
cd carokaz-autoconfig
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # puis remplir .env
```

## Utilisation

```bash
# 1. TOUJOURS commencer par une simulation
python carokaz_setup.py --all --dry-run

# 2. Si le rapport est correct, exécuter réellement
python carokaz_setup.py --all

# Tâches ciblées
python carokaz_setup.py --only T1              # webhook Messenger seul
python carokaz_setup.py --only T2              # audit lecture seule
python carokaz_setup.py --only T3 --gti-price 90000000
python carokaz_setup.py --only T8 --dry-run     # contrôle SEO sans écriture
python carokaz_setup.py --only T9,T10,T11 --dry-run # collections, articles et crawl public
python carokaz_setup.py --only T12              # Search Console Madagascar
```

## Tâches

| Tâche | Description |
|---|---|
| T1 | Messenger : souscription des champs webhook (`messages`, `messaging_postbacks`, ...) |
| T2 | Shopify : audit lecture seule du catalogue (SEO, canaux, metafields) |
| T3 | Shopify : création + publication de la Volkswagen Golf 7 GTI |
| T4 | Shopify : publication de tous les produits sur les 3 canaux (Online Store, Facebook & Instagram, Google & YouTube) |
| T5 | Shopify : ajout des metafields Google manquants (`condition=used`, `google_product_category`) |
| T6 | Google Search Console : soumission du sitemap |
| T7 | Génération du rapport JSON + Markdown dans `./rapports` |
| T8 | Contrôle SEO idempotent : complète les ALT manquants des médias et signale les produits sans métadonnées SEO, sans écraser les données existantes |
| T9 | Contrôle et complétion idempotente des métadonnées SEO des collections ciblées |
| T10 | Contrôle et complétion idempotente des `global.title_tag` et `global.description_tag` des articles |
| T11 | Crawl public : HTTP, title, description, H1, canonical, ALT, robots.txt et sitemap.xml |
| T12 | Collecte Search Console sur les 28 derniers jours : requêtes, pages, pays, clics |

Le rapport de chaque exécution est écrit dans `./rapports/rapport-<horodatage>.{json,md}`. Pour une exécution récurrente, utiliser le workflow GitHub Actions fourni dans `.github/workflows/carokaz-seo.yml` et renseigner le secret `SHOPIFY_ADMIN_TOKEN` avec les droits `read_products` et `write_products`. Le workflow exécute maintenant `T2,T5,T8,T9,T10,T11`, avec un arrêt explicite si le secret Shopify est absent. Un job Search Console séparé exécute `T12` lorsque `GOOGLE_SERVICE_ACCOUNT_JSON` est présent ; sinon il crée un rapport `DIFFÉRÉ` sans bloquer le crawl public.
