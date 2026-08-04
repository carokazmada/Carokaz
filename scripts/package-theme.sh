#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${ROOT_DIR}/dist"
OUTPUT_FILE="${OUTPUT_DIR}/carokaz-theme.zip"
THEME_DIRECTORIES=(assets config layout locales sections snippets templates)

if ! command -v zip >/dev/null 2>&1; then
  printf 'Erreur : la commande « zip » est requise.\n' >&2
  exit 1
fi

for directory in "${THEME_DIRECTORIES[@]}"; do
  if [[ ! -d "${ROOT_DIR}/${directory}" ]]; then
    printf 'Erreur : le dossier Shopify « %s » est absent.\n' "${directory}" >&2
    exit 1
  fi
done

mkdir -p "${OUTPUT_DIR}"
rm -f "${OUTPUT_FILE}"

(
  cd "${ROOT_DIR}"
  zip -qr "${OUTPUT_FILE}" "${THEME_DIRECTORIES[@]}"
)

printf 'Thème prêt à importer : %s\n' "${OUTPUT_FILE}"
