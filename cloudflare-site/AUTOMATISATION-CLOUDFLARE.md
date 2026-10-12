# Connexion GitHub → Cloudflare Pages sans ZIP manuel

## Projet existant

Site de travail visible : https://carokazmada.pages.dev/

Ce dépôt prépare **deux workflows indépendants** :
- `cloudflare-preflight.yml` : tests, rapport public et ZIP de secours, sans déploiement.
- `cloudflare-preview-gated.yml` : chaîne Cloudflare Wrangler **désactivée par défaut** qui, une fois autorisée, ne publie que sur la branche d'aperçu `carokaz-validation`, jamais sur la branche de production.

L'ancienne version Cloudflare reste inchangée. Il n'est pas nécessaire de créer un nouveau projet si celui-ci est en mode Direct Upload : Wrangler fonctionne avec le projet existant.

## Première autorisation indispensable, une seule fois

1. Se connecter au bon compte Cloudflare sur https://dash.cloudflare.com/.
2. Confirmer le nom du projet Cloudflare Pages ; le plan préparé s'attend à `carokazmada` (le sous-domaine seul ne prouve pas le nom de projet).
3. Dans **Mon profil → API Tokens**, créer un jeton personnel limité au compte concerné et à **Cloudflare Pages: Edit** (ne pas partager le jeton dans un chat).
4. Dans **GitHub → carokazmada/Carokaz → Settings → Secrets and variables → Actions → Secrets**, enregistrer deux secrets nommés exactement `CLOUDFLARE_ACCOUNT_ID` et `CLOUDFLARE_API_TOKEN`. Ne jamais mettre les valeurs dans le code ou la conversation.
5. Tant que les secrets ne sont pas présents, aucun déploiement ne peut partir de cette automatisation.

**Sécurité :** Les secrets ne sont utilisés que dans un job soumis à une condition. Le premier appel est une vérification de projet en lecture seule. Le déploiement est bloqué si le projet n'existe pas ou si `carokaz-validation` correspond à la branche de production. Les fichiers d'audit et scripts ne sont jamais téléversés.

## Activer ultérieurement les prévisualisations automatiques

Quand les autorisations sont en place, dans **GitHub → Settings → Secrets and variables → Actions → Variables**, ajouter `CAROKAZ_CLOUDFLARE_PREVIEW_AUTO` avec la valeur `true`.

À chaque push sur la branche `preparation/cloudflare-contact-automatisation-20261012`, les tests précèdent le déploiement de **prévisualisation seulement**. Si la variable n'est pas `true`, le job Cloudflare est ignoré. La présence des secrets ne suffit pas à activer les publications.

Le lancement manuel par `workflow_dispatch` et la saisie de `PREVIEW` est une seconde option une fois que le workflow est disponible sur la branche par défaut ; ne pas fusionner la PR simplement pour l'obtenir.

Après un déploiement d'essai, une URL de type `carokaz-validation.carokazmada.pages.dev` peut apparaître si Cloudflare attribue cet alias ; ne pas traiter cette adresse comme une preuve avant de la vérifier.

**IMPORTANT :** Cette chaîne ne remplace pas la version principale `carokazmada.pages.dev`, elle prépare seulement une version de test. Le passage en production et tout changement de DNS nécessitent une décision distincte.

Documentation officielle Cloudflare :
- https://developers.cloudflare.com/pages/how-to/use-direct-upload-with-continuous-integration/
- https://developers.cloudflare.com/pages/get-started/direct-upload/
- https://developers.cloudflare.com/pages/configuration/git-integration/

## Correction de la politique GitHub Actions (12 octobre 2026)

La politique du dépôt refuse l'action externe cloudflare/wrangler-action. Le workflow a été corrigé pour utiliser la **CLI officielle Wrangler** avec `npx --yes wrangler@4 pages deploy` dans une étape shell conditionnelle. Aucune ouverture de permissions GitHub n'est nécessaire. Le workflow GitHub a été testé avec succès après correction : les tests locaux ont fonctionné et toutes les étapes de déploiement Cloudflare ont été ignorées par le verrou de sécurité (activation absente). Aucun déploiement n'a été effectué.

La validation finale d'un déploiement de prévisualisation nécessitera toujours une autorisation Cloudflare unique : ajouter `CLOUDFLARE_ACCOUNT_ID` et `CLOUDFLARE_API_TOKEN` dans les secrets GitHub, puis `CAROKAZ_CLOUDFLARE_PREVIEW_AUTO=true` seulement si l'automatisation de prévisualisation est souhaitée. Ne jamais transmettre ces identifiants dans la conversation.
