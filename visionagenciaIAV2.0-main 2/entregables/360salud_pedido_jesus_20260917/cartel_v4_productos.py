"""Cartel de CÁPSULAS v4 — pedido de Jesús del 17 sep.

Audios 11:21 / 11:29 / 11:53: agregarle el frasco real de cápsulas "ahí en un ladito",
con "una ruedita con el precio", y que diga "POR TIEMPO LIMITADO".
Precios (texto de las 11:44): cápsulas $1,392 · bálsamo $895 · dúo $1,895 con envío.
NO se quitan números ni nombres: a las 11:29 se retractó ("mejor no le quite los números").
Parte del cartel del 14 sep; sólo se aprieta la reja de ingredientes para abrir el hueco.
"""
import os
import pymupdf as fitz
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(AQUI, "..", "360salud_cartel_beneficios_20260914")
F = os.path.join(BASE, "fuentes")
W, H = 2550, 3300
VERDE, TINTA, GRIS, BLANCO = (13, 60, 40), (25, 30, 28), (70, 80, 75), (255, 255, 255)
ROJO = (176, 24, 24)

pix = fitz.open(os.path.join(BASE, "original_jesus_RarAmore_CARTEL_carta.pdf"))[0].get_pixmap(dpi=300)
im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
d = ImageDraw.Draw(im)


def fuente(nombre, tam, peso):
    f = ImageFont.truetype(os.path.join(F, nombre + ".ttf"), tam)
    f.set_variation_by_name(peso)
    return f


