"""Compone el logo de Cinthia Payán: icono de Qwen + nombre (Cormorant) + línea «Entender · Sanar · Crecer» (Montserrat) en degradado lila→turquesa.
Uso: python3 armar_logo.py a1 b1 c2"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageChops

AQUI = Path(__file__).resolve().parent
F = Path('/workspaces/Nexusv2.0launch18octubre/visionagenciaIAV2.0-main 2/entregables/360salud_cartel_beneficios_20260914/fuentes')
LILA, ROSA, TURQ = (150, 95, 170), (205, 110, 160), (40, 160, 155)


def degradado(w, h, cols):
    g = Image.new('RGB', (w, 1))
    for x in range(w):
        t = x / max(w - 1, 1) * (len(cols) - 1); i = min(int(t), len(cols) - 2); f = t - i
        g.putpixel((x, 0), tuple(int(cols[i][k] + (cols[i + 1][k] - cols[i][k]) * f) for k in range(3)))
    return g.resize((w, h))


def texto(lienzo, txt, fuente, y, cols, espacio=0):
    d = ImageDraw.Draw(lienzo)
    anchos = [d.textlength(c, font=fuente) + espacio for c in txt]
    w = int(sum(anchos) - espacio); asc, desc = fuente.getmetrics(); h = asc + desc
    m = Image.new('L', (w, h)); dm = ImageDraw.Draw(m); x = 0
    for c, a in zip(txt, anchos):
        dm.text((x, 0), c, font=fuente, fill=255); x += a
    x0 = (lienzo.width - w) // 2
    lienzo.paste(degradado(w, h, cols), (x0, y), m)
    return y + h


def icono_recortado(n):
    im = Image.open(AQUI / 'iconos' / f'icono_{n}.png').convert('RGB')
    fondo = Image.new('RGB', im.size, im.getpixel((5, 5)))
    caja = ImageChops.difference(im, fondo).convert('L').point(lambda v: 255 if v > 18 else 0).getbbox()
    im = im.crop(caja)
    # fondo a blanco puro sin tocar el dibujo
    blanco = Image.new('RGB', im.size, 'white')
    mascara = ImageChops.difference(im, Image.new('RGB', im.size, fondo.getpixel((0, 0)))).convert('L').point(lambda v: min(255, v * 6))
    return Image.composite(im, blanco, mascara)


def icono_rgba(n):
    """Icono con el fondo blanco convertido en transparencia (para fondos de color)."""
    im = icono_recortado(n).convert('RGBA'); px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]; m = min(r, g, b)
            if m > 235: px[x, y] = (r, g, b, int(255 * (255 - m) / 20))
    return im


def armar(n):
    W, H = 1600, 1600
    L = Image.new('RGB', (W, H), 'white')
    ic = icono_recortado(n)
    alto = 900 if ic.height > ic.width * 1.3 else 860
    ic = ic.resize((int(ic.width * alto / ic.height), alto), Image.LANCZOS)
    if ic.width > 1100:
        ic = ic.resize((1100, int(ic.height * 1100 / ic.width)), Image.LANCZOS)
    y = 150
    L.paste(ic, ((W - ic.width) // 2, y)); y += ic.height + 60
    nombre = ImageFont.truetype(str(F / 'Cormorant.ttf'), 150); nombre.set_variation_by_axes([600])
    y = texto(L, 'Cinthia Payán', nombre, y, [LILA, ROSA, TURQ]) + 2
    titulo = ImageFont.truetype(str(F / 'Cormorant.ttf'), 78); titulo.set_variation_by_axes([500])
    y = texto(L, 'Lic. Psicología', titulo, y, [(95, 85, 105), (95, 85, 105)]) + 28
    linea = ImageFont.truetype(str(F / 'Montserrat.ttf'), 44); linea.set_variation_by_axes([500])
    texto(L, 'ENTENDER · SANAR · CRECER', linea, y, [LILA, TURQ], espacio=9)
    caja = ImageChops.difference(L, Image.new('RGB', L.size, 'white')).getbbox()
    m = 110; L = L.crop((max(0, caja[0] - m), max(0, caja[1] - m), min(W, caja[2] + m), min(H, caja[3] + m)))
    lado = max(L.size); C = Image.new('RGB', (lado, lado), 'white'); C.paste(L, ((lado - L.width) // 2, (lado - L.height) // 2))
    (AQUI / 'logos').mkdir(exist_ok=True)
    C.save(AQUI / 'logos' / f'logo_cinthia_{n}.png')
    ic.save(AQUI / 'logos' / f'icono_solo_{n}.png')
    return C


if __name__ == '__main__':
    hechos = [armar(n) for n in (sys.argv[1:] or ['a1', 'b1', 'c2'])]
    hoja = Image.new('RGB', (600 * len(hechos), 600), 'white')
    for k, im in enumerate(hechos):
        hoja.paste(im.resize((600, 600), Image.LANCZOS), (600 * k, 0))
    hoja.save(AQUI / 'logos' / 'propuestas_logo_cinthia.jpg', quality=92)
