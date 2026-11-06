"""Dos estilos nuevos, sacados de lo que SÍ hacen los dentistas virales (Apify, 18 sep).

Lo que se vio en los 6 videos bajados (1.3M a 16.1M de reproducciones):
  - Los DOS más vistos (@smile_doc 16.1M y @dentaltreatmentweb 2.7M) y @doctorleonperu (1.7M)
    casi no llevan texto, o ninguno. Nadie usa letras gigantes.
  - Ninguno usa serif. Todos sans.
  - El texto va ARRIBA o al centro-alto. Ninguno lo pone abajo, porque ahí Instagram y TikTok
    montan la descripción y los botones.
  - El único con texto grande (@odontoseguro, 1.5M) usa cajas de color pastel con contorno
    grueso y emoji, estilo calcomanía — no tipografía fina.

  D · DISCRETO    Montserrat SemiBold, dos líneas chicas arriba, blanco con sombra suave.
                  Es lo que hacen los de más reproducciones.
  E · CALCOMANÍA  Caja de color con contorno negro grueso, como @odontoseguro. Sólo para el
                  gancho y la llamada a la acción; en medio va el estilo D.
"""
import subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = Path(__file__).resolve().parent
BASE = AQUI.parent / "kling_7_tramos_20260917" / "IMPLANTE_ALBERTO_FINAL_35s.mp4"
W, H, FPS = 1080, 1920, 30
MONT = str(AQUI / "fuentes" / "Montserrat.ttf")
# Zona segura de reel: abajo del 78 % lo tapan la descripción y los botones
Y_TEXTO = 0.215

MOMENTOS = [
    (2.10, ["esto es lo que pasa", "POR DENTRO"], (255, 214, 92)),
    (6.95, ["no duele:", "ni lo vas a sentir"], (140, 230, 220)),
    (16.40, ["el dentista abre un espacio", "en el hueso"], (255, 214, 92)),
    (34.15, ["agenda tu valoración", "en VENEERS DENTAL"], (255, 168, 90)),
]


def fuente(tam, peso):
    f = ImageFont.truetype(MONT, tam); f.set_variation_by_name(peso); return f


def cuadro(t):
    n = int(round(t * FPS))
    crudo = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(BASE), "-vf",
                                     "select=eq(n\\,%d)" % n, "-frames:v", "1",
                                     "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    return Image.fromarray(np.frombuffer(crudo, np.uint8).reshape(H, W, 3).copy())


def discreto(im, lineas, acento):
    f1 = fuente(52, "SemiBold")
    f2 = fuente(60, "Bold")
    fs = [f1, f2]
    altos = [int(f.size * 1.32) for f in fs]
    y = H * Y_TEXTO - sum(altos) / 2
    # sombra suave debajo, como la que usan las autocaption de TikTok
    sombra = Image.new("L", im.size, 0); ds = ImageDraw.Draw(sombra)
    for linea, f, alto in zip(lineas, fs, altos):
        ds.text((W / 2, y), linea, font=f, fill=255, anchor="ma")
        y += alto
    arr = np.asarray(im, np.float32) * (1 - 0.55 * (np.asarray(
        sombra.filter(ImageFilter.GaussianBlur(20)), np.float32) / 255.0))[:, :, None]
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    y = H * Y_TEXTO - sum(altos) / 2
    for i, (linea, f, alto) in enumerate(zip(lineas, fs, altos)):
        d.text((W / 2, y), linea, font=f, fill=(255, 255, 255) if i == 0 else acento, anchor="ma")
        y += alto
    return im


def calcomania(im, lineas, acento):
    d = ImageDraw.Draw(im)
    f = fuente(62, "ExtraBold")
    altos = [int(f.size * 1.5)] * len(lineas)
    y = H * Y_TEXTO - sum(altos) / 2
    capa = Image.new("RGBA", im.size, (0, 0, 0, 0)); dc = ImageDraw.Draw(capa)
    for linea, alto in zip(lineas, altos):
        anc = f.getlength(linea)
        x0 = (W - anc) / 2 - 30
        dc.rounded_rectangle([x0, y, x0 + anc + 60, y + alto - 12], radius=20,
                             fill=acento + (244,), outline=(18, 14, 12, 255), width=7)
        y += alto
    im = Image.alpha_composite(im.convert("RGBA"), capa).convert("RGB")
    d = ImageDraw.Draw(im)
    y = H * Y_TEXTO - sum(altos) / 2
    for linea, alto in zip(lineas, altos):
        d.text((W / 2, y + alto * 0.20), linea, font=f, fill=(22, 18, 16), anchor="ma")
        y += alto
    return im


if __name__ == "__main__":
    filas = []
    for nombre, fn in [("D · DISCRETO  (como los de mas vistas)", discreto),
                       ("E · CALCOMANIA  (como @odontoseguro 1.5M)", calcomania)]:
        fila = []
        for t, lineas, acento in MOMENTOS:
            im = fn(cuadro(t).convert("RGB"), lineas, acento).resize((330, 587), Image.LANCZOS)
            d = ImageDraw.Draw(im)
            d.rectangle([0, 0, 330, 38], fill=(0, 0, 0))
            d.text((9, 6), nombre, font=fuente(21, "Bold"), fill=(255, 210, 90))
            fila.append(np.asarray(im))
        filas.append(np.hstack(fila))
    Image.fromarray(np.vstack(filas)).save(AQUI / "MUESTRAS_V2.jpg", quality=93)
    print("-> MUESTRAS_V2.jpg")
