"""Cuadros clave GPT Image 2 para rehacer el video del implante en Genjutsu (Motion Transfer) con mejor estética.
Carlos (15 sep): «crea los frames necesarios en gpt image 2 para que genjutsu pueda rehacer el video pero con mejor
estética, pero al final la mujer feliz con todos los dientes para morph de la cara a sonriente».

Un cuadro por fase de la voz (voz_fish/tiempos.json). El 01 y el 10 comparten encuadre exacto para el morph final.
Uso: python3 generar_frames.py            (todos, en paralelo)
     python3 generar_frames.py 03 10      (solo esos)"""
import json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "/workspaces/visionagenciaIAV2.0/entregables/implante_dental/gpt_transicion")
import gpt_transicion as v1

AQUI = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(AQUI, "IMAGENES"); os.makedirs(IMG, exist_ok=True)
DENTAL_ENT = "/workspaces/visionagenciaIAV2.0/entregables/implante_dental"
HOJA = os.path.join(v1.DENTAL, "hoja_proceso_implante")
ROSTRO = os.path.join(DENTAL_ENT, "gpt_estilo_hoja", "GPT2_CUADRO_1_ROSTRO.png")
CLOSEUP = os.path.join(DENTAL_ENT, "gpt_estilo_hoja", "GPT2_CUADRO_150_CLOSEUP.png")
# Carlos: «los dientes, encías y fondo deben verse como en la imagen genial que le mandé a Alberto» = la hoja del proceso
SECCION = os.path.join(HOJA, "f5_cicatrizacion.png")
HOJA_COMPLETA = os.path.join(HOJA, "hoja_proceso_implante.png")
# Anatomía del MAXILAR SUPERIOR ya aprobada: la hoja trae muelas de abajo y en 04/09 GPT copió esa mandíbula
ARRIBA = os.path.join(DENTAL_ENT, "gpt_transicion", "GPT2_SOLO_DIENTES_ENCIAS_v4.png")
SUPERIOR = ("UPPER jaw ONLY: the bone is ABOVE, the roots go UP into it and the front teeth hang DOWN from the gum, "
            "exactly like image of the approved upper section. No molars, no lower jaw, no teeth pointing up. ")
