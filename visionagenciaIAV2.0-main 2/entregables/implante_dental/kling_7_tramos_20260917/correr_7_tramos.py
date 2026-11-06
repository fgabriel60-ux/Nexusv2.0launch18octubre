"""Video del implante de Alberto en Kling: 7 tramos de 5 s (Carlos, 17 sep).

Por qué por pedazos: en un solo tiro el modelo alucina (cambia la cara, mete muelas,
duplica dientes). Con 8 cuadros llave y tramos de 5 s, cada pedazo tiene principio y fin
fijos, y si uno sale mal se repite ese y no los 35 segundos.

La reja de cuadros llave y por qué son esos está en REJA_5S.md.
Reanudable: cada tramo guarda su job en estado_7_tramos.json; si se corta, sigue donde iba.

Uso:  python3 correr_7_tramos.py            (los 7 y el montaje)
      python3 correr_7_tramos.py 3          (solo el tramo 3)
      python3 correr_7_tramos.py montaje    (solo rearmar el video final)
"""
import json, os, subprocess, sys, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
DENTAL = os.path.dirname(AQUI)
sys.path.insert(0, os.path.join(DENTAL, "kling_transicion"))
sys.path.insert(0, os.path.join(DENTAL, "..", "catania_mariano_montaje_20260914"))
import gancho_kling_habla_giro as g
from kling_transicion import cuadro_916

GENJ = os.path.join(DENTAL, "genjutsu_20260915", "IMAGENES")
CUAD = os.path.join(AQUI, "CUADROS")
# Carlos eligió la versión 3 (AGENDA) el 17 sep: cierre "Agenda tu valoración en Veneers Dental"
VOZ = os.path.join(DENTAL, "voz_adictiva_20260917", "FINAL_AGENDA_35s.mp3")
CLIPS = os.path.join(AQUI, "CLIPS"); os.makedirs(CLIPS, exist_ok=True)
FINAL = os.path.join(AQUI, "IMPLANTE_ALBERTO_KLING_35s.mp4")
MODELO = "kwaivgi/kling-v2.6-pro/image-to-video"

# --- Los 8 cuadros llave de la reja de 5 s (ver REJA_5S.md)
LLAVE = {
    0:  os.path.join(GENJ, "01_rostro_hueco.png"),
    5:  os.path.join(GENJ, "02_closeup_espacio.png"),
    10: os.path.join(CUAD, "R10_anestesia_sale.png"),
    15: os.path.join(CUAD, "R15_fresa_dentro.png"),
    20: os.path.join(GENJ, "06_implante_entra.png"),
    25: os.path.join(GENJ, "07_integracion.png"),
    30: os.path.join(GENJ, "09_corona_colocada.png"),
    35: os.path.join(GENJ, "10_sonrisa_feliz.png"),
}

LOOK = (" Dark near-black background with deep teal and warm orange bokeh, soft teal rim light, shallow depth of "
        "field. Premium 3D medical visualisation, calm and elegant. One smooth continuous motion, ending exactly "
        "on the final image.")
NEG = ("blood, gore, wound, open flesh, extra teeth, duplicated teeth, teeth changing count, lower jaw, molars, "
       "deformed mouth, face identity change, melting skin, morphing, flicker, jump cut, crossfade dissolve, "
       "text, labels, watermark, camera shake, low quality")
# El tramo 7 SÍ necesita el morph de la cara, así que ahí no va en el negativo
NEG_MORPH = NEG.replace("melting skin, morphing, ", "melting skin, ")
# El tramo 6 falló dos veces: pieza nueva cayendo del cielo y el implante volteado
NEG_T6 = NEG + (", second implant, duplicated implant, two screws, object falling from above, part flying in, "
                "screw entering through the top of the bone, implant upside down, threaded tip pointing down, "
                "flat cap at the top inside the bone, crown detached from the abutment, floating crowns, "
                "flat cartoon shading, grey clay look, mint green outline, "
                "morph, morphing, shape shifting, objects turning into other objects, melting, stretching, "
                "growing out of nothing, fading in, materialising, warping")
# El tramo 3 falló por superposición: la sección apareció encima de la cara todavía puesta
NEG_T3 = NEG + (", cross-section overlapping the face, anatomy on top of skin, teeth over lips, "
                "double exposure, superimposed layers, dissolve, fade through, ghosting, transparency, "
                "x-ray effect, see-through skin, open mouth, jaw dropping, distorted lips, stretched mouth")

