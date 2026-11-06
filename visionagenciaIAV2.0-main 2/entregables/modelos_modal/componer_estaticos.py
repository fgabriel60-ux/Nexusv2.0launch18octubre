"""Estáticos finales: fondo Qwen-Image + persona/producto recortado (rembg) o foto en tarjeta + texto exacto Montserrat."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from rembg import new_session, remove

AQUI = Path(__file__).resolve().parent
E = AQUI.parent
FUENTE = str(AQUI / 'fuentes' / 'Montserrat.ttf')
W, H = 1080, 1350
WA = (37, 211, 102)
SES_P = new_session('u2net_human_seg')
SES_G = new_session('isnet-general-use')


def f(tam, peso='Black'):
    ft = ImageFont.truetype(FUENTE, tam); ft.set_variation_by_name(peso); return ft


def cubrir(ruta):
    im = Image.open(ruta).convert('RGB')
    esc = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * esc), round(im.height * esc)), Image.LANCZOS)
    x = (im.width - W) // 2; y = (im.height - H) // 2
    return im.crop((x, y, x + W, y + H))


def recorte(ruta, persona=True, alto=920):
    im = Image.open(ruta).convert('RGB')
    m = remove(im, session=SES_P if persona else SES_G, only_mask=True, post_process_mask=True).convert('L')
    caja = m.getbbox(); im, m = im.crop(caja), m.crop(caja)
    esc = alto / im.height
    im = im.resize((int(im.width * esc), alto), Image.LANCZOS); m = m.resize(im.size, Image.LANCZOS)
    rgba = im.convert('RGBA'); rgba.putalpha(m); return rgba


def pegar_sujeto(base, suj, color, abajo=150):
    x = (W - suj.width) // 2; y = H - suj.height - abajo
    sombra = Image.new('RGBA', base.size, (0, 0, 0, 0))
    a = suj.split()[3].filter(ImageFilter.GaussianBlur(18))
    glow = Image.new('RGBA', suj.size, (*color, 0)); glow.putalpha(a.point(lambda v: int(v * 0.55)))
    sombra.paste(glow, (x, y), glow)
    base = Image.alpha_composite(base, sombra.filter(ImageFilter.GaussianBlur(10)))
    base.alpha_composite(suj, (x, y)); return base


def tarjeta(base, ruta, color, alto=760, y=360):
    im = Image.open(ruta).convert('RGB'); esc = alto / im.height
    im = im.resize((int(im.width * esc), alto), Image.LANCZOS)
    if im.width > W - 120:
        x0 = (im.width - (W - 120)) // 2; im = im.crop((x0, 0, x0 + W - 120, alto))
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), 36, fill=255)
    x = (W - im.width) // 2
    marco = Image.new('RGBA', (im.width + 16, im.height + 16), (0, 0, 0, 0))
    ImageDraw.Draw(marco).rounded_rectangle((0, 0, marco.width - 1, marco.height - 1), 44, fill=(*color, 255))
    base.alpha_composite(marco.filter(ImageFilter.GaussianBlur(2)), (x - 8, y - 8))
    rgba = im.convert('RGBA'); rgba.putalpha(m); base.alpha_composite(rgba, (x, y)); return base


def velos(base):
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    for y in range(420):
        d.line([(0, y), (W, y)], fill=(0, 0, 0, int(175 * (1 - y / 420))))
    for y in range(H - 360, H):
        d.line([(0, y), (W, y)], fill=(0, 0, 0, int(205 * (y - H + 360) / 360)))
    return Image.alpha_composite(base, capa)


def texto(img, titulo, color, sub, cta):
    d = ImageDraw.Draw(img)
    y = 54
    for k, t in enumerate(titulo):
        tam = 96
        while d.textlength(t, font=f(tam)) > W - 100: tam -= 2
        ft = f(tam); x = (W - d.textlength(t, font=ft)) / 2
        d.text((x + 3, y + 4), t, font=ft, fill=(0, 0, 0, 160))
        d.text((x, y), t, font=ft, fill=color if k == len(titulo) - 1 and len(titulo) > 1 else (255, 255, 255))
        y += int(ft.size * 1.1)
    tam = 38
    while d.textlength(sub, font=f(tam, 'Bold')) > W - 100: tam -= 2
    ft = f(tam, 'Bold'); d.text(((W - d.textlength(sub, font=ft)) / 2, H - 250), sub, font=ft, fill=(255, 255, 255))
    tam = 46
    while d.textlength(cta, font=f(tam, 'ExtraBold')) > W - 260: tam -= 2
    ft = f(tam, 'ExtraBold'); a = d.textlength(cta, font=ft) + 110
    d.rounded_rectangle(((W - a) / 2, H - 160, (W + a) / 2, H - 56), 52, fill=WA)
    d.text(((W - a) / 2 + 55, H - 134), cta, font=ft, fill=(255, 255, 255))
    return img


TQ, ORO, AZ, VC, NE, AR = (90, 235, 205), (255, 206, 92), (120, 210, 255), (150, 240, 170), (120, 255, 150), (255, 190, 120)
SV, RA, OR, OM, MA, CA, LI = [AQUI / 'fondos' / f'{n}.png' for n in ('servilin', 'rar', 'ortega', 'omar', 'mariano', 'carlos', 'lisbeth')]
V = E / 'victor_servilin_20261012' / 'flyers_modal'
PIEZAS = [
    ('Servilin_1', SV, ('tarjeta', V / 'foto_mejorada_F1.png'), TQ, ['GERENTE DE PLANTA:', '¿TU PERSONAL', 'DE LIMPIEZA FALTA?'], 'Plantillas desde $16,000/mes por elemento · IMSS incluido', 'COTIZA: 56 3634 1441'),
    ('Servilin_2', SV, ('tarjeta', V / 'foto_mejorada_F2.png'), TQ, ['TU PLANTA IMPECABLE', 'EN CADA TURNO'], 'Personal capacitado, uniformado y con IMSS', 'COTIZA: 56 3634 1441'),
    ('Servilin_3', SV, ('tarjeta', V / 'foto_mejorada_F3.png'), TQ, ['JARDINERÍA', 'INDUSTRIAL'], 'Áreas verdes de tu empresa siempre cuidadas', 'COTIZA: 56 3634 1441'),
    ('RarAmore_1', RA, ('producto', E / '360salud_cartilago_20261013' / 'cuadros' / 'J5.png'), ORO, ['MANTÉN TU RITMO', 'TODOS LOS DÍAS'], 'Colágeno · Magnesio · Calcio · Vitamina D', 'PIDE: 81 8466 8456'),
    ('RarAmore_2', RA, ('producto', E / '360salud_cartilago_20261013' / 'cuadros_manos' / 'Z4.png'), ORO, ['NUTRICIÓN DIARIA', 'PARA TUS ARTICULACIONES'], 'Suplemento alimenticio · 2 cápsulas al día', 'PIDE: 81 8466 8456'),
    ('Ortega_1', OR, ('persona', E / 'caminando_20261013' / 'cuadros' / 'M1A.png'), ORO, ['¿TE QUEDASTE', 'SIN TRABAJO?'], 'Tu Afore te puede dar hasta $35,192', 'ESCRÍBENOS POR WHATSAPP'),
    ('Ortega_2', OR, ('persona', E / 'caminando_20261013' / 'cuadros' / 'M3B.png'), ORO, ['SIN ANTICIPOS'], 'Pagas cuando recibes tu dinero · Asesoría sin costo', 'ESCRÍBENOS POR WHATSAPP'),
    ('Omar_1', OM, ('persona', E / 'omar_20261013' / 'omar_foto.jpg'), VC, ['¿CONOCES EL', 'MULTINIVEL?'], 'Red Natura · Omar · RIR 225430', 'WHATSAPP 56 5587 4031'),
    ('Omar_2', OM, ('persona', E / 'caminando_20261013' / 'cuadros' / 'O2A.png'), VC, ['ÚNETE A', 'MI EQUIPO'], 'Control de peso · Detox · Nutrición · +50 productos', 'WHATSAPP 56 5587 4031'),
    ('Mariano_1', MA, ('persona', E / 'mariano_helicoptero_20261013' / 'cuadros' / 'H5.png'), AZ, ['SOLO NOS', 'QUEDAN 5'], 'Brescia · Siena · Catania · San Marino Residencial', 'AGENDA TU CITA'),
    ('Carlos_1', CA, ('persona', E / 'carlos_vision_20261013' / 'fotos' / '04_First_frame_v4.jpg'), NE, ['CONSEGUIR MENSAJES', 'YA NO ES PROBLEMA'], 'Estrategia + videos calidad viral · Visión Agencia', 'AGENDA TU LLAMADA'),
    ('Carlos_2', CA, ('persona', E / 'carlos_vision_20261013' / 'fotos' / '03_First_frame_v5.jpg'), NE, ['SOLO 5 CLIENTES', 'POR SEMANA'], '50 conversaciones a $13.76 en mi campaña', 'MÁNDAME MENSAJE'),
    ('Lisbeth_1', LI, ('tarjeta', E / 'lisbeth_20261013' / 'anterior' / 'lisbeth' / 'S2_fin.png'), AR, ['NO ES COMPRAR UN TERRENO,', 'ES COMPRAR EL CORRECTO'], 'Terreno en la costa · Zona con proyección', 'PIDE INFORMACIÓN'),
    ('Lisbeth_2', LI, ('tarjeta', E / 'lisbeth_20261013' / 'anterior' / 'lisbeth' / 'S6_fin.png'), AR, ['CONSTRUYE', 'TU CASA FRENTE AL MAR'], 'Medidas equilibradas · Cerca del nuevo desarrollo', 'PIDE INFORMACIÓN'),
]
(AQUI / 'estaticos_finales').mkdir(exist_ok=True)
for nombre, fondo, (tipo, ruta), color, titulo, sub, cta in PIEZAS:
    base = cubrir(fondo).filter(ImageFilter.GaussianBlur(1.2)).convert('RGBA')
    base = velos(base)
    if tipo == 'tarjeta':
        base = tarjeta(base, ruta, color)
    else:
        base = pegar_sujeto(base, recorte(ruta, tipo == 'persona', 900 if tipo == 'persona' else 760), color)
    base = texto(base, titulo, color, sub, cta)
    base.convert('RGB').save(AQUI / 'estaticos_finales' / f'{nombre}.jpg', quality=93)
    print('listo', nombre, flush=True)
