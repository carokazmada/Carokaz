#!/usr/bin/env python3
"""Rapport automatique local : distingue les fichiers GitHub du site Cloudflare."""
import json
import os
from pathlib import Path

REPORT = Path("rapports-publics/cloudflare-public.json")
OUTPUT = os.environ.get("GITHUB_STEP_SUMMARY")
PRIORITY = ("contact", "facebook", "robots_txt", "404")


def main():
    lines = [
        "## Carokaz Mada — préparation vs site public",
        "",
        "**Tests GitHub réussis ne signifient pas que le site est publié.**",
        "",
        "Fichiers préparés : branche GitHub. Site public : carokazmada.pages.dev.",
        "",
    ]
    if not REPORT.is_file():
        lines.append("**Audit public non disponible.** Impossible de conclure à une panne.")
    else:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        facts = {x["id"]: x for x in report.get("facts", [])}
        labels = {
            "homepage": "Accueil",
            "contact": "Téléphone officiel",
            "facebook": "Facebook officiel",
            "noindex": "Noindex provisoire",
            "robots_txt": "robots.txt",
            "404": "Page 404",
        }
        lines += ["### Contrôles publics", "", "| Contrôle | État | Observation |", "|---|---|---|"]
        for key, label in labels.items():
            item = facts.get(key, {})
            status = str(item.get("status", "NON TESTÉ")).replace("|", "/")
            detail = str(item.get("detail", "Aucune donnée")).replace("|", "/").replace("\n", " ")
            lines.append(f"| {label} | {status} | {detail} |")
        issues = [k for k in PRIORITY if facts.get(k, {}).get("status") != "OK"]
        has_blocked = any(f.get("status") == "BLOQUÉ" for f in facts.values())
        lines += ["", "### Conclusion", ""]
        if has_blocked:
            lines.append("**Audit partiel :** vérifier l'accès avant toute conclusion.")
        elif issues:
            lines.append(
                "**Site public encore incomplet sur :** "
                + ", ".join(labels[k] for k in issues)
                + ". Les corrections GitHub ne sont pas nécessairement en ligne."
            )
        else:
            lines.append("Contrôles prioritaires conformes ; équivalence des versions non prouvée.")
    lines += ["", "Ce rapport ne déploie pas et ne modifie pas les DNS ou le site public.", ""]
    content = "\n".join(lines)
    if OUTPUT:
        with open(OUTPUT, "a", encoding="utf-8") as f:
            f.write(content + "\n")
        print("Résumé GitHub Actions généré.")
    else:
        print(content)


if __name__ == "__main__":
    main()