TRAMOS = {
    1: (0, 5, "T1_rostro_a_closeup",
        "The same woman keeps her slightly embarrassed closed-lip smile with ONE missing upper front tooth. The "
        "camera pushes in slowly and steadily from the portrait to an extreme macro of her mouth, until the single "
        "gap is centred and sharp, exactly as in the final image. She stays perfectly still and her identity, skin, "
        "lips, nose and hair never change." + LOOK, NEG),

    2: (5, 10, "T2_anestesia",
        "Extreme macro of the same woman's mouth with the single missing upper front tooth. A slim realistic dental "
        "anaesthetic syringe enters from the upper right, its fine needle gently touches the translucent pink gum "
        "right at the gap and rests there for a moment, calm and clinical. Then the syringe withdraws smoothly and "
        "leaves the frame, ending exactly as in the final image, with only a faint fresh glisten on the gum. Her "
        "lips, skin and face stay completely intact and still: nothing peels, splits or opens." + LOOK, NEG),

    # Reintento 17 sep: el primero metió la anatomía ENCIMA de la cara antes de que la piel
    # se quitara. Ahora el tiempo va repartido por escrito y la superposición va al negativo.
    3: (10, 15, "T3_sticker_y_fresa",
        "Extreme macro of the same woman's mouth with one missing upper front tooth; the syringe has just left. "
        "STRICT ORDER OF EVENTS, one after the other, never at the same time. "
        "FIRST, for the first two seconds: ONLY her skin moves. Her face and lips peel away from the right side "
        "like a glossy photographic sticker, the skin curling smoothly and continuously toward the left, showing "
        "its pale paper-like back and a thin warm glowing edge, with a soft shadow under the curl. Her mouth stays "
        "closed and relaxed while it peels; nothing else appears; NOTHING is visible through or on top of her skin. "
        "SECOND: only as the curling skin clears each part of the frame, the clean front cross-section of the UPPER "
        "jaw is uncovered BEHIND it, never over it: porous cream bone on top, glowing translucent pink gum, exactly "
        "four upper front teeth hanging down with their long roots going up, and the gap in the centre. The skin "
        "keeps curling until it has completely left the frame and only the cross-section remains. "
        "THIRD, in the last second only, once no skin is left: a thin polished steel dental drill rises from below "
        "through the gap and its tip enters the bone above the gap, ending exactly as in the final image. "
        "The drill does not exist before that last second." + LOOK, NEG_T3),

    4: (15, 20, "T4_canal_y_tornillo",
        "Front cross-section of the UPPER jaw: porous cream bone on top, pink gum, four teeth hanging down, one gap "
        "in the centre. The steel drill finishes cutting the narrow channel in the bone above the gap, then "
        "withdraws smoothly downward and out of the frame, leaving the clean prepared channel. Immediately a satin "
        "grey titanium threaded implant rises through the gap and starts screwing UPWARD into that channel, "
        "rotating on its vertical axis, its threaded tip pointing up into the bone, until it is halfway in, exactly "
        "as in the final image. The four teeth and the gum never move." + LOOK, NEG),

    5: (20, 25, "T5_tornillo_e_integracion",
        "Front cross-section of the UPPER jaw. The satin titanium threaded implant continues screwing UPWARD into "
        "the bone above the gap, rotating steadily on its vertical axis until it is fully seated inside the bone "
        "with its flat top at the gum line, where a small round silver healing cap appears. Then time passes: the "
        "bone glows softly and fine new bone grows tightly into the threads all around the implant, ending exactly "
        "as in the final image. The four neighbouring teeth and the gum never move." + LOOK, NEG),

    # Tercera escritura del 6. El pilar se QUITA: en esta vista el hueso está arriba y los dientes
    # cuelgan hacia abajo, así que "el pilar va encima del implante" lo leyeron los tres intentos
    # como "arriba en pantalla" y se lo pegaron al techo del hueso. La voz no menciona el pilar,
    # así que sacarlo no cuesta nada y le quita al modelo la pieza ambigua.
    # Carlos pidió además que nada haga morph: las piezas se mueven como sólidos.
    6: (25, 30, "T6_pilar_y_corona",
        "Front cross-section of the UPPER jaw with one satin grey titanium implant already fully seated inside the "
        "bone above the gap. ORIENTATION, unchanged for the whole shot: the implant's threaded body points UP into "
        "the bone and its flat platform is at the BOTTOM, level with the gum line. Nothing is ever added to the "
        "top of the implant and nothing appears above it inside the bone. "
        "First, the bone glows softly while fine new bone grows tightly into the implant threads. Then ONE natural "
        "ivory crown, already fully formed, travels UPWARD from below the frame as a rigid solid object and seats "
        "directly onto the flat platform of the implant, filling the gap and leaving a tight row of exactly FIVE "
        "upper front teeth with no gap, identical in colour and shape to its neighbours, exactly as in the final "
        "image. Every object keeps its shape at all times: the crown slides into place, it does not morph, grow, "
        "melt, stretch or fade in, and no shape turns into another shape. The implant, the four neighbouring "
        "teeth, their roots and the gum never move." + LOOK, NEG_T6),
    # Carlos confirmó (17 sep) que el morph de la CARA sí va: es el cierre del video y el cuadro 10
    # se generó con el mismo encuadre que el 01 justo para poder morphearse. Lo que se ordena aquí
    # es la secuencia, que es lo que destrabó el despegue del tramo 3: primero vuelve la piel,
    # DESPUÉS cambia la expresión. Nunca las dos cosas encimadas.
    7: (30, 35, "T7_morph_sonrisa",
        "Front cross-section of the UPPER jaw with a complete row of five upper front teeth and no gap. "
        "STRICT ORDER OF EVENTS, one after the other, never at the same time. "
        "FIRST, for about two seconds: the camera eases back and her skin and lips travel back over the anatomy "
        "from the left, the glossy sticker un-peeling and flattening back into place, the curl unrolling until it "
        "has covered everything. The anatomy is progressively hidden BEHIND the returning skin, never faded out "
        "underneath it, and her face is never transparent. She keeps her shy closed smile the whole time. "
        "SECOND, once her face is whole again in the original framing and no anatomy is left visible: her "
        "expression changes smoothly into a radiant, genuinely happy open smile, cheeks lifted, eyes warm and "
        "squinting slightly, lips opening to show the complete row of upper teeth with no gap, exactly as in the "
        "final image. Same woman, same identity, same skin, same hair, same framing and lighting throughout. "
        "Hold on her happy smile until the end." + LOOK, NEG_MORPH),
}


