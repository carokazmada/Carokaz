# Carokaz Mada — Préparation Cloudflare Pages

Site statique de **préparation** : les annonces ne sont pas encore importées.

## Garanties

- Aucun changement du DNS `carokazmada.com` ou `www.carokazmada.com`.
- Aucun remplacement de Shopify ou de Hostinger.
- Pas d'envoi de message, aucune publicité payante, aucune commande.
- Catalogue vide : ne pas inventer de prix ni de véhicules.
- Indexation bloquée jusqu'à la validation d'un catalogue réel (`robots.txt`, métadonnée `noindex`, en-tête `X-Robots-Tag`).
- Numéro validé : **038 84 241 38**, lien d'appel `tel:+261388424138`.
- Page Facebook validée : `https://www.facebook.com/carokazmada/`.
- Numéro secondaire, adresse e-mail et adresse du showroom non affichés car non revalidés.

## Intégration automatique recommandée

### Nouveau projet avec intégration Git (préféré)

1. Dans Cloudflare, **Workers & Pages > Create > Pages > Connect to Git**.
2. Choisir **GitHub** puis le dépôt `carokazmada/Carokaz`.
3. Branche de production : **ne pas associer un domaine en production avant vérification**.
4. Build command : **laisser vide** (site statique, sans build).
5. Build output directory : `cloudflare-site` ; repository root `/`.
6. Prévisualiser, vérifier visuellement et contrôler les liens.
7. Après validation seulement, planifier la bascule DNS / domaine / SEO.

Attention : un projet **Direct Upload** existant ne peut pas être converti en projet Git. Le conserver intact et créer, si nécessaire, **un autre projet** Git-integrated, ou utiliser `wrangler pages deploy` avec des secrets Cloudflare (solution CI séparée).

### Vérification locale

```bash
python3 cloudflare-site/scripts/verify.py
python3 -m http.server 8000 --directory cloudflare-site
```

Ouvrir `http://localhost:8000` pour examiner la maquette. Lancer les tests avant toute proposition de déploiement.

## Future mise en ligne

- Importer uniquement les fiches produit validées (source catalogue autorisée, prix et disponibilité confirmés).
- Corriger les contacts obsolètes ; ne pas ajouter de téléphone incertain.
- Ajouter alors le canonical, sitemap, données structurées réelles et éventuelle indexation.
- Préserver les URL Shopify importantes par des redirections 301 **uniquement lors d'une migration approuvée**.
