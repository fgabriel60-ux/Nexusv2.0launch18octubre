"""Papá (16 sep, con su foto): «Sácala vestidos de charros revolucionarios ☺️».
Dos versiones de la misma foto, cambiando SOLO la ropa: charro de gala y revolucionario con bandoleras.
Las caras, la pose y el encuadre se conservan para que sigan siendo ellos.
Uso: python3 charros_revolucionarios.py"""
import json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "/workspaces/visionagenciaIAV2.0/entregables/implante_dental/gpt_transicion")
import gpt_transicion as v1

AQUI = os.path.dirname(os.path.abspath(__file__))
FOTO = os.path.join(AQUI, "FOTO_PAPA_CHARROS.jpg")
FIEL = ("Keep BOTH men exactly the same people: same faces, facial features, skin tone, hair, beard, expressions, "
        "head positions, body poses, height difference and the same camera framing and lighting. Do not beautify, "
        "slim, age or rejuvenate them, do not swap who is who. Photorealistic, natural fabric texture. "
        "No text, no logos, no watermark.")
VERSIONES = {
    "CHARROS_v1_gala": (
        "Edit this photo so both men are dressed as traditional Mexican CHARROS in full gala outfit for the "
        "September 16th fiestas: dark charro jacket with fine silver embroidery and botonadura down the sleeves, "
        "matching charro trousers, crisp white shirt, a red silk bow tie (moño de charro), and a wide-brimmed "
        "embroidered charro sombrero on the head of each one, well fitted. Elegant and dignified, like a family "
        "photo taken at a charrería event. " + FIEL),
    "CHARROS_v2_revolucionarios": (
        "Edit this photo so both men are dressed as Mexican REVOLUCIONARIOS of 1910, in charro style: dark rustic "
        "charro jacket and trousers, white shirt, a red or beige neckerchief tied at the neck, crossed leather "
        "cartridge bandoliers over the chest, and a wide-brimmed sombrero on the head of each one. Warm sepia-tinted "
        "cinematic light, like a proud revolution-era portrait, but keep the photo modern and sharp. " + FIEL),
}


def generar(nombre):
    destino = os.path.join(AQUI, nombre + ".png")
    cuerpo = {"prompt": VERSIONES[nombre], "images": [v1.uri(FOTO)], "aspect_ratio": "1:1", "output_format": "png"}
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
            print("listo", nombre, flush=True); return
        if d.get("status") == "failed":
            print("FALLÓ", nombre, d.get("error"), flush=True); return


if __name__ == "__main__":
    with ThreadPoolExecutor(2) as ex:
        list(ex.map(generar, VERSIONES))
