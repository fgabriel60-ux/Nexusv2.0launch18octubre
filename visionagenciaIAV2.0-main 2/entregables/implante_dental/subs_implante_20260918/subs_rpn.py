"""Subtítulos al estilo de @rpn (Roberto P. Nickson), medidos de sus propios videos.

Carlos (18 sep): «mira el creador rpn, me gusta sus ediciones».

Se bajaron 5 reels suyos con Apify (de 0.3M a 3.4M de vistas) y se midió el subtítulo
pixel por pixel sobre los cuadros, no a ojo:

  tipografía   serif en CURSIVA, minúsculas, con su puntuación (punto y coma incluidos).
               Se lee como transcripción, no como rótulo.
  color        #F9C813 — dorado ámbar, no blanco. Medido sobre el núcleo de las letras.
  tamaño       la caja de texto mide 37 px de alto sobre 1920, o sea 1.9 % de la altura.
               Es CHICO: cabe una frase corta por vez.
  posición     centrado, con el centro vertical en 0.677 de la altura.
  sin caja     ni borde ni contorno. Sólo el color.

Lo que yo tenía estaba mal en casi todo menos la familia tipográfica: letras enormes,
blancas, en VERSALES, con jerarquía de tres niveles y abajo en 0.84.

Aquí se le agrega una sombra muy suave que él no necesita —sus fondos van oscuros y
degradados— porque este video tiene dientes y hueso muy claros donde el dorado se perdería.

Uso: python3 subs_rpn.py prueba    (tira de cuadros)
     python3 subs_rpn.py           (video completo)
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = Path(__file__).resolve().parent
DENTAL = AQUI.parent
BASE = DENTAL / "kling_7_tramos_20260917" / "IMPLANTE_ALBERTO_FINAL_35s.mp4"
PALABRAS = DENTAL / "voz_adictiva_20260917" / "voz_palabras_agenda.json"
SALIDA = AQUI / "IMPLANTE_ALBERTO_SUBS_RPN_1080.mp4"
WHATSAPP = AQUI / "IMPLANTE_ALBERTO_SUBS_RPN_WHATSAPP.mp4"

W, H, FPS = 1080, 1920, 30
ORO = (249, 200, 19)          # #F9C813, medido en sus videos
Y = 0.677                     # medido en sus videos
TAM = 62                      # da ~37 px de caja, como el suyo
SOMBRA, SOMBRA_PX = 0.55, 22
FUENTE = str(AQUI / "fuentes" / "PlayfairDisplay-Italic[wght].ttf")

# Frases cortas, minúsculas y con puntuación, como las suyas.
# El número es cuántas palabras de la voz cubre cada una; la suma tiene que dar 79.
FRASES = [
    ("¿te falta un diente?", 4), ("esto es lo que pasa", 5), ("por dentro.", 2),
    ("empieza con anestesia.", 3), ("no duele,", 2), ("ni lo vas a sentir.", 5),
    ("y aquí está", 3), ("lo que nadie te enseña.", 5),
    ("el dentista abre un espacio", 5), ("en el hueso,", 3), ("justo donde estaba tu raíz.", 5),
    ("ahí entra un tornillo", 4), ("de titanio.", 2),
    ("esa va a ser", 4), ("tu nueva raíz.", 3),
    ("con los meses", 3), ("tu hueso crece alrededor", 4), ("y lo deja firme.", 4),
    ("encima, una corona", 3), ("igual a tus dientes.", 4),
    ("agenda tu valoración", 3), ("en Veneers Dental.", 3),
]

voz = json.load(open(PALABRAS))
assert sum(n for _, n in FRASES) == len(voz), "no cuadran las palabras"

f_base = ImageFont.truetype(FUENTE, TAM); f_base.set_variation_by_name("Medium Italic")

bloques, i = [], 0
for texto, n in FRASES:
    tramo = voz[i:i + n]; i += n
    f = f_base
    if f.getlength(texto) > W * 0.82:
        t = TAM
        while True:
            t -= 2
            f = ImageFont.truetype(FUENTE, t); f.set_variation_by_name("Medium Italic")
            if f.getlength(texto) <= W * 0.82 or t < 30:
                break
    bloques.append(dict(texto=texto, f=f, ini=tramo[0]["start"], fin_voz=tramo[-1]["end"]))

for k, b in enumerate(bloques):
    sig = bloques[k + 1]["ini"] if k + 1 < len(bloques) else 99
    b["fin"] = min(b["fin_voz"] + 0.45, sig - 0.06)
bloques[-1]["fin"] = 35.0


def suave(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def capa(t):
    alfa = np.zeros((H, W), np.float32)
    for b in bloques:
        if t < b["ini"] - 0.001 or t > b["fin"] + 0.14:
            continue
        op = suave((t - b["ini"]) / (4 / FPS)) * (1 - suave((t - b["fin"]) / (4 / FPS)))
        if op <= 0:
            continue
        img = Image.new("L", (W, 200), 0)
        ImageDraw.Draw(img).text((W / 2, 100), b["texto"], font=b["f"], fill=255, anchor="mm")
        y0 = int(H * Y) - 100
        a = np.asarray(img, np.float32) / 255.0 * op
        ya, yb = max(0, y0), min(H, y0 + 200)
        np.maximum(alfa[ya:yb], a[ya - y0:yb - y0], out=alfa[ya:yb])
    return alfa


def componer(fondo, t):
    alfa = capa(t)
    if not alfa.any():
        return fondo
    f32 = fondo.astype(np.float32)
    s = np.asarray(Image.fromarray((alfa * 255).astype(np.uint8))
                   .filter(ImageFilter.GaussianBlur(SOMBRA_PX)), np.float32) / 255.0
    f32 = f32 * (1 - SOMBRA * np.clip(s * 1.7, 0, 1))[:, :, None]
    col = np.array(ORO, np.float32)
    salida = f32 + (col[None, None, :] - f32) * alfa[:, :, None]
    return np.clip(salida + 0.5, 0, 255).astype(np.uint8)


def cuadro(n):
    return np.frombuffer(subprocess.check_output(
        ["ffmpeg", "-v", "error", "-i", str(BASE), "-vf", "select=eq(n\\,%d)" % n,
         "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]), np.uint8).reshape(H, W, 3)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "prueba":
        tiras = [np.asarray(Image.fromarray(componer(cuadro(int(round(t * FPS))), t))
                            .resize((300, 533), Image.LANCZOS))
                 for t in [1.0, 2.4, 6.0, 11.0, 16.5, 21.0, 26.5, 34.4]]
        Image.fromarray(np.hstack(tiras)).save(AQUI / "PRUEBA_SUBS_RPN.jpg", quality=93)
        print("-> PRUEBA_SUBS_RPN.jpg")
        raise SystemExit
    total = int(round(35.0 * FPS))
    lee = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(BASE), "-f", "rawvideo",
                            "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    esc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-", "-i", str(BASE),
                            "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "17",
                            "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "copy",
                            str(SALIDA)], stdin=subprocess.PIPE)
    for n in range(total):
        crudo = lee.stdout.read(W * H * 3)
        if len(crudo) < W * H * 3:
            break
        esc.stdin.write(componer(np.frombuffer(crudo, np.uint8).reshape(H, W, 3), n / FPS).tobytes())
        if n % 120 == 0:
            print("  %d/%d" % (n, total), flush=True)
    esc.stdin.close(); esc.wait(); lee.wait()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(SALIDA), "-vf", "scale=720:1280",
                    "-c:v", "libx264", "-crf", "24", "-preset", "medium", "-profile:v", "baseline",
                    "-level", "3.1", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
                    "-movflags", "+faststart", str(WHATSAPP)], check=True)
    print("listo ->", SALIDA.name)
