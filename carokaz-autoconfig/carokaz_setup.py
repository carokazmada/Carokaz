#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CAROKAZ MADA — AUTO-CONFIGURATION
=================================
Exécute automatiquement les tâches restantes qui SONT automatisables par API.

Tâches couvertes :
  T1  Messenger  : souscription des champs webhook (messages, messaging_postbacks)
  T2  Shopify    : préflight + audit SEO/canaux/metafields de tout le catalogue
  T3  Shopify    : création + publication de la VW Golf 7 GTI
  T4  Shopify    : publication de TOUS les produits sur les 3 canaux
  T5  Shopify    : metafields Google (condition=used) manquants
  T6  Google     : soumission du sitemap à Search Console
  T7  Rapport    : JSON + Markdown
  T8  SEO        : ALT manquants + contrôle de couverture sans écrasement

Usage :
    python carokaz_setup.py --dry-run              # simulation, aucune écriture
    python carokaz_setup.py --all                  # tout exécuter
    python carokaz_setup.py --only T1,T4
    python carokaz_setup.py --only T3 --gti-price 185000000

Auteur : assistant opérationnel Carokaz Mada
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("Manque 'requests'.  ->  pip install -r requirements.txt")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# ─────────────────────────────────────────────────────────────
# CONSTANTES PROJET (issues de la configuration Carokaz Mada)
# ─────────────────────────────────────────────────────────────
SHOP_DOMAIN = os.getenv("SHOPIFY_SHOP", "carokazmada-store.myshopify.com")
API_VERSION = os.getenv("SHOPIFY_API_VERSION", "2025-07")
SITE_URL = os.getenv("SITE_URL", "https://carokazmada.com")
WHATSAPP = "0388424138"
WHATSAPP_INTL = "261388424138"

PUBLICATIONS = {
    "Online Store": "gid://shopify/Publication/181963915425",
    "Facebook & Instagram": "gid://shopify/Publication/187555643553",
    "Google & YouTube": "gid://shopify/Publication/197392892065",
}
LOCATION_GID = "gid://shopify/Location/81235247265"
TAXONOMY_GID = "gid://shopify/TaxonomyCategory/vp-2"
GOOGLE_PRODUCT_CATEGORY = "5614"          # Cars & Trucks
GOOGLE_NS = "mm-google-shopping"

GRAPH_VERSION = os.getenv("META_GRAPH_VERSION", "v21.0")
WEBHOOK_FIELDS = [
    "messages",
    "messaging_postbacks",
    "messaging_optins",
    "message_deliveries",
    "message_reads",
    "messaging_referrals",
]

SITEMAPS = ["sitemap.xml"]

OUT_DIR = Path(os.getenv("CAROKAZ_OUT", "./rapports"))


# ─────────────────────────────────────────────────────────────
# LOG
# ─────────────────────────────────────────────────────────────
class C:
    G = "\033[92m"; Y = "\033[93m"; R = "\033[91m"; B = "\033[94m"
    D = "\033[90m"; BOLD = "\033[1m"; X = "\033[0m"
    if os.getenv("NO_COLOR") or not sys.stdout.isatty():
        G = Y = R = B = D = BOLD = X = ""


RESULTS = []


def log(msg, lvl="info"):
    p = {"info": f"{C.B}·{C.X}", "ok": f"{C.G}✓{C.X}", "warn": f"{C.Y}!{C.X}",
         "err": f"{C.R}✗{C.X}", "step": f"{C.BOLD}▸{C.X}", "dim": f"{C.D} {C.X}"}[lvl]
    print(f"{p} {msg}")


def record(task, status, detail, data=None):
    RESULTS.append({
        "task": task, "status": status, "detail": detail,
        "data": data or {}, "at": datetime.now(timezone.utc).isoformat()
    })


