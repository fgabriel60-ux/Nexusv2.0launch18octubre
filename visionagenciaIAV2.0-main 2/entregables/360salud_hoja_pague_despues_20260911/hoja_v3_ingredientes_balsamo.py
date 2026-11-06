"""v3: agrega los ingredientes del bálsamo en el espacio libre (árboles a la derecha de la señora).
Pedido de Jesús 14 sep 00:55: "únicamente acomodar eso, ya no le ponga más información". Texto tal cual lo mandó."""
import os
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
FUENTE = os.path.join(AQUI, "..", "360salud_cartel_beneficios_20260914", "fuentes", "RobotoCondensed.ttf")
CREMA, VERDE, TINTA = (254, 251, 244), (1, 83, 37), (17, 17, 17)

im = Image.open(os.path.join(AQUI, "HOJA_PAGUE_DESPUES_v2_CARTA.png")).convert("RGBA")
capa = Image.new("RGBA", im.size, (0, 0, 0, 0))
d = ImageDraw.Draw(capa)


def fuente(tam, peso):
    f = ImageFont.truetype(FUENTE, tam)
    f.set_variation_by_name(peso)
    return f


# Recuadro entre el título (termina ~y 540) y el recuadro de Facebook (empieza ~y 1560), a la derecha de la señora
X0, Y0, X1 = 1340, 600, 2470
CX = (X0 + X1) // 2
MEDIA = (X1 - X0) // 2
filas = []  # (texto, fuente, color, x, y) — se calcula el alto antes de pintar el fondo
y = Y0 + 110
filas.append(("BÁLSAMO Rar~Amore", fuente(96, "Black"), VERDE, CX, y, "ms"))
y += 95
filas.append(("INGREDIENTES", fuente(58, "Bold"), VERDE, CX, y, "ms"))
f_item = fuente(68, "Bold")
for i, ing in enumerate(["Caléndula", "Ajo", "Árnica", "Mentol"]):
    filas.append(("• " + ing, f_item, TINTA, X0 + 90 + (i % 2) * MEDIA, y + 88 + (i // 2) * 82, "ls"))
y += 88 + 82 + 105
filas.append(("ÚTIL PARA MÚLTIPLES DOLENCIAS:", fuente(58, "Bold"), VERDE, CX, y, "ms"))
f_util = fuente(64, "Bold")
for i, u in enumerate(["Cabeza", "Hombros", "Espalda", "Rodillas", "Nervio ciático", "Musculares", "Reumáticos"]):
    filas.append(("• " + u, f_util, TINTA, X0 + 90 + (i % 2) * MEDIA, y + 88 + (i // 2) * 78, "ls"))
Y1 = y + 88 + 3 * 78 + 55
print("recuadro", X0, Y0, X1, Y1, "(Facebook empieza ~1560)")

d.rounded_rectangle([X0, Y0, X1, Y1], radius=36, fill=CREMA + (238,), outline=VERDE + (255,), width=6)
for texto, f, color, x, yy, anc in filas:
    d.text((x, yy), texto, font=f, fill=color, anchor=anc)

carta = Image.alpha_composite(im, capa).convert("RGB")
carta.save(os.path.join(AQUI, "HOJA_PAGUE_DESPUES_v3_CARTA.png"), dpi=(300, 300))
carta.save(os.path.join(AQUI, "HOJA_PAGUE_DESPUES_v3_CARTA.pdf"), resolution=300)
carta.resize((1275, 1650), Image.LANCZOS).save(os.path.join(AQUI, "HOJA_PAGUE_DESPUES_v3_preview.jpg"), quality=90)
print("listo")
