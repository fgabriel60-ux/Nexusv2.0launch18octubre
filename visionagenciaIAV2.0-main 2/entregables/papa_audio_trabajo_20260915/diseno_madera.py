"""Diseño que pidió el cliente de papá (audio 15 sep): «un diseño de madera, color madera, con una cajonera y un
comedorcito». Dos propuestas GPT Image 2 para enseñarle mientras manda la foto del diseño que le gusta.
Uso: python3 diseno_madera.py"""
import json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "/workspaces/visionagenciaIAV2.0/entregables/implante_dental/gpt_transicion")
import gpt_transicion as v1

AQUI = os.path.dirname(os.path.abspath(__file__))
MODELO = "openai/gpt-image-2/text-to-image"
BASE = ("Photorealistic interior photo of custom-made furniture by a local Mexican carpenter, warm natural wood colour "
        "(honey / walnut-toned wood, visible natural grain, satin finish), well lit, clean modern home in Sonora, "
        "realistic proportions, eye-level camera, no people, no text, no watermark. ")
PROPUESTAS = {
    "PROPUESTA_1_cocina_cajonera_comedorcito": BASE +
        "A wall of wood-colour kitchen cabinets with a tall column of drawers (cajonera) with simple wooden pulls, and "
        "an attached small breakfast dining nook: a compact wood table for two to four people built into the end of "
        "the cabinet run, with matching wooden chairs. Cohesive design, everything in the same warm wood colour.",
    "PROPUESTA_2_cajonera_y_comedor": BASE +
        "A solid wood chest of drawers (cajonera) with five drawers and a small matching dining set next to it: a "
        "compact square wood table with four wooden chairs, same warm wood colour and style, simple elegant lines.",
}


def generar(nombre):
    cuerpo = {"prompt": PROPUESTAS[nombre], "aspect_ratio": "4:3", "output_format": "png"}
    req = urllib.request.Request(v1.WAVESPEED + "/" + MODELO, data=json.dumps(cuerpo).encode(), headers=v1.CAB)
    with urllib.request.urlopen(req, timeout=300) as r:
        id_ = json.loads(r.read())["data"]["id"]
    for _ in range(200):
        time.sleep(5)
        q = urllib.request.Request("%s/predictions/%s/result" % (v1.WAVESPEED, id_), headers=v1.CAB)
        d = (json.loads(urllib.request.urlopen(q, timeout=60).read()) or {}).get("data") or {}
        if d.get("status") == "completed":
            with urllib.request.urlopen(d["outputs"][0], timeout=300) as r:
                open(os.path.join(AQUI, nombre + ".png"), "wb").write(r.read())
            print(nombre, "listo", flush=True); return
        if d.get("status") == "failed":
            print(nombre, "FALLÓ", d.get("error"), flush=True); return


if __name__ == "__main__":
    with ThreadPoolExecutor(2) as ex:
        list(ex.map(generar, PROPUESTAS))