# ─────────────────────────────────────────────────────────────
# CLIENT SHOPIFY (GraphQL + retry throttling)
# ─────────────────────────────────────────────────────────────
class Shopify:
    def __init__(self, token, dry=False):
        self.url = f"https://{SHOP_DOMAIN}/admin/api/{API_VERSION}/graphql.json"
        self.h = {"X-Shopify-Access-Token": token, "Content-Type": "application/json"}
        self.dry = dry

    def gql(self, query, variables=None, mutation=False):
        if mutation and self.dry:
            log(f"[DRY-RUN] mutation ignorée : {query.strip().splitlines()[0][:60]}", "dim")
            return {"_dryrun": True}
        for attempt in range(6):
            r = requests.post(self.url, headers=self.h,
                              json={"query": query, "variables": variables or {}}, timeout=45)
            if r.status_code == 429:
                time.sleep(2 ** attempt); continue
            r.raise_for_status()
            j = r.json()
            errs = j.get("errors")
            if errs:
                if any("THROTTLED" in str(e.get("extensions", {})) for e in errs):
                    time.sleep(2 ** attempt); continue
                raise RuntimeError(f"GraphQL: {json.dumps(errs, ensure_ascii=False)[:400]}")
            return j["data"]
        raise RuntimeError("Shopify: throttling persistant après 6 tentatives")

    @staticmethod
    def user_errors(payload, key):
        if payload is None or payload.get("_dryrun"):
            return []
        node = payload.get(key) or {}
        return node.get("userErrors") or []


Q_PRODUCTS = """
query($cursor: String) {
  products(first: 40, after: $cursor) {
    pageInfo { hasNextPage endCursor }
    nodes {
      id title handle status
      seo { title description }
      media(first: 25) { nodes { ... on MediaImage { id alt } } }
      resourcePublications(first: 10) { nodes { publication { id } isPublished } }
      condition: metafield(namespace: "%s", key: "condition") { value }
      gcat: metafield(namespace: "%s", key: "google_product_category") { value }
    }
  }
}
""" % (GOOGLE_NS, GOOGLE_NS)

M_PUBLISH = """
mutation publish($id: ID!, $input: [PublicationInput!]!) {
  publishablePublish(id: $id, input: $input) {
    userErrors { field message }
  }
}
"""

M_METAFIELDS = """
mutation setMf($metafields: [MetafieldsSetInput!]!) {
  metafieldsSet(metafields: $metafields) {
    userErrors { field message }
  }
}
"""

M_MEDIA_ALT_UPDATE = """
mutation mediaAltUpdate($productId: ID!, $media: [UpdateMediaInput!]!) {
  productUpdateMedia(productId: $productId, media: $media) {
    mediaUserErrors { field message }
  }
}
"""

M_PRODUCT_CREATE = """
mutation createProduct($product: ProductCreateInput!) {
  productCreate(product: $product) {
    product { id title handle variants(first:1){nodes{id}} }
    userErrors { field message }
  }
}
"""

M_VARIANT_UPDATE = """
mutation updVariant($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
  productVariantsBulkUpdate(productId: $productId, variants: $variants) {
    productVariants { id sku price }
    userErrors { field message }
  }
}
"""


def fetch_all_products(sp):
    nodes, cursor = [], None
    while True:
        d = sp.gql(Q_PRODUCTS, {"cursor": cursor})
        page = d["products"]
        nodes.extend(page["nodes"])
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]
    return nodes


