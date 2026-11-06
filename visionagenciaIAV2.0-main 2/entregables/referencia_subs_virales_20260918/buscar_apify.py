"""Busca videos virales de dentistas/médicos con Apify, para copiar cómo subtitulan.

Carlos (18 sep): «busca en videos virales de dentistas o medicos con apify», después de decir
que los subtítulos estilo Playfair estaban feos.

Lo que importa no es el contenido sino la TIPOGRAFÍA: qué fuente, qué tamaño, dónde la ponen,
si resaltan la palabra viva y de qué color. Por eso se bajan los videos y se muestrean cuadros.

Cuenta Apify: plan FREE, $5 al mes. Al 18 sep iban $0.378 usados.
Uso: python3 buscar_apify.py
"""
import json, os, sys, time, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = "/workspaces/visionagenciaIAV2.0/visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main"


def env(n):
    for l in open(os.path.join(RAIZ, ".env"), encoding="utf8", errors="replace"):
        if l.startswith(n + "="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


TOKEN = env("APIFY_TOKEN")
API = "https://api.apify.com/v2"


def corre(actor, entrada, espera=600):
    """Lanza el actor y devuelve los items del dataset."""
    url = "%s/acts/%s/runs?token=%s" % (API, actor.replace("/", "~"), TOKEN)
    req = urllib.request.Request(url, data=json.dumps(entrada).encode(),
                                 headers={"Content-Type": "application/json"})
    r = json.loads(urllib.request.urlopen(req, timeout=120).read())["data"]
    rid, ds = r["id"], r["defaultDatasetId"]
    print("  run", rid, flush=True)
    t0 = time.time()
    while time.time() - t0 < espera:
        time.sleep(10)
        e = json.loads(urllib.request.urlopen(
            "%s/actor-runs/%s?token=%s" % (API, rid, TOKEN), timeout=60).read())["data"]
        if e["status"] in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            print("  ->", e["status"], "| USD", round(float(
                (e.get("usageTotalUsd") or 0)), 4), flush=True)
            break
    items = json.loads(urllib.request.urlopen(
        "%s/datasets/%s/items?token=%s&limit=200" % (API, ds, TOKEN), timeout=120).read())
    return items


if __name__ == "__main__":
    salida = {}
    # TikTok: es donde el subtítulo quemado es la norma, así que es la mejor referencia
    print("TikTok, hashtags de implantes y odontología...", flush=True)
    items = corre("clockworks/tiktok-scraper", {
        "hashtags": ["implantedental", "dentista", "odontologia", "implantesdentales"],
        "resultsPerPage": 15,
        "shouldDownloadVideos": False,
        "shouldDownloadCovers": False,
    })
    vids = []
    for it in items:
        vids.append({
            "red": "tiktok",
            "url": it.get("webVideoUrl"),
            "autor": (it.get("authorMeta") or {}).get("name"),
            "plays": it.get("playCount") or 0,
            "likes": it.get("diggCount") or 0,
            "dura": (it.get("videoMeta") or {}).get("duration"),
            "texto": (it.get("text") or "")[:120],
        })
    vids.sort(key=lambda v: -v["plays"])
    salida["tiktok"] = vids
    json.dump(salida, open(os.path.join(AQUI, "encontrados.json"), "w"), ensure_ascii=False, indent=1)
    print("\n%d videos. Los 15 más vistos:\n" % len(vids))
    for v in vids[:15]:
        print("%12s  %9s plays  %6ss  @%-22s %s" % (
            v["red"], "{:,}".format(v["plays"]), v["dura"], v["autor"], v["url"]))
