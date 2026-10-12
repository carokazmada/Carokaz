# Carokaz Mada — Préparation Cloudflare Pages

**Version de travail, non publiée.** Le fichier d'origine `Carokaz_Mada_Contact_V2.zip` n'était pas accessible : cette page a été préparée séparément, ce n'est pas sa copie exacte.

## État
- Page vitrine responsive en français, lien d'appel **038 84 241 38**, page Facebook officielle : https://www.facebook.com/carokazmada/
- Page d'erreur 404, catalogue volontairement vide (aucun prix ni véhicule inventé).
- `robots.txt`, balises robots et `X-Robots-Tag` désactivent l'indexation **du site provisoire**.
- Numéro secondaire, e-mail et adresse de showroom omis, faute de revalidation.
- Aucune modification de DNS, Shopify, Hostinger, campagnes, messages ou paiement.

## Validation automatique actuelle

Le workflow `.github/workflows/cloudflare-preflight.yml` est déclenché par toute modification pertinente sur la PR de brouillon. Il :
1. Vérifie les pages, les liens locaux, les boutons, le catalogue, les contrôles de base et `noindex`.
2. Assemble un paquet de site statique dans `cloudflare-preview-output`.
3. Archive ce paquet, avec sa somme de contrôle SHA-256, comme **artefact GitHub Actions** appelé `carokaz-cloudflare-pages-preview` (conservation 7 jours).

**L'artefact n'est PAS un déploiement Cloudflare.** Il est accessible depuis l'exécution correspondante dans l'onglet Actions de GitHub, sans changer les DNS. Il peut être utilisé ultérieurement pour un projet Pages compatible. Les contrôles automatiques n'assurent pas à eux seuls que les couleurs, textes ou cadrages sont satisfaisants sur tous les mobiles.

Exécution locale :

```sh
python3 cloudflare-site/scripts/verify.py
python3 -m http.server 8000 --directory cloudflare-site
```

## Future mise à jour automatique sans ZIP

Solution recommandée : créer **un projet Cloudflare Pages lié à GitHub** dans un compte Cloudflare autorisé. Le projet peut recevoir automatiquement des mises à jour issues du dépôt, sans import de ZIP.

Précautions :
- Le dossier `cloudflare-site` se trouve actuellement dans la branche `preparation/cloudflare-contact-automatisation-20261012`, **pas** dans `main`. Ne pas sélectionner `main` comme source du dossier tant que celui-ci n'y est pas présent.
- Pour un projet indépendant de test, ne pas lui associer `carokazmada.com` ni `www.carokazmada.com`.
- Réglages de build envisagés : *Framework preset* = None, commande de build = vide, dossier de sortie = `cloudflare-site`, racine = `/`.
- Attention : relier GitHub à Cloudflare et sélectionner une branche peut rendre la page visible sur un sous-domaine `pages.dev` ; cela reste une publication à examiner séparément.
- Un projet Cloudflare *Direct Upload* existant ne peut pas être simplement converti en projet Git ; laisser l'existant intact. Une autre solution est un déploiement via Wrangler dans un workflow distinct, avec secrets configurés dans GitHub, mais il ne doit pas être activé sans accès et validation spécifiques.
- Ne jamais placer de jeton ou de code de vérification dans GitHub, dans les pages du site, ni dans les conversations.

Documents Cloudflare officiels :
- https://developers.cloudflare.com/pages/configuration/git-integration/
- https://developers.cloudflare.com/pages/configuration/branch-build-controls/
- https://developers.cloudflare.com/pages/configuration/build-configuration/

## Migration complète éventuelle

Vérifier le stock et les prix avant d'importer les fiches, tester les mobiles et les conversions, inventorier les URL Shopify et préparer les redirections 301. Ensuite seulement approuver le basculement du domaine et le retrait du blocage d'indexation sur la nouvelle production.