FASE = lambda n: os.path.join(DENTAL_ENT, "capturas_animacion", "FASE_%04d.png" % n)
PREV = lambda n: os.path.join(DENTAL_ENT, "mejora_sticker", "preview_v3_cpu", "frame_%04d.png" % n)

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
    "01_rostro_hueco": ([ROSTRO, FASE(1)],
        "Image 1 is the approved portrait of the woman. Recreate it as a more polished hero frame: exactly the same "
        "woman, same head position, framing, expression and hair, same SINGLE missing upper front tooth gap clearly "
        "visible, slightly embarrassed smile. Improve lighting and skin quality to a premium commercial finish. "
        "Image 2 is only a rough 3D reference of the shot. " + ESTILO),
    "02_closeup_espacio": ([CLOSEUP, ROSTRO, FASE(150)],
        "Close macro of the same woman's mouth and nose (image 1 is the approved close-up, image 2 her portrait): "
        "the single missing upper front tooth gap centred and sharp, lips parted, natural teeth on both sides. "
        "Image 3 is a rough 3D reference of the framing. " + ESTILO),
    "03_anestesia": ([PREV(265), CLOSEUP, os.path.join(HOJA, "f2_anestesia.png")],
        "Same macro framing as image 1: the woman's mouth with the single missing upper front tooth. A slim, "
        "realistic dental anaesthetic syringe with a fine needle gently touches the pink gum right at the gap, "
        "calm and clinical, no blood. Image 2 is the approved close-up of her mouth for identity and skin; image 3 "
        "is the approved style-sheet panel for the anaesthesia step. Keep her teeth and gap exactly as in image 1. " + ESTILO),
    "04_sticker_revela": ([PREV(374), CLOSEUP, ARRIBA],
        "Transition frame, same framing as image 1: the photographic close-up of her mouth (image 2) peels away "
        "from the right side like a glossy sticker curling toward the left, showing its soft white back, and behind "
        "it the dental cross-section of image 3 is revealed: porous ivory bone, pink gum, natural teeth and the gap. "
        "Elegant, seamless, the curl has a soft shadow and a thin luminous edge. The revealed anatomy is the "
        "same upper front teeth and gap that were under her lip, at the same height. " + SUPERIOR + ESTILO),
    "05_preparacion_fresa": ([SECCION, FASE(420), os.path.join(HOJA, "f3_perforacion.png")],
        SECCION_TXT + "Step: bone preparation. A thin polished steel dental drill with a precise tip rises from below "
        "through the gap and gently enters the bone exactly above the gap, where the missing root was, leaving a "
        "clean narrow channel; no implant yet, no blood. Image 1 is the approved anatomy and look, image 2 a rough "
        "3D reference of the drill position, image 3 the style-sheet panel for drilling. " + ESTILO),
    "06_implante_entra": ([SECCION, FASE(620), os.path.join(HOJA, "f4_implante.png")],
        SECCION_TXT + "Step: implant placement. A satin titanium threaded implant screw is halfway into the prepared "
        "channel in the bone above the gap, screwing upward along its vertical axis with its threaded tip pointing "
        "UP into the bone and its flat top still below the gum. Image 1 is the approved look, image 2 a rough 3D "
        "reference of the position, image 3 the style-sheet panel for this step. " + ESTILO),
    "07_integracion": ([SECCION, FASE(740), os.path.join(HOJA, "f5_cicatrizacion.png")],
        SECCION_TXT + "Step: osseointegration. The titanium implant is fully seated inside the bone above the gap "
        "with a small round silver healing cap at the gum line, no crown yet. Around the implant threads the bone "
        "glows softly with fine new bone growing tightly into the threads. Match image 1 closely; image 2 is a rough "
        "3D reference, image 3 the style-sheet panel for healing. " + ESTILO),
    "08_pilar_corona": ([SECCION, FASE(950), os.path.join(HOJA, "f6_corona.png")],
        SECCION_TXT + "Step: abutment and crown. The implant is fully integrated in the bone; a short polished "
        "titanium abutment sits on top of it at the gum line, and one natural ivory crown matching the neighbouring "
        "teeth is rising from below, almost touching the abutment, perfectly aligned with the gap. Image 1 is the "
        "approved look, image 2 a rough 3D reference, image 3 the style-sheet panel for the crown. " + ESTILO),
    "09_corona_colocada": ([ARRIBA, FASE(950)],
        "Anatomy: the same front view of the UPPER jaw section as image 1 (bone on top, gum across the middle, teeth "
        "hanging down), but now COMPLETE: FIVE natural-looking upper front teeth in a perfect tight row, the centre "
        "one is the new ivory crown seated on its abutment with the titanium implant going UP into the bone, "
        "indistinguishable in colour and shape from its neighbours; the other four teeth with their natural roots "
        "going up. No gap. No face. Image 2 is a rough 3D reference of the framing. " + SUPERIOR + ESTILO),
    "10_sonrisa_feliz": ([ROSTRO, os.path.join(DENTAL_ENT, "mejora_sticker", "CHICA_SONRISA_FINAL.png")],
        "Image 1 is the woman at the start of the video. Create the final frame for a face morph: EXACTLY the same "
        "camera framing, crop, head position, angle, hair, clothing, background and lighting as image 1 so the two "
        "frames can be morphed, but now she is RADIANTLY, VISIBLY HAPPY: a big wide joyful laugh-smile, cheeks lifted, "
        "happy eyes squinting slightly with smile lines, eyebrows raised and relaxed with NO worry or tension at all, "
        "glowing with confidence and relief, showing a COMPLETE, beautiful row of upper teeth with NO gap and a little "
        "healthy pink gum visible ABOVE the teeth, the replaced front tooth identical in colour and shape to the others "
        "(image 2 shows her restored teeth). Same woman, same identity, natural skin, not plastic. " + ESTILO),
}


def generar(nombre):
    refs, prompt = CUADROS[nombre]
    refs = refs + [HOJA_COMPLETA]
    # Carlos: «las encías siempre deben estar arriba»
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
            print(nombre, "listo", flush=True); return nombre, "ok"
        if d.get("status") == "failed":
            print(nombre, "FALLÓ", d.get("error"), flush=True); return nombre, "fallo"
    return nombre, "timeout"


if __name__ == "__main__":
    pedidos = [k for k in CUADROS if not sys.argv[1:] or k[:2] in sys.argv[1:]]
    with ThreadPoolExecutor(5) as ex:
        res = dict(ex.map(generar, pedidos))
    json.dump(res, open(os.path.join(AQUI, "resultado_frames.json"), "w"), indent=1)
    print(res)
