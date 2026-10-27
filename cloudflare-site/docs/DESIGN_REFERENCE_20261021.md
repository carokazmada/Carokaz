# ECM — Référence visuelle VERROUILLÉE (21 octobre 2026)

Périmètre exclusif : **Carokaz Mada**. Ne jamais intégrer des identifiants, comptes, catalogues ou contenus d'autres entités.

## Image canonique / continuité Work

Dossier Drive ECM : https://drive.google.com/drive/folders/1VPs8PaVssGqdCL3s3wbESnZHDH5Hgsse

1. **SOURCE ORIGINALE** (prioritaire et non modifiable) : `ECM_THEME_REFERENCE_ORIGINALE_2026-10-21.jpg` — https://drive.google.com/file/d/13TnFSq4hCiZXxrHk9fRQs6yTdAr83vP1/view
2. Aperçu secondaire : `ECM_APERCU_REGENERE_2026-10-21.png` — https://drive.google.com/file/d/1pUt0XPObB_gBj_FxBSxo6jg2RrKXkxso/view
3. Instructions Work : `ECM_CONSIGNES_CHATGPT_WORK_THEME_2026-10-21.md` — https://drive.google.com/file/d/1ON8IY2CZ5DVbylMdJ9bfT9tBKVIx0ow6/view

**Contrat visuel :** le design de la source originale doit être reproduit à l'identique : logo, en-tête, navigation, couleurs blanc/noir/jaune, disposition des filtres, catégories, image de couverture, cadres de véhicules et typographie. N'apporter aucune modification volontaire au fichier image d'origine. Les fonctionnalités réelles doivent être accessibles et responsive sans altérer la composition de référence sur desktop.

**Important :** les quatre annonces, prix, kilométrages et l'affirmation « N°1 » visibles **dans l'image** sont des éléments graphiques de référence, non des informations commerciales certifiées. La conformité visuelle n'autorise pas la publication de ces données. Tant que le stock / les affirmations ne sont pas vérifiés, ne publier aucune fiche ni promesse fictive; réserver la référence à la maquette de travail et aux prévisualisations non indexables.

## État technique constaté via API Cloudflare (21/10/2026)

- Projet Pages `carokazmada` associé à `carokazmada/Carokaz`.
- Production depuis `main` ; déploiements automatiques production **OFF**. Prévisualisations réservées à la branche `fix/ecm-audit-20261021`.
- Build configuré : `python3 cloudflare-site/scripts/verify.py` ; sortie `cloudflare-output`.
- Prévisualisation réussie (21/10) : https://74ed70b9.carokazmada.pages.dev (une réussite de déploiement ne suffit pas à certifier le visuel).
- Dernière production réussie : 12/10 ; aucune modification de production autorisée dans ce document.
- Zone Cloudflare `carokazmada.com` : **pending** ; DNS racine A vers Shopify et `www` CNAME `shops.myshopify.com`, sans domaine personnalisé relié au projet Pages. MX Hostinger existants.
- **Ne pas modifier DNS, MX, DKIM, domaine, réglages production ni publier** avant inventaire des URL Shopify, plan 301, validation domaine/SSL, contenu réel, contrôles d'indexation et rollback.

## Contrôles bloquants du passage en production

- [ ] Design codé et comparé visuellement à l'original, aux largeurs 1440/390/320 px.
- [ ] Données réelles du stock (marque, modèle, prix, année, kilométrage, photos, disponibilité) vérifiées et approuvées.
- [ ] Aucune fausse publicité de classement « N°1 ».
- [ ] Source unique catalogue confirmée et restauration possible.
- [ ] Tests automatisés Python/JS réussis sur le commit exact candidat.
- [ ] Robots/headers noindex sur preview, indexation correct en production, canonical, sitemap.
- [ ] Domaine/délégation DNS/SSL, Shopify historique et redirections 301 documentés, sans perdre le courrier Hostinger.
- [ ] Approbation de publication informée après contrôle des risques.

N'utiliser que les offres gratuites : **0 Ar**, pas d'API payante ni de dépassement de quota. Mettre à jour les tâches vérifiées dans `carokazmada/carokaz-ecosystem-os` issue #14. Ce fichier n'effectue aucun déploiement.
