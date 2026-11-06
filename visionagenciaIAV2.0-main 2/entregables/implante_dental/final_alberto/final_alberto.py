"""Video del implante de Alberto (Veneers Dental), versión final del 19 sep.

Carlos: «quítale los silencios para que sea más fluido, mejores subtítulos estilo RPN con la misma tipografía
que él usa, la pone en medio, y pon logo de Veneers Dental, su WhatsApp y la dirección». Alberto: «a lo
último puede terminar solo agenda tu valoración».

1. Sin silencios: cada hueco de la voz de más de GAP_MIN se deja en GAP_OUT. El video de ese hueco NO se corta:
   se acelera para caber, así la animación no brinca. La voz termina en «agenda tu valoración» (se quita
   «en Veneers Dental», que ya lo dice el logo).
2. Subtítulos RPN: frases cortas en minúsculas con su puntuación, dorado #F9C813, sin caja. Tipografía:
   Crimson Pro Italic, la de Google Fonts más parecida a la de RPN (comparación en fuentes/comparacion_fuentes.png;
   la suya parece comercial). Centrados a media pantalla, como pidió Carlos.
3. Cierre de CIERRE_S s: fondo FONDO_CIERRE_GPT.png (GPT Image 2, mismo estilo de la animación) con el logo
   en blanco, «agenda tu valoración», la dirección y el WhatsApp.
Uso: python3 final_alberto.py [prueba]"""
import json, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = Path(__file__).resolve().parent
DENTAL = AQUI.parent
BASE = DENTAL / "kling_7_tramos_20260917" / "IMPLANTE_ALBERTO_FINAL_35s.mp4"
PALABRAS = DENTAL / "voz_adictiva_20260917" / "voz_palabras_agenda.json"
FONDO = AQUI / "FONDO_CIERRE_GPT.png"
LOGO = AQUI / "logo_alberto_whatsapp.jpg"
SIN_SILENCIOS = AQUI / "_sin_silencios.mp4"
SALIDA = AQUI / "IMPLANTE_ALBERTO_FINAL_v2_1080.mp4"
WHATSAPP = AQUI / "IMPLANTE_ALBERTO_FINAL_v2_WHATSAPP.mp4"

W, H, FPS = 1080, 1920, 30
GAP_MIN, GAP_OUT = 0.45, 0.22
CIERRE_S, FUNDIDO = 3.6, 0.4
ORO = (249, 200, 19)
Y_SUBS = 0.50
TAM = 70
F_ITAL = str(AQUI / "fuentes" / "CrimsonPro-Italic.ttf")
DIRECCION = ["Av. Álvaro Obregón 695", "frente a Farmacia Especializada"]
WHATS = "WhatsApp  631 308 8021"

FRASES = [
    ("¿te falta un diente?", 4), ("esto es lo que pasa", 5), ("por dentro.", 2),
    ("empieza con anestesia.", 3), ("no duele,", 2), ("ni lo vas a sentir.", 5),
    ("y aquí está", 3), ("lo que nadie te enseña.", 5),
    ("el dentista abre un espacio", 5), ("en el hueso,", 3), ("justo donde estaba tu raíz.", 5),
    ("ahí entra un tornillo", 4), ("de titanio.", 2),
    ("esa va a ser", 4), ("tu nueva raíz.", 3),
    ("con los meses", 3), ("tu hueso crece alrededor", 4), ("y lo deja firme.", 4),
    ("encima, una corona", 3), ("igual a tus dientes.", 4),
    ("agenda tu valoración.", 3),
]

voz = json.load(open(PALABRAS))
FIN_VOZ = next(i for i, w in enumerate(voz) if w["w"].lower().startswith("valoraci")) + 1
voz = voz[:FIN_VOZ]
assert sum(n for _, n in FRASES) == len(voz), "no cuadran las palabras"


# ---------------------------------------------------------------- 1. tramos sin silencios
def tramos():
    """[(ini, fin, dur_salida, es_voz)] sobre el video original."""
    out, ini = [], 0.0
    for a, b in zip(voz, voz[1:]):
        hueco = b["start"] - a["end"]
        if hueco > GAP_MIN:
            corte = a["end"] + 0.10
            out.append((ini, corte, corte - ini, True))
            vuelta = b["start"] - 0.08
            out.append((corte, vuelta, GAP_OUT, False))
            ini = vuelta
    fin = voz[-1]["end"] + 0.02
    out.append((ini, fin, fin - ini, True))
    out.append((fin, fin + 0.30, 0.30, False))       # respiro final con la sonrisa, sin «en Veneers Dental»
    return out


TRAMOS = tramos()


def mapea(t):
    """Tiempo del video original → tiempo del video sin silencios."""
    acum = 0.0
    for a, b, d, _ in TRAMOS:
        if t <= b:
            return acum + (t - a) * d / (b - a) if t >= a else acum
        acum += d
    return acum


DUR_VIDEO = sum(d for *_, d, _ in TRAMOS)


