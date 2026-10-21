# ECM / Carokaz Mada — migration des archives Shopify (préparation)

État vérifié le 21 octobre 2026.

- Source : `ECM_RECUPERATION_ALTERNATIVE_2026-10-21.zip` (fichier externe au dépôt).
- Lot autorisé : **19 fiches historiques en brouillon** et **35 photos** ; les images concernent seulement 4 véhicules (Hilux, Fortuner, Tiguan et BMW X3).
- Archives : aucun stock actuel ni tarif public vérifié ; conserver `publie=false`, `prix_public_mga=null`, `stock_actuel_verifie=false`.
- Éléments exclus : catalogue maître historique de 71 lignes, données clients, commandes, jetons, identifiants privés.
- Les photographies ont des plaques visibles. Vérifier les droits de diffusion et l'identité des véhicules avant exposition sur le site.
- Cette branche de préparation n'est pas une branche de production Cloudflare et n'est pas ajoutée à la liste des branches de prévisualisation.
- Ne pas copier l'archive brute dans `cloudflare-site/` ou `cloudflare-output/` : les fichiers d'import ne doivent pas devenir des ressources HTTP indexables.
- Le catalogue actuel du site est vide et son JavaScript ne charge pas automatiquement ces archives : un rendu et des fiches accessibles doivent d'abord être développés puis testés.
- Prérequis avant mise en ligne : revue visuelle des photos, disponibilité et prix confirmés, pages véhicules, URL historiques/redirections 301, canonical, sitemap, sécurité, recette mobile.
- Aucun changement DNS ou messagerie Hostinger, aucune fusion de `main`, aucun paiement, aucun déploiement de production dans cette tâche.

## Plan de transfert contrôlé

1. Récupérer le ZIP de préparation dans ChatGPT Work ou Codex et vérifier les empreintes SHA256.
2. Exécuter le script de contrôle local du lot `preparer_import_ecm.py` avant import.
3. Verser uniquement le lot approuvé dans un dossier de **migration hors site** sur une branche dédiée ; ne pas toucher au catalogue public.
4. Comparer les quatre galeries avec les annonces et l'identité de chaque véhicule ; valider manuellement les 19 fiches.
5. Construire l'affichage des fiches sur une branche distincte puis tester Cloudflare preview en `noindex`.
6. Obtenir l'approbation requise sur la PR et valider rollback / DNS avant toute mise en production.

*ECM seulement. EBP / Best Price Car strictement exclu.*