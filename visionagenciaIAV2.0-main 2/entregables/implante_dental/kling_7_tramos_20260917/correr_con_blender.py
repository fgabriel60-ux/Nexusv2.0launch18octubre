"""Los tramos con el video de Blender como referencia de movimiento (kling-video-o3-pro/reference-to-video).

Carlos (17 sep): «¿no le has estado dando a Kling una parte del video de Blender?». Los primeros
tramos iban solo con cuadro inicial y final, así que el modelo inventaba el movimiento de en medio
(en el 5 bajó un segundo tornillo desde arriba). Con el Blender de guía eso se arregla de raíz.

Descartados en el camino:
  - kling-v2.6-pro/motion-control: exige detectar una persona de medio cuerpo. Rechaza el corte
    anatómico ("No complete upper body detected"). No cobró.
  - seedance-2.0-fast: buenísimo para el despegue, pero $2.50 reales (5x su lista).

Costo real medido de este modelo: $0.84 por tramo (lista $0.56, o sea 1.5x).
No tiene negative_prompt, así que las prohibiciones van dentro del prompt positivo.

El video de Blender pide lados entre 700 y 3840 px: el render es 432x768, por eso se escala a
720x1280. También se tapa el rótulo "MESES DE CICATRIZACIÓN" que trae abajo.

Reanudable: cada tramo guarda su job en estado_blender.json.
Uso: python3 correr_con_blender.py 6        (un tramo)
     python3 correr_con_blender.py 1 2 4 6 7
"""
import base64, json, os, subprocess, sys, time, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
DENTAL = os.path.dirname(AQUI)
sys.path.insert(0, os.path.join(DENTAL, "kling_transicion"))
sys.path.insert(0, os.path.join(DENTAL, "..", "catania_mariano_montaje_20260914"))
import gancho_kling_habla_giro as g
from kling_transicion import cuadro_916

MODELO = "kwaivgi/kling-video-o3-pro/reference-to-video"
GENJ = os.path.join(DENTAL, "genjutsu_20260915", "IMAGENES")
BLENDER = os.path.join(DENTAL, "genjutsu_20260915", "MONTAJE", "RECORRIDO_BLENDER_COMPLETO_35s.mp4")
CLIPS = os.path.join(AQUI, "CLIPS_BLENDER"); os.makedirs(CLIPS, exist_ok=True)
ESTADO = os.path.join(AQUI, "estado_blender.json")

LOOK = (" Near-black background with deep teal and warm orange bokeh, soft teal rim light, shallow depth of field, "
        "premium 3D medical visualisation, calm and elegant.")
PROHIBIDO = (" Anatomically clean: no blood, no wound, no gore, no molars, no lower jaw, no extra or duplicated "
             "teeth, no second implant, nothing entering the frame from above, no instrument falling from the sky. "
             "One smooth continuous shot, no cuts, no camera shake, no text, labels or watermark. Ignore the flat "
             "grey clay look of the reference video and render with the look of the reference images.")
SECCION = ("Front cross-section of the UPPER jaw: porous cream bone on top with a glowing warm orange cut edge, "
           "translucent glowing pink gum across the middle, exactly four natural upper teeth hanging DOWN with "
           "their long roots going UP into the bone, and one gap in the centre. ")

# tramo: (de_s, a_s, nombre, referencias, acción)
TRAMOS = {
    1: (0, 5, "T1_rostro_a_closeup", ["01_rostro_hueco.png", "02_closeup_espacio.png"],
        "A woman smiles with a slightly embarrassed closed-lip smile showing ONE missing upper front tooth. The "
        "camera pushes in slowly and steadily from her portrait to an extreme macro of her mouth, until the single "
        "gap is centred and sharp. Her identity, skin, lips, nose and hair never change."),
    2: (5, 10, "T2_anestesia", ["02_closeup_espacio.png", "03_anestesia.png"],
        "Extreme macro of the same woman's mouth with the single missing upper front tooth. A slim realistic dental "
        "anaesthetic syringe enters, its fine needle gently touches the pink gum right at the gap, rests there a "
        "moment, then withdraws and leaves the frame. Her lips, skin and face stay completely intact: nothing "
        "peels, splits or opens."),
    4: (15, 20, "T4_canal_y_tornillo", ["05_preparacion_fresa.png", "06_implante_entra.png"],
        SECCION + "The steel drill finishes cutting the narrow channel in the bone above the gap, then withdraws "
        "downward out of the frame. A satin grey titanium threaded implant then rises from BELOW through the gap "
        "and starts screwing UPWARD into that channel, its threaded tip pointing up into the bone."),
    6: (25, 30, "T6_pilar_y_corona", ["07_integracion.png", "08_pilar_corona.png", "09_corona_colocada.png"],
        SECCION + "A satin grey titanium implant is already fully seated inside the bone above the gap. The bone "
        "glows softly while fine new bone grows tightly into its threads. A short polished titanium abutment is "
        "then placed on the implant at the gum line, and ONE natural ivory crown rises from BELOW and seats onto "
        "it, filling the gap and leaving a tight row of exactly FIVE upper front teeth with no gap, the new crown "
        "identical in colour and shape to its neighbours. The four neighbouring teeth and the gum never move."),
    7: (30, 35, "T7_morph_sonrisa", ["09_corona_colocada.png", "01_rostro_hueco.png", "10_sonrisa_feliz.png"],
        "The cross-section of the upper jaw now has a complete row of five upper front teeth with no gap. The "
        "camera eases back and the woman's skin and lips flow back over the anatomy until her face is whole again "
        "in the original framing. Her expression then changes smoothly from the shy closed smile into a radiant, "
        "genuinely happy open smile: cheeks lifted, warm eyes, showing the complete row of upper teeth with no "
        "gap. Same woman, same identity, same framing and lighting throughout. Hold on her happy smile at the end."),
}


