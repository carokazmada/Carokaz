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

Le rapport de chaque exécution est écrit dans `./rapports/rapport-<horodatage>.{json,md}`.
