#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STORE="${1:-carokazmada-store.myshopify.com}"

if ! command -v shopify >/dev/null 2>&1; then
  cat >&2 <<'MESSAGE'
Erreur : Shopify CLI n'est pas installé.
Installez-le avec la commande officielle « npm install -g @shopify/cli@latest »,
puis relancez ce script depuis un terminal permettant l'authentification Shopify.
MESSAGE
  exit 1
fi

if [[ ! "${STORE}" =~ ^[a-zA-Z0-9][a-zA-Z0-9-]*\.myshopify\.com$ ]]; then
  printf 'Erreur : « %s » n’est pas une adresse myshopify.com valide.\n' "${STORE}" >&2
  exit 1
fi

cd "${ROOT_DIR}"

printf 'Validation du thème pour %s…\n' "${STORE}"
shopify theme check

printf 'Envoi sécurisé comme thème non publié…\n'
shopify theme push --store "${STORE}" --unpublished
