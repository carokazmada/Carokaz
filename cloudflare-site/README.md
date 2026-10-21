# Carokaz Mada — site statique

## Construire

Depuis la racine du dépôt :

```sh
python3 cloudflare-site/scripts/verify.py
```

Les fichiers générés se trouvent dans `cloudflare-output/`. Le script copie toutes les ressources nécessaires ; ne pas ajouter de copie manuelle après son exécution.

## Vérifier

```sh
python3 -m unittest discover -s cloudflare-site/tests -p 'test_*.py'
node --check cloudflare-site/app.js
```

`CF_PAGES_BRANCH=main` construit explicitement le candidat de production. Toute autre branche **ainsi qu'une exécution locale sans `CF_PAGES_BRANCH`** construisent une prévisualisation non indexable (`noindex,nofollow`, `X-Robots-Tag` et `robots.txt`). Sur Cloudflare, une identité de branche absente provoque un échec volontaire pour éviter toute ambiguïté. Les paramètres de l'hébergement doivent correspondre à cette convention.

Le thème et les photos sont conservés. Les règles CSS pour tablette et petits écrans empêchent les boutons de dépasser la largeur disponible.

Le site peut servir de vitrine institutionnelle avec une notice de disponibilité et des liens de contact. Les annonces automobiles doivent provenir de données validées avant leur ajout.

## Contrôle avant publication

- La branche `main` ne doit pas être modifiée ou déployée sans validation de la PR et des tests.
- Vérifier que le projet Pages est relié à la branche attendue, que la compilation réussit et que les prévisualisations restent `noindex`.
- Vérifier le stock réel, les photos, les droits de diffusion et les redirections des anciennes URLs. Le catalogue vide ne représente pas une migration achevée.
- Vérifier séparément les domaines Cloudflare Pages, les DNS Shopify/Hostinger, la réception des e-mails et le certificat TLS.
- Prévoir une sauvegarde et un chemin de retour arrière avant d'activer la publication de production.
- Conserver l'écosystème ECM indépendant de tout autre projet.
