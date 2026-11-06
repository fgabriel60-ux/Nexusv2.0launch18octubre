"""Estáticos 4-6 (4:5, 1080x1350) para Omar · Red Natura con la fórmula de los flyers de Giovanni:
titular «TU ___ MERECE ___» en dos tonos + subtítulo + 3 tarjetas de datos + barra inferior + botón de WhatsApp. Foto a pantalla completa."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
FUENTE = str(AQUI.parent / 'modelos_modal' / 'fuentes' / 'Montserrat.ttf')
W, H = 1080, 1350
AZUL, AZUL2, ORO, VERDE, BLANCO = (8, 34, 92), (20, 70, 160), (255, 196, 70), (37, 211, 102), (255, 255, 255)


def fu(t, peso='Black'):
    f = ImageFont.truetype(FUENTE, t); f.set_variation_by_name(peso); return f


def ajusta(d, txt, tam, ancho, peso='Black'):
    while d.textlength(txt, font=fu(tam, peso)) > ancho: tam -= 2
    return fu(tam, peso)


def cubrir(ruta, dx=0.5, dy=0.15, zoom=1.0):
    im = Image.open(ruta).convert('RGB'); e = max(W / im.width, H / im.height) * zoom
    im = im.resize((round(im.width * e), round(im.height * e)), Image.LANCZOS)
    x, y = int((im.width - W) * dx), int((im.height - H) * dy); return im.crop((x, y, x + W, y + H))


def velo(img, lado):
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    for i in range(W if lado == 'izq' else H):
        a = int(238 * max(0.0, 1 - i / (800 if lado == 'izq' else 700)) ** 1.15)
        d.line([(i, 0), (i, H)] if lado == 'izq' else [(0, i), (W, i)], fill=(*AZUL, a))
    for y in range(H - 300, H):
        d.line([(0, y), (W, y)], fill=(*AZUL, int(235 * (y - (H - 300)) / 300)))
    return Image.alpha_composite(img.convert('RGBA'), capa).convert('RGB')


def velo_abajo(img):
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    for y in range(0, 200):
        d.line([(0, y), (W, y)], fill=(*AZUL, int(215 * (1 - y / 200) ** 1.3)))
    for y in range(480, H):
        d.line([(0, y), (W, y)], fill=(*AZUL, int(242 * min(1.0, (y - 480) / 330) ** 1.1)))
    return Image.alpha_composite(img.convert('RGBA'), capa).convert('RGB')


def titular(d, l1, l2, y, ancho=640, tam=112):
    f1 = ajusta(d, l1, tam, ancho); d.text((60, y), l1, font=f1, fill=BLANCO, stroke_width=2, stroke_fill=(0, 0, 0)); y += int(f1.size * 1.05)
    f2 = ajusta(d, l2, tam, ancho); d.text((60, y), l2, font=f2, fill=ORO, stroke_width=2, stroke_fill=(0, 0, 0)); return y + int(f2.size * 1.2)


def tarjetas(d, datos, y):
    """3 tarjetas con borde dorado: número/palabra grande + descripción."""
    ancho, sep, x = 300, 24, 60 if False else (W - 3 * 300 - 2 * 24) // 2
    for grande, chico in datos:
        d.rounded_rectangle((x, y, x + ancho, y + 230), 26, fill=(10, 24, 60), outline=ORO, width=4)
        f = ajusta(d, grande, 74, ancho - 30); d.text((x + (ancho - d.textlength(grande, font=f)) / 2, y + 28), grande, font=f, fill=BLANCO)
        for i, l in enumerate(chico):
            ff = ajusta(d, l, 27, ancho - 24, 'Bold'); d.text((x + (ancho - d.textlength(l, font=ff)) / 2, y + 128 + i * 38), l, font=ff, fill=ORO)
        x += ancho + sep
    return y + 230


def barra(d, items, y):
    d.rectangle((0, y, W, y + 90), fill=(6, 20, 56)); ancho = W // len(items)
    for i, t in enumerate(items):
        f = ajusta(d, t, 28, ancho - 24, 'ExtraBold'); d.text((i * ancho + (ancho - d.textlength(t, font=f)) / 2, y + 28), t, font=f, fill=BLANCO)


def boton(d, y):
    txt = 'ESCRÍBEME · 56 5587 4031'; f = fu(46, 'ExtraBold'); a = d.textlength(txt, font=f) + 110
    x = (W - a) / 2; d.rounded_rectangle((x, y, x + a, y + 104), 52, fill=VERDE); d.text((x + 55, y + 26), txt, font=f, fill=BLANCO)


def marca(d):
    d.text((60, 48), 'RED NATURA', font=fu(40, 'ExtraBold'), fill=BLANCO)
    d.text((60, 98), 'OMAR · DISTRIBUIDOR INDEPENDIENTE · RIR 225430', font=fu(22, 'Bold'), fill=(200, 215, 255))


def pieza(foto, dx, dy, lado, l1, l2, sub, datos, items, zoom=1.0):
    if lado == 'izq':   # sujeto a la derecha: texto a la izquierda
        if foto == 'omar_foto.jpg':
            base = Image.new('RGB', (W, H)); db = ImageDraw.Draw(base)
            for yy in range(H):
                t = yy / H; db.line([(0, yy), (W, yy)], fill=tuple(int(AZUL[i] * (1 - t) + AZUL2[i] * t) for i in range(3)))
            p = Image.open(AQUI / foto).convert('RGB'); e = 1250 / p.height; p = p.resize((int(p.width * e), 1250), Image.LANCZOS)
            base.paste(p, (W - p.width + 140, H - p.height)); img = velo(base, 'izq')
        else:
            img = velo(cubrir(AQUI / foto, dx, dy, zoom), 'izq')
        d = ImageDraw.Draw(img); marca(d)
        y = titular(d, l1, l2, 190, 520, 96)
        for i, l in enumerate(sub): d.text((60, y + i * 44), l, font=ajusta(d, l, 32, 520, 'Medium'), fill=BLANCO)
        tarjetas(d, datos, 700)
    else:               # sujeto al centro: cara libre arriba, texto abajo
        img = velo_abajo(cubrir(AQUI / foto, dx, dy, zoom)); d = ImageDraw.Draw(img); marca(d)
        y = titular(d, l1, l2, 560, 960, 92)
        for i, l in enumerate(sub): d.text((60, y - 6 + i * 38), l, font=fu(29, 'Medium'), fill=BLANCO)
        tarjetas(d, datos, 925 if False else 905)
    boton(d, 1000 if lado == 'izq' else 1168)
    if lado == 'izq': barra(d, items, H - 150)
    txt = 'Información sin compromiso. Resultados varían por persona.'
    d.text((W / 2 - d.textlength(txt, font=fu(20, 'Medium')) / 2, H - 38 if lado == 'izq' else H - 48), txt, font=fu(20, 'Medium'), fill=(190, 205, 240))
    return img


piezas = [
    pieza('omar_foto.jpg', 0.5, 0.0, 'izq', 'TU FAMILIA', 'MERECE CUIDARSE', ['Más de 50 productos naturales', 'para toda la familia. Te explico', 'paso a paso, sin compromiso.'],
          [('+50', ['PRODUCTOS', 'NATURALES']), ('DETOX', ['CONTROL DE PESO', 'Y NUTRICIÓN']), ('1 A 1', ['TE EXPLICO', 'POR WHATSAPP'])], ['ASESORÍA PERSONAL', 'SIN COMPROMISO', 'POR WHATSAPP'], zoom=1.0),
    pieza('cuadros/O1.png', 0.5, 0.0, 'abajo', 'TU TIEMPO', 'MERECE UN PLAN', ['Conoce el multinivel con Red Natura.', 'Te cuento cómo funciona,', 'sin presión y sin compromiso.'],
          [('6', ['FORMAS DE', 'GENERAR INGRESOS']), ('+50', ['PRODUCTOS', 'PARA VENDER']), ('0', ['PRESIÓN, TODO', 'SIN COMPROMISO'])], ['MULTINIVEL', 'RED NATURA', 'EMPIEZA HOY']),
    pieza('cuadros/O2.png', 0.5, 0.0, 'abajo', 'TU FUTURO', 'MERECE UN EQUIPO', ['Únete a mi equipo de Red Natura.', 'Ventas, clientes preferentes', 'y comisiones de equipo.'],
          [('3', ['TIPOS DE', 'GANANCIA']), ('EQUIPO', ['TE ACOMPAÑO', 'PASO A PASO']), ('YA', ['ESCRÍBEME', 'POR WHATSAPP'])], ['VENTAS PERSONALES', 'CLIENTES PREFERENTES', 'COMISIONES']),
]
for i, im in enumerate(piezas, 4):
    r = AQUI / 'estaticos' / f'Omar_RedNatura_estatico_{i}.jpg'; im.save(r, quality=92); print(r.name)
