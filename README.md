# Carokaz — thème Shopify

Thème Shopify Online Store 2.0 gratuit, rapide et responsive, conçu pour la vente de pièces et accessoires automobiles.

## Solution la plus simple : installation par fichier ZIP

1. Créez automatiquement le fichier installable :

   ```bash
   ./scripts/package-theme.sh
   ```

2. Le fichier à importer sera disponible dans `dist/carokaz-theme.zip`.
3. Dans l'administration Shopify, ouvrez **Boutique en ligne → Thèmes**.
4. Cliquez sur **Ajouter un thème → Importer un fichier ZIP** et choisissez `dist/carokaz-theme.zip`.
5. Une fois le traitement terminé, cliquez sur **Personnaliser** pour associer les collections et ajouter le logo.
6. Utilisez **Publier** uniquement après avoir vérifié l'aperçu sur ordinateur et mobile.

> L'adresse publique ou le mot de passe de la boutique ne permettent pas d'installer un thème. Il faut être connecté à un compte ayant l'autorisation **Thèmes** dans l'administration Shopify.

## Développement local

```bash
shopify theme dev --store carokazmada-store.myshopify.com
```

Pour envoyer le thème comme thème non publié depuis Shopify CLI :

```bash
./scripts/deploy-theme.sh
```

Le script cible `carokazmada-store.myshopify.com`, contrôle Shopify CLI, valide les fichiers puis envoie le thème en mode **non publié**. Il ne remplace donc jamais automatiquement le thème actuellement visible. Lors de la première exécution, Shopify demande au propriétaire de se connecter et d'autoriser l'accès.

Pour cibler une autre boutique :

```bash
./scripts/deploy-theme.sh autre-boutique.myshopify.com
```

Ne partagez jamais de mot de passe ou de jeton d'administration dans ce dépôt. Une installation distante ne peut pas être forcée sans autorisation Shopify : cette protection empêche un tiers de modifier une boutique.

Le thème ne contient aucune dépendance payante, police distante ou bibliothèque JavaScript tierce.
