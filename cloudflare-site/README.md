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

## Future mise à jour automatique sans ZIP : conserver le projet existant

Le projet Cloudflare Pages **carokazmada** a été vérifié avec le compte Cloudflare connecté. État observé le 13 octobre 2026 :
- Sous-domaine existant : `https://carokazmada.pages.dev`
- Mode : **Direct Upload** (`source = null`).
- Branche de production : `main`.
- Aucun domaine personnalisé lié.
- Dernier déploiement connu : production du 12 octobre 2026 ; aucun déploiement GitHub automatique observé.

**Choix retenu : GitHub Actions + Wrangler CLI, sans créer de nouveau projet Cloudflare.**

- La branche GitHub `preparation/cloudflare-contact-automatisation-20261012` contient les fichiers corrigés et les vérifications.
- Le workflow `.github/workflows/cloudflare-preflight.yml` produit automatiquement un ZIP contrôlé, un rapport d'audit et une archive statique, sans publier.
- Le workflow `.github/workflows/cloudflare-preview-gated.yml` permet une **prévisualisation uniquement** sur la branche Cloudflare `carokaz-validation`, mais son déploiement est désactivé par défaut.
- Il faudra, lors d'une autorisation spécifique distincte, configurer les secrets `CLOUDFLARE_ACCOUNT_ID` et `CLOUDFLARE_API_TOKEN` directement dans GitHub, puis activer la variable de dépôt `CAROKAZ_CLOUDFLARE_PREVIEW_AUTO=true`. Ces actions sont **en attente** et ne doivent jamais être réalisées en copiant les valeurs dans un fichier public.
- Installer l'application officielle Cloudflare Workers & Pages sur GitHub ne suffit pas, à lui seul, à convertir ce projet Direct Upload en intégration Git native ; cette conversion n'est pas prise en charge par Cloudflare.
- La connexion du compte Cloudflare à ChatGPT n'installe pas de secret automatiquement dans GitHub Actions.
- Toute modification de la production Cloudflare, du domaine `carokazmada.com`, des DNS ou de Shopify reste exclue de cette préparation.

Voir `cloudflare-site/AUTOMATISATION-CLOUDFLARE.md` pour les détails d'activation.

Documentation officielle : https://developers.cloudflare.com/pages/how-to/use-direct-upload-with-continuous-integration/

## Migration complète éventuelle

Vérifier le stock et les prix avant d'importer les fiches, tester les mobiles et les conversions, inventorier les URL Shopify et préparer les redirections 301. Ensuite seulement approuver le basculement du domaine et le retrait du blocage d'indexation sur la nouvelle production.
