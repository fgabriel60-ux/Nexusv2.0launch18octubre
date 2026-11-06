"""Tarjeta de presentación de Casa Comercial Graciela (cliente de papá).

Carlos (16 sep): «el diseño de los muebles era para una tarjeta de presentación, hazlo con la segunda».
Datos del audio de Marco Antonio (`transcripcion_2.txt`): nombre del negocio, «Prop. Marco Antonio Ortiz» y el
teléfono. Él dijo que NO tiene Facebook ni correo, así que no se inventa nada más.

El texto se compone con tipografía real (no con IA) para que el nombre y el teléfono salgan exactos al imprimir.
Tamaño 9 x 5.5 cm a 300 dpi con 3 mm de rebase (sangrado). Salen PNG y PDF.
Uso: python3 tarjeta_graciela.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
FOTO = os.path.join(AQUI, "PROPUESTA_2_cajonera_y_comedor.png")
NEGOCIO = "Casa Comercial Graciela"
PROPIETARIO = "Prop. Marco Antonio Ortiz"
TELEFONO = "631 123 1961"

DPI = 300
MM = DPI / 25.4
ANCHO, ALTO = int(90 * MM), int(55 * MM)          # 9 x 5.5 cm
SANGRADO = int(3 * MM)                             # 3 mm por lado para imprenta
CREMA, CAFE, CAFE_CLARO, LINEA = (247, 241, 231), (61, 40, 25), (120, 85, 55), (176, 141, 98)

CANDIDATAS = {
    "serif_bold": ["DejaVuSerif-Bold.ttf", "LiberationSerif-Bold.ttf", "NotoSerif-Bold.ttf", "Georgia_Bold.ttf"],
    "serif": ["DejaVuSerif.ttf", "LiberationSerif-Regular.ttf", "NotoSerif-Regular.ttf"],
    "sans": ["DejaVuSans.ttf", "LiberationSans-Regular.ttf", "NotoSans-Regular.ttf"],
    "sans_bold": ["DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf", "NotoSans-Bold.ttf"],
}


def fuente(tipo, tam):
    for nombre in CANDIDATAS[tipo]:
        for raiz, _, archivos in os.walk("/usr/share/fonts"):
            if nombre in archivos:
                return ImageFont.truetype(os.path.join(raiz, nombre), tam)
    return ImageFont.load_default()


def centrado(d, texto, f, y, color, cx):
    a = d.textbbox((0, 0), texto, font=f)
    d.text((cx - (a[2] - a[0]) / 2, y), texto, font=f, fill=color)
    return a[3] - a[1]


def tarjeta():
    W, H = ANCHO + 2 * SANGRADO, ALTO + 2 * SANGRADO
    im = Image.new("RGB", (W, H), CREMA)
    d = ImageDraw.Draw(im)

    # Foto de los muebles a la izquierda, recortada a su columna
    col = int(W * 0.42)
    foto = Image.open(FOTO).convert("RGB")
    fw, fh = foto.size
    escala = max(col / fw, H / fh)
    foto = foto.resize((int(fw * escala), int(fh * escala)), Image.Resampling.LANCZOS)
    foto = foto.crop(((foto.width - col) // 2, (foto.height - H) // 2,
                      (foto.width - col) // 2 + col, (foto.height - H) // 2 + H))
    im.paste(foto, (0, 0))
    d.rectangle([col, 0, col + int(2 * MM / 3), H], fill=LINEA)   # filete que separa

    cx = col + (W - col) / 2
    f_nombre = fuente("serif_bold", int(7.4 * MM))
    f_casa = fuente("serif", int(4.2 * MM))
    f_prop = fuente("sans", int(3.4 * MM))
    f_tel = fuente("sans_bold", int(5.6 * MM))

    y = int(H * 0.20)
    y += centrado(d, "Casa Comercial", f_casa, y, CAFE_CLARO, cx) + int(3.2 * MM)
    y += centrado(d, "Graciela", f_nombre, y, CAFE, cx) + int(3.6 * MM)
    d.line([(cx - 16 * MM, y), (cx + 16 * MM, y)], fill=LINEA, width=max(2, int(0.35 * MM)))
    y += int(4.2 * MM)
    y += centrado(d, PROPIETARIO, f_prop, y, CAFE_CLARO, cx) + int(4.6 * MM)
    centrado(d, TELEFONO, f_tel, y, CAFE, cx)

    im.save(os.path.join(AQUI, "TARJETA_GRACIELA_con_sangrado.png"), dpi=(DPI, DPI))
    final = im.crop((SANGRADO, SANGRADO, SANGRADO + ANCHO, SANGRADO + ALTO))
    final.save(os.path.join(AQUI, "TARJETA_GRACIELA.png"), dpi=(DPI, DPI))
    final.save(os.path.join(AQUI, "TARJETA_GRACIELA.pdf"), "PDF", resolution=DPI)
    print("listo:", final.size, "px @", DPI, "dpi =", round(ANCHO / MM), "x", round(ALTO / MM), "mm")


if __name__ == "__main__":
    tarjeta()