def centrado(y, texto, f, color, x=W // 2, espacio=0):
    if espacio:
        ancho = sum(d.textlength(c, font=f) for c in texto) + espacio * (len(texto) - 1)
        xx = x - ancho / 2
        for c in texto:
            d.text((xx, y), c, font=f, fill=color, anchor="ls")
            xx += d.textlength(c, font=f) + espacio
    else:
        d.text((x, y), texto, font=f, fill=color, anchor="ms")


def envuelve(texto, f, ancho):
    lineas, actual = [], ""
    for p in texto.split():
        prueba = (actual + " " + p).strip()
        if d.textlength(prueba, font=f) <= ancho:
            actual = prueba
        else:
            lineas.append(actual)
            actual = p
    return lineas + [actual]


d.rectangle([215, 655, 2335, 2870], fill=BLANCO)

# ---- Encabezado (igual que el del 14 sep)
centrado(740, "BIENESTAR PARA TUS MÚSCULOS Y ARTICULACIONES", fuente("Montserrat", 62, "ExtraBold"), VERDE)
centrado(905, "RAR~AMORE", fuente("Cormorant", 170, "SemiBold"), VERDE, espacio=38)
d.line([1000, 945, 1550, 945], fill=VERDE, width=5)
centrado(1010, "BÁLSAMO · CÁPSULAS", fuente("Montserrat", 50, "Medium"), VERDE, espacio=10)
centrado(1110, "Vive sin dolores · Vive sin estrés · Vive sin insomnio", fuente("Cormorant", 84, "Bold"), TINTA)

# ---- Ingredientes con beneficios (letra grande; ALTO 238->214 para abrir hueco al frasco)
centrado(1225, "LAS CÁPSULAS CONTIENEN:", fuente("Montserrat", 64, "Black"), VERDE)
INGREDIENTES = [
    ("COLÁGENO", "Apoya el cartílago, la flexibilidad de las articulaciones y la piel."),
    ("BOSWELIA SERRATA", "Planta que ayuda a calmar la inflamación y la rigidez."),
    ("CALCIO", "Ayuda a mantener los huesos y dientes fuertes."),
    ("VITAMINA D", "Ayuda al cuerpo a aprovechar el calcio y fortalecer huesos."),
    ("MAGNESIO", "Ayuda a relajar los músculos, evitar calambres y dormir mejor."),
    ("EXTRACTO DE NARANJA", "Vitamina C y antioxidantes que apoyan las defensas."),
    ("EXTRACTO DE LIMÓN", "Vitamina C, que ayuda al cuerpo a formar colágeno."),
    ("SEMILLA DE UVA (RESVERATROL)", "Antioxidante que apoya la circulación y el corazón."),
]
f_nom = fuente("Montserrat", 60, "ExtraBold")
f_ben = fuente("Montserrat", 54, "Medium")
COL_X, COL_W = (255, 1320), 975
y_fila, ALTO = 1290, 214
for i, (nombre, beneficio) in enumerate(INGREDIENTES):
    x, y = COL_X[i % 2], y_fila + (i // 2) * ALTO
    d.ellipse([x, y + 22, x + 26, y + 48], fill=VERDE)
    tam = 60
    while d.textlength(nombre, font=f_nom) > COL_W - 45:
        tam -= 2
        f_nom = fuente("Montserrat", tam, "ExtraBold")
    d.text((x + 45, y + 58), nombre, font=f_nom, fill=VERDE, anchor="ls")
    f_nom = fuente("Montserrat", 60, "ExtraBold")
    for j, linea in enumerate(envuelve(beneficio, f_ben, COL_W - 45)):
        d.text((x + 45, y + 130, ), linea, font=f_ben, fill=TINTA, anchor="ls") if False else \
            d.text((x + 45, y + 130 + j * 66), linea, font=f_ben, fill=TINTA, anchor="ls")
y = y_fila + 4 * ALTO

# Modo de uso + contenido
t_eti, t_uso = "MODO DE USO SUGERIDO: ", "2 cápsulas diarias junto con los alimentos"
tam = 60
while True:
    f_eti, f_uso = fuente("Montserrat", tam, "ExtraBold"), fuente("Montserrat", tam, "SemiBold")
    ancho = d.textlength(t_eti, font=f_eti) + d.textlength(t_uso, font=f_uso)
    if ancho <= 2000:
        break
    tam -= 2
x0 = W / 2 - ancho / 2
d.text((x0, y + 55), t_eti, font=f_eti, fill=VERDE, anchor="ls")
d.text((x0 + d.textlength(t_eti, font=f_eti), y + 55), t_uso, font=f_uso, fill=TINTA, anchor="ls")
centrado(y + 115, "CONTENIDO: 30 CÁPSULAS", fuente("Montserrat", 46, "SemiBold"), GRIS)

# ---- Caja de precios con el frasco real y la ruedita (pedido del 17 sep)
CAJA = [300, y + 145, 2250, y + 145 + 470]
d.rounded_rectangle(CAJA, radius=24, outline=VERDE, width=6)
cx0, cy0, cx1, cy1 = CAJA

# Frasco recortado de la foto que mandó Jesús el 17 sep 11:27
frasco = Image.open(os.path.join(AQUI, "productos", "capsulas.png"))
alto = 432
frasco = frasco.resize((round(frasco.width * alto / frasco.height), alto), Image.LANCZOS)
fx, fy = cx0 + 55, cy0 + 20
sombra = Image.new("RGBA", im.size, (0, 0, 0, 0))
ImageDraw.Draw(sombra).ellipse([fx - 10, fy + alto - 34, fx + frasco.width + 10, fy + alto + 6],
                               fill=(0, 0, 0, 60))
im.paste(Image.alpha_composite(im.convert("RGBA"), sombra).convert("RGB"), (0, 0))
d = ImageDraw.Draw(im)
im.paste(frasco, (fx, fy), frasco)

# La ruedita del precio, encima del frasco
RX, RY, R = fx + frasco.width + 84, fy + alto - 122, 132
d.ellipse([RX - R, RY - R, RX + R, RY + R], fill=VERDE, outline=BLANCO, width=8)
d.text((RX, RY - 34), "CÁPSULAS", font=fuente("Montserrat", 38, "Bold"), fill=BLANCO, anchor="mm")
d.text((RX, RY + 32), "$1,392", font=fuente("Montserrat", 72, "Black"), fill=BLANCO, anchor="mm")

# Columna derecha: tiempo limitado + los otros dos precios
TX0, TX1 = RX + R + 45, cx1 - 55
TCX = (TX0 + TX1) // 2
d.rounded_rectangle([TX0, cy0 + 30, TX1, cy0 + 118], radius=18, fill=ROJO)
d.text((TCX, cy0 + 74), "¡POR TIEMPO LIMITADO!", font=fuente("Montserrat", 54, "ExtraBold"),
       fill=BLANCO, anchor="mm")
d.text((TCX, cy0 + 186), "BÁLSAMO por separado: $895", font=fuente("Montserrat", 52, "SemiBold"),
       fill=TINTA, anchor="mm")
# Audio 17 sep 13:18: "pegadito donde diga la palabra DÚO... paréntesis cápsulas más bálsamo"
d.text((TCX, cy0 + 268), "SI SE LLEVA EL DÚO (CÁPSULAS + BÁLSAMO):",
       font=fuente("Montserrat", 50, "ExtraBold"), fill=VERDE, anchor="mm")
f_p, f_e = fuente("Montserrat", 104, "Black"), fuente("Montserrat", 44, "SemiBold")
t1, t2 = "$1,895", "  incluye envío"
xx = TCX - (d.textlength(t1, font=f_p) + d.textlength(t2, font=f_e)) / 2
d.text((xx, cy0 + 385), t1, font=f_p, fill=VERDE, anchor="ls")
d.text((xx + d.textlength(t1, font=f_p), cy0 + 385), t2, font=f_e, fill=GRIS, anchor="ls")
d.text((TCX, cy0 + 435), "Precio normal $2,359", font=fuente("Montserrat", 42, "Medium"),
       fill=GRIS, anchor="mm")

# ---- Leyenda y banda de WhatsApp (la banda tapa el número original, y≈2950-3060)
centrado(cy1 + 46, "Este producto no es un medicamento. Es responsabilidad de quien lo recomienda y de quien lo usa.",
         fuente("Montserrat", 34, "Medium"), GRIS)
banda = 2840
assert cy1 + 46 < banda - 10, "la leyenda se encima con la banda: %d" % (cy1 + 46)
d.rounded_rectangle([330, banda, 2220, banda + 250], radius=40, fill=VERDE)
centrado(banda + 90, "PEDIDOS POR WHATSAPP", fuente("Montserrat", 60, "Bold"), BLANCO)
centrado(banda + 215, "818 466 8456", fuente("Montserrat", 124, "Black"), BLANCO)
print("caja", CAJA, "| leyenda", cy1 + 46, "| banda", banda)

im.save(os.path.join(AQUI, "CARTEL_CAPSULAS_v4_CARTA.png"), dpi=(300, 300))
im.save(os.path.join(AQUI, "CARTEL_CAPSULAS_v4_CARTA.pdf"), resolution=300)
im.resize((1275, 1650), Image.LANCZOS).save(os.path.join(AQUI, "CARTEL_CAPSULAS_v4_preview.jpg"), quality=92)
print("listo")
