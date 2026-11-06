"""Tramo 6 con kling-v2.6-pro/motion-control: video de Blender + UNA referencia.

Carlos (17 sep): «intenta el siguiente con motion control».

Diferencias contra reference-to-video (que costó $0.84 en el tramo 5):
  - más barato de lista ($0.336 contra $0.56)
  - SÍ tiene negative_prompt, que en reference-to-video se pierde
  - pero solo acepta UNA imagen de referencia (contra 4)

Se le da 08_pilar_corona como referencia única porque es el cuadro que contiene todos los
elementos que deben aparecer en este tramo: hueso, encía, dientes, implante, pilar y corona.
Con 07_integracion el modelo no tendría de dónde sacar cómo se ve la corona.
"""
import json, os, sys, time, urllib.request, base64

AQUI = os.path.dirname(os.path.abspath(__file__))
DENTAL = os.path.dirname(AQUI)
sys.path.insert(0, os.path.join(DENTAL, "kling_transicion"))
sys.path.insert(0, os.path.join(DENTAL, "..", "catania_mariano_montaje_20260914"))
import gancho_kling_habla_giro as g
from kling_transicion import cuadro_916

MODELO = "kwaivgi/kling-v2.6-pro/motion-control"
GENJ = os.path.join(DENTAL, "genjutsu_20260915", "IMAGENES")
VIDEO = os.path.join(AQUI, "MOVIMIENTO_BLENDER_T6.mp4")
SALIDA = os.path.join(AQUI, "PRUEBA_MOTIONCONTROL_T6.mp4")

PROMPT = (
    "Follow the reference video exactly for motion, timing, framing and camera; ignore its flat grey clay look "
    "and render everything with the look of the reference image. "
    "Front cross-section of the UPPER jaw: porous cream bone on top with a glowing warm orange cut edge, "
    "translucent glowing pink gum across the middle, exactly four natural upper teeth hanging DOWN with their long "
    "roots going UP into the bone, and one gap in the centre with a satin grey titanium implant already fully "
    "seated inside the bone. "
    "The action: the bone glows softly while fine new bone grows tightly into the implant threads. Then a short "
    "polished titanium abutment is placed on the implant at the gum line, and ONE natural ivory crown rises from "
    "BELOW and seats onto it, filling the gap and leaving a tight row of exactly FIVE upper front teeth with no "
    "gap, the new crown identical in colour and shape to its neighbours. "
    "The four neighbouring teeth and the gum never move. Near-black background with deep teal and warm orange "
    "bokeh, soft teal rim light, shallow depth of field, premium 3D medical visualisation."
)
NEG = ("blood, gore, wound, open flesh, extra teeth, duplicated teeth, teeth changing count, lower jaw, molars, "
       "second implant, duplicated implant, two screws, object falling from above, screw entering through the top "
       "of the bone, instrument from the sky, grey clay look, untextured plastic, flat shading, "
       "flicker, jump cut, crossfade dissolve, text, labels, watermark, camera shake, low quality")


def saldo():
    try:
        req = urllib.request.Request(g.WAVESPEED + "/balance", headers=g.CAB)
        return json.loads(urllib.request.urlopen(req, timeout=60).read()).get("data", {}).get("balance")
    except Exception as e:
        return "sin dato (%s)" % e


if __name__ == "__main__":
    assert os.path.exists(VIDEO), "falta el video de movimiento"
    antes = saldo()
    print("saldo antes:", antes, flush=True)
    cuerpo = {"prompt": PROMPT, "negative_prompt": NEG,
              "video": "data:video/mp4;base64," + base64.b64encode(open(VIDEO, "rb").read()).decode(),
              "image": cuadro_916(os.path.join(GENJ, "08_pilar_corona.png")),
              "keep_original_sound": False}
    req = urllib.request.Request(g.WAVESPEED + "/" + MODELO, data=json.dumps(cuerpo).encode(), headers=g.CAB)
    try:
        id_ = json.loads(urllib.request.urlopen(req, timeout=600).read())["data"]["id"]
    except urllib.error.HTTPError as e:
        raise SystemExit("rechazado: %s %s" % (e.code, e.read().decode()[:500]))
    print("JOB", id_, flush=True)
    url = None
    for _ in range(300):
        time.sleep(5)
        q = urllib.request.Request("%s/predictions/%s/result" % (g.WAVESPEED, id_), headers=g.CAB)
        d = (json.loads(urllib.request.urlopen(q, timeout=60).read()) or {}).get("data") or {}
        if d.get("status") == "completed":
            url = d["outputs"][0]; break
        if d.get("status") == "failed":
            raise SystemExit("FALLÓ: %s" % d.get("error"))
    assert url, "timeout"
    with urllib.request.urlopen(url, timeout=600) as r:
        open(SALIDA, "wb").write(r.read())
    despues = saldo()
    costo = round(float(antes) - float(despues), 4) if isinstance(antes, (int, float)) else None
    print("saldo despues:", despues, "| COSTO REAL:", costo, "| lista 0.336", flush=True)
    json.dump({"modelo": MODELO, "id": id_, "url": url, "saldo": {"antes": antes, "despues": despues},
               "costo_real": costo}, open(os.path.join(AQUI, "recibo_motioncontrol.json"), "w"), indent=1)
    print("listo ->", SALIDA, flush=True)
