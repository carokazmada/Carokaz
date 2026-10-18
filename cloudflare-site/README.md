# Carokaz Mada — version de préparation Cloudflare Pages

Dernière configuration vérifiée le 13 octobre 2026 : **Cloudflare Pages `carokazmada` est relié directement à GitHub `carokazmada/Carokaz`.** La connexion Git native remplace l'ancien déploiement Wrangler via GitHub Actions.

## Arborescence et déploiement

- **Production Cloudflare** : branche GitHub `main`, URL `https://carokazmada.pages.dev`.
- **Prévisualisations** : les autres branches GitHub sont actuellement acceptées par Cloudflare. La branche de travail est `preparation/cloudflare-contact-automatisation-20261012`.
- **Fichiers du site** : dossier `cloudflare-site/`, présent **uniquement sur la branche de préparation**, et non encore sur `main`.
- **Commande de build Cloudflare configurée** : `python3 cloudflare-site/scripts/verify.py && mkdir -p cloudflare-output && cp cloudflare-site/index.html cloudflare-site/404.html cloudflare-site/style.css cloudflare-site/robots.txt cloudflare-site/_headers cloudflare-site/catalogue.json cloudflare-output/`
- **Dossier de sortie** : `cloudflare-output`. Racine : `/`.
- La première compilation depuis `main` a échoué le 12 octobre, car `cloudflare-site/scripts/verify.py` n'existe pas sur `main`. Le dernier déploiement de production réussi avant la connexion Git reste à préserver.
- **Ne pas modifier la branche de production, fusionner la PR n°12 ou changer DNS/Shopify** pendant cette préparation.

## Travail déjà préparé

- Site vitrine français, responsive ; bouton d'appel `038 84 241 38` ; Facebook officiel `https://www.facebook.com/carokazmada/`.
- `404.html`, `robots.txt` et `_headers` ; catalogue volontairement vide et directives `noindex` pendant les essais.
- Aucune fiche, photo de véhicule, prix, courriel ou adresse non confirmés.
- `cloudflare-preflight.yml` teste les fichiers et conserve un ZIP et des rapports dans GitHub Actions.
- `cloudflare-preview-gated.yml` ne fait **plus aucun déploiement** via Wrangler : il exécute les tests locaux. **Cloudflare Git Integration** se charge désormais des prévisualisations Git, de manière indépendante.
- Les secrets GitHub R2 et Cloudflare API ne sont pas nécessaires aux builds Git de Pages. Ne jamais exposer de clés ou ajouter des permissions inutiles.

## Méthode pour une future mise en production

1. Vérifier l'URL et les pages de prévisualisation : téléphone, Facebook, catalogue, 404, `robots.txt` et responsive.
2. Vérifier les informations de contact, la disponibilité réelle, les prix et les images des véhicules.
3. Préparer une PR contrôlée apportant le dossier `cloudflare-site` sur `main`, en prévoyant sauvegarde et retour arrière. **La fusion sur `main` déclenchera alors une publication de production. Elle nécessite une approbation distincte.**
4. Tant qu'il s'agit d'un site de préparation, garder `noindex`; ne pas toucher au domaine `carokazmada.com` ni à Shopify.

Références : https://developers.cloudflare.com/pages/configuration/git-integration/ et https://developers.cloudflare.com/pages/configuration/preview-deployments/