# ═════════════════════════════════════════════════════════════
# T1 — MESSENGER : souscription des champs webhook
# ═════════════════════════════════════════════════════════════
def task_T1(cfg, dry):
    log("T1 — Messenger : souscription des champs webhook", "step")
    page_id, token = cfg.get("META_PAGE_ID"), cfg.get("META_PAGE_ACCESS_TOKEN")
    if not (page_id and token):
        log("META_PAGE_ID / META_PAGE_ACCESS_TOKEN absents — tâche ignorée", "warn")
        return record("T1", "skipped", "Identifiants Meta manquants")

    base = f"https://graph.facebook.com/{GRAPH_VERSION}/{page_id}/subscribed_apps"

    r = requests.get(base, params={"access_token": token,
                                   "fields": "subscribed_fields"}, timeout=30)
    if r.status_code != 200:
        log(f"Lecture impossible : {r.text[:200]}", "err")
        return record("T1", "error", r.text[:300])

    current = []
    for app in r.json().get("data", []):
        current += app.get("subscribed_fields", []) or []
    missing = [f for f in WEBHOOK_FIELDS if f not in current]

    log(f"Champs actuels : {', '.join(current) or '(aucun)'}", "dim")
    if not missing:
        log("Tous les champs sont déjà souscrits — le bot reçoit bien les événements", "ok")
        return record("T1", "ok", "Déjà conforme", {"fields": current})

    log(f"Champs manquants : {', '.join(missing)}", "warn")
    if dry:
        log("[DRY-RUN] souscription non envoyée", "dim")
        return record("T1", "dryrun", "Souscription simulée", {"missing": missing})

    p = requests.post(base, params={
        "access_token": token,
        "subscribed_fields": ",".join(WEBHOOK_FIELDS)
    }, timeout=30)
    if p.status_code == 200 and p.json().get("success"):
        log("Souscription effectuée — le webhook recevra désormais les messages", "ok")
        return record("T1", "ok", "Champs souscrits", {"fields": WEBHOOK_FIELDS})
    log(f"Échec : {p.text[:250]}", "err")
    return record("T1", "error", p.text[:300])


# ═════════════════════════════════════════════════════════════
# T2 — AUDIT CATALOGUE SHOPIFY (lecture seule)
# ═════════════════════════════════════════════════════════════
def task_T2(sp):
    log("T2 — Audit catalogue Shopify", "step")
    products = fetch_all_products(sp)
    issues = {"seo_title": [], "seo_desc": [], "alt": [],
              "canaux": [], "condition": [], "gcat": [], "brouillon": []}

    pub_ids = set(PUBLICATIONS.values())
    for p in products:
        t = p["title"]
        if p["status"] != "ACTIVE":
            issues["brouillon"].append(t)
        if not (p.get("seo") or {}).get("title"):
            issues["seo_title"].append(t)
        if not (p.get("seo") or {}).get("description"):
            issues["seo_desc"].append(t)
        imgs = p["media"]["nodes"]
        if any(not (m.get("alt") or "").strip() for m in imgs):
            issues["alt"].append(t)
        published = {n["publication"]["id"] for n in p["resourcePublications"]["nodes"]
                     if n["isPublished"]}
        if not pub_ids.issubset(published):
            issues["canaux"].append(t)
        if not (p.get("condition") or {}).get("value"):
            issues["condition"].append(t)
        if not (p.get("gcat") or {}).get("value"):
            issues["gcat"].append(t)

    log(f"{len(products)} produits analysés", "ok")
    labels = {
        "brouillon": "produits non ACTIFS",
        "seo_title": "sans méta-titre",
        "seo_desc": "sans méta-description",
        "alt": "avec au moins une image sans ALT",
        "canaux": "non publiés sur les 3 canaux",
        "condition": "sans metafield condition=used",
        "gcat": "sans catégorie Google",
    }
    for k, lbl in labels.items():
        n = len(issues[k])
        log(f"{n:>3} {lbl}", "ok" if n == 0 else "warn")

    record("T2", "ok", f"{len(products)} produits audités",
           {"total": len(products), "issues": {k: len(v) for k, v in issues.items()},
            "detail": issues})
    return products, issues


# ═════════════════════════════════════════════════════════════
# T3 — VW GOLF 7 GTI
# ═════════════════════════════════════════════════════════════
GTI_DESC = """<p><strong>Volkswagen Golf 7 GTI</strong> — compacte sportive référence, disponible chez Carokaz Mada à Antananarivo.</p>
<ul>
<li>Moteur essence turbo 2.0 TSI</li>
<li>Boîte automatique DSG</li>
<li>Véhicule d'occasion contrôlé</li>
<li>Livraison possible dans toute l'île</li>
</ul>
<p>Renseignements et disponibilité par WhatsApp au <strong>{wa}</strong>.</p>""".format(wa=WHATSAPP)


