"""Baja los videos de referencia por Apify (yt-dlp ya no puede con TikTok: 'Unexpected response').

El scraper sube los mp4 al key-value store de la corrida; de ahí se descargan.
"""
import json, os, sys, time, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = "/workspaces/visionagenciaIAV2.0/visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main"
def env(n):
    for l in open(os.path.join(RAIZ, ".env"), encoding="utf8", errors="replace"):
        if l.startswith(n + "="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
TOKEN = env("APIFY_TOKEN")
API = "https://api.apify.com/v2"
VIDEOS = os.path.join(AQUI, "videos"); os.makedirs(VIDEOS, exist_ok=True)

# Dentistas hispanohablantes con videos cortos, lo más parecido a lo nuestro
OBJETIVO = [
    "https://www.tiktok.com/@doctorleonperu/video/7682513956929359124",
    "https://www.tiktok.com/@odontoseguro123.4/video/7663537415079939346",
    "https://www.tiktok.com/@dental.sonris/video/7602448293825711368",
    "https://www.tiktok.com/@dr.felicianorojas/video/7676175915923164436",
    "https://www.tiktok.com/@dentaltreatmentweb/video/7670629719372483862",
    "https://www.tiktok.com/@smile_doc/video/7668141929267301662",
]

if __name__ == "__main__":
    entrada = {"postURLs": OBJETIVO, "shouldDownloadVideos": True,
               "shouldDownloadCovers": False, "resultsPerPage": 1}
    req = urllib.request.Request("%s/acts/clockworks~tiktok-scraper/runs?token=%s" % (API, TOKEN),
                                 data=json.dumps(entrada).encode(),
                                 headers={"Content-Type": "application/json"})
    r = json.loads(urllib.request.urlopen(req, timeout=120).read())["data"]
    rid, ds, kv = r["id"], r["defaultDatasetId"], r["defaultKeyValueStoreId"]
    print("run", rid, flush=True)
    for _ in range(90):
        time.sleep(10)
        e = json.loads(urllib.request.urlopen("%s/actor-runs/%s?token=%s" % (API, rid, TOKEN),
                                              timeout=60).read())["data"]
        if e["status"] in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            print(e["status"], "| USD", round(float(e.get("usageTotalUsd") or 0), 4), flush=True)
            break
    claves = json.loads(urllib.request.urlopen(
        "%s/key-value-stores/%s/keys?token=%s&limit=200" % (API, kv, TOKEN), timeout=60).read())
    n = 0
    for k in claves.get("data", {}).get("items", []):
        if "video" not in k["key"].lower():
            continue
        url = "%s/key-value-stores/%s/records/%s?token=%s" % (API, kv, k["key"], TOKEN)
        dst = os.path.join(VIDEOS, k["key"] + ".mp4")
        with urllib.request.urlopen(url, timeout=300) as resp:
            open(dst, "wb").write(resp.read())
        n += 1
        print("  bajado", k["key"], os.path.getsize(dst) // 1000, "KB", flush=True)
    print(n, "videos en videos/")
