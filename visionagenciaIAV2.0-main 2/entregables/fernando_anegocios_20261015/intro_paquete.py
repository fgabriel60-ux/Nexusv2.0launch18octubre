"""Intro 'lo que vendo': piezas reales del kit (recortadas de refs/fernando_image.jpg) aparecen con pop/rebote sobre el azul de su marca."""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
A = Path(__file__).resolve().parent
W, H = 720, 1280
FD = '/usr/share/fonts/truetype/dejavu/'
fnt = lambda s: ImageFont.truetype(FD + 'DejaVuSans-Bold.ttf', s)
AMAR = (255, 230, 0); NEGRO = (17, 17, 17); BLANCO = (255, 255, 255)
SRC = Image.open(A / 'refs' / 'fernando_image.jpg').convert('RGB')
# (clave, caja en la imagen, etiqueta, celda de destino cx, cy, alto máx)
PIEZAS = [('caja', (68, 352, 358, 762), 'Software 1 año', 185, 292, 205),
          ('lector', (360, 410, 636, 772), 'Lector', 535, 292, 205),
          ('impresora', (640, 455, 935, 765), 'Impresora', 185, 547, 205),
          ('rollos', (925, 470, 1215, 790), 'Rollos', 535, 547, 205)]
CHIPS = [('Instalación y capacitación', 742), ('Soporte 1 año', 797)]
INI = {'caja': 0.25, 'lector': 0.95, 'impresora': 1.65, 'rollos': 2.3, 'chip0': 2.9, 'chip1': 3.4, 'precio': 3.85}
LARGO = 5.0


def _pieza(caja, tam=(300, 190)):
    """Tarjeta con esquinas redondeadas: recorte ajustado de la foto real (cover) con borde blanco."""
    c = SRC.crop(caja); w, h = c.size; k = max(tam[0] / w, tam[1] / h)
    c = c.resize((round(w * k), round(h * k)), Image.LANCZOS)
    x, y = (c.width - tam[0]) // 2, (c.height - tam[1]) // 2; c = c.crop((x, y, x + tam[0], y + tam[1])).convert('RGBA')
    m = Image.new('L', tam, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, tam[0] - 1, tam[1] - 1), 30, fill=255)
    c.putalpha(m); ImageDraw.Draw(c).rounded_rectangle((1, 1, tam[0] - 2, tam[1] - 2), 30, outline=(255, 255, 255, 235), width=4); return c
CROP = {k: _pieza(b, (max(215, round((b[2] - b[0]) / (b[3] - b[1]) * hh)), hh)) for k, b, e_, cx_, cy_, hh in PIEZAS}
ease = lambda x: 1 - (1 - min(max(x, 0), 1)) ** 3
def pop(x):
    """0->1 con rebote (overshoot)."""
    x = min(max(x, 0), 1); return 1 + 2.4 * (x - 1) ** 3 + 1.4 * (x - 1) ** 2 if x < 1 else 1.0


def fondo():
    g = Image.new('RGB', (W, H)); d = ImageDraw.Draw(g)
    for y in range(H):
        k = y / H; d.line((0, y, W, y), fill=(int(8 + 6 * k), int(70 - 30 * k), int(185 - 55 * k)))
    return g.convert('RGBA')
FONDO = fondo()


def pastilla(capa, cx, cy, txt, f, escala):
    d = ImageDraw.Draw(capa); w = d.textlength(txt, font=f) + 44; h = f.size + 24
    s = Image.new('RGBA', (int(w) + 4, h + 4), (0, 0, 0, 0)); sd = ImageDraw.Draw(s)
    sd.rounded_rectangle((2, 2, w + 2, h + 2), h // 2, fill=AMAR); sd.text((w / 2 + 2, h / 2 + 2), txt, font=f, fill=NEGRO, anchor='mm')
    s = s.resize((max(1, int(s.width * escala)), max(1, int(s.height * escala))), Image.LANCZOS)
    capa.alpha_composite(s, (int(cx - s.width / 2), int(cy - s.height / 2)))


def frame(t):
    """t = segundos desde el inicio de la intro."""
    im = FONDO.copy(); capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    for clave, caja, etq, cx, cy, hmax in PIEZAS:
        e = pop((t - INI[clave]) / 0.45)
        if t < INI[clave]: continue
        c = CROP[clave]; esc = e
        p = c.resize((max(1, int(c.width * esc)), max(1, int(c.height * esc))), Image.LANCZOS)
        sh = Image.new('RGBA', p.size, (0, 0, 0, 0)); sh.putalpha(p.getchannel('A').point(lambda v: int(v * 0.35)))
        capa.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), (int(cx - p.width / 2), int(cy - p.height / 2 + 14)))
        capa.alpha_composite(p, (int(cx - p.width / 2), int(cy - p.height / 2)))
        pastilla(capa, cx, cy + hmax / 2 + 24, etq, fnt(26), pop((t - INI[clave] - 0.25) / 0.35))
    for i, (txt, y) in enumerate(CHIPS):
        k = INI[f'chip{i}']
        if t >= k: pastilla(capa, W // 2, y, txt, fnt(32), pop((t - k) / 0.4))
    tp = t - INI['precio']
    if tp >= 0:
        esc = pop(tp / 0.45) * (1 + 0.05 * math.sin(max(tp - 0.45, 0) * 9))
        pw, ph = 400 * esc, 104 * esc; cx, cy = W / 2, 890
        s = Image.new('RGBA', (int(pw), int(ph)), (0, 0, 0, 0)); sd = ImageDraw.Draw(s)
        sd.rounded_rectangle((0, 0, pw - 1, ph - 1), int(ph / 2), fill=AMAR)
        sd.text((pw / 2, ph / 2), '$3,500', font=fnt(max(10, int(70 * esc))), fill=NEGRO, anchor='mm')
        capa.alpha_composite(s, (int(cx - pw / 2), int(cy - ph / 2)))
    im.alpha_composite(capa); return im