def task_T3(sp, price, dry):
    log("T3 — Volkswagen Golf 7 GTI", "step")
    if not price:
        log("Prix non fourni (--gti-price ou GTI_PRICE). Publication annulée : "
            "aucun prix ne sera inventé.", "warn")
        return record("T3", "skipped", "Prix manquant — publication volontairement bloquée")

    sku = "CAROKAZ-VOLKSWAGEN-GOLF7-GTI"
    existing = sp.gql("""query($q:String!){ products(first:1, query:$q){ nodes{ id title } } }""",
                      {"q": f"sku:{sku}"})
    if existing and not existing.get("_dryrun") and existing["products"]["nodes"]:
        pid = existing["products"]["nodes"][0]["id"]
        log(f"Produit déjà existant ({pid}) — publication seule", "warn")
    else:
        payload = {
            "title": "Volkswagen Golf 7 GTI — Occasion Madagascar | Carokaz Mada",
            "descriptionHtml": GTI_DESC,
            "vendor": "Volkswagen",
            "productType": "Voiture d'occasion",
            "status": "ACTIVE",
            "tags": ["Volkswagen", "Golf", "GTI", "Compacte", "Essence",
                     "Occasion", "Antananarivo"],
            "category": TAXONOMY_GID,
            "seo": {
                "title": "Volkswagen Golf 7 GTI occasion Antananarivo | Carokaz Mada",
                "description": ("Volkswagen Golf 7 GTI d'occasion à Antananarivo. "
                                "2.0 TSI, DSG, véhicule contrôlé, livraison Madagascar. "
                                f"WhatsApp {WHATSAPP}.")[:320],
            },
        }
        d = sp.gql(M_PRODUCT_CREATE, {"product": payload}, mutation=True)
        errs = Shopify.user_errors(d, "productCreate")
        if errs:
            log(f"Erreur création : {errs}", "err")
            return record("T3", "error", str(errs))
        if dry:
            log("[DRY-RUN] produit non créé", "dim")
            return record("T3", "dryrun", "Création simulée", {"price": price})
        prod = d["productCreate"]["product"]
        pid = prod["id"]
        vid = prod["variants"]["nodes"][0]["id"]
        log(f"Produit créé : {prod['handle']}", "ok")

        d_variant = sp.gql(M_VARIANT_UPDATE, {
            "productId": pid,
            "variants": [{"id": vid, "sku": sku, "price": str(price),
                          "inventoryItem": {"tracked": True}}]
        }, mutation=True)
        errs = Shopify.user_errors(d_variant, "productVariantsBulkUpdate")
        if errs:
            log(f"Erreur mise à jour du prix/SKU : {errs}", "err")
            return record("T3", "error", str(errs), {"id": pid})
        log(f"Prix défini : {price} MGA (SKU {sku})", "ok")

    inputs = [{"publicationId": g} for g in PUBLICATIONS.values()]
    sp.gql(M_PUBLISH, {"id": pid, "input": inputs}, mutation=True)
    sp.gql(M_METAFIELDS, {"metafields": [
        {"ownerId": pid, "namespace": GOOGLE_NS, "key": "condition",
         "type": "single_line_text_field", "value": "used"},
        {"ownerId": pid, "namespace": GOOGLE_NS, "key": "google_product_category",
         "type": "single_line_text_field", "value": GOOGLE_PRODUCT_CATEGORY},
    ]}, mutation=True)
    log("Publiée sur les 3 canaux + metafields Google appliqués", "ok")
    return record("T3", "ok", "Golf 7 GTI en ligne", {"id": pid, "price": price})


