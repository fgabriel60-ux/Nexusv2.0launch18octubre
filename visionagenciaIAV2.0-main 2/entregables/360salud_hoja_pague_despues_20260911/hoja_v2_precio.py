"""v2: precio $1,895 y WhatsApp de comprobantes 818 466 8456, editando la v1 sin regenerar."""
import os
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
FUENTE = "/tmp/claude-1000/-workspaces-visionagenciaIAV2-0/aab4157b-ec02-40e2-b064-d2608e8a1ed9/scratchpad/RobotoCondensed.ttf"
CREMA, VERDE, TINTA, BLANCO = (254, 251, 244), (1, 83, 37), (17, 17, 17), (255, 255, 255)

v1 = Image.open(os.path.join(AQUI, "HOJA_PAGUE_DESPUES_v1.png")).convert("RGB")
W, H = 2550, 3300
k = H / v1.height
im = v1.resize((round(v1.width * k), H), Image.LANCZOS)
d = ImageDraw.Draw(im)
S = lambda v: round(v * k)


def fuente(tam, peso):
    f = ImageFont.truetype(FUENTE, tam)
    f.set_variation_by_name(peso)
    return f


def ajusta(partes, ancho_max, tam):
    while True:
        fs = [fuente(tam if not grande else round(tam * 1.18), peso) for _, _, peso, grande in partes]
        ancho = sum(d.textlength(t, font=f) for (t, *_), f in zip(partes, fs))
        if ancho <= ancho_max:
            return fs, ancho
        tam -= 2


def escribe(partes, y_centro, x_centro, ancho_max, tam):
    fs, ancho = ajusta(partes, ancho_max, tam)
    x = x_centro - ancho / 2
    for (t, color, _, _), f in zip(partes, fs):
        d.text((x, y_centro), t, font=f, fill=color, anchor="lm")
        x += d.textlength(t, font=f)


d.rectangle([S(28), S(964), S(1058), S(1023)], fill=CREMA)
escribe([("Si el DÚO Rar~Amore le gustó, deposite ", TINTA, "Bold", False),
         ("$1,895", VERDE, "Black", True),
         (" en:", TINTA, "Bold", False)],
        S(992), S(543), S(1000), S(44))

d.rectangle([S(18), S(1299), S(1068), S(1355)], fill=VERDE)
escribe([("Mande foto de su comprobante por WhatsApp: ", BLANCO, "Bold", False),
         ("818 466 8456", BLANCO, "Black", False)],
        S(1327), S(543), S(1015), S(46))

carta = Image.new("RGB", (W, H), "white")
carta.paste(im, ((W - im.width) // 2, 0))
carta.save(os.path.join(AQUI, "HOJA_PAGUE_DESPUES_v2_CARTA.png"), dpi=(300, 300))
carta.save(os.path.join(AQUI, "HOJA_PAGUE_DESPUES_v2_CARTA.pdf"), resolution=300)
carta.resize((1275, 1650), Image.LANCZOS).save(os.path.join(AQUI, "HOJA_PAGUE_DESPUES_v2_preview.jpg"), quality=90)
print("listo")
