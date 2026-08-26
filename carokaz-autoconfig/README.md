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

# 2. Après revue humaine explicite du rapport, autoriser les écritures
python carokaz_setup.py --all --apply

# Tâches ciblées
python carokaz_setup.py --only T1 --dry-run  # webhook Messenger simulé
python carokaz_setup.py --only T2 --dry-run   # audit lecture seule
python carokaz_setup.py --only T3 --gti-price 90000000 --dry-run
python carokaz_setup.py --only T8 --dry-run     # contrôle SEO sans écriture
python carokaz_setup.py --only T9,T10,T11 --dry-run # collections, articles et crawl public
python carokaz_setup.py --only T12 --dry-run   # Search Console Madagascar
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

Le rapport de chaque exécution est écrit dans `./rapports/rapport-<horodatage>.{json,md}`. Pour une exécution récurrente, utiliser le workflow GitHub Actions fourni dans `.github/workflows/carokaz-seo.yml` et renseigner le secret `SHOPIFY_ADMIN_TOKEN` avec les droits `read_products` et `write_products`. Le workflow exécute les contrôles publics à chaque run ; si le secret Shopify est absent, le job Shopify est marqué `DIFFÉRÉ` sans bloquer le crawl. Un job Search Console séparé exécute `T12` lorsque `GOOGLE_SERVICE_ACCOUNT_JSON` est présent ; sinon il crée également un rapport `DIFFÉRÉ`.

## Renforcement de sécurité

Le script fonctionne désormais en **lecture seule par défaut**. Utiliser `--dry-run` pour une simulation explicite. Les écritures externes exigent `--apply` et doivent être lancées manuellement après revue du rapport. La tâche T4, qui peut modifier tout le catalogue, est bloquée même avec `--apply` tant que `--allow-bulk` n’est pas ajouté explicitement.

Exemples prudents :

```bash
python carokaz_setup.py --all --dry-run
python carokaz_setup.py --only T2,T5,T8,T9,T10 --dry-run
# Après revue humaine du rapport uniquement :
python carokaz_setup.py --only T5,T8 --apply
# T4 reste volontairement bloquée sans cette confirmation distincte :
python carokaz_setup.py --only T4 --apply --allow-bulk
```

Les rapports sont créés avec les permissions locales `0600`. Le script valide le domaine Shopify, n’envoie pas le jeton dans l’URL, borne les délais réseau et réessaie les erreurs de transport avec une temporisation limitée.
