"""Tres estilos de subtítulo sobre los MISMOS cuadros, para escoger de vista.

Carlos (18 sep): «están muy feos esos subtítulos». El de Playfair venía del video de Catania
(bienes raíces, serif con cursivas) y no le queda a un explicativo médico para reel.

  A · REEL      Montserrat Black, VERSALES, apiladas. La palabra que se está diciendo se
                enciende en el naranja de la escena; las demás quedan en blanco apagado.
                Borde oscuro fino. Es el estilo de TikTok/Reels, el que más engancha.
  B · CAJA      Montserrat ExtraBold sobre una caja redondeada oscura semitransparente, una
                sola línea. Lo más legible de los tres sobre cualquier fondo. Estilo de
                subtítulo de noticia o explicativo serio.
  C · LIMPIO    Roboto Condensed, versales delgadas y espaciadas, blanco con sombra suave,
                una línea discreta abajo. El más elegante y el que menos tapa el video.

Uso: python3 muestras_estilos.py
"""
import json, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = Path(__file__).resolve().parent
BASE = AQUI.parent / "kling_7_tramos_20260917" / "IMPLANTE_ALBERTO_FINAL_35s.mp4"
W, H, FPS = 1080, 1920, 30
MONT = str(AQUI / "fuentes" / "Montserrat.ttf")
ROBO = str(AQUI / "fuentes" / "RobotoCondensed.ttf")
NARANJA = (255, 138, 42)
TURQUESA = (64, 224, 208)

# (segundo, líneas de la frase, índice de la palabra que se está diciendo)
MOMENTOS = [
    (2.10, ["ESTO ES LO QUE PASA", "POR DENTRO"], (1, 0)),
    (6.95, ["NO DUELE", "NI LO VAS A SENTIR"], (1, 0)),
    (16.40, ["EL DENTISTA ABRE UN", "ESPACIO EN EL HUESO"], (1, 1)),
    (34.15, ["AGENDA TU VALORACIÓN", "EN VENEERS DENTAL"], (1, 1)),
]


def fuente(ruta, tam, peso):
    f = ImageFont.truetype(ruta, tam); f.set_variation_by_name(peso); return f


def cuadro(t):
    n = int(round(t * FPS))
    crudo = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(BASE), "-vf",
                                     "select=eq(n\\,%d)" % n, "-frames:v", "1",
                                     "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    return Image.fromarray(np.frombuffer(crudo, np.uint8).reshape(H, W, 3).copy())


def ajusta(ruta, peso, texto, ancho, tam0):
    tam = tam0
    while fuente(ruta, tam, peso).getlength(texto) > ancho and tam > 20:
        tam -= 2
    return fuente(ruta, tam, peso)


def estilo_reel(im, lineas, activa):
    d = ImageDraw.Draw(im)
    fs = [ajusta(MONT, "Black", l, W * 0.86, 104) for l in lineas]
    altos = [int(f.size * 1.16) for f in fs]
    y = H * 0.80 - sum(altos) / 2
    for li, (linea, f, alto) in enumerate(zip(lineas, fs, altos)):
        pals = linea.split()
        esp = f.getlength(" ")
        x = (W - (sum(f.getlength(p) for p in pals) + esp * (len(pals) - 1))) / 2
        for pi, p in enumerate(pals):
            viva = (li, pi) == (activa[0], activa[1]) or (li == activa[0] and activa[1] == -1)
            col = NARANJA if viva else (238, 238, 238)
            d.text((x, y), p, font=f, fill=col, stroke_width=7, stroke_fill=(10, 8, 6))
            d.text((x, y), p, font=f, fill=col)
            x += f.getlength(p) + esp
        y += alto
    return im


def estilo_caja(im, lineas, activa):
    texto = " ".join(lineas)
    f = ajusta(MONT, "ExtraBold", texto, W * 0.82, 62)
    d = ImageDraw.Draw(im)
    anc = f.getlength(texto); alto = int(f.size * 1.5)
    x0 = (W - anc) / 2 - 34; y0 = H * 0.82
    capa = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(capa).rounded_rectangle([x0, y0, x0 + anc + 68, y0 + alto], radius=22,
                                           fill=(8, 12, 16, 214))
    im = Image.alpha_composite(im.convert("RGBA"), capa).convert("RGB")
    d = ImageDraw.Draw(im)
    pals = texto.split(); esp = f.getlength(" "); x = x0 + 34
    idx = sum(len(l.split()) for l in lineas[:activa[0]]) + activa[1]
    for pi, p in enumerate(pals):
        d.text((x, y0 + alto * 0.24), p, font=f, fill=TURQUESA if pi == idx else (255, 255, 255))
        x += f.getlength(p) + esp
    return im


def estilo_limpio(im, lineas, activa):
    texto = " ".join(lineas)
    f = ajusta(ROBO, "Medium", " ".join(texto), W * 0.80, 58)
    d = ImageDraw.Draw(im)
    # espaciado entre letras, a mano
    letras = list(texto); tr = 5
    anc = sum(f.getlength(c) for c in letras) + tr * (len(letras) - 1)
    x = (W - anc) / 2; y = H * 0.855
    sombra = Image.new("L", im.size, 0)
    ds = ImageDraw.Draw(sombra)
    xx = x
    for c in letras:
        ds.text((xx, y), c, font=f, fill=255); xx += f.getlength(c) + tr
    sombra = sombra.filter(ImageFilter.GaussianBlur(18))
    arr = np.asarray(im, np.float32) * (1 - 0.6 * (np.asarray(sombra, np.float32) / 255.0))[:, :, None]
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    for c in letras:
        d.text((x, y), c, font=f, fill=(255, 255, 255)); x += f.getlength(c) + tr
    return im


if __name__ == "__main__":
    filas = []
    for nombre, fn in [("A · REEL", estilo_reel), ("B · CAJA", estilo_caja), ("C · LIMPIO", estilo_limpio)]:
        fila = []
        for t, lineas, activa in MOMENTOS:
            im = fn(cuadro(t).convert("RGB"), lineas, activa)
            im = im.resize((330, 587), Image.LANCZOS)
            d = ImageDraw.Draw(im)
            f = fuente(MONT, 26, "Bold")
            d.rectangle([0, 0, 330, 40], fill=(0, 0, 0))
            d.text((10, 6), nombre, font=f, fill=(255, 210, 90))
            fila.append(np.asarray(im))
        filas.append(np.hstack(fila))
    Image.fromarray(np.vstack(filas)).save(AQUI / "MUESTRAS_ESTILOS.jpg", quality=93)
    print("-> MUESTRAS_ESTILOS.jpg")
