"""v4: igual que v3 (ingredientes del bálsamo en el espacio libre) + MODO DE USO.
Pedido de Jesús 14 sep 02:50: "modo de uso: aplicar generosamente en el área afectada". Parte de la v2 para no encimar recuadros."""
import os
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
FUENTE = os.path.join(AQUI, "..", "360salud_cartel_beneficios_20260914", "fuentes", "RobotoCondensed.ttf")
CREMA, VERDE, TINTA = (254, 251, 244), (1, 83, 37), (17, 17, 17)
LIMITE_FACEBOOK = 1545  # el recuadro de Facebook empieza ~1560

im = Image.open(os.path.join(AQUI, "HOJA_PAGUE_DESPUES_v2_CARTA.png")).convert("RGBA")
capa = Image.new("RGBA", im.size, (0, 0, 0, 0))
d = ImageDraw.Draw(capa)


def fuente(tam, peso):
    f = ImageFont.truetype(FUENTE, tam)
    f.set_variation_by_name(peso)
    return f


X0, Y0, X1 = 1340, 585, 2470
CX, MEDIA = (X0 + X1) // 2, (X1 - X0) // 2
filas = []
y = Y0 + 100
filas.append(("BÁLSAMO Rar~Amore", fuente(92, "Black"), VERDE, CX, y, "ms"))
y += 88
filas.append(("INGREDIENTES", fuente(56, "Bold"), VERDE, CX, y, "ms"))
for i, ing in enumerate(["Caléndula", "Ajo", "Árnica", "Mentol"]):
    filas.append(("• " + ing, fuente(64, "Bold"), TINTA, X0 + 90 + (i % 2) * MEDIA, y + 80 + (i // 2) * 72, "ls"))
y += 80 + 72 + 88
filas.append(("ÚTIL PARA MÚLTIPLES DOLENCIAS:", fuente(56, "Bold"), VERDE, CX, y, "ms"))
for i, u in enumerate(["Cabeza", "Hombros", "Espalda", "Rodillas", "Nervio ciático", "Musculares", "Reumáticos"]):
    filas.append(("• " + u, fuente(60, "Bold"), TINTA, X0 + 90 + (i % 2) * MEDIA, y + 78 + (i // 2) * 68, "ls"))
y += 78 + 3 * 68 + 88
filas.append(("MODO DE USO:", fuente(56, "Bold"), VERDE, CX, y, "ms"))
filas.append(("Aplicar generosamente en el área afectada.", fuente(60, "Bold"), TINTA, CX, y + 72, "ms"))
Y1 = y + 72 + 45

# Comprobaciones: nada se sale del recuadro ni se encima con Facebook
for texto, f, _, x, yy, anc in filas:
    ancho = d.textlength(texto, font=f)
    izq = x - ancho / 2 if anc == "ms" else x
    assert izq >= X0 + 20 and izq + ancho <= X1 - 20, "no cabe a lo ancho: " + texto
assert Y1 <= LIMITE_FACEBOOK, "se encima con Facebook: Y1=%d" % Y1
print("recuadro", X0, Y0, X1, Y1)

d.rounded_rectangle([X0, Y0, X1, Y1], radius=36, fill=CREMA + (238,), outline=VERDE + (255,), width=6)
for texto, f, color, x, yy, anc in filas:
    d.text((x, yy), texto, font=f, fill=color, anchor=anc)

carta = Image.alpha_composite(im, capa).convert("RGB")
carta.save(os.path.join(AQUI, "HOJA_PAGUE_DESPUES_v4_CARTA.png"), dpi=(300, 300))
carta.save(os.path.join(AQUI, "HOJA_PAGUE_DESPUES_v4_CARTA.pdf"), resolution=300)
carta.resize((1275, 1650), Image.LANCZOS).save(os.path.join(AQUI, "HOJA_PAGUE_DESPUES_v4_preview.jpg"), quality=90)
print("listo")
