"""Cartel Rar~Amore de Jesús + beneficios de cada ingrediente de las cápsulas, en letra grande.
Toma su PDF (una sola imagen), conserva el marco y las hojas, y redibuje el centro."""
import os
import pymupdf as fitz
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(AQUI, "fuentes")
W, H = 2550, 3300
VERDE, TINTA, GRIS, BLANCO = (13, 60, 40), (25, 30, 28), (70, 80, 75), (255, 255, 255)

pix = fitz.open(os.path.join(AQUI, "original_jesus_RarAmore_CARTEL_carta.pdf"))[0].get_pixmap(dpi=300)
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


# Limpia el centro (entre las hojas de los lados, abajo de las de arriba)
d.rectangle([215, 655, 2335, 2870], fill=BLANCO)

# ---- Encabezado
centrado(740, "BIENESTAR PARA TUS MÚSCULOS Y ARTICULACIONES", fuente("Montserrat", 62, "ExtraBold"), VERDE)
centrado(905, "RAR~AMORE", fuente("Cormorant", 170, "SemiBold"), VERDE, espacio=38)
d.line([1000, 945, 1550, 945], fill=VERDE, width=5)
centrado(1010, "BÁLSAMO · CÁPSULAS", fuente("Montserrat", 50, "Medium"), VERDE, espacio=10)
centrado(1110, "Vive sin dolores · Vive sin estrés · Vive sin insomnio", fuente("Cormorant", 84, "Bold"), TINTA)

# ---- Ingredientes con beneficios (2 columnas, letra grande)
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
f_ben = fuente("Montserrat", 56, "Medium")
COL_X, COL_W = (255, 1320), 975
y_fila, ALTO = 1295, 238
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
        d.text((x + 45, y + 136 + j * 70), linea, font=f_ben, fill=TINTA, anchor="ls")
y = y_fila + 4 * ALTO
# Modo de uso (pedido de Jesús, 14 sep 02:48): etiqueta verde + texto, centrado y ajustado al ancho
t_eti, t_uso = "MODO DE USO SUGERIDO: ", "2 cápsulas diarias junto con los alimentos"  # texto de Jesús 14 sep 03:23
tam = 60
while True:
    f_eti, f_uso = fuente("Montserrat", tam, "ExtraBold"), fuente("Montserrat", tam, "SemiBold")
    ancho = d.textlength(t_eti, font=f_eti) + d.textlength(t_uso, font=f_uso)
    if ancho <= 2000:
        break
    tam -= 2
x0 = W / 2 - ancho / 2
d.text((x0, y + 60), t_eti, font=f_eti, fill=VERDE, anchor="ls")
d.text((x0 + d.textlength(t_eti, font=f_eti), y + 60), t_uso, font=f_uso, fill=TINTA, anchor="ls")
centrado(y + 122, "CONTENIDO: 30 CÁPSULAS", fuente("Montserrat", 46, "SemiBold"), GRIS)

# ---- Precio
caja_y = y + 150
d.rounded_rectangle([300, caja_y, 2250, caja_y + 330], radius=24, outline=VERDE, width=6)
centrado(caja_y + 80, "PRECIO DE PROMOCIÓN", fuente("Montserrat", 56, "ExtraBold"), VERDE)
centrado(caja_y + 170, "Paquete Bálsamo + Cápsulas", fuente("Cormorant", 88, "Bold"), TINTA)
f_precio, f_normal = fuente("Montserrat", 130, "Black"), fuente("Montserrat", 52, "Medium")
t1, t2 = "$1,895", "   Precio normal $2,359"
x0 = W / 2 - (d.textlength(t1, font=f_precio) + d.textlength(t2, font=f_normal)) / 2
d.text((x0, caja_y + 305), t1, font=f_precio, fill=VERDE, anchor="ls")
d.text((x0 + d.textlength(t1, font=f_precio), caja_y + 305), t2, font=f_normal, fill=GRIS, anchor="ls")

# ---- Leyenda y WhatsApp
centrado(caja_y + 385, "Este producto no es un medicamento. Es responsabilidad de quien lo recomienda y de quien lo usa.",
         fuente("Montserrat", 34, "Medium"), GRIS)
# La banda tapa el número original de Jesús, que está dibujado encima de las hojas de abajo (y≈2950-3060)
banda = 2840
d.rounded_rectangle([330, banda, 2220, banda + 250], radius=40, fill=VERDE)
centrado(banda + 90, "PEDIDOS POR WHATSAPP", fuente("Montserrat", 60, "Bold"), BLANCO)
centrado(banda + 215, "818 466 8456", fuente("Montserrat", 124, "Black"), BLANCO)
print("leyenda y =", caja_y + 400, "| banda", banda, "-", banda + 250)

im.save(os.path.join(AQUI, "CARTEL_BENEFICIOS_CARTA.png"), dpi=(300, 300))
im.save(os.path.join(AQUI, "CARTEL_BENEFICIOS_CARTA.pdf"), resolution=300)
im.resize((1275, 1650), Image.LANCZOS).save(os.path.join(AQUI, "CARTEL_BENEFICIOS_preview.jpg"), quality=90)
print("listo")
