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

`CF_PAGES_BRANCH=main` construit le candidat de production. Les autres noms de branche construisent une prévisualisation avec directives de non-indexation. Les paramètres du service d’hébergement doivent correspondre à cette convention avant déploiement.

Le thème et les photos sont conservés. Les règles CSS pour tablette et petits écrans empêchent les boutons de dépasser la largeur disponible.

Le site peut servir de vitrine institutionnelle avec une notice de disponibilité et des liens de contact. Les annonces automobiles doivent provenir de données validées avant leur ajout.
