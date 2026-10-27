# Cloudflare Pages — réglages exacts à appliquer (Carokaz Mada)

Ce document décrit la configuration **attendue** du projet Pages. L'agent n'a
aucun accès Cloudflare dans cette session : ces réglages doivent être appliqués
par un humain dans le tableau de bord Cloudflare.

## Projet

- Projet : `carokazmada`
- Source : Git — dépôt `carokazmada/Carokaz`
- Branche de production : `main`
- Prévisualisations Git : **activées** pour les autres branches (elles restent
  `noindex,nofollow` grâce à `verify.py`).

## Compilation et déploiement

- Framework preset : **None**
- Commande de build : `python3 cloudflare-site/scripts/verify.py`
- Répertoire de sortie : `cloudflare-output`
- Version Python : 3.12 (`PYTHON_VERSION=3.12` si nécessaire)
- Node : non requis (site statique).

`verify.py` copie uniquement les fichiers attendus dans `cloudflare-output`. Il
refuse toute compilation ambiguë : si `CF_PAGES` est défini sans
`CF_PAGES_BRANCH`, la build échoue volontairement.

## Mode production vs prévisualisation

- `CF_PAGES_BRANCH=main` → sortie indexable (production).
- Toute autre branche, ou une exécution locale sans `CF_PAGES_BRANCH` → sortie
  `noindex,nofollow` + `robots.txt` en `Disallow: /`.

## Domaine personnalisé (étape sensible, validation humaine requise)

1. **Ne pas toucher au DNS avant d'avoir confirmé l'impact messagerie.**
   `carokazmada.com` porte les MX Hostinger (`mx1/mx2.hostinger.com`). Une
   bascule DNS mal préparée coupe les e-mails professionnels.
2. Ajouter le domaine dans Pages → onglet « Custom domains » → `carokazmada.com`
   et `www.carokazmada.com`.
3. Conserver les enregistrements **MX** Hostinger tels quels.
4. Faire pointer l'enregistrement **A/AAAA** (ou CNAME `www`) vers Pages
   conformément à l'assistant Cloudflare.
5. Vérifier après bascule : HTTPS, redirections `www` → apex, `robots.txt`,
   `sitemap.xml`, réception ET envoi d'e-mail.

## Vérification après publication

- `https://carokazmada.com/` → HTTP 200 (actuellement 402 Shopify).
- `https://carokazmada.com/robots.txt` → `Allow: /` + ligne `Sitemap:`.
- `https://carokazmada.com/sitemap.xml` → HTTP 200 avec `<loc>https://carokazmada.com/</loc>`.
- En-têtes présents : `Content-Security-Policy`, `Strict-Transport-Security`,
  `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`.
- Aucune balise `noindex` sur la production.

## Retour arrière

- La PR #15 est **purement additive** : `git revert` du merge restaure l'état
  précédent sans perte.
- Le DNS peut être rebasculé vers Shopify en rétablissant les enregistrements
  A/CNAME d'origine (à sauvegarder avant modification).
