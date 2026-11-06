"""Estáticos (4:5, 1080x1350) para Omar · Red Natura, con su foto y los cuadros de la oficina."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = Path(__file__).resolve().parent
NEGRITA = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
NORMAL = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
W, H = 1080, 1350
AZUL, AZUL2, ORO, VERDE, BLANCO = (8, 34, 92), (20, 70, 160), (255, 196, 70), (37, 211, 102), (255, 255, 255)


def fondo():
    img = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(AZUL[i] * (1 - t) + AZUL2[i] * t) for i in range(3)))
    return img


def foto(ruta, alto, recorte_arriba=0.0):
    im = Image.open(ruta).convert('RGB')
    esc = alto / im.height
    im = im.resize((int(im.width * esc), alto), Image.LANCZOS)
    return im


def cubrir(ruta, dx=0.5, dy=0.0):
    im = Image.open(ruta).convert('RGB')
    esc = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * esc), round(im.height * esc)), Image.LANCZOS)
    x = int((im.width - W) * dx); y = int((im.height - H) * dy)
    return im.crop((x, y, x + W, y + H))


def sobre_fondo(ruta, alto, x_rel):
    """Foto completa a la altura dada, sobre un fondo desenfocado de la misma imagen (sin bordes duros)."""
    base = cubrir(ruta).filter(ImageFilter.GaussianBlur(28))
    p = foto(ruta, alto)
    mascara = Image.new('L', p.size, 255)
    dm = ImageDraw.Draw(mascara)
    for i in range(60):
        v = int(255 * i / 60)
        dm.rectangle((i, i, p.width - 1 - i, p.height + 200), outline=v)
    x = int(W * x_rel - p.width / 2)
    base.paste(p, (x, H - p.height), mascara)
    return base


def degradado(img, lado):
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    if lado == 'izq':
        for x in range(W):
            a = int(235 * max(0.0, 1 - x / 760) ** 1.2)
            d.line([(x, 0), (x, H)], fill=(*AZUL, a))
    else:
        for y in range(H):
            a = int(240 * max(0.0, 1 - y / 640) ** 1.1) if y < 640 else 0
            d.line([(0, y), (W, y)], fill=(*AZUL, a))
        for y in range(H - 260, H):
            a = int(220 * (y - (H - 260)) / 260)
            d.line([(0, y), (W, y)], fill=(*AZUL, a))
    return Image.alpha_composite(img.convert('RGBA'), capa).convert('RGB')


def texto_ajustado(d, txt, fuente, ancho_max, tam):
    while d.textlength(txt, font=ImageFont.truetype(fuente, tam)) > ancho_max:
        tam -= 2
    return ImageFont.truetype(fuente, tam)


def bloque(d, lineas, x, y, ancho, tam, color, fuente=NEGRITA, salto=1.18):
    for l in lineas:
        f = texto_ajustado(d, l, fuente, ancho, tam)
        d.text((x, y), l, font=f, fill=color)
        y += int(f.size * salto)
    return y


def boton(d, y, x=60):
    f = ImageFont.truetype(NEGRITA, 46)
    txt = 'WhatsApp 56 5587 4031'
    a = d.textlength(txt, font=f) + 100
    d.rounded_rectangle((x, y, x + a, y + 100), 50, fill=VERDE)
    d.text((x + 50, y + 25), txt, font=f, fill=BLANCO)


def marca(d):
    d.text((60, 55), 'RED NATURA', font=ImageFont.truetype(NEGRITA, 44), fill=BLANCO)
    d.text((60, 108), 'Omar · Distribuidor independiente', font=ImageFont.truetype(NORMAL, 30), fill=(200, 215, 255))


def pieza1():
    base = fondo()
    p = foto(AQUI / 'omar_foto.jpg', 1250)
    base.paste(p, (W - p.width + 140, H - p.height))
    img = degradado(base.filter(ImageFilter.GaussianBlur(0)), 'izq')
    d = ImageDraw.Draw(img)
    marca(d)
    y = bloque(d, ['¿CONOCES EL', 'MULTINIVEL?'], 60, 330, 560, 92, BLANCO)
    y = bloque(d, ['Tu libertad financiera', 'puede empezar hoy.'], 60, y + 40, 560, 50, ORO)
    bloque(d, ['Te explico paso a paso,', 'sin compromiso.'], 60, y + 40, 560, 38, BLANCO, NORMAL)
    boton(d, 1170)
    return img


def pieza2():
    img = degradado(sobre_fondo(AQUI / 'cuadros' / 'O1.png', 900, 0.5), 'arriba')
    d = ImageDraw.Draw(img)
    marca(d)
    y = bloque(d, ['+50 PRODUCTOS PARA', 'TODA LA FAMILIA'], 60, 190, W - 120, 74, BLANCO)
    bloque(d, ['Control de peso · Detox · Nutrición'], 60, y + 20, W - 120, 46, ORO)
    boton(d, 1200, (W - 760) // 2)
    return img


def pieza3():
    img = degradado(sobre_fondo(AQUI / 'cuadros' / 'O2.png', 1350, 0.82), 'izq')
    d = ImageDraw.Draw(img)
    marca(d)
    y = bloque(d, ['6 FORMAS', 'DE GENERAR', 'INGRESOS'], 60, 300, 580, 96, BLANCO)
    y = bloque(d, ['Ventas personales', 'Clientes preferentes', 'Comisiones de equipo'], 60, y + 40, 560, 42, ORO)
    bloque(d, ['Únete a mi equipo.'], 60, y + 30, 560, 44, BLANCO)
    boton(d, 1170)
    return img


for i, f in enumerate((pieza1, pieza2, pieza3), 1):
    ruta = AQUI / 'estaticos' / f'Omar_RedNatura_estatico_{i}.jpg'
    f().save(ruta, quality=92)
    print(ruta.name)
