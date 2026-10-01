# Carokaz Mada — automatisation et qualité SEO

Ce dépôt contient l’**orchestration technique** de l’écosystème Carokaz Mada. La boutique publique actuellement contrôlée par les workflows est la boutique Shopify accessible à l’adresse [carokazmada.com](https://carokazmada.com). Le dépôt `carokazmada.github.io` correspond à une version statique historique et ne doit pas être considéré comme la source de vérité du catalogue en production.

## Périmètre des dépôts

| Dépôt | Rôle | Source de vérité |
|---|---|---|
| `Carokaz` | Scripts d’auto-configuration, audits SEO publics, Shopify et Search Console | Automatisation opérationnelle |
| `carokazmada.github.io` | Prototype/site statique historique | Non, sauf décision explicite de migration |
| `glowing-system` | Bot vocal Messenger avec transcription, génération de réponse et synthèse vocale | Service conversationnel séparé |

## Automatisation actuelle

Le workflow `.github/workflows/carokaz-seo.yml` est lancé chaque lundi à **03:17 UTC** et peut aussi être déclenché manuellement. Il produit trois familles de rapports :

1. Le crawl public vérifie les pages, les statuts HTTP, les titres, les méta-descriptions, les H1, les canoniques, les ALT, les données structurées, `robots.txt` et le sitemap.
2. Le rapport Search Console agrège les requêtes et pages visibles pour Madagascar sur les 28 derniers jours.
3. L’hygiène Shopify contrôle le catalogue, les métadonnées SEO, les ALT, les publications multicanales et les champs Google nécessaires au catalogue.

Les tâches externes sont **différées proprement** lorsque leurs secrets ne sont pas configurés. Le crawl public reste indépendant des accès Shopify et Google.

## Prérequis GitHub Actions

Les secrets suivants sont nécessaires pour activer les écritures ou les rapports privés :

| Secret | Utilisation |
|---|---|
| `SHOPIFY_ADMIN_TOKEN` | Audit et corrections idempotentes du catalogue Shopify |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Search Console et soumission du sitemap |

Les identifiants Meta nécessaires au bot et à la souscription des webhooks sont actuellement attendus dans l’environnement d’exécution du script, mais ne sont pas requis par le crawl public.

## Exécution locale

Depuis `carokaz-autoconfig` :

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python carokaz_setup.py --only T11 --dry-run
python carokaz_setup.py --only T1,T6,T12 --dry-run
```

La commande `--dry-run` ne doit pas être confondue avec un mode hors ligne : le crawl public continue de consulter le site pour mesurer son état, mais aucune mutation Shopify, Meta ou Google n’est envoyée.

Pour lancer les corrections Shopify, il faut d’abord vérifier le rapport de simulation, puis fournir `SHOPIFY_ADMIN_TOKEN` avec les scopes minimaux nécessaires. Les rapports sont écrits dans `carokaz-autoconfig/rapports/` et les artefacts CI sont conservés pendant 30 jours.

## Règles d’exploitation

Les données de prix, de stock, de disponibilité et de credentials ne doivent jamais être inventées ni ajoutées au dépôt. Les mutations sont conçues pour être idempotentes et ne complètent que les valeurs manquantes lorsque cela est possible. Toute mise en production d’une nouvelle source de catalogue doit d’abord préciser quel dépôt devient la source de vérité et comment la synchronisation sera effectuée.
