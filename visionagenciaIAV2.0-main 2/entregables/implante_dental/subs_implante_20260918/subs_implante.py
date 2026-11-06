"""Subtítulos del video de Alberto, con el estilo que ya se armó para Catania el 14 sep.

Carlos (18 sep): «ponle subtítulos geniales».

Se reusa tal cual el método de catania_mariano_subs_20260914/subs_difference_sfx.py:
  - Playfair Display. Conector chico en cursiva / palabra protagonista grande en negrita /
    remate en cursiva. La jerarquía cambia por frase.
  - Cada palabra entra con su voz: opacidad 0→100, escala 94→100 % y una subida leve,
    en 5 cuadros.
  - Modo DIFFERENCE con empuje de contraste: la letra invierte el fondo y además se le
    fuerza una diferencia mínima de brillo píxel por píxel. Así se lee igual sobre el fondo
    casi negro, sobre el hueso claro y sobre los dientes blancos, sin caja ni borde negro.

Los tiempos salen de voz_palabras_agenda.json (faster-whisper con word_timestamps sobre
FINAL_AGENDA_35s.wav, 79 palabras). No se estiman: cada palabra entra en su milisegundo.

Colocación: el video tiene la acción SIEMPRE al centro (la boca en macro, o el corte del
maxilar con los instrumentos entrando por abajo). Por eso el texto va arriba o abajo según
el tramo, nunca encima de la anatomía. La fracción de altura va por grupo en Y.

Uso: python3 subs_implante.py prueba    (tira de cuadros para revisar, sin render completo)
     python3 subs_implante.py           (video completo)
"""
import json, os, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = Path(__file__).resolve().parent
DENTAL = AQUI.parent
BASE = DENTAL / "kling_7_tramos_20260917" / "IMPLANTE_ALBERTO_FINAL_35s.mp4"
PALABRAS = DENTAL / "voz_adictiva_20260917" / "voz_palabras_agenda.json"
SALIDA = AQUI / "IMPLANTE_ALBERTO_SUBS_1080.mp4"
WHATSAPP = AQUI / "IMPLANTE_ALBERTO_SUBS_WHATSAPP.mp4"

W, H, FPS = 1080, 1920, 30
COLOR = np.array([255, 255, 255], np.float32)
CONTRASTE = 118          # diferencia mínima de brillo entre letra y fondo (0-255)
SOMBRA = 0.62            # cuánto se oscurece el fondo bajo las letras
SOMBRA_PX = 16           # radio del desenfoque de esa sombra
F_BOLD = str(AQUI / "fuentes" / "PlayfairDisplay[wght].ttf")
F_ITAL = str(AQUI / "fuentes" / "PlayfairDisplay-Italic[wght].ttf")
ESTILOS = {
    "c":  (F_ITAL, b"SemiBold Italic", 74),    # conector
    "M":  (F_BOLD, b"Black", 150),             # protagonista
    "Mi": (F_ITAL, b"Black Italic", 142),      # protagonista en cursiva
    "r":  (F_ITAL, b"SemiBold Italic", 100),   # remate
}

# (líneas del grupo, fracción de altura donde se centra)
# Cada línea: (texto en pantalla, estilo, cuántas palabras de la VOZ cubre).
# La suma de esas cuentas tiene que dar las 79 palabras del audio, en orden.
GRUPOS = [
    # 0-5 s · su cara y la cámara entrando al macro → texto abajo, sobre el cuello y el fondo
    ([("¿Te falta", "c", 2), ("UN DIENTE?", "M", 2)], 0.84),
    ([("esto es lo que pasa", "c", 5), ("POR DENTRO", "Mi", 2)], 0.84),
    # 5-10 s · macro de la boca al centro → texto abajo, sobre la barbilla
    ([("empieza con", "c", 2), ("ANESTESIA", "M", 1)], 0.84),
    ([("NO DUELE", "Mi", 2), ("ni lo vas a sentir", "r", 5)], 0.84),
    # 10-15 s · el despegue → texto abajo; arriba está la sección que se revela
    ([("y aquí está", "c", 3), ("LO QUE NADIE", "M", 3), ("te enseña", "r", 2)], 0.84),
    # 15-30 s · corte del maxilar; los instrumentos entran por ABAJO → texto arriba
    ([("el dentista abre un", "c", 4), ("ESPACIO EN EL HUESO", "M", 4)], 0.13),
    ([("justo donde estaba", "c", 3), ("TU RAÍZ", "Mi", 2)], 0.13),
    ([("ahí entra un", "c", 3), ("TORNILLO DE TITANIO", "M", 3)], 0.13),
    ([("esa va a ser tu", "c", 5), ("NUEVA RAÍZ", "Mi", 2)], 0.13),
    ([("con los meses", "c", 3), ("TU HUESO CRECE", "M", 3)], 0.13),
    ([("alrededor y lo deja", "c", 4), ("FIRME", "Mi", 1)], 0.13),
    # 30-35 s · la corona y luego su cara sonriendo → abajo, para no taparle los ojos
    ([("encima, una", "c", 2), ("CORONA", "M", 1), ("igual a tus dientes", "r", 4)], 0.84),
    ([("agenda tu", "c", 2), ("VALORACIÓN", "M", 1), ("en Veneers Dental", "Mi", 3)], 0.84),
]

