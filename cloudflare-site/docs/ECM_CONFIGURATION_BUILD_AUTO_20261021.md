# ECM — Paramètres et builds automatiques
Contrôles du 21 octobre 2026. Périmètre strict : Carokaz Mada uniquement. Objectif : budget zéro Ariary.

## Architecture effective

- Compte Cloudflare Pages : carokazmada
- Dépôt GitHub : carokazmada/Carokaz
- Branche de production : main
- Branche de corrections : fix/ecm-audit-20261021
- Branche d'automatisation : automation/ecm-build-gates-20261021
- Commande Pages : python3 cloudflare-site/scripts/verify.py
- Dossier de sortie : cloudflare-output
- Production : désactivée pour préserver l'ancien site
- Domaine personnalisé Pages : aucun
- DNS : zone carokazmada.com active, mais A/www pointent encore vers Shopify
- Mail : MX/SPF/DKIM/DMARC Hostinger présents, envoi et réception non testés

## Contrôles automatisés

| Contrôle | Exécution GitHub CI | Autorise la publication ? |
|---|---|---|
| Tests Python et sécurité | Chaque push/PR éligible | Non |
| Syntaxe Python et JavaScript | Chaque push/PR éligible | Non |
| Build candidat production | CF_PAGES_BRANCH=main | Non |
| Audit HTML canonical, robots, sitemap | Candidat produit localement | Non |
| Audit des headers CSP, nosniff | Candidat produit localement | Non |
| Contrôle catalogue en MGA | Candidat produit localement | Non |
| Build prévisualisation | CF_PAGES_BRANCH=ecm-ci-preview | Non |
| Test noindex HTML + HTTP + robots.txt | Prévisualisation produite localement | Non |
| Rapport automatique | Fichiers JSON locaux et résumé GitHub | Non |
| Planification quotidienne | Cron UTC 03:00, équivalent 06:00 Madagascar | Uniquement quand le workflow existe sur main ; jamais un déploiement |

Les audits de build ne lisent pas les comptes Cloudflare ou Shopify. Ils ne valident que les fichiers générés. Les paramètres distants doivent être contrôlés séparément.

## État réel des paramètres externes

| Domaine | État | Prochain critère |
|---|---|---|
| Cloudflare zone DNS | Active selon API | Vérification de résolution externe |
| Cloudflare Pages | Projet et build configurés | Réussite réelle après merge validé |
| Domaine dans Pages | Absent | Rattachement contrôlé après recette |
| Publication prod | Désactivée | Go/No-Go humain et sauvegardes |
| DNS A et CNAME web | Encore Shopify | Migration avec rollback, pas maintenant |
| E-mail MX Hostinger | Présent | Test de réception et émission |
| SPF/DKIM/DMARC | Présents | Vérification de délivrabilité ; p=none |
| TLS | Full / min 1.2 / TLS1.3 actif | Contrôler certificat origine avant Full strict |
| DNSSEC | Désactivé | Préparer DS côté registraire |
| Catalogue | Vide en production candidate | Stock et fiches validés |
| Inventaire historique | 19 fiches, 35 photos, 4 galeries | Trier, associer, autoriser les images |
| SEO statique | Canonical/sitemap/JSON-LD définis | Contrôler HTTP et indexation réelle |
| SEO historique | Redirections à préparer | Inventaire URLs puis 301 |
| Search Console / GA4 / GTM | Non certifiés en direct | Vérifier collecte et indexation |
| Formulaires et conversion | Non testés de bout en bout | Tester sur vrai hébergement |
| Google Business Profile | Compte identifié | Vérifier contenu, accès et métriques |
| Social / Metricool | Partiellement connecté | Contrôle droits et flux |
| Sécurité MFA / permissions | Non certifiée | Vérification humaine des comptes |
| Sauvegarde et restauration | Non testées | Snapshot avant migration |
| Performance mobile | Non certifiée | Mesures sur domaine public |
| Consentement et données clients | Non certifiés | Vérifier la conformité |

## Ordre d'achèvement sans risque

1. Maintenir les règles GitHub, le verrou production et les prévisualisations non indexées.
2. Terminer le catalogue sans publier de stock ou d'images non confirmés.
3. Vérifier les anciens URL, les redirections 301 et la sauvegarde Shopify.
4. Tester réception mail, HTTPS, DNS, formulaires et parcours clients.
5. Examiner et approuver la branche corrective avant toute intégration dans main.
6. Relancer les tests complets, vérifier preview, sécurité, design et SEO.
7. Appliquer le changement de domaine uniquement après Go/No-Go et chemin de retour arrière.
8. Contrôler après publication l'indexation, la vitesse, les conversions et le référencement local.

## Exécution locale

    python3 -m unittest discover -s cloudflare-site/tests -p 'test_*.py'
    node --check cloudflare-site/app.js
    CF_PAGES_BRANCH=main python3 cloudflare-site/scripts/verify.py
    python3 cloudflare-site/scripts/check_build.py --mode production
    CF_PAGES_BRANCH=ecm-ci-preview python3 cloudflare-site/scripts/verify.py
    python3 cloudflare-site/scripts/check_build.py --mode preview

Les rapports générés dans rapports-build/ sont locaux ; ils ne publient aucune donnée sur le domaine officiel.

## Barrières permanentes

Aucune fusion automatique, aucun déploiement production, aucun changement DNS, aucune dépense, aucun transfert de secret, aucune copie d'autres écosystèmes. Le design et les photos approuvés restent intacts dans cette PR. Le statut publication_autorisee reste false jusqu'à validation indépendante de la disponibilité commerciale.
