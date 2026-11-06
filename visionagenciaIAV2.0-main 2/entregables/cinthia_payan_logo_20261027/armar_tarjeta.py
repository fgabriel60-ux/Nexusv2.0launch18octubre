"""Tarjeta de presentación de Cinthia Payán (3.5x2 in a 600 dpi) + versión digital vertical.
Frente: icono B + nombre + «Lic. Psicología» + lema. Reverso: datos de la tarjeta blanca de Carlos y un tallo de peonía
(la apertura de la mente) que termina en la flor (el florecer).
Uso: python3 armar_tarjeta.py [verde] [clasica|moderna|suave]   (letras: Cormorant+Montserrat, Playfair+Quicksand, Lora+Josefin Sans)"""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageChops
from armar_logo import AQUI, F, LILA, ROSA, TURQ, degradado, icono_recortado, icono_rgba

W, H = 2100, 1200
NOMBRE = 'Cinthia Payán'
SERVICIOS = ['Acompañamiento en Adicciones', 'Terapia individual', 'Trastorno por Déficit de Atención\ne Hiperactividad (TDAH)',
             'Terapia de pareja y familia', 'Manejo de ansiedad y depresión']
FONDO = (255, 255, 255)
VERDE_PASTEL = (233, 245, 236)
VERDE_SUTIL = (244, 250, 245)
GRIS = (95, 85, 105)
OSCURA = False  # modo impresión: `python3 armar_tarjeta.py verde3 clasica oscura grande`
GRANDE = False  # letra más grande (5 nov 2026, Carlos)
ESCALA = (1.32, 1.16, 1.06)  # máximo que cabe sin que los servicios peguen con la columna de contacto
ANCHO_SERVICIOS = 1010 - 192  # hasta donde puede llegar un renglón antes de pegar con el contacto


def envolver(txt, f, ancho):
    """Parte un servicio en renglones que quepan en `ancho`.

    Con letra grande el límite de la tarjeta no es el alto sino el ancho: la línea más
    larga («Acompañamiento en Adicciones») ya llegaba a la columna de contacto. Partir
    por palabras cambia ancho por alto, que es lo que sobra en esa cara.
    """
    def mide(s):  # la misma métrica que usa `texto`: suma letra por letra, no la cadena
        return sum(f.getlength(c) for c in s) + 4
    out = []
    for parte in txt.split('\n'):
        linea = ''
        for palabra in parte.split():
            prueba = (linea + ' ' + palabra).strip()
            if linea and mide(prueba) > ancho:
                out.append(linea); linea = palabra
            else:
                linea = prueba
        if linea:
            out.append(linea)
    return out


def tinta(cols, tam):
    """Modo impresión (5 nov 2026, Carlos): baja la luminancia de la letra según su tamaño.

    En papel el texto chico con los colores de marca sale lavado, y el peor es el
    turquesa (40,160,155): a 600 dpi una letra de 30-40 px pone poquísima tinta por
    trazo y el fondo verde pastel le come el contraste. Los títulos grandes (112-140 px)
    sí aguantan el color tal cual, así que se oscurecen mucho menos y la tarjeta no
    pierde el tono de la marca.
    """
    if not OSCURA:
        return cols
    k = 0.60 if tam <= 45 else 0.76 if tam <= 80 else 0.88
    return [tuple(max(0, int(round(c * k))) for c in col) for col in cols]


FUENTES = AQUI / 'fuentes'
LETRAS = {'clasica': (F / 'Cormorant.ttf', F / 'Montserrat.ttf'),
          'moderna': (FUENTES / 'PlayfairDisplay.ttf', FUENTES / 'Quicksand.ttf'),
          'suave': (FUENTES / 'Lora.ttf', FUENTES / 'JosefinSans.ttf')}
SERIF, SANS = LETRAS['clasica']


def fuente(archivo, tam, peso):
    """«Cormorant.ttf» = letra de títulos y «Montserrat.ttf» = letra de texto de la variante activa.

    Con `grande`, el texto chico crece más que los títulos: es el que cuesta leer en una
    tarjeta de 3.5 x 2 pulgadas, y los títulos ya se leen de sobra. Crecer todo por igual
    desbordaría el reverso, que es la cara apretada.
    """
    if GRANDE:
        a, b, c = ESCALA
        tam = round(tam * (a if tam <= 45 else b if tam <= 80 else c))
    ruta = SERIF if archivo == 'Cormorant.ttf' else SANS if archivo == 'Montserrat.ttf' else F / archivo
    f = ImageFont.truetype(str(ruta), tam); ej = f.get_variation_axes()[0]
    f.set_variation_by_axes([max(ej['minimum'], min(ej['maximum'], peso))]); return f


def pin(L, x, y, alto=46):
    """Alfiler de ubicación: palito gris con puntito rojo."""
    esc = 3; g = Image.new('RGBA', (40 * esc, alto * esc)); d = ImageDraw.Draw(g)
    d.line((20 * esc, 14 * esc, 20 * esc, alto * esc), fill=(120, 115, 125, 255), width=4 * esc)
    d.ellipse((6 * esc, 0, 34 * esc, 28 * esc), fill=(222, 60, 70, 255))
    d.ellipse((12 * esc, 5 * esc, 19 * esc, 12 * esc), fill=(255, 190, 195, 255))
    g = g.resize((40, alto), Image.LANCZOS); L.paste(g, (x, y), g)


