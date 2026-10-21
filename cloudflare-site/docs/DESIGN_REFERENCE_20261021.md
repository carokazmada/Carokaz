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

## Aperçu visuel inchangé (21 octobre 2026)

- **Source propriétaire ECM** : `ECM_THEME_REFERENCE_ORIGINALE_2026-10-21.jpg` enregistrée dans le Google Drive Carokaz Mada. Une copie binaire inchangée se trouve dans `cloudflare-site/assets/`.
- **Page visuelle** : `cloudflare-site/theme-exact.html`, avec `theme-exact.css`. L'image originale n'est ni redessinée, ni recadrée, ni recolorisée ; affichage à largeur proportionnelle.
- **Prévisualisation** : branche `design/ecm-theme-exact-20261021`, page servie comme racine uniquement sur cette branche. Environnement prévisualisation **noindex,nofollow** ; aucun changement en production.
- **Important** : capture graphique, non une page marchande opérationnelle. Les quatre cartes et tarifs montrés font partie de l'image de référence, ne sont pas des annonces vérifiées. Ne pas reprendre les prix en base de données, ne pas rétablir le slogan de positionnement n°1 comme affirmation factuelle sans justificatif.
- **À produire avant le site commercial final** : reproduction HTML/CSS accessible et fonctionnelle visuellement fidèle, catalogue et images authentifiés, approbation GitHub indépendante, validation SEO et plan de bascule.
- **Sécurité** : comptes, médias, données et budget strictement ECM, zéro mélange EBP.


## Variante de qualité visuelle publiée en aperçu (21/10/2026)

- Image améliorée fournie par l'utilisateur : `assets/ECM_THEME_VISUEL_AMELIORE_2026-10-21.png` (format 1448 × 1086), conservée telle quelle dans GitHub et le Google Drive ECM ; la référence originale JPG reste accessible et inchangée.
- La branche `design/ecm-theme-quality-20261021` remplace exclusivement la **présentation de prévisualisation** par ce PNG ; aucune modification du site marchand Shopify ni du domaine.
- Prévisualisation `noindex,nofollow`, filtres simulés non interactifs ; prix et promesse de classement intégrés à l'image non vérifiés. Le texte de bas de page avertit le visiteur.
- Branche `main` et déploiements de production Cloudflare **non modifiés**. Séparation complète avec EBP.