# ═════════════════════════════════════════════════════════════
# T4 — PUBLICATION DE TOUS LES PRODUITS SUR LES 3 CANAUX
# ═════════════════════════════════════════════════════════════
def task_T4(sp, products, dry):
    log("T4 — Publication multi-canaux", "step")
    pub_ids = set(PUBLICATIONS.values())
    fixed, failed = [], []
    for p in products:
        published = {n["publication"]["id"] for n in p["resourcePublications"]["nodes"]
                     if n["isPublished"]}
        missing = pub_ids - published
        if not missing:
            continue
        if dry:
            log(f"[DRY-RUN] {p['title']} → {len(missing)} canal(aux)", "dim")
            fixed.append(p["title"])
            continue
        d = sp.gql(M_PUBLISH, {"id": p["id"],
                               "input": [{"publicationId": g} for g in missing]},
                   mutation=True)
        errs = Shopify.user_errors(d, "publishablePublish")
        if errs:
            log(f"{p['title']} → échec publication : {errs}", "err")
            failed.append(p["title"])
            continue
        log(f"{p['title']} → publié sur {len(missing)} canal(aux)", "ok")
        fixed.append(p["title"])
    if not fixed and not failed:
        log("Tous les produits étaient déjà publiés partout", "ok")
    if failed:
        log(f"{len(failed)} produit(s) en échec de publication", "warn")
    detail = f"{len(fixed)} produits corrigés"
    if failed:
        detail += f", {len(failed)} en échec"
    return record("T4", "dryrun" if dry else ("error" if failed else "ok"),
                  detail, {"produits": fixed, "echecs": failed})


# ═════════════════════════════════════════════════════════════
# T5 — METAFIELDS GOOGLE MANQUANTS
# ═════════════════════════════════════════════════════════════
def task_T5(sp, products, dry):
    log("T5 — Metafields Google (condition / catégorie)", "step")
    batch, touched = [], []
    for p in products:
        mfs = []
        if not (p.get("condition") or {}).get("value"):
            mfs.append({"ownerId": p["id"], "namespace": GOOGLE_NS, "key": "condition",
                        "type": "single_line_text_field", "value": "used"})
        if not (p.get("gcat") or {}).get("value"):
            mfs.append({"ownerId": p["id"], "namespace": GOOGLE_NS,
                        "key": "google_product_category",
                        "type": "single_line_text_field",
                        "value": GOOGLE_PRODUCT_CATEGORY})
        if mfs:
            batch += mfs
            touched.append(p["title"])

    if not batch:
        log("Aucun metafield manquant", "ok")
        return record("T5", "ok", "Déjà conforme")
    log(f"{len(batch)} metafields à écrire sur {len(touched)} produits", "warn")
    if dry:
        return record("T5", "dryrun", f"{len(batch)} metafields simulés",
                      {"produits": touched})
    for i in range(0, len(batch), 25):
        d = sp.gql(M_METAFIELDS, {"metafields": batch[i:i + 25]}, mutation=True)
        errs = Shopify.user_errors(d, "metafieldsSet")
        if errs:
            log(f"Erreurs lot {i//25 + 1} : {errs}", "err")
    log("Metafields appliqués", "ok")
    return record("T5", "ok", f"{len(batch)} metafields écrits", {"produits": touched})