def texto(L, txt, f, xy, cols, centro=False, espacio=0):
    cols = tinta(cols, f.size)
    d = ImageDraw.Draw(L)
    anchos = [d.textlength(c, font=f) + espacio for c in txt]
    w = int(sum(anchos) - espacio) + 4; asc, desc = f.getmetrics(); h = asc + desc
    m = Image.new('L', (w, h)); dm = ImageDraw.Draw(m); x = 0
    for c, a in zip(txt, anchos):
        dm.text((x, 0), c, font=f, fill=255); x += a
    x0 = xy[0] - w // 2 if centro else xy[0] - f.getbbox(txt[0])[0]  # alinea el trazo, no la caja
    L.paste(degradado(w, h, cols) if len(cols) > 1 else Image.new('RGB', (w, h), cols[0]), (x0, xy[1]), m)
    return x0 + w, xy[1] + h


def tallo(L, puntos, grosor, cols):
    """Curva Catmull-Rom con degradado a lo largo del tallo."""
    pts = []
    P = [puntos[0]] + puntos + [puntos[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(40):
            t = k / 40
            pts.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in range(2)))
    pts.append(puntos[-1])
    esc = 3; grande = Image.new('L', (L.width * esc, L.height * esc)); d = ImageDraw.Draw(grande)
    d.line([(x * esc, y * esc) for x, y in pts], fill=255, width=grosor * esc, joint='curve')
    m = grande.resize(L.size, Image.LANCZOS)
    L.paste(degradado(L.width, L.height, cols), (0, 0), m)
    return pts


def hoja(L, base, angulo, largo, color):
    esc = 3; g = Image.new('L', (L.width * esc, L.height * esc)); d = ImageDraw.Draw(g)
    a = math.radians(angulo); n = (math.cos(a), math.sin(a)); p = (-n[1], n[0])
    contorno = []
    for k in range(21):
        t = k / 20; ancho = math.sin(math.pi * t) * largo * 0.28
        contorno.append(((base[0] + n[0] * largo * t + p[0] * ancho) * esc, (base[1] + n[1] * largo * t + p[1] * ancho) * esc))
    for k in range(20, -1, -1):
        t = k / 20; ancho = math.sin(math.pi * t) * largo * 0.28
        contorno.append(((base[0] + n[0] * largo * t - p[0] * ancho) * esc, (base[1] + n[1] * largo * t - p[1] * ancho) * esc))
    d.line(contorno + [contorno[0]], fill=255, width=4 * esc)
    d.line([(base[0] * esc, base[1] * esc), ((base[0] + n[0] * largo * 0.85) * esc, (base[1] + n[1] * largo * 0.85) * esc)], fill=255, width=3 * esc)
    L.paste(Image.new('RGB', L.size, color), (0, 0), g.resize(L.size, Image.LANCZOS))


def flor(L, centro, alto):
    fl = Image.open(AQUI / 'refs' / 'peonia_flor.png').convert('RGB')
    fl = fl.resize((int(fl.width * alto / fl.height), alto), Image.LANCZOS)
    x, y = centro[0] - fl.width // 2, centro[1] - fl.height // 2
    # la flor tapa la punta del tallo: máscara = qué tan lejos del blanco está cada pixel
    m = ImageChops.invert(fl.convert('L')).point(lambda v: min(255, v * 5))
    L.paste(fl, (x, y), m)


