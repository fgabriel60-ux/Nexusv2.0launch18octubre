"""Pone el texto exacto (Montserrat) sobre los diseños sin texto de Qwen → estáticos finales 1080x1350 sin faltas."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
FUENTE = str(AQUI / 'fuentes' / 'Montserrat.ttf')
W, H = 1080, 1350
WA = (37, 211, 102)


def f(tam, peso='Black'):
    ft = ImageFont.truetype(FUENTE, tam); ft.set_variation_by_name(peso); return ft


def ajusta(d, txt, ancho, tam, peso):
    while d.textlength(txt, font=f(tam, peso)) > ancho and tam > 20:
        tam -= 2
    return f(tam, peso)


def linea(d, txt, y, tam, color, peso='Black', sombra=True):
    ft = ajusta(d, txt, W - 110, tam, peso)
    x = (W - d.textlength(txt, font=ft)) / 2
    if sombra:
        d.text((x + 3, y + 4), txt, font=ft, fill=(0, 0, 0, 170))
    d.text((x, y), txt, font=ft, fill=color)
    return y + int(ft.size * 1.12)


def degradado(img, arriba=430, abajo=330):
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    for y in range(arriba):
        d.line([(0, y), (W, y)], fill=(0, 0, 0, int(170 * (1 - y / arriba))))
    for y in range(H - abajo, H):
        d.line([(0, y), (W, y)], fill=(0, 0, 0, int(190 * (y - H + abajo) / abajo)))
    return Image.alpha_composite(img.convert('RGBA'), capa)


def boton(d, txt, y=H - 150):
    ft = ajusta(d, txt, W - 240, 46, 'ExtraBold')
    a = d.textlength(txt, font=ft) + 110
    d.rounded_rectangle(((W - a) / 2, y, (W + a) / 2, y + 104), 52, fill=WA)
    d.text(((W - a) / 2 + 55, y + 26), txt, font=ft, fill=(255, 255, 255))


BLANCO, ORO, TURQ, VERDE_CL = (255, 255, 255), (255, 206, 92), (90, 235, 205), (150, 240, 170)
PIEZAS = {
    'Servilin_1': (['GERENTE DE PLANTA:', '¿TU PERSONAL DE', 'LIMPIEZA FALTA?'], TURQ, 'Plantillas desde $16,000/mes por elemento · IMSS incluido', 'COTIZA: 56 3634 1441'),
    'Servilin_2': (['TU PLANTA', 'IMPECABLE', 'EN CADA TURNO'], TURQ, 'Personal capacitado, uniformado y con IMSS', 'COTIZA: 56 3634 1441'),
    'Servilin_3': (['JARDINERÍA', 'INDUSTRIAL'], TURQ, 'Áreas verdes de tu empresa siempre cuidadas', 'COTIZA: 56 3634 1441'),
    'RarAmore_1': (['MANTÉN TU RITMO', 'TODOS LOS DÍAS'], ORO, 'Colágeno · Magnesio · Calcio · Vitamina D', 'PIDE: 81 8466 8456'),
    'RarAmore_2': (['NUTRICIÓN DIARIA', 'PARA TUS', 'ARTICULACIONES'], ORO, 'Suplemento alimenticio · 2 cápsulas al día', 'PIDE: 81 8466 8456'),
    'RarAmore_3': (['TU BIENESTAR,', 'UN HÁBITO DIARIO'], ORO, 'Promoción por tiempo limitado · Envíos a todo México', 'PIDE: 81 8466 8456'),
    'Ortega_1': (['¿TE QUEDASTE', 'SIN TRABAJO?'], ORO, 'Tu Afore te puede dar hasta $35,192', 'ESCRÍBENOS POR WHATSAPP'),
    'Ortega_2': (['SIN ANTICIPOS'], ORO, 'Pagas cuando recibes tu dinero', 'ESCRÍBENOS POR WHATSAPP'),
    'Ortega_3': (['NO ESTÁS SOLO'], ORO, 'Desempleo · Pensión · RFC · Semanas · Mejoravit', 'ESCRÍBENOS POR WHATSAPP'),
    'Omar_1': (['¿CONOCES EL', 'MULTINIVEL?'], VERDE_CL, 'Red Natura · Omar · RIR 225430', 'WHATSAPP 56 5587 4031'),
    'Omar_2': (['+50 PRODUCTOS', 'PARA TODA', 'LA FAMILIA'], VERDE_CL, 'Control de peso · Detox · Nutrición', 'WHATSAPP 56 5587 4031'),
    'Omar_3': (['ÚNETE A', 'MI EQUIPO'], VERDE_CL, 'Te explico paso a paso cómo empezar', 'WHATSAPP 56 5587 4031'),
    'Mariano_1': (['VISTA AL MAR', 'Y CARRETERA NUEVA'], (120, 210, 255), 'Brescia · Siena · Catania · San Marino Residencial', 'AGENDA TU CITA'),
    'Mariano_2': (['SOLO NOS', 'QUEDAN 5'], (120, 210, 255), 'Te prometo que te va a encantar · Mariano Herrera', 'AGENDA TU CITA'),
    'Carlos_1': (['CONSEGUIR MENSAJES', 'YA NO ES UN PROBLEMA'], (120, 255, 150), 'Estrategia + videos calidad viral · Visión Agencia', 'AGENDA TU LLAMADA'),
    'Carlos_2': (['50 CONVERSACIONES', 'A $13.76'], (120, 255, 150), 'Solo acepto 5 clientes por semana · Visión Agencia', 'MÁNDAME MENSAJE'),
}

(AQUI / 'estaticos_finales').mkdir(exist_ok=True)
for nombre, (titulo, color, sub, cta) in PIEZAS.items():
    ruta = AQUI / 'salida' / f'{nombre}.png'
    if not ruta.exists():
        print('falta', nombre); continue
    img = Image.open(ruta).convert('RGB')
    esc = max(W / img.width, H / img.height)
    img = img.resize((round(img.width * esc), round(img.height * esc)), Image.LANCZOS)
    x = (img.width - W) // 2; img = img.crop((x, 0, x + W, H))
    img = degradado(img)
    d = ImageDraw.Draw(img)
    y = 60
    for k, t in enumerate(titulo):
        y = linea(d, t, y, 92, BLANCO if k < len(titulo) - 1 or len(titulo) == 1 else color)
    linea(d, sub, H - 260, 38, BLANCO, 'Bold')
    boton(d, cta)
    img.convert('RGB').save(AQUI / 'estaticos_finales' / f'{nombre}.jpg', quality=93)
    print('listo', nombre)