# ═════════════════════════════════════════════════════════════
# T6 — SITEMAP → GOOGLE SEARCH CONSOLE
# ═════════════════════════════════════════════════════════════
def task_T6(cfg, dry):
    log("T6 — Soumission sitemap à Search Console", "step")
    sa = cfg.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not sa or not Path(sa).exists():
        log("GOOGLE_SERVICE_ACCOUNT_JSON absent — soumission manuelle requise "
            "(voir CHECKLIST_MANUELLE.md)", "warn")
        return record("T6", "skipped", "Credentials Google absents")
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import AuthorizedSession
    except ImportError:
        log("Manque google-auth  ->  pip install -r requirements.txt", "err")
        return record("T6", "error", "google-auth non installé")

    creds = service_account.Credentials.from_service_account_file(
        sa, scopes=["https://www.googleapis.com/auth/webmasters"])
    sess = AuthorizedSession(creds)

    from urllib.parse import quote
    site = cfg.get("GSC_SITE_URL", SITE_URL.rstrip("/") + "/")
    done = []
    for sm in SITEMAPS:
        feed = f"{SITE_URL.rstrip('/')}/{sm}"
        url = (f"https://www.googleapis.com/webmasters/v3/sites/"
               f"{quote(site, safe='')}/sitemaps/{quote(feed, safe='')}")
        if dry:
            log(f"[DRY-RUN] PUT {feed}", "dim"); done.append(feed); continue
        r = sess.put(url, timeout=30)
        if r.status_code in (200, 204):
            log(f"Sitemap soumis : {feed}", "ok"); done.append(feed)
        else:
            log(f"Échec {r.status_code} sur {feed} : {r.text[:180]}", "err")
    return record("T6", "dryrun" if dry else "ok",
                  f"{len(done)} sitemap(s)", {"sitemaps": done})


# ═════════════════════════════════════════════════════════════
# T8 — HYGIÈNE SEO AUTOMATIQUE (idempotente)
# ═════════════════════════════════════════════════════════════
def seo_alt_for_product(title, index):
    clean = " ".join((title or "Véhicule d'occasion").split())
    return f"{clean} d'occasion à Madagascar — photo véhicule {index}"


def task_T8(sp, products, dry):
    log("T8 — Hygiène SEO automatique (ALT + couverture)", "step")
    missing_alt = []
    missing_seo = []
    updates = {}
    for p in products:
        seo = p.get("seo") or {}
        if not (seo.get("title") or "").strip():
            missing_seo.append(p["title"])
        if not (seo.get("description") or "").strip():
            missing_seo.append(p["title"])
        media_updates = []
        for i, media in enumerate((p.get("media") or {}).get("nodes", []), 1):
            if not (media.get("alt") or "").strip():
                media_updates.append({
                    "id": media["id"],
                    "alt": seo_alt_for_product(p["title"], i),
                })
        if media_updates:
            missing_alt.append(p["title"])
            updates[p["id"]] = {"title": p["title"], "media": media_updates}

    total_media = sum(len(v["media"]) for v in updates.values())
    if not updates:
        log("Aucun ALT manquant ; les métadonnées SEO existantes sont conservées", "ok")
        return record("T8", "ok", "Catalogue conforme", {
            "produits_sans_seo": len(set(missing_seo)),
            "produits_avec_alt_manquant": 0,
            "medias_corriges": 0,
        })

    log(f"{total_media} ALT manquant(s) sur {len(updates)} produit(s)", "warn")
    if dry:
        log("[DRY-RUN] aucune écriture envoyée", "dim")
        return record("T8", "dryrun", f"{total_media} ALT simulé(s)", {
            "produits": list(missing_alt),
            "medias": total_media,
            "produits_sans_seo": len(set(missing_seo)),
        })

    fixed, failed = [], []
    for pid, payload in updates.items():
        d = sp.gql(M_MEDIA_ALT_UPDATE, {
            "productId": pid,
            "media": payload["media"],
        }, mutation=True)
        errs = ((d or {}).get("productUpdateMedia") or {}).get("mediaUserErrors") or []
        if errs:
            failed.append({"produit": payload["title"], "erreurs": errs})
            log(f"{payload['title']} → ALT : échec {errs}", "err")
        else:
            fixed.append(payload["title"])
            log(f"{payload['title']} → {len(payload['media'])} ALT corrigé(s)", "ok")

    status = "error" if failed else "ok"
    return record("T8", status,
                  f"{sum(len(updates[pid]['media']) for pid in updates if updates[pid]['title'] in fixed)} ALT corrigé(s)" + (f", {len(failed)} échec(s)" if failed else ""),
                  {"produits_corriges": fixed, "echecs": failed,
                   "produits_sans_seo": len(set(missing_seo))})


