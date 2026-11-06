"""Los 2 cuadros llave que faltan para la reja de 5 s (Kling, 7 tramos).

Mismo método y mismo estilo que genjutsu_20260915/generar_frames.py (GPT Image 2 edit,
hoja de proceso aprobada como referencia de look). Solo faltan los segundos 10 y 15:
el resto de la reja ya sale de los cuadros 01, 02, 06, 07, 09 y 10.
Uso: python3 generar_cuadros_reja5s.py  [R10] [R15]
"""
import json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, "/workspaces/visionagenciaIAV2.0/entregables/implante_dental/gpt_transicion")
import gpt_transicion as v1

AQUI = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(AQUI, "CUADROS"); os.makedirs(IMG, exist_ok=True)
DENTAL_ENT = "/workspaces/visionagenciaIAV2.0/entregables/implante_dental"
GENJ = os.path.join(DENTAL_ENT, "genjutsu_20260915", "IMAGENES")
HOJA = os.path.join(v1.DENTAL, "hoja_proceso_implante")
HOJA_COMPLETA = os.path.join(HOJA, "hoja_proceso_implante.png")
CLOSEUP = os.path.join(DENTAL_ENT, "gpt_estilo_hoja", "GPT2_CUADRO_150_CLOSEUP.png")
SECCION = os.path.join(HOJA, "f5_cicatrizacion.png")
FASE = lambda n: os.path.join(DENTAL_ENT, "capturas_animacion", "FASE_%04d.png" % n)

# Copiados tal cual de generar_frames.py para que el look no se mueva
ESTILO = ("LOOK MUST MATCH THE APPROVED STYLE SHEET PANELS EXACTLY: near-black background with deep teal and warm "
          "orange out-of-focus bokeh; teeth bright glossy white enamel with sharp specular highlights; gums translucent "
          "glossy pink with a warm orange-red subsurface glow and a luminous warm outline; bone cream-ivory with fine "
          "porous spongy interior and a glowing warm orange edge where it is cut; titanium satin grey with fine threads; "
          "cinematic 3D medical render, soft teal rim light, shallow depth of field, anatomically clean, not gore. "
          "Vertical 9:16. No text, no labels, no arrows, no watermark.")
SECCION_TXT = ("Anatomy, framed as in the rough 3D reference image (front view of the section): a clean cross-section of "
               "the UPPER jaw: porous cream bone with a glowing edge on top, translucent glowing pink scalloped gum "
               "across the middle, and exactly "
               "FOUR natural upper teeth with their long roots inside the bone, two on the left and two on the right, "
               "tight together, with ONE gap exactly one tooth wide in the centre. No face, no lips, no skin, no lower "
               "teeth, no extra or floating teeth. ")

CUADROS = {
    # Segundo 10 (cuadro 300): la anestesia ya se puso y la jeringa sale. La cara TODAVÍA entera:
    # el despegue es a los 12.09 s, dentro del tramo 3, y lo tiene que hacer Kling.
    "R10_anestesia_sale": ([os.path.join(GENJ, "03_anestesia.png"), CLOSEUP, os.path.join(HOJA, "f2_anestesia.png")],
        "Same macro framing, same woman, same lighting as image 1: her mouth with the single missing upper front "
        "tooth. The anaesthetic syringe has just been withdrawn and is leaving the frame at the edge, only its "
        "needle tip still visible, moving away; it is NOT touching the gum any more. A tiny fresh glisten on the "
        "pink gum right at the gap where the needle was, no blood, no swelling, no mark. Her lips, skin and face "
        "are COMPLETELY INTACT and normal: the face has NOT started to peel, split, curl or open in any way, there "
        "is no sticker edge, no seam and no cross-section visible anywhere. Calm and clinical. Image 2 is the "
        "approved close-up of her mouth for identity and skin; image 3 is the approved style-sheet panel for the "
        "anaesthesia step. Keep her teeth and the single gap exactly as in image 1. " + ESTILO),

    # Segundo 15 (cuadro 450): la fresa ya está DENTRO del hueso, a medio canal.
    "R15_fresa_dentro": ([os.path.join(GENJ, "05_preparacion_fresa.png"), SECCION, FASE(420),
                          os.path.join(HOJA, "f3_perforacion.png")],
        SECCION_TXT + "Step: the bone preparation is already under way. The thin polished steel dental drill has "
        "risen through the gap and its tip is now clearly INSIDE the bone above the gap, about halfway along the "
        "channel it is cutting, with the narrow clean channel already opened behind it and a faint dusting of fine "
        "pale bone particles around the entry. The drill is deeper into the bone than in image 1. No implant yet, "
        "no screw, no crown, no blood. Image 1 is the approved previous step and the exact look to match, image 2 "
        "the approved anatomy, image 3 a rough 3D reference of the framing, image 4 the style-sheet panel for "
        "drilling. " + ESTILO),
}


def saldo():
    try:
        req = urllib.request.Request(v1.WAVESPEED + "/balance", headers=v1.CAB)
        return json.loads(urllib.request.urlopen(req, timeout=60).read()).get("data", {}).get("balance")
    except Exception as e:
        return "sin dato (%s)" % e


def generar(nombre):
    refs, prompt = CUADROS[nombre]
    refs = refs + [HOJA_COMPLETA]
    prompt += (" RULE: the pink gum is ALWAYS ABOVE the teeth: teeth hang down from the gum line, the gum never "
               "appears below or in front of the teeth.")
    prompt += (" The LAST reference image is the approved style sheet: copy its teeth, gums, bone, lighting and "
               "background look, but not its layout, text or tooth arrangement.")
    destino = os.path.join(IMG, nombre + ".png")
    cuerpo = {"prompt": prompt, "images": [v1.uri(r) for r in refs], "aspect_ratio": "9:16", "output_format": "png"}
    req = urllib.request.Request(v1.WAVESPEED + "/" + v1.MODELO, data=json.dumps(cuerpo).encode(), headers=v1.CAB)
    with urllib.request.urlopen(req, timeout=300) as r:
        id_ = json.loads(r.read())["data"]["id"]
    print(nombre, "job", id_, flush=True)
    for _ in range(300):
        time.sleep(5)
        q = urllib.request.Request("%s/predictions/%s/result" % (v1.WAVESPEED, id_), headers=v1.CAB)
        d = (json.loads(urllib.request.urlopen(q, timeout=60).read()) or {}).get("data") or {}
        if d.get("status") == "completed":
            with urllib.request.urlopen(d["outputs"][0], timeout=300) as r:
                open(destino, "wb").write(r.read())
            print(nombre, "listo ->", destino, flush=True)
            return nombre, "ok"
        if d.get("status") == "failed":
            print(nombre, "FALLÓ", d.get("error"), flush=True)
            return nombre, "fallo: %s" % d.get("error")
    return nombre, "timeout"


if __name__ == "__main__":
    for refs, _ in CUADROS.values():
        for r in refs:
            assert os.path.exists(r), "falta referencia: " + r
    pedidos = [k for k in CUADROS if not sys.argv[1:] or k.split("_")[0] in sys.argv[1:]]
    antes = saldo(); print("saldo antes:", antes, flush=True)
    with ThreadPoolExecutor(2) as ex:
        res = dict(ex.map(generar, pedidos))
    despues = saldo(); print("saldo despues:", despues, flush=True)
    json.dump({"cuadros": res, "saldo": {"antes": antes, "despues": despues}},
              open(os.path.join(AQUI, "resultado_cuadros.json"), "w"), indent=1)
    print(res)