def saldo():
    try:
        req = urllib.request.Request(g.WAVESPEED + "/balance", headers=g.CAB)
        return json.loads(urllib.request.urlopen(req, timeout=60).read()).get("data", {}).get("balance")
    except Exception as e:
        return "sin dato (%s)" % e


def corre(n):
    ini, fin, nombre, prompt, neg = (TRAMOS[n][0], TRAMOS[n][1], TRAMOS[n][2], TRAMOS[n][3], TRAMOS[n][4])
    salida = os.path.join(CLIPS, "%s.mp4" % nombre)
    g.paso("tramo_%d" % n, MODELO,
           lambda: dict(image=cuadro_916(LLAVE[ini]), end_image=cuadro_916(LLAVE[fin]),
                        prompt=prompt, negative_prompt=neg, duration=5, sound=False),
           salida)
    return salida


def montaje():
    """Recorta cada tramo a 5.000 s exactos (Kling entrega 5.08) y pega la voz."""
    lista = os.path.join(AQUI, "_lista.txt")
    recortes = []
    for n in sorted(TRAMOS):
        src = os.path.join(CLIPS, "%s.mp4" % TRAMOS[n][2])
        assert os.path.exists(src), "falta el tramo %d: %s" % (n, src)
        dst = os.path.join(CLIPS, "_c%d.mp4" % n)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-t", "5.000",
                        "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-an", dst], check=True)
        recortes.append(dst)
    open(lista, "w").write("".join("file '%s'\n" % r for r in recortes))
    mudo = os.path.join(AQUI, "_mudo.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista,
                    "-c", "copy", mudo], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mudo, "-i", VOZ, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", FINAL], check=True)
    d = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                 "-of", "csv=p=0", FINAL]).decode().strip()
    print("FINAL ->", FINAL, d, "s", flush=True)


if __name__ == "__main__":
    for s, r in LLAVE.items():
        assert os.path.exists(r), "falta el cuadro llave de los %d s: %s" % (s, r)
    g.ESTADO = os.path.join(AQUI, "estado_7_tramos.json")
    args = sys.argv[1:]
    solo_montaje = args == ["montaje"]
    pedidos = [int(a) for a in args if a.isdigit()] or sorted(TRAMOS)

    if not solo_montaje:
        antes = saldo(); print("saldo antes:", antes, flush=True)
        for n in pedidos:
            print("--- tramo %d (%d-%d s) ---" % (n, TRAMOS[n][0], TRAMOS[n][1]), flush=True)
            corre(n)
        despues = saldo(); print("saldo despues:", despues, flush=True)
        g.guarda("saldo", {"antes": antes, "despues": despues})

    if solo_montaje or pedidos == sorted(TRAMOS):
        montaje()
