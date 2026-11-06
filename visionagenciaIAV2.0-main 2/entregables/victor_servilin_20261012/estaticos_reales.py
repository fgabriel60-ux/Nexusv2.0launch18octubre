"""Estáticos 4:5 (1080x1350) de Servilin con fotos reales del equipo de Victor."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
R = AQUI / 'reenviados'
NEGRITA = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
NORMAL = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
W, H = 1080, 1350
NAVY, TURQ, BLANCO, NARANJA, VERDE_WA = (13, 32, 44), (38, 191, 170), (255, 255, 255), (245, 140, 40), (37, 211, 102)
LOGO = Image.open(R / '017_image.jpg').convert('RGB')


def cubrir(ruta, dy=0.5):
    im = Image.open(ruta).convert('RGB')
    esc = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * esc), round(im.height * esc)), Image.LANCZOS)
    x = (im.width - W) // 2; y = int((im.height - H) * dy)
    return im.crop((x, y, x + W, y + H))


def degradado(img, desde, hasta, alfa_max=235, abajo=True):
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    for y in range(desde, hasta):
        t = (y - desde) / (hasta - desde)
        a = int(alfa_max * (t if abajo else 1 - t))
        d.line([(0, y), (W, y)], fill=(*NAVY, a))
    return Image.alpha_composite(img.convert('RGBA'), capa).convert('RGB')


def ajustada(d, txt, fuente, ancho, tam):
    while d.textlength(txt, font=ImageFont.truetype(fuente, tam)) > ancho:
        tam -= 2
    return ImageFont.truetype(fuente, tam)


def lineas(d, textos, y, tam, color, fuente=NEGRITA, x=60):
    for t in textos:
        f = ajustada(d, t, fuente, W - 2 * x, tam)
        d.text((x, y), t, font=f, fill=color, stroke_width=2 if fuente == NEGRITA else 0, stroke_fill=NAVY)
        y += int(f.size * 1.2)
    return y


def logo(img):
    tarjeta = Image.new('RGB', (440, 160), BLANCO)
    l = LOGO.copy(); l.thumbnail((410, 140))
    tarjeta.paste(l, ((440 - l.width) // 2, (160 - l.height) // 2))
    m = Image.new('L', tarjeta.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 439, 159), 26, fill=255)
    img.paste(tarjeta, (W - 440 - 40, 40), m)


def boton(d, y):
    f = ImageFont.truetype(NEGRITA, 44)
    txt = 'Cotiza por WhatsApp 56 3634 1441'
    a = d.textlength(txt, font=f) + 90
    d.rounded_rectangle(((W - a) / 2, y, (W + a) / 2, y + 96), 48, fill=VERDE_WA)
    d.text(((W - a) / 2 + 45, y + 24), txt, font=f, fill=BLANCO)


def sellos(d, y, textos):
    f = ImageFont.truetype(NEGRITA, 30)
    x = 60
    for t in textos:
        a = d.textlength(t, font=f) + 44
        d.rounded_rectangle((x, y, x + a, y + 60), 30, fill=TURQ)
        d.text((x + 22, y + 13), t, font=f, fill=NAVY)
        x += a + 16


def pieza(foto, dy, arriba, abajo, chips, y_titulo=230):
    img = cubrir(R / foto, dy)
    img = degradado(img, 0, 520, 230, abajo=False)
    img = degradado(img, 700, H, 245, abajo=True)
    logo(img)
    d = ImageDraw.Draw(img)
    lineas(d, arriba, y_titulo, 76, BLANCO)
    y = lineas(d, abajo[:1], max(860, y_titulo + 220), 54, (120, 240, 220))
    y = lineas(d, abajo[1:], y + 4, 38, BLANCO, NORMAL)
    sellos(d, y + 18, chips)
    boton(d, H - 140)
    return img


PIEZAS = [
    ('../flyers_modal/foto_mejorada_F1.png', 0.55, ['GERENTE DE PLANTA:', '¿TU PERSONAL DE', 'LIMPIEZA FALTA?'],
     ['Plantillas desde $16,000/mes por elemento', 'Nosotros cubrimos IMSS, prestaciones y supervisión.'],
     ['IMSS al corriente', 'Certificación ISO']),
    ('../flyers_modal/foto_mejorada_F2.png', 0.55, ['TU PLANTA IMPECABLE', 'EN CADA TURNO'],
     ['Personal capacitado y uniformado', 'Procesos estandarizados: el mismo resultado siempre.'],
     ['Limpieza industrial', 'Supervisión']),
    ('../flyers_modal/foto_mejorada_F3.png', 0.35, ['JARDINERÍA', 'INDUSTRIAL'],
     ['Áreas verdes siempre cuidadas', 'Diseño, poda y mantenimiento para tu empresa.'],
     ['Jardinería', 'Mantenimiento'], 640),
]
for i, (foto, dy, arriba, abajo, chips, *resto) in enumerate(PIEZAS, 1):
    ruta = AQUI / 'estaticos_reales' / f'Servilin_flyer_modal_{i}.jpg'
    pieza(foto, dy, arriba, abajo, chips, *resto).save(ruta, quality=92)
    print(ruta.name)