def logo_jayil(L, centro_x, y, alto):
    lg = Image.open(AQUI / 'refs' / 'jayil_logo.png'); lg = lg.resize((int(lg.width * alto / lg.height), alto), Image.LANCZOS)
    L.paste(lg, (centro_x - lg.width // 2, y), lg)
    return y + alto


def frente():
    L = Image.new('RGB', (W, H), FONDO)
    ic = icono_rgba('b2p'); ic = ic.resize((int(ic.width * 640 / ic.height), 640), Image.LANCZOS)
    L.paste(ic, ((W - ic.width) // 2, 90), ic)
    y = 90 + 640 + 45
    _, y = texto(L, NOMBRE, fuente('Cormorant.ttf', 140, 600), (W // 2, y), [LILA, ROSA, TURQ], centro=True)
    _, y = texto(L, 'Lic. Psicología', fuente('Cormorant.ttf', 70, 500), (W // 2, y + 2), [GRIS], centro=True)
    texto(L, 'ENTENDER · SANAR · CRECER', fuente('Montserrat.ttf', 38, 500), (W // 2, y + 28), [LILA, TURQ], centro=True, espacio=8)
    logo_jayil(L, W - 250, H - 330, 200)
    texto(L, 'Somos Jayil', fuente('Cormorant.ttf', 42, 600), (W - 250, H - 110), [LILA, ROSA, TURQ], centro=True)
    return L


def reverso():
    L = Image.new('RGB', (W, H), FONDO)
    # tallo: nace abajo a la izquierda, ondula por debajo de los datos y sube por la derecha hasta la peonía
    pts = [(-20, 1110), (300, 1060), (640, 1120), (980, 1050), (1330, 1095), (1620, 980), (1800, 760), (1830, 520), (1797, 300)]
    tallo(L, pts, 7, [TURQ, LILA, ROSA])
    hoja(L, (1700, 900), -150, 120, (120, 175, 150)); hoja(L, (1815, 620), -20, 110, (120, 175, 150)); hoja(L, (700, 1105), -60, 95, (150, 120, 180))
    flor(L, (1797, 195), 265)
    x0 = 150
    _, y = texto(L, 'Terapia Psicológica', fuente('Cormorant.ttf', 112, 600), (x0, 95), [LILA, ROSA, TURQ])
    _, y = texto(L, 'ADOLESCENTES Y ADULTOS', fuente('Montserrat.ttf', 36, 600), (x0, y + 5), [LILA, TURQ], espacio=6)
    y += 24 if GRANDE else 35
    f = fuente('Montserrat.ttf', 40, 400)
    for s in SERVICIOS:
        d = ImageDraw.Draw(L); d.ellipse((x0 + 4, y + 19, x0 + 17, y + 32), fill=tinta([ROSA], 40)[0])
        for renglon in (envolver(s, f, ANCHO_SERVICIOS) if GRANDE else s.split('\n')):
            _, y = texto(L, renglon, f, (x0 + 42, y), [GRIS]); y -= 2
        y += 12
    # columna de contacto
    cx = 1080; cy = 430 if GRANDE else 470
    d = ImageDraw.Draw(L); d.line((cx - 50, cy, cx - 50, cy + 400), fill=tinta([(215, 195, 225)], 46)[0], width=3)
    _, yy = texto(L, 'Agenda tu consulta', fuente('Cormorant.ttf', 66, 600), (cx, cy - 40), [LILA, TURQ])
    _, yy = texto(L, '(Modalidad presencial y virtual)', fuente('Montserrat.ttf', 30, 500), (cx, yy + 2), [LILA, TURQ])
    ft = fuente('Montserrat.ttf', 40, 500); fp = fuente('Montserrat.ttf', 34, 400)
    _, yy = texto(L, 'WhatsApp  631 132 9429', ft, (cx, yy + 26), [GRIS])
    pin(L, cx - 4, yy + 26)
    _, yy = texto(L, 'Calle Lago Espejo #69', fp, (cx + 48, yy + 26), [GRIS])
    _, yy = texto(L, 'Col. Jardines de la Montaña', fp, (cx + 48, yy + 4), [GRIS])
    _, yy = texto(L, 'Cédula Profesional 5455037', fp, (cx, yy + 26), [GRIS])
    _, yy = texto(L, 'Somos Jayil', fuente('Cormorant.ttf', 60, 600), (cx, yy + 22), [LILA, ROSA, TURQ])
    logo_jayil(L, cx + 400, yy - 75, 140)
    return L


if __name__ == '__main__':
    out = AQUI / 'tarjeta'; out.mkdir(exist_ok=True)
    import sys
    suf = ''
    MAS_VERDE = {'verde2': (222, 240, 227), 'verde3': (210, 234, 217), 'verde4': (196, 227, 206)}
    otro = [a for a in sys.argv if a in MAS_VERDE]
    if otro:
        FONDO = MAS_VERDE[otro[0]]; suf = '_' + otro[0]
    elif 'sutil' in sys.argv:
        FONDO = VERDE_SUTIL; suf = '_sutil'
    elif 'verde' in sys.argv:
        FONDO = VERDE_PASTEL; suf = '_verde'
    for v in LETRAS:
        if v in sys.argv:
            SERIF, SANS = LETRAS[v]; suf += '_' + v
    if 'oscura' in sys.argv:
        OSCURA = True; suf += '_oscura'
    if 'grande' in sys.argv:
        GRANDE = True; suf += '_grande'
    fr, rv = frente(), reverso()
    fr.save(out / f'tarjeta_frente{suf}_600dpi.png', dpi=(600, 600)); rv.save(out / f'tarjeta_reverso{suf}_600dpi.png', dpi=(600, 600))
    fr.save(out / f'tarjeta_cinthia{suf}_imprimir.pdf', save_all=True, append_images=[rv], resolution=600)
    # digital (para mandar por WhatsApp): ambas caras en vertical con sombra suave
    D = Image.new('RGB', (1080, 1350), (246, 241, 248) if not suf else (230, 241, 233) if 'sutil' in suf else (190, 220, 199) if 'verde4' in suf else (200, 225, 207) if 'verde3' in suf else (210, 231, 215) if 'verde2' in suf else (220, 236, 224)); s = 960 / W
    for k, cara in enumerate((fr, rv)):
        c = cara.resize((960, int(H * s)), Image.LANCZOS); y = 90 + k * (c.height + 70)
        sombra = Image.new('RGB', (c.width, c.height), (225, 215, 232)); D.paste(sombra, (66, y + 10)); D.paste(c, (60, y))
    D.save(out / f'tarjeta_cinthia{suf}_digital.jpg', quality=93)