def quita_silencios():
    fil, n = [], len(TRAMOS)
    n_voz = sum(1 for t in TRAMOS if t[3])
    # cada entrada de ffmpeg se usa una sola vez: se reparte con split/asplit
    fil.append(f"[0:v]split={n}" + "".join(f"[sv{k}]" for k in range(n)))
    fil.append(f"[0:a]aresample=48000,aformat=channel_layouts=stereo,asplit={n_voz}" +
               "".join(f"[sa{k}]" for k in range(n_voz)))
    j = 0
    for k, (a, b, d, es_voz) in enumerate(TRAMOS):
        f = d / (b - a)
        fil.append(f"[sv{k}]trim={a:.3f}:{b:.3f},setpts=(PTS-STARTPTS)*{f:.5f},fps={FPS}[v{k}]")
        if es_voz:
            fade = ",afade=t=out:st=%.3f:d=0.06" % (d - 0.06) if k == n - 2 else ""
            fil.append(f"[sa{j}]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS{fade}[a{k}]"); j += 1
        else:
            fil.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{d:.3f}[a{k}]")
    fil.append("".join(f"[v{k}][a{k}]" for k in range(n)) + f"concat=n={n}:v=1:a=1[v][a]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(BASE), "-filter_complex", ";".join(fil),
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "14", "-preset", "fast",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(SIN_SILENCIOS)],
                   check=True)


# ---------------------------------------------------------------- 2. subtítulos RPN
def fuente(tam, variacion=b"Medium Italic"):
    f = ImageFont.truetype(F_ITAL, tam)
    try:
        f.set_variation_by_name(variacion)
    except Exception:
        pass
    return f


bloques, i = [], 0
for texto, n in FRASES:
    tramo = voz[i:i + n]; i += n
    t, f = TAM, fuente(TAM)
    while f.getlength(texto) > W * 0.84 and t > 34:
        t -= 2; f = fuente(t)
    bloques.append(dict(texto=texto, f=f, ini=mapea(tramo[0]["start"]), fin_voz=mapea(tramo[-1]["end"])))
for k, b in enumerate(bloques):
    sig = bloques[k + 1]["ini"] if k + 1 < len(bloques) else DUR_VIDEO
    b["fin"] = min(b["fin_voz"] + 0.40, sig - 0.05)


def suave(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def capa_subs(t):
    alfa = np.zeros((H, W), np.float32)
    for b in bloques:
        if t < b["ini"] - 0.001 or t > b["fin"] + 0.14:
            continue
        op = suave((t - b["ini"]) / (4 / FPS)) * (1 - suave((t - b["fin"]) / (4 / FPS)))
        if op <= 0:
            continue
        img = Image.new("L", (W, 220), 0)
        ImageDraw.Draw(img).text((W / 2, 110), b["texto"], font=b["f"], fill=255, anchor="mm")
        y0 = int(H * Y_SUBS) - 110
        np.maximum(alfa[y0:y0 + 220], np.asarray(img, np.float32) / 255.0 * op, out=alfa[y0:y0 + 220])
    return alfa


def pinta(fondo, alfa, color=ORO, sombra=0.82, radio=26):
    if not alfa.any():
        return fondo
    f32 = fondo.astype(np.float32)
    s = np.asarray(Image.fromarray((alfa * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(radio)),
                   np.float32) / 255.0
    f32 *= (1 - sombra * np.clip(s * 1.7, 0, 1))[:, :, None]
    f32 += (np.array(color, np.float32)[None, None, :] - f32) * alfa[:, :, None]
    return np.clip(f32 + 0.5, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- 3. cierre
def logo_blanco(ancho):
    """El logo viene negro sobre franja blanca (captura del celular): se recorta la franja y se vuelve
    blanco con transparencia, para que viva sobre el fondo oscuro."""
    im = Image.open(LOGO).convert("L")
    a = np.asarray(im, np.float32)
    filas = np.where(a.mean(axis=1) > 200)[0]
    franja = a[filas.min() + 4:filas.max() - 4]
    alfa = np.clip((255 - franja) * 1.25, 0, 255).astype(np.uint8)
    cols = np.where(alfa.max(axis=0) > 60)[0]; fil = np.where(alfa.max(axis=1) > 60)[0]
    alfa = alfa[fil.min():fil.max() + 1, cols.min():cols.max() + 1]
    img = Image.fromarray(alfa)
    return img.resize((ancho, int(img.height * ancho / img.width)), Image.LANCZOS)


def fondo_cierre():
    im = Image.open(FONDO).convert("RGB")
    esc = max(W / im.width, H / im.height) * 1.08          # margen para el zoom lento
    return im.resize((int(im.width * esc), int(im.height * esc)), Image.LANCZOS)


FONDO_IMG = fondo_cierre()
LOGO_A = logo_blanco(860)
F_CTA, F_DIR, F_WA = fuente(96, b"SemiBold Italic"), fuente(52), fuente(60, b"SemiBold Italic")


def texto_alfa(texto, f, y):
    img = Image.new("L", (W, H), 0)
    ImageDraw.Draw(img).text((W / 2, y), texto, font=f, fill=255, anchor="mm")
    return np.asarray(img, np.float32) / 255.0


CAPAS_CIERRE = [  # (alfa, color, entra en s, sombra)
    (None, (255, 255, 255), 0.15, 0.5),                     # logo
    (texto_alfa("agenda tu valoración", F_CTA, H * 0.405), ORO, 0.55, 0.6),
    (texto_alfa(DIRECCION[0], F_DIR, H * 0.475), (240, 240, 240), 0.85, 0.6),
    (texto_alfa(DIRECCION[1], F_DIR, H * 0.508), (240, 240, 240), 0.95, 0.6),
    (texto_alfa(WHATS, F_WA, H * 0.575), ORO, 1.2, 0.6),
]
_l = np.zeros((H, W), np.float32)
_y = int(H * 0.23 - LOGO_A.height / 2); _x = (W - LOGO_A.width) // 2
_l[_y:_y + LOGO_A.height, _x:_x + LOGO_A.width] = np.asarray(LOGO_A, np.float32) / 255.0
CAPAS_CIERRE[0] = (_l, *CAPAS_CIERRE[0][1:])


def cuadro_cierre(t):
    z = 1.0 + 0.05 * (t / CIERRE_S)                          # acercamiento lento
    fw, fh = FONDO_IMG.size
    cw, ch = int(fw / (1.08 * z) * 1.0), int(fh / (1.08 * z))
    x0, y0 = (fw - cw) // 2, (fh - ch) // 2
    base = np.asarray(FONDO_IMG.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.BILINEAR))
    for alfa, color, entra, sombra in CAPAS_CIERRE:
        op = suave((t - entra) / 0.35)
        if op > 0:
            base = pinta(base, alfa * op, color, sombra, 24)
    return base


# ---------------------------------------------------------------- armado
def leer_cuadros(ruta):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(ruta), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         stdout=subprocess.PIPE)
    while True:
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3:
            break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3)
    p.wait()


