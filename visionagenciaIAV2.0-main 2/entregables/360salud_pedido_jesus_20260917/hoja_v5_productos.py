"""Hoja del BÁLSAMO v5 — pedido de Jesús del 17 sep.

Mismo pedido que el cartel: el bote real del bálsamo "en un ladito", "una ruedita
con el precio" ($895) y que diga "POR TIEMPO LIMITADO". Los números de cuenta y los
nombres SE QUEDAN (audio 11:29: "mejor no le quite los números").
Parte de la v2 (igual que hizo la v4) y redibuja el recuadro crema, ahora con el bote.
"""
import os
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(AQUI, "..", "360salud_hoja_pague_despues_20260911")
FUENTE = os.path.join(AQUI, "..", "360salud_cartel_beneficios_20260914", "fuentes", "RobotoCondensed.ttf")
CREMA, VERDE, TINTA, BLANCO = (254, 251, 244), (1, 83, 37), (17, 17, 17), (255, 255, 255)
ROJO = (176, 24, 24)
LIMITE_FACEBOOK = 1545  # el recuadro de Facebook empieza ~1560

im = Image.open(os.path.join(BASE, "HOJA_PAGUE_DESPUES_v2_CARTA.png")).convert("RGBA")
capa = Image.new("RGBA", im.size, (0, 0, 0, 0))
d = ImageDraw.Draw(capa)


def fuente(tam, peso):
    f = ImageFont.truetype(FUENTE, tam)
    f.set_variation_by_name(peso)
    return f


X0, Y0, X1 = 1340, 585, 2470   # Y0 585 como la v4: mas arriba se come el titulo 'Y ESPALDA'
CX = (X0 + X1) // 2

# ---- Bote del bálsamo, recortado de la foto que mandó Jesús el 17 sep 11:27
bote = Image.open(os.path.join(AQUI, "productos", "balsamo.png"))
alto = 378
bote = bote.resize((round(bote.width * alto / bote.height), alto), Image.LANCZOS)
BX, BY = X0 + 38, Y0 + 112

# ---- Todo el texto, con su posición, para poder comprobarlo antes de dibujar
filas = []
filas.append(("BÁLSAMO Rar~Amore", fuente(86, "Black"), VERDE, CX, Y0 + 82, "ms"))

# Columna derecha del bote
DX0, DX1 = BX + bote.width + 78, X1 - 40
DCX = (DX0 + DX1) // 2
filas.append(("INGREDIENTES", fuente(52, "Bold"), VERDE, DCX, BY + 158, "ms"))
for i, ing in enumerate(["Caléndula", "Ajo", "Árnica", "Mentol"]):
    filas.append(("• " + ing, fuente(58, "Bold"), TINTA,
                  DX0 + 30 + (i % 2) * ((DX1 - DX0) // 2), BY + 218 + (i // 2) * 62, "ls"))
# Audio 17 sep 13:18: donde dice el DÚO / los $1,895, que diga "cápsulas + bálsamo"
filas.append(("LOS DOS (CÁPSULAS + BÁLSAMO)", fuente(44, "Bold"), VERDE, DCX, BY + 348, "ms"))
filas.append(("$1,895 con envío", fuente(48, "Black"), VERDE, DCX, BY + 400, "ms"))

# Debajo del bote, a todo lo ancho
y = BY + alto + 80
filas.append(("ÚTIL PARA MÚLTIPLES DOLENCIAS:", fuente(54, "Bold"), VERDE, CX, y, "ms"))
COL = (X1 - X0 - 120) // 3   # 3 columnas: 7 dolencias en 3 renglones, no 4
for i, u in enumerate(["Cabeza", "Hombros", "Espalda", "Rodillas",
                       "Nervio ciático", "Musculares", "Reumáticos"]):
    filas.append(("• " + u, fuente(52, "Bold"), TINTA,
                  X0 + 60 + (i % 3) * COL, y + 70 + (i // 3) * 62, "ls"))
y += 70 + 2 * 62 + 78
filas.append(("MODO DE USO:", fuente(54, "Bold"), VERDE, CX, y, "ms"))
filas.append(("Aplicar generosamente en el área afectada.", fuente(58, "Bold"), TINTA, CX, y + 68, "ms"))
Y1 = y + 68 + 42

for texto, f, _, x, yy, anc in filas:
    ancho = d.textlength(texto, font=f)
    izq = x - ancho / 2 if anc == "ms" else x
    assert izq >= X0 + 18 and izq + ancho <= X1 - 18, "no cabe a lo ancho: " + texto
assert Y1 <= LIMITE_FACEBOOK, "se encima con Facebook: Y1=%d" % Y1
assert BY + alto < y - 60, "el bote se encima con el texto de abajo"
assert BY + 158 - 52 > BY + 104, "INGREDIENTES se encima con el cintillo rojo"
print("recuadro", X0, Y0, X1, Y1, "| bote", BX, BY, bote.size)

# ---- Dibujo
d.rounded_rectangle([X0, Y0, X1, Y1], radius=36, fill=CREMA + (238,), outline=VERDE + (255,), width=6)
d.ellipse([BX - 8, BY + alto - 26, BX + bote.width + 8, BY + alto + 12], fill=(0, 0, 0, 55))
capa.alpha_composite(bote, (BX, BY))

# Cintillo de tiempo limitado, arriba de la columna derecha
d.rounded_rectangle([DX0, BY + 16, DX1, BY + 104], radius=16, fill=ROJO + (255,))
d.text(((DX0 + DX1) // 2, BY + 60), "¡POR TIEMPO LIMITADO!", font=fuente(48, "ExtraBold"),
       fill=BLANCO, anchor="mm")

# La ruedita del precio, montada en la orilla del bote
RX, RY, R = X0 - 4, BY + alto - 55, 96   # montada en la orilla del recuadro, como calcomania: no tapa el nombre del bote
d.ellipse([RX - R, RY - R, RX + R, RY + R], fill=VERDE + (255,), outline=BLANCO + (255,), width=7)
d.text((RX, RY - 28), "BÁLSAMO", font=fuente(32, "Bold"), fill=BLANCO, anchor="mm")
d.text((RX, RY + 26), "$895", font=fuente(66, "Black"), fill=BLANCO, anchor="mm")

for texto, f, color, x, yy, anc in filas:
    d.text((x, yy), texto, font=f, fill=color, anchor=anc)

carta = Image.alpha_composite(im, capa).convert("RGB")
carta.save(os.path.join(AQUI, "HOJA_BALSAMO_v5_CARTA.png"), dpi=(300, 300))
carta.save(os.path.join(AQUI, "HOJA_BALSAMO_v5_CARTA.pdf"), resolution=300)
carta.resize((1275, 1650), Image.LANCZOS).save(os.path.join(AQUI, "HOJA_BALSAMO_v5_preview.jpg"), quality=92)
print("listo")
