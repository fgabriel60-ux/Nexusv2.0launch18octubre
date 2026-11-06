"""Tramos con Seedance 2.0 fast, con la resolución como parámetro.

Seedance es el único que resolvió la transición de la calcomanía (tramo 3), pero cobra por
píxeles: el tramo 3 a 1080p costó $2.50 reales sobre una lista de $0.50. Por eso aquí la
resolución se pasa por línea de comandos y el saldo se mide siempre.

Estimación por píxeles, tomando el tramo 3 como referencia:
   480p  0.41 Mpx  ~$0.50      720p  0.92 Mpx  ~$1.13      1080p  2.07 Mpx  $2.50 (medido)

Seedance no tiene negative_prompt: las prohibiciones van dentro del prompt positivo.
Uso: python3 correr_seedance.py 7 480p
"""
import json, os, sys, time, urllib.request, base64

AQUI = os.path.dirname(os.path.abspath(__file__))
DENTAL = os.path.dirname(AQUI)
sys.path.insert(0, os.path.join(DENTAL, "kling_transicion"))
sys.path.insert(0, os.path.join(DENTAL, "..", "catania_mariano_montaje_20260914"))
import gancho_kling_habla_giro as g
from kling_transicion import cuadro_916

MODELO = "bytedance/seedance-2.0-fast/image-to-video"
GENJ = os.path.join(DENTAL, "genjutsu_20260915", "IMAGENES")
CUAD = os.path.join(AQUI, "CUADROS")
CLIPS = os.path.join(AQUI, "CLIPS_SEEDANCE"); os.makedirs(CLIPS, exist_ok=True)

LOOK = (" Near-black background with deep teal and warm orange bokeh, soft teal rim light, shallow depth of field. "
        "Premium 3D medical visualisation, calm and elegant. One smooth continuous shot ending exactly on the "
        "final image. Anatomically clean with NO blood, no wound, no gore, no molars, no lower jaw, no extra or "
        "duplicated teeth. No cuts, no camera shake, no text, labels or watermark.")

TRAMOS = {
    7: (os.path.join(GENJ, "09_corona_colocada.png"), os.path.join(GENJ, "10_sonrisa_feliz.png"),
        "T7_morph_sonrisa",
        "Front cross-section of the UPPER jaw with a complete row of five upper front teeth and no gap. "
        "STRICT ORDER OF EVENTS, one after the other, never at the same time. "
        "FIRST, for the first two seconds: a sheet of the woman's skin and lips travels in from the left as a "
        "glossy curled sheet, showing its pale paper-like back and a thin warm glowing edge with a soft shadow "
        "under the curl, and unrolls smoothly to the right, covering the anatomy IN FRONT of it as it goes. The "
        "bone and gum are progressively hidden BEHIND the advancing skin, never faded out underneath it and never "
        "showing through it; her face is never transparent and the anatomy is never superimposed over her skin. "
        "The sheet keeps unrolling until it has flattened completely and her face is whole again in the original "
        "framing, wearing a shy closed-lip smile. "
        "SECOND, only once her face is whole and no anatomy is left: her expression opens smoothly into a radiant, "
        "genuinely happy smile, cheeks lifted, eyes warm and squinting slightly, lips parting to show a complete "
        "row of upper teeth with no gap, exactly as in the final image. Same woman, same identity, same skin, "
        "same hair, same framing and lighting throughout. Hold on her happy smile until the end."),
}


def saldo():
    try:
        req = urllib.request.Request(g.WAVESPEED + "/balance", headers=g.CAB)
        return json.loads(urllib.request.urlopen(req, timeout=60).read()).get("data", {}).get("balance")
    except Exception as e:
        return "sin dato (%s)" % e


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    res = sys.argv[2] if len(sys.argv) > 2 else "480p"
    ini, fin, nombre, prompt = TRAMOS[n]
    salida = os.path.join(CLIPS, "%s_%s.mp4" % (nombre, res))
    antes = saldo(); print("saldo antes:", antes, "| resolución:", res, flush=True)
    cuerpo = {"prompt": prompt + LOOK, "image": cuadro_916(ini), "last_image": cuadro_916(fin),
              "duration": 5, "aspect_ratio": "9:16", "resolution": res, "generate_audio": False}
    req = urllib.request.Request(g.WAVESPEED + "/" + MODELO, data=json.dumps(cuerpo).encode(), headers=g.CAB)
    try:
        id_ = json.loads(urllib.request.urlopen(req, timeout=600).read())["data"]["id"]
    except urllib.error.HTTPError as e:
        raise SystemExit("rechazado: %s %s" % (e.code, e.read().decode()[:400]))
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
        open(salida, "wb").write(r.read())
    despues = saldo()
    costo = round(float(antes) - float(despues), 4) if isinstance(antes, (int, float)) else None
    print("saldo despues:", despues, "| COSTO REAL:", costo, "| a 1080p fueron 2.50", flush=True)
    rec = json.load(open(os.path.join(AQUI, "recibo_seedance_res.json"))) if os.path.exists(
        os.path.join(AQUI, "recibo_seedance_res.json")) else {}
    rec["%s_%s" % (nombre, res)] = {"id": id_, "resolucion": res, "costo_real": costo, "url": url}
    json.dump(rec, open(os.path.join(AQUI, "recibo_seedance_res.json"), "w"), indent=1)
    print("listo ->", salida, flush=True)