if __name__ == "__main__":
    if not (len(sys.argv) > 1 and sys.argv[1] == "prueba" and SIN_SILENCIOS.exists()):
        quita_silencios()
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                                         "csv=p=0", str(SIN_SILENCIOS)]).decode())
    print("sin silencios: %.2f s (antes 35.00) · %d tramos" % (dur, len(TRAMOS)), flush=True)
    if len(sys.argv) > 1 and sys.argv[1] == "prueba":
        def uno(t):
            return np.frombuffer(subprocess.check_output(
                ["ffmpeg", "-v", "error", "-ss", "%.3f" % t, "-i", str(SIN_SILENCIOS), "-frames:v", "1",
                 "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]), np.uint8).reshape(H, W, 3)
        tiras = [pinta(uno(t), capa_subs(t)) for t in (0.6, 3.2, 8.0, 12.5, 18.0, 23.0)]
        tiras += [cuadro_cierre(t) for t in (0.3, 2.5)]
        Image.fromarray(np.hstack([np.asarray(Image.fromarray(x).resize((270, 480))) for x in tiras])).save(
            AQUI / "PRUEBA_FINAL.jpg", quality=90)
        raise SystemExit("-> PRUEBA_FINAL.jpg")
    n_video = int(round(dur * FPS))
    n_cierre = int(round(CIERRE_S * FPS))
    n_fund = int(round(FUNDIDO * FPS))
    total = n_video + n_cierre - n_fund
    esc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-i", str(SIN_SILENCIOS), "-filter_complex",
                            f"[1:a]apad=whole_dur={total / FPS:.3f}[a]", "-map", "0:v", "-map", "[a]",
                            "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p",
                            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(SALIDA)],
                           stdin=subprocess.PIPE)
    ultimo = None
    for n, c in enumerate(leer_cuadros(SIN_SILENCIOS)):
        t = n / FPS
        cuadro = pinta(c, capa_subs(t))
        if n >= n_video - n_fund:                           # fundido al cierre
            k = (n - (n_video - n_fund)) / n_fund
            cuadro = (cuadro * (1 - k) + cuadro_cierre(k * FUNDIDO) * k).astype(np.uint8)
        esc.stdin.write(cuadro.tobytes()); ultimo = n
    for m in range(n_fund, n_cierre):
        esc.stdin.write(cuadro_cierre(m / FPS).tobytes())
    esc.stdin.close(); esc.wait()
    assert esc.returncode == 0
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(SALIDA), "-vf", "scale=720:1280", "-c:v", "libx264",
                    "-crf", "24", "-preset", "medium", "-profile:v", "baseline", "-level", "3.1", "-pix_fmt",
                    "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(WHATSAPP)], check=True)
    print("listo", SALIDA, "%.2f s" % (total / FPS))
