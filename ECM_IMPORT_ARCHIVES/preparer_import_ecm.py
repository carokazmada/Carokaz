#!/usr/bin/env python3
"""Vérifie une archive ECM, extrait uniquement les 19 brouillons et 35 photos dans un dossier non public."""
import argparse, hashlib, json
from pathlib import Path
from zipfile import ZipFile

BASE = "ECM_IMPORT_ARCHIVES/"
def sha(b): return hashlib.sha256(b).hexdigest()

def importer(archive, dest):
    archive, dest = Path(archive), Path(dest)
    if dest.exists(): raise ValueError("Le dossier cible existe : refus d'écraser")
    if any(p in ("cloudflare-site", "cloudflare-output") for p in dest.parts):
        raise ValueError("Refus d'importer directement dans le site public")
    with ZipFile(archive) as z:
        names = set(z.namelist())
        if any(n.startswith("/") or ".." in Path(n).parts or "\\" in n for n in names):
            raise ValueError("Chemin d'archive non sûr")
        cat = json.loads(z.read(BASE + "ECM_catalogue_archives.json"))
        media = json.loads(z.read(BASE + "ECM_medias_controles.json"))
        fiches = cat.get("vehicules", [])
        if cat.get("ecosysteme") != "ECM / Carokaz Mada" or len(fiches) != 19 or len(media) != 35:
            raise ValueError("Périmètre non conforme : 19 brouillons, 35 photos")
        skus = [v.get("sku") for v in fiches]
        if len(set(skus)) != 19: raise ValueError("SKU en double")
        for v in fiches:
            if not (v.get("statut") == "brouillon" and v.get("publie") is False
                    and v.get("prix_public_mga") is None
                    and v.get("stock_actuel_verifie") is False
                    and v.get("photos_identite_verifiee") is False):
                raise ValueError("Une fiche porte un statut incompatible")
        photos = [BASE + str(m["fichier"]) for m in media]
        if len(set(photos)) != 35 or not all(p in names for p in photos):
            raise ValueError("Photos manquantes ou dupliquées")
        if any(m.get("SKU") not in skus for m in media):
            raise ValueError("Photo attribuée à un SKU absent")
        for path,m in zip(photos,media):
            if m.get("sha256") and sha(z.read(path)) != m["sha256"]:
                raise ValueError("SHA256 photo incorrect : " + path)
        dest.mkdir(parents=True, exist_ok=False)
        kept = [BASE + "ECM_catalogue_archives.json", BASE + "ECM_medias_controles.json"] + photos
        manifest = {}
        for name in kept:
            data = z.read(name)
            rel = name.removeprefix(BASE)
            target = dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            manifest[rel] = sha(data)
        (dest/"SHA256.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print("Préparation vérifiée : 19 fiches, 35 photos, 4 galeries. Aucun déploiement.")

if __name__ == "__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("archive")
    ap.add_argument("destination")
    a=ap.parse_args()
    importer(a.archive,a.destination)