voz = json.load(open(PALABRAS))
total = sum(n for g, _ in GRUPOS for _, _, n in g)
assert total == len(voz), "las cuentas no cuadran: %d en pantalla contra %d de la voz" % (total, len(voz))

fuentes = {}
def fuente(estilo, escala=1.0):
    ruta, var, tam = ESTILOS[estilo]
    clave = (estilo, int(tam * escala))
    if clave not in fuentes:
        f = ImageFont.truetype(ruta, clave[1]); f.set_variation_by_name(var); fuentes[clave] = f
    return fuentes[clave]

# ---------- armar los grupos con su tiempo ----------
grupos, i = [], 0
for lineas_def, frac_y in GRUPOS:
    lineas = []
    for texto, estilo, n in lineas_def:
        tramo = voz[i:i + n]; i += n
        palabras = texto.split()
        escala = 1.0
        while fuente(estilo, escala).getlength(texto) > W * 0.88:
            escala *= 0.96
        f = fuente(estilo, escala)
        tiempos = [w["start"] for w in tramo] if len(palabras) == n else [tramo[0]["start"]] * len(palabras)
        lineas.append((palabras, f, tiempos, estilo))
    grupos.append(dict(lineas=lineas, inicio=min(t for l in lineas for t in l[2]),
                       fin_voz=voz[i - 1]["end"], y=frac_y))

for k, g in enumerate(grupos):
    siguiente = grupos[k + 1]["inicio"] if k + 1 < len(grupos) else 99
    # se queda un poco después de la voz, pero siempre sale antes de que entre el siguiente
    g["fin"] = min(g["fin_voz"] + 0.75, siguiente - 0.10)
grupos[-1]["fin"] = 35.0    # la llamada a la acción se queda hasta el final

# ---------- maquetar palabra por palabra ----------
piezas = []
for g in grupos:
    medidas = []
    for palabras, f, tiempos, estilo in g["lineas"]:
        asc, desc = f.getmetrics()
        medidas.append(int((asc + desc) * (0.78 if estilo in ("M", "Mi") else 0.9)))
    y = H * g["y"] - sum(medidas) / 2
    for (palabras, f, tiempos, estilo), alto in zip(g["lineas"], medidas):
        espacio = f.getlength(" ")
        ancho = sum(f.getlength(p) for p in palabras) + espacio * (len(palabras) - 1)
        x = (W - ancho) / 2
        for p, t in zip(palabras, tiempos):
            l, top, r, b = f.getbbox(p)
            img = Image.new("L", (int(r - l) + 8, int(b - top) + 8), 0)
            ImageDraw.Draw(img).text((4 - l, 4 - top), p, font=f, fill=255)
            asc, _ = f.getmetrics()
            piezas.append(dict(img=img, x=x + l - 4,
                               y=y + (top - asc * 0.18) - 4 - (alto * 0.08 if estilo in ("M", "Mi") else 0),
                               t=t, fin=g["fin"]))
            x += f.getlength(p) + espacio
        y += alto

def suave(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)

