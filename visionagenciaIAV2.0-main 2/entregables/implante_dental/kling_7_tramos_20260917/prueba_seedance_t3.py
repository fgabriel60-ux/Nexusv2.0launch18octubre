"""A/B contra Kling: el MISMO tramo 3 (el despegue) hecho con Seedance 2.0 fast.

Carlos (17 sep) preguntó si con Seedance 2.0 fast se vería mejor. Se prueba con los mismos
dos cuadros llave (R10_anestesia_sale -> R15_fresa_dentro) para que la comparación sea justa.

Diferencia importante del modelo: Seedance NO tiene negative_prompt. Todo lo que en Kling
iba en el negativo (sin sangre, sin muelas, sin anatomía encima de la piel) hay que meterlo
como instrucción en el prompt positivo.

Mide el saldo antes y después: el precio de lista ($0.50) puede no ser el real — MiniMax
tenía lista $0.25 y cobró $2.85 el 16 sep.
"""
import json, os, sys, time, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
DENTAL = os.path.dirname(AQUI)
sys.path.insert(0, os.path.join(DENTAL, "kling_transicion"))
sys.path.insert(0, os.path.join(DENTAL, "..", "catania_mariano_montaje_20260914"))
import gancho_kling_habla_giro as g
from kling_transicion import cuadro_916

MODELO = "bytedance/seedance-2.0-fast/image-to-video"
INICIO = os.path.join(AQUI, "CUADROS", "R10_anestesia_sale.png")
FIN = os.path.join(AQUI, "CUADROS", "R15_fresa_dentro.png")
SALIDA = os.path.join(AQUI, "PRUEBA_SEEDANCE_T3.mp4")

PROMPT = (
    "Extreme macro of a woman's mouth with one missing upper front tooth; a dental syringe has just left the frame. "
    "STRICT ORDER OF EVENTS, one after the other, never at the same time. "
    "FIRST, for the first two seconds: ONLY her skin moves. Her face and lips peel away from the right side like a "
    "glossy photographic sticker, the skin curling smoothly and continuously toward the left, showing its pale "
    "paper-like back and a thin warm glowing edge, with a soft shadow under the curl. Her mouth stays closed and "
    "relaxed while it peels. Nothing else appears and nothing is visible through or on top of her skin: the "
    "anatomy must NOT be superimposed, ghosted, cross-faded or dissolved over her face at any moment. "
    "SECOND: only as the curling skin clears each part of the frame, the clean front cross-section of the UPPER "
    "jaw is uncovered BEHIND it, never over it: porous cream bone on top, glowing translucent pink gum, exactly "
    "four natural upper teeth hanging down with their long roots going up, and one gap in the centre. No molars, "
    "no lower jaw, no extra or duplicated teeth. The skin keeps curling until it has completely left the frame. "
    "THIRD, in the last second only, once no skin is left: a thin polished steel dental drill rises from below "
    "through the gap and its tip enters the bone above the gap, ending exactly on the final image. "
    "Dark near-black background with deep teal and warm orange bokeh, soft teal rim light, shallow depth of field. "
    "Premium 3D medical visualisation, calm and elegant, anatomically clean with NO blood, no wound, no gore. "
    "One smooth continuous shot: no cuts, no jump cuts, no camera shake, no text, labels or watermark."
)


def saldo():
    try:
        req = urllib.request.Request(g.WAVESPEED + "/balance", headers=g.CAB)
        return json.loads(urllib.request.urlopen(req, timeout=60).read()).get("data", {}).get("balance")
    except Exception as e:
        return "sin dato (%s)" % e


if __name__ == "__main__":
    antes = saldo()
    print("saldo antes:", antes, flush=True)
    cuerpo = {"prompt": PROMPT, "image": cuadro_916(INICIO), "last_image": cuadro_916(FIN),
              "duration": 5, "aspect_ratio": "9:16", "resolution": "1080p", "generate_audio": False}
    req = urllib.request.Request(g.WAVESPEED + "/" + MODELO, data=json.dumps(cuerpo).encode(), headers=g.CAB)
    try:
        id_ = json.loads(urllib.request.urlopen(req, timeout=300).read())["data"]["id"]
    except urllib.error.HTTPError as e:
        raise SystemExit("Seedance rechazó la petición: %s %s" % (e.code, e.read().decode()[:400]))
    print("JOB", id_, flush=True)
    url = None
    for _ in range(240):
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
    json.dump({"modelo": MODELO, "id": id_, "url": url, "saldo": {"antes": antes, "despues": despues},
               "costo_real": round(float(antes) - float(despues), 4) if isinstance(antes, (int, float)) else None},
              open(os.path.join(AQUI, "recibo_seedance.json"), "w"), indent=1)
    print("listo ->", SALIDA, flush=True)
