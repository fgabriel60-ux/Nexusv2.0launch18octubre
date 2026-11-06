"""v2: Jesús pidió cambiar el WhatsApp de la barra "PÍDALO HOY" a 818 466 8456, editando la v1 sin regenerar."""
import os
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
FUENTE = "/tmp/claude-1000/-workspaces-visionagenciaIAV2-0/011a9a4b-1c9e-4fe9-a2a5-875470559470/scratchpad/RobotoCondensed.ttf"
VERDE = (5, 35, 3)
NUMERO = "818 466 8456"

v1 = Image.open(os.path.join(AQUI, "ANUNCIO_PRUEBELO_v1.png")).convert("RGB")
W, H = 2550, 3300
k = H / v1.height
im = v1.resize((round(v1.width * k), H), Image.LANCZOS)
d = ImageDraw.Draw(im)
S = lambda v: round(v * k)

# tapa "627 517 7203" (dígitos en x 635-1054, y 1335-1397 de la v1) con el naranja y grano reales de la barra,
# tomados de la zona limpia a la derecha de "Mereces Amarte MXN", y bordes difuminados para que no se note el parche
import numpy as np
from PIL import ImageFilter
limpio = np.array(im)[S(1420):S(1465), S(800):S(1090)].reshape(-1, 3).astype(float)
media, sigma = limpio.mean(axis=0), limpio.std(axis=0)
x0, y0, x1, y1 = S(618), S(1322), S(1080), S(1410)
ruido = np.random.default_rng(1).normal(media, sigma * 0.6, (y1 - y0, x1 - x0, 3))
parche = Image.fromarray(np.clip(ruido, 0, 255).astype("uint8"))
mascara = Image.new("L", (x1 - x0, y1 - y0), 0)
ImageDraw.Draw(mascara).rectangle([12, 10, x1 - x0 - 13, y1 - y0 - 11], fill=255)
im.paste(parche, (x0, y0), mascara.filter(ImageFilter.GaussianBlur(6)))

# fuente cuya altura de dígito iguala la original (63 px en la v1)
alto = S(1397) - S(1335)
tam = alto
while True:
    f = ImageFont.truetype(FUENTE, tam)
    f.set_variation_by_name("Black")
    _, arriba, _, abajo = d.textbbox((0, 0), "8", font=f, anchor="ls")
    if abajo - arriba >= alto:
        break
    tam += 1
ancho_max = S(1056) - S(635)
while d.textlength(NUMERO, font=f) > ancho_max:
    tam -= 1
    f = ImageFont.truetype(FUENTE, tam)
    f.set_variation_by_name("Black")
d.text((S(635), S(1397) + 1), NUMERO, font=f, fill=VERDE, anchor="ls")

im.save(os.path.join(AQUI, "ANUNCIO_PRUEBELO_v2.png"))
im.convert("RGB").resize((1104, 1472), Image.LANCZOS).save(os.path.join(AQUI, "ANUNCIO_PRUEBELO_v2.jpg"), quality=92)
carta = Image.new("RGB", (W, H), "white")
carta.paste(im, ((W - im.width) // 2, 0))
carta.save(os.path.join(AQUI, "ANUNCIO_PRUEBELO_v2_CARTA.pdf"), resolution=300)
print("listo", tam)
