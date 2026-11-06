"""Guillermo (Vicens) · v9 = v8 con efectos de sonido + TARJETAS DE PRECIO.

Los precios y la redaccion son los que pidio Glimmer el 3 nov 2026
(entregables/glimmer_evaluador/guillermo_precios_20261103/glimmer.log), con los
precios que dio Guillermo por WhatsApp ese mismo dia. No se inventa ningun dato.

  Celosias  desde $1,400 /m2   (segundo 3-5)
  Zaguanes  desde $2,300 /m2   (segundo 7-9)
  Puertas economicas desde $3,200 (segundo 11-13)
  Descargo: "*Precios desde por m2, segun medidas y diseno. Cotizacion sin compromiso por WhatsApp."

Uso: python3 armar_far12_v9_precios.py
"""
import pathlib
import subprocess

from PIL import Image, ImageDraw, ImageFont

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
ENTRADA = RAIZ / "entregables/guillermo_hoy_20261102/v8_click_sonido.mp4"
SALIDA = AQUI / "Vicens_far12_v9b_precios.mp4"
TMP = AQUI / "tmp_v9p"

NEGRA = RAIZ / "clientes/Carlos_Nexus/pixar/fonts/Inter-Black.ttf"
MONT = RAIZ / "visionagenciaIAV2.0-main 2/entregables/modelos_modal/fuentes/Montserrat.ttf"

ANCHO, ALTO = 720, 1280
# Franja libre del video: debajo del titular y encima del subtitulo/CTA.
CARD_Y, CARD_W, CARD_H = 424, 648, 206
AMARILLO = (255, 209, 0, 255)
BLANCO = (255, 255, 255, 255)
GRIS = (214, 214, 214, 255)

# Texto literal que dio Glimmer, partido en dos renglones para que se lea.
DESCARGO = ["*Precios desde por m², según medidas y diseño.",
            "Cotización sin compromiso por WhatsApp."]

# (archivo, producto, precio, desde_seg, hasta_seg)
# Glimmer pidió los 3 precios en tarjetas en los segundos 3-5, 7-9 y 11-13, pero en esos
# momentos el video muestra OTRO producto. Se respetan sus textos y su descargo, y cada
# tarjeta se mueve al tramo donde de verdad se ve ese producto:
#   zaguán 0.5-3.0 · celosías 3.2-5.2 · puertas 5.5-8.0 · portones 8.2-9.5 · celosías 10-13
TARJETAS = [
    ("c1", "ZAGUANES", "DESDE $2,300 /m²", 1.0, 3.0),
    ("c2", "PUERTAS DE HERRERÍA ECONÓMICAS", "DESDE $3,200", 5.8, 7.5),
    ("c3", "CELOSÍAS DECORATIVAS", "DESDE $1,400 /m²", 10.6, 12.8),
]


def _duracion(v):
    """ffprobe no está en el sandbox; la duración sale del stderr de `ffmpeg -i`."""
    import re
    err = subprocess.run(["ffmpeg", "-i", str(v)], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", err)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


def _fuente(ruta, tam):
    return ImageFont.truetype(str(ruta), tam)


def _ancho(dib, txt, fnt):
    a, _, b, _ = dib.textbbox((0, 0), txt, font=fnt)
    return b - a


def _centrado(dib, y, txt, fnt, color):
    dib.text(((ANCHO - _ancho(dib, txt, fnt)) / 2, y), txt, font=fnt, fill=color)


def _encoge(dib, txt, ruta, tam, limite, minimo=14):
    """Baja el tamaño hasta que el texto quepa en `limite` px."""
    fnt = _fuente(ruta, tam)
    while _ancho(dib, txt, fnt) > limite and tam > minimo:
        tam -= 2
        fnt = _fuente(ruta, tam)
    return fnt


def tarjeta(nombre, producto, precio):
    """Tarjeta de precio: caja oscura, producto en blanco, precio en amarillo, descargo abajo."""
    img = Image.new("RGBA", (ANCHO, ALTO), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x0 = (ANCHO - CARD_W) // 2
    d.rounded_rectangle([x0, CARD_Y, x0 + CARD_W, CARD_Y + CARD_H], radius=26,
                        fill=(10, 14, 22, 232), outline=(255, 209, 0, 255), width=4)

    f_prod = _encoge(d, producto, NEGRA, 33, CARD_W - 56, minimo=20)
    _centrado(d, CARD_Y + 20, producto, f_prod, BLANCO)

    f_prec = _encoge(d, precio, NEGRA, 62, CARD_W - 56, minimo=34)
    _centrado(d, CARD_Y + 66, precio, f_prec, AMARILLO)

    # El descargo va DENTRO de la tarjeta (debajo queda el subtítulo del video),
    # en dos renglones para que se pueda leer. Texto literal de Glimmer.
    for j, linea in enumerate(DESCARGO):
        f_desc = _encoge(d, linea, MONT, 21, CARD_W - 48, minimo=14)
        _centrado(d, CARD_Y + CARD_H - 54 + j * 24, linea, f_desc, GRIS)

    ruta = TMP / f"{nombre}.png"
    img.save(ruta)
    return ruta


def main():
    if not ENTRADA.exists():
        raise SystemExit(f"No está el video base: {ENTRADA}")
    TMP.mkdir(parents=True, exist_ok=True)

    dur = _duracion(ENTRADA)
    entradas = ["-i", str(ENTRADA)]
    filtros = []
    etiqueta = "0:v"
    for i, (nombre, producto, precio, desde, hasta) in enumerate(TARJETAS):
        png = tarjeta(nombre, producto, precio)
        # Sin -loop el PNG es UN solo cuadro en t=0 y el overlay nunca se ve.
        entradas += ["-loop", "1", "-t", f"{dur:.2f}", "-i", str(png)]
        sig = f"v{i + 1}"
        # Aparición y salida suaves (0.25 s) para que no "brinque".
        filtros.append(
            f"[{i + 1}:v]format=rgba,fade=t=in:st={desde}:d=0.25:alpha=1,"
            f"fade=t=out:st={hasta - 0.25}:d=0.25:alpha=1[o{i}];"
            f"[{etiqueta}][o{i}]overlay=0:0:enable='between(t,{desde},{hasta})'[{sig}]"
        )
        etiqueta = sig

    cadena = ";".join(filtros)
    cmd = ["ffmpeg", "-v", "error", "-y", *entradas, "-filter_complex", f"{cadena}",
           "-map", f"[{etiqueta}]", "-map", "0:a?",
           "-c:v", "libx264", "-profile:v", "main", "-pix_fmt", "yuv420p",
           "-crf", "20", "-preset", "medium", "-c:a", "copy", "-movflags", "+faststart",
           str(SALIDA)]
    subprocess.run(cmd, check=True)
    print("listo:", SALIDA, SALIDA.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