def capa_texto(t):
    alfa = np.zeros((H, W), np.float32)
    for p in piezas:
        if t < p["t"] - 0.001 or t > p["fin"] + 0.17:
            continue
        entra = suave((t - p["t"]) / (5 / FPS))
        sale = 1 - suave((t - p["fin"]) / (4 / FPS))
        op = entra * sale
        if op <= 0:
            continue
        esc = 0.94 + 0.06 * entra
        img = p["img"]
        if esc < 0.999:
            img = img.resize((max(1, int(img.width * esc)), max(1, int(img.height * esc))),
                             Image.Resampling.BILINEAR)
        cx = p["x"] + p["img"].width / 2
        cy = p["y"] + p["img"].height / 2 + 18 * (1 - entra)
        x0, y0 = int(round(cx - img.width / 2)), int(round(cy - img.height / 2))
        a = np.asarray(img, np.float32) / 255.0 * op
        xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + img.width), min(H, y0 + img.height)
        if xa >= xb or ya >= yb:
            continue
        zona = alfa[ya:yb, xa:xb]
        np.maximum(zona, a[ya - y0:yb - y0, xa - x0:xb - x0], out=zona)
    return alfa

coef = np.array([0.299, 0.587, 0.114], np.float32)

def componer(fondo, t):
    alfa = capa_texto(t)
    if not alfa.any():
        return fondo
    f32 = fondo.astype(np.float32)
    # Sombra: se oscurece el fondo bajo un desenfoque de las letras. Sin esto el difference
    # desaparece sobre tonos medios (los labios, la lámina de piel), donde el fondo y su
    # inverso tienen brillo parecido.
    sombra = np.asarray(Image.fromarray((alfa * 255).astype(np.uint8))
                        .filter(ImageFilter.GaussianBlur(SOMBRA_PX)), np.float32) / 255.0
    f32 = f32 * (1 - SOMBRA * np.clip(sombra * 1.6, 0, 1))[:, :, None]
    dif = np.abs(f32 - COLOR)
    l_fondo, l_dif = f32 @ coef, dif @ coef
    meta = np.where(l_fondo >= 128, np.minimum(l_dif, l_fondo - CONTRASTE),
                    np.maximum(l_dif, l_fondo + CONTRASTE))
    letras = dif + (np.clip(meta, 0, 255) - l_dif)[:, :, None]
    salida = f32 + (letras - f32) * alfa[:, :, None]
    return np.clip(salida + 0.5, 0, 255).astype(np.uint8)


def cuadro(n):
    return np.frombuffer(subprocess.check_output(
        ["ffmpeg", "-v", "error", "-i", str(BASE), "-vf", "select=eq(n\\,%d)" % n,
         "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]), np.uint8).reshape(H, W, 3)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "prueba":
        tiras = []
        for t in [0.9, 2.5, 6.2, 7.9, 11.5, 16.6, 21.5, 26.6, 31.5, 34.6]:
            c = componer(cuadro(int(round(t * FPS))), t)
            tiras.append(np.asarray(Image.fromarray(c).resize((216, 384), Image.LANCZOS)))
        Image.fromarray(np.hstack(tiras)).save(AQUI / "PRUEBA_SUBS.jpg", quality=92)
        print("-> PRUEBA_SUBS.jpg")
        raise SystemExit

    total_n = int(round(35.0 * FPS))
    lee = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(BASE), "-f", "rawvideo",
                            "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    esc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-", "-i", str(BASE),
                            "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "17",
                            "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "copy",
                            str(SALIDA)], stdin=subprocess.PIPE)
    for n in range(total_n):
        crudo = lee.stdout.read(W * H * 3)
        if len(crudo) < W * H * 3:
            break
        esc.stdin.write(componer(np.frombuffer(crudo, np.uint8).reshape(H, W, 3), n / FPS).tobytes())
        if n % 60 == 0:
            print("  %d/%d" % (n, total_n), flush=True)
    esc.stdin.close(); esc.wait(); lee.wait()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(SALIDA), "-vf", "scale=720:1280",
                    "-c:v", "libx264", "-crf", "24", "-preset", "medium", "-profile:v", "baseline",
                    "-level", "3.1", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
                    "-movflags", "+faststart", str(WHATSAPP)], check=True)
    print("listo ->", SALIDA.name, "y", WHATSAPP.name)
