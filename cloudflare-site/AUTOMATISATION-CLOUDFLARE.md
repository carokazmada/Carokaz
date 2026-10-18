# Cloudflare Pages + GitHub — configuration actuellement active

État vérifié le 13 octobre 2026 par l'API Cloudflare du compte connecté :

- Projet existant : `carokazmada` ; URL `https://carokazmada.pages.dev`.
- Source Cloudflare : `github`, dépôt `carokazmada/Carokaz`.
- Branche de production : `main`.
- Prévisualisations Git activées pour les branches autres que `main`.
- Compilation Git intégrée : vérifier `cloudflare-site/scripts/verify.py`, copier les fichiers statiques dans `cloudflare-output`.
- Le dossier `cloudflare-site` n'est **pas dans `main`**, d'où l'échec de la compilation initiale de la branche de production.
- Le dossier est présent dans la branche `preparation/cloudflare-contact-automatisation-20261012`, source candidate pour une prévisualisation Git.
- Aucun domaine personnalisé n'est lié au projet Pages. Shopify et le domaine principal ne sont pas concernés par cette connexion.

## Modification de la chaîne CI

Le workflow GitHub Actions `.github/workflows/cloudflare-preview-gated.yml` ne tente plus de publier avec Wrangler ou `CLOUDFLARE_API_TOKEN`. Il est désormais limité à la **validation**. Les déploiements de prévisualisation sont effectués automatiquement par l'intégration Git Cloudflare lors des pushes autorisés.

Ainsi, le refus API `upload-token` (erreur 10000) du jeton GitHub n'empêche pas la Git Integration de fonctionner. Les deux mécanismes sont distincts.

## Barrières

- Ne jamais fusionner la PR n°12 ou changer la branche de production sans décision explicite : ce serait une publication du site sur `carokazmada.pages.dev`.
- Ne jamais désactiver `noindex` durant les tests, inventer les véhicules ni modifier le DNS.
- Toute modification dans la branche de préparation peut entraîner une **prévisualisation publique** par la Git Integration.
- Les deux secrets Cloudflare de GitHub ne sont plus requis pour cette intégration, mais leur révocation ou modification relève d'une décision séparée, pas de cette préparation.
- Les identifiants `Access Key ID` et `Secret Access Key` sont généralement des clés R2 et ne doivent pas être utilisés pour les déploiements Git Pages.

## Diagnostic et tests

`python3 cloudflare-site/scripts/verify.py`

Les tests GitHub sont non destructifs ; les compilations Cloudflare sont indépendantes. Vérifier leur résultat dans **Cloudflare → Workers & Pages → carokazmada → Déploiements**.

## Déclenchement des previews Git — correction du 13 octobre 2026

Cloudflare Pages ignore intentionnellement une compilation si le message du commit commence par certains marqueurs, notamment `[CF-Pages-Skip]`, `[CI Skip]` ou `[Skip CI]`. Les commits préparatoires précédents utilisaient ce préfixe, d'où leur déploiement Cloudflare créé mais immédiatement ignoré (`queued/idle`).

Désormais :
- Utiliser un message de commit **sans marqueur de saut** pour demander une prévisualisation sur la branche de travail.
- Les changements poussés sur `preparation/cloudflare-contact-automatisation-20261012` déclenchent une prévisualisation **publique** mais distincte de la production.
- Conserver `main` inchangé : aucun commit ou merge vers `main` avant validation de la mise en production.
- Vérifier le résultat effectif dans Cloudflare (état `success`) et la présence des pages avant d'annoncer que le déploiement a réussi.

Référence officielle : https://developers.cloudflare.com/pages/configuration/git-integration/github-integration/