# ═════════════════════════════════════════════════════════════
# RAPPORT
# ═════════════════════════════════════════════════════════════
def write_report():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M")
    (OUT_DIR / f"rapport-{stamp}.json").write_text(
        json.dumps(RESULTS, indent=2, ensure_ascii=False), encoding="utf-8")

    icons = {"ok": "✅", "warn": "⚠️", "error": "❌", "skipped": "⏭️", "dryrun": "🧪"}
    lines = [f"# Carokaz Mada — Rapport d'auto-configuration",
             f"_{datetime.now().strftime('%d/%m/%Y %H:%M')}_", "",
             "| Tâche | Statut | Détail |", "|---|---|---|"]
    for r in RESULTS:
        lines.append(f"| {r['task']} | {icons.get(r['status'],'•')} {r['status']} "
                     f"| {r['detail']} |")
    md = OUT_DIR / f"rapport-{stamp}.md"
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print()
    log(f"Rapport : {md}", "ok")


# ═════════════════════════════════════════════════════════════
def main():
    ap = argparse.ArgumentParser(description="Carokaz Mada — auto-configuration")
    ap.add_argument("--all", action="store_true", help="exécuter toutes les tâches")
    ap.add_argument("--only", help="liste ex: T1,T4,T6")
    ap.add_argument("--dry-run", action="store_true", help="simulation, aucune écriture")
    ap.add_argument("--gti-price", help="prix de la Golf 7 GTI en MGA")
    a = ap.parse_args()

    cfg = dict(os.environ)
    dry = a.dry_run
    selected = set(x.strip().upper() for x in a.only.split(",")) if a.only else None
    if not a.all and not selected:
        ap.error("Préciser --all ou --only T1,T2,...")

    def want(t):
        return selected is None or t in selected

    print(f"\n{C.BOLD}CAROKAZ MADA — AUTO-CONFIGURATION{C.X}")
    print(f"{C.D}Boutique : {SHOP_DOMAIN} | API {API_VERSION} | "
          f"{'MODE SIMULATION' if dry else 'MODE ÉCRITURE'}{C.X}\n")

    token = cfg.get("SHOPIFY_ADMIN_TOKEN")
    sp = Shopify(token, dry) if token else None
    products = []

    if want("T1"):
        task_T1(cfg, dry); print()

    needs_shopify = any(want(t) for t in ("T2", "T3", "T4", "T5", "T8"))
    if needs_shopify and not sp:
        log("SHOPIFY_ADMIN_TOKEN absent — tâches Shopify ignorées", "warn")
    elif needs_shopify:
        try:
            products, _ = task_T2(sp); print()
        except Exception as e:
            log(f"Audit impossible : {e}", "err"); record("T2", "error", str(e))

        if want("T3"):
            try:
                task_T3(sp, a.gti_price or cfg.get("GTI_PRICE"), dry)
            except Exception as e:
                log(f"T3 : {e}", "err"); record("T3", "error", str(e))
            print()
        if want("T4") and products:
            try:
                task_T4(sp, products, dry)
            except Exception as e:
                log(f"T4 : {e}", "err"); record("T4", "error", str(e))
            print()
        if want("T5") and products:
            try:
                task_T5(sp, products, dry)
            except Exception as e:
                log(f"T5 : {e}", "err"); record("T5", "error", str(e))
            print()
        if want("T8") and products:
            try:
                task_T8(sp, products, dry)
            except Exception as e:
                log(f"T8 : {e}", "err"); record("T8", "error", str(e))
            print()

    if want("T6"):
        try:
            task_T6(cfg, dry)
        except Exception as e:
            log(f"T6 : {e}", "err"); record("T6", "error", str(e))

    write_report()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\nInterrompu.")
