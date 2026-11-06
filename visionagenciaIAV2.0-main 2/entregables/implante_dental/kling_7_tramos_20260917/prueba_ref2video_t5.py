"""Tramo 5 con kling-video-o3-pro/reference-to-video: video de movimiento de Blender + referencias.

Carlos (17 sep): «¿no le has estado dando a Kling una parte del video de Blender?» — tenía razón,
los 7 tramos iban solo con cuadro inicial y final, así que Kling se inventaba el movimiento de en
medio (en el tramo 5 bajó un segundo tornillo desde arriba, al revés de la anatomía).

Este modelo es lo más parecido a Genjutsu que hay en WaveSpeed: acepta el video de movimiento MÁS
hasta 4 imágenes de referencia. No tiene negative_prompt, así que las prohibiciones van dentro del
prompt positivo.

El video tiene que medir entre 700 y 3840 px por lado: el render de Blender es 432x768, por eso se
escala a 720x1280. También se tapa el rótulo "MESES DE CICATRIZACIÓN" del final para que no se cuele.

Objetivo principal de esta corrida: MEDIR EL COSTO REAL (lista $0.56; Seedance cobró 5x su lista).
"""
import json, os, sys, time, urllib.request, base64

AQUI = os.path.dirname(os.path.abspath(__file__))
DENTAL = os.path.dirname(AQUI)
sys.path.insert(0, os.path.join(DENTAL, "kling_transicion"))
sys.path.insert(0, os.path.join(DENTAL, "..", "catania_mariano_montaje_20260914"))
import gancho_kling_habla_giro as g
from kling_transicion import cuadro_916

MODELO = "kwaivgi/kling-video-o3-pro/reference-to-video"
GENJ = os.path.join(DENTAL, "genjutsu_20260915", "IMAGENES")
VIDEO = os.path.join(AQUI, "MOVIMIENTO_BLENDER_T5.mp4")
SALIDA = os.path.join(AQUI, "PRUEBA_REF2VIDEO_T5.mp4")

PROMPT = (
    "Use the reference video ONLY as the exact motion, timing and camera reference; ignore its grey clay look. "
    "Render it with the look of the reference images: front cross-section of the UPPER jaw, porous cream bone on "
    "top with a glowing warm orange cut edge, translucent glowing pink gum across the middle, exactly four natural "
    "upper teeth hanging DOWN with their long roots going UP into the bone, one gap in the centre, satin grey "
    "titanium with fine threads, near-black background with deep teal and warm orange bokeh, soft teal rim light, "
    "shallow depth of field, premium 3D medical visualisation. "
    "The action, exactly as in the reference video: the titanium threaded implant rises from BELOW through the gap "
    "and screws UPWARD into the bone, rotating on its vertical axis, until it is fully seated with its flat top at "
    "the gum line. The bone then glows softly and fine new bone grows tightly into the threads. "
    "The flat top of the implant is part of the implant itself, already there: no new part arrives, nothing enters "
    "the frame from above, and the bone is never pierced from its top surface. There is only ONE implant in the "
    "whole shot. The four neighbouring teeth and the gum never move. "
    "Anatomically clean: no blood, no wound, no gore, no molars, no lower jaw, no extra or duplicated teeth, no "
    "second implant, no instrument falling from the sky. One smooth continuous shot, no cuts, no camera shake, "
    "no text, labels or watermark."
)


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
    cuerpo = {
        "prompt": PROMPT,
        "video": "data:video/mp4;base64," + base64.b64encode(open(VIDEO, "rb").read()).decode(),
        "images": [cuadro_916(os.path.join(GENJ, "06_implante_entra.png")),
                   cuadro_916(os.path.join(GENJ, "07_integracion.png"))],
        "duration": 5, "aspect_ratio": "9:16", "sound": False, "keep_original_sound": False,
    }
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
    print("saldo despues:", despues, flush=True)
    costo = round(float(antes) - float(despues), 4) if isinstance(antes, (int, float)) else None
    json.dump({"modelo": MODELO, "id": id_, "url": url, "video_movimiento": os.path.basename(VIDEO),
               "saldo": {"antes": antes, "despues": despues}, "costo_real": costo},
              open(os.path.join(AQUI, "recibo_ref2video.json"), "w"), indent=1)
    print("COSTO REAL:", costo, "| lista 0.56", flush=True)
    print("listo ->", SALIDA, flush=True)