def estado():
    return json.load(open(ESTADO)) if os.path.exists(ESTADO) else {}


def guarda(k, v):
    e = estado(); e[k] = v; json.dump(e, open(ESTADO, "w"), indent=1)


def saldo():
    try:
        req = urllib.request.Request(g.WAVESPEED + "/balance", headers=g.CAB)
        return json.loads(urllib.request.urlopen(req, timeout=60).read()).get("data", {}).get("balance")
    except Exception as e:
        return "sin dato (%s)" % e


def recorta_blender(n):
    """Saca el pedazo del render de Blender, tapa el rótulo y lo sube a 720x1280 (mínimo 700 px)."""
    a, b = TRAMOS[n][0], TRAMOS[n][1]
    dst = os.path.join(AQUI, "MOVIMIENTO_BLENDER_T%d.mp4" % n)
    if not os.path.exists(dst):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-t", str(b - a), "-i", BLENDER,
                        "-vf", "drawbox=x=0:y=630:w=432:h=138:color=black@1:t=fill,scale=720:1280:flags=lanczos",
                        "-r", "30", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                        "-pix_fmt", "yuv420p", "-an", dst], check=True)
        print("  recortado", os.path.basename(dst), flush=True)
    return dst


def corre(n):
    a, b, nombre, refs, accion = TRAMOS[n]
    salida = os.path.join(CLIPS, nombre + ".mp4")
    e = estado()
    if e.get("tramo_%d" % n, {}).get("url") and os.path.exists(salida):
        print("tramo %d ya estaba listo" % n, flush=True); return salida
    video = recorta_blender(n)
    cuerpo = {
        "prompt": ("Use the reference video ONLY as the exact motion, timing, framing and camera reference. "
                   + accion + LOOK + PROHIBIDO),
        "video": "data:video/mp4;base64," + base64.b64encode(open(video, "rb").read()).decode(),
        "images": [cuadro_916(os.path.join(GENJ, r)) for r in refs],
        "duration": b - a, "aspect_ratio": "9:16", "sound": False, "keep_original_sound": False,
    }
    job = e.get("tramo_%d" % n, {}).get("id")
    if not job:
        req = urllib.request.Request(g.WAVESPEED + "/" + MODELO, data=json.dumps(cuerpo).encode(), headers=g.CAB)
        try:
            job = json.loads(urllib.request.urlopen(req, timeout=600).read())["data"]["id"]
        except urllib.error.HTTPError as ex:
            raise SystemExit("tramo %d rechazado: %s %s" % (n, ex.code, ex.read().decode()[:400]))
    guarda("tramo_%d" % n, {"id": job, "model": MODELO, "refs": refs})
    print("  JOB", job, flush=True)
    url = None
    for _ in range(300):
        time.sleep(5)
        q = urllib.request.Request("%s/predictions/%s/result" % (g.WAVESPEED, job), headers=g.CAB)
        d = (json.loads(urllib.request.urlopen(q, timeout=60).read()) or {}).get("data") or {}
        if d.get("status") == "completed":
            url = d["outputs"][0]; break
        if d.get("status") == "failed":
            raise SystemExit("tramo %d FALLÓ: %s" % (n, d.get("error")))
    assert url, "timeout en el tramo %d" % n
    with urllib.request.urlopen(url, timeout=600) as r:
        open(salida, "wb").write(r.read())
    guarda("tramo_%d" % n, {"id": job, "model": MODELO, "refs": refs, "url": url})
    print("  listo ->", os.path.basename(salida), flush=True)
    return salida


if __name__ == "__main__":
    pedidos = [int(x) for x in sys.argv[1:] if x.isdigit() and int(x) in TRAMOS] or sorted(TRAMOS)
    antes = saldo(); print("saldo antes:", antes, flush=True)
    for n in pedidos:
        print("--- tramo %d (%d-%d s) ---" % (n, TRAMOS[n][0], TRAMOS[n][1]), flush=True)
        corre(n)
    despues = saldo()
    costo = round(float(antes) - float(despues), 4) if isinstance(antes, (int, float)) else None
    print("saldo despues:", despues, "| costo de esta corrida:", costo, flush=True)
    guarda("saldo", {"antes": antes, "despues": despues, "tramos": pedidos, "costo": costo})
