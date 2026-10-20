# ECM — site Carokaz Mada

Source reprise du commit `c98177646f7cdaeef1b6088ea198c25bac61005e`.
Thème, photos et CSS préservés. Domaine canonique retenu d'après le registre ECM : `https://carokazmada.com/`.
Ce choix dans le code ne prouve pas que le domaine serve ce site.

## Build

Racine du dépôt. Commande unique :

```sh
python3 cloudflare-site/scripts/verify.py
```

Sortie : `cloudflare-output/`. Ne pas ajouter de copie de fichiers après cette commande : elle peut écraser les protections preview.
`CF_PAGES_BRANCH=main` produit le candidat de production ; toute autre branche produit noindex/nofollow + X-Robots-Tag + Disallow: /.
Cette convention attend main comme future branche stable ; vérifier et aligner les paramètres réels Cloudflare avant bascule.
Sans variable Cloudflare, le build local valide un candidat de production, sans le publier.

## Tests

```sh
python3 -m unittest discover -s cloudflare-site/tests -p 'test_*.py'
node --check cloudflare-site/app.js
```

Les tests créent des fichiers temporaires et vérifient les modes production et prévisualisation, les ressources manquantes, le canonical et le hash CSP du JSON-LD.

## État de publication

Le catalogue est vide car le stock actuel n'est pas certifié. Ce n'est pas une preuve de zéro véhicule en stock.
Ne pas republier les anciennes disponibilités à partir des seules dates de modification Drive.
Le Tiguan de référence garde le prix validé de 60 000 000 Ar ; aucune disponibilité nouvelle n'est déduite.
JSON-LD Organization et WebSite uniquement, sans prix, note, avis, adresse précise ni offre inventés.
GA4 : propriété 529721310 identifiée, identifiant de flux G- et réception des contacts non vérifiés ; aucun faux suivi installé.
WordPress de préparation conserve sa protection d'indexation et ses brouillons.

## Avant mise en production

1. Rétablir la lecture Cloudflare et sauvegarder projet, branche, commande, domaines et déploiement courant.
2. Certifier stock/prix/photos du catalogue, puis intégrer et tester les fiches et anciennes URL.
3. Récupérer le flux Web GA4 exact, valider la confidentialité, intégrer et tester les clics contact sans les compter comme ventes.
4. Faire passer les tests sur le SHA final. Examiner puis fusionner la PR uniquement lorsque les conditions de publication sont remplies.
5. Configurer la commande ci-dessus ; confirmer main comme branche stable ; contrôler la preview exacte avant toute bascule du domaine.
6. Vérifier HTTPS, redirections, robots, sitemap, 404, contacts et réponse réelle sur le domaine officiel.

Rollback : ne pas réécrire l'historique. Revenir au déploiement Cloudflare sauvegardé ; ne pas choisir le service actuel en erreur 402 comme repli sans vérifier sa santé. Annuler le commit de correction si nécessaire via revert revu.
