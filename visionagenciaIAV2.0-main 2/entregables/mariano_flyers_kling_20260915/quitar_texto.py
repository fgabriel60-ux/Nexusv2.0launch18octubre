"""Flyers de Mariano (12 sep): quitar todo el texto, logos e íconos y dejar el puro fondo, para animar con Kling y
poner los textos encima después. Carlos (15 sep): «quítales el texto y deja el puro fondo, primero uno».
Uso: python3 quitar_texto.py 1          (solo flyer_1)
     python3 quitar_texto.py 1 2 3 ...  (varios)"""
import json, os, sys, time, urllib.request
sys.path.insert(0, "/workspaces/visionagenciaIAV2.0/entregables/implante_dental/gpt_transicion")
import gpt_transicion as v1
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
PROMPT = (
    "Remove ALL text, numbers, prices, titles, logos, brand marks, shields, icons, badges, buttons, boxes and small print "
    "from this real-estate flyer, leaving ONLY the clean photographic background. Where text or graphics covered the "
    "image, reconstruct what would naturally be behind them (sky, sea, hills, streets, houses, grass, clouds) so it "
    "looks like one untouched photo. Keep every person, animal, house, road, landscape, colour, light and the exact "
    "framing and composition identical; do not add anything new. No text of any kind, no watermark."
)


def aspecto(ruta):
    w, h = Image.open(ruta).size
    r = w / h
    return "1:1" if abs(r - 1) < 0.08 else ("2:3" if r < 1 else "3:2")


def limpiar(n):
    src = next(p for p in (os.path.join(AQUI, "flyer_%s.%s" % (n, e)) for e in ("jpg", "png")) if os.path.exists(p))
    destino = os.path.join(AQUI, "fondo_flyer_%s.png" % n)
    cuerpo = {"prompt": PROMPT, "images": [v1.uri(src)], "aspect_ratio": aspecto(src), "output_format": "png"}
    req = urllib.request.Request(v1.WAVESPEED + "/" + v1.MODELO, data=json.dumps(cuerpo).encode(), headers=v1.CAB)
    with urllib.request.urlopen(req, timeout=300) as r:
        id_ = json.loads(r.read())["data"]["id"]
    for _ in range(200):
        time.sleep(5)
        q = urllib.request.Request("%s/predictions/%s/result" % (v1.WAVESPEED, id_), headers=v1.CAB)
        d = (json.loads(urllib.request.urlopen(q, timeout=60).read()) or {}).get("data") or {}
        if d.get("status") == "completed":
            with urllib.request.urlopen(d["outputs"][0], timeout=300) as r:
                open(destino, "wb").write(r.read())
            print("listo", destino, flush=True); return
        if d.get("status") == "failed":
            print("FALLÓ", n, d.get("error"), flush=True); return


if __name__ == "__main__":
    for n in sys.argv[1:] or ["1"]:
        limpiar(n)
