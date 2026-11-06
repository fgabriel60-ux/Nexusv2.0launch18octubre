"""Imágenes de la semana de posts de Anegocios (plan de Glimmer, SEMANA_POSTS_GLIMMER.md) con material real de Fernando.
Feed 1080x1350 (4:5) e historias/portada 1080x1920. Sale en imagenes/."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

AQUI = Path(__file__).resolve().parent; M = AQUI.parent / 'whatsapp' / 'del_cliente'; OUT = AQUI / 'imagenes'; OUT.mkdir(exist_ok=True)
FU = Path('/workspaces/Nexusv2.0launch18octubre/clientes/Carlos_Nexus/pixar/fonts')
NAVY, AZUL, BLANCO = (16, 24, 58), (59, 91, 219), (255, 255, 255)
GRAD = [(250, 176, 64), (236, 72, 153), (139, 92, 246), (59, 130, 246)]  # colores del check del logo


def f(n, t): return ImageFont.truetype(str(FU / n), t)


def degr(w, h, cols, vertical=False):
    g = Image.new('RGB', (w, h)); d = ImageDraw.Draw(g); n = h if vertical else w
    for i in range(n):
        t = i / max(n - 1, 1) * (len(cols) - 1); k = min(int(t), len(cols) - 2); u = t - k
        c = tuple(int(cols[k][j] + (cols[k + 1][j] - cols[k][j]) * u) for j in range(3))
        d.line((0, i, w, i) if vertical else (i, 0, i, h), fill=c)
    return g


def logo():
    im = Image.open(M / '1015_220059_image.jpg').convert('RGB').crop((122, 512, 488, 585))
    im = im.resize((300, int(300 * im.height / im.width)), Image.LANCZOS).convert('RGBA'); px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if min(r, g, b) > 225: px[x, y] = (r, g, b, 0)
    return im
LOGO = logo()


def cubrir(im, w, h, foco=0.4):
    im = im.convert('RGB'); s = max(w / im.width, h / im.height); im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    x = (im.width - w) // 2; y = int((im.height - h) * foco); return im.crop((x, y, x + w, y + h))


def sombra_abajo(L, desde=0.45, fuerza=235):
    w, h = L.size; m = Image.new('L', (1, h))
    for y in range(h): m.putpixel((0, y), int(fuerza * max(0, (y / h - desde) / (1 - desde)) ** 1.3))
    L.paste(Image.new('RGB', (w, h), NAVY), (0, 0), m.resize((w, h)))


def texto(L, xy, s, fuente, color=BLANCO, ancho=None, inter=1.1):
    d = ImageDraw.Draw(L); x, y = xy; palabras = s.split(); linea = ''; lineas = []
    for p in palabras:
        prueba = (linea + ' ' + p).strip()
        if ancho and d.textlength(prueba, font=fuente) > ancho and linea: lineas.append(linea); linea = p
        else: linea = prueba
    lineas.append(linea)
    for ln in lineas:
        d.text((x, y), ln, font=fuente, fill=color); y += int(fuente.size * inter)
    return y


def barra_marca(L, y=None, chip=True):
    w, h = L.size
    if chip:
        c = Image.new('RGBA', (LOGO.width + 56, LOGO.height + 34)); ImageDraw.Draw(c).rounded_rectangle((0, 0, c.width - 1, c.height - 1), radius=c.height // 2, fill=(255, 255, 255, 240))
        c.alpha_composite(LOGO, (28, 17)); L.paste(c, (60, 60), c)
    L.paste(degr(w, 12, GRAD), (0, h - 12))


def boton(L, xy, s, alto=86):
    d = ImageDraw.Draw(L); fu = f('Inter-Bold.ttf', 38); w = int(d.textlength(s, font=fu)) + 110
    b = degr(w, alto, [(37, 211, 102), (18, 140, 126)]); m = Image.new('L', (w, alto)); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, alto - 1), radius=alto // 2, fill=255)
    L.paste(b, xy, m); ImageDraw.Draw(L).text((xy[0] + 55, xy[1] + (alto - 46) // 2), s, font=fu, fill=BLANCO)


def producto(L, ruta, caja, recorte=None):
    """Foto de producto (fondo claro de tienda) dentro de una tarjeta blanca redondeada con sombra."""
    im = Image.open(ruta).convert('RGB')
    if recorte: im = im.crop(recorte)
    pad = 34; im.thumbnail((caja[2] - 2 * pad, caja[3] - 2 * pad), Image.LANCZOS)
    t = Image.new('RGB', (im.width + 2 * pad, im.height + 2 * pad), im.getpixel((3, 3))); t.paste(im, (pad, pad))
    m = Image.new('L', t.size); ImageDraw.Draw(m).rounded_rectangle((0, 0, t.width - 1, t.height - 1), radius=36, fill=255)
    x = caja[0] + (caja[2] - t.width) // 2; y = caja[1] + (caja[3] - t.height) // 2
    sh = Image.new('RGBA', (t.width + 120, t.height + 120)); ImageDraw.Draw(sh).rounded_rectangle((60, 80, t.width + 60, t.height + 80), radius=40, fill=(0, 0, 0, 140))
    sh = sh.filter(ImageFilter.GaussianBlur(28)); L.paste(sh, (x - 60, y - 60), sh); L.paste(t, (x, y), m)


def puntos(L, n, act):
    d = ImageDraw.Draw(L); w = L.width; x0 = w // 2 - (n * 34) // 2
    for i in range(n): d.ellipse((x0 + i * 34, 1290, x0 + i * 34 + 16, 1306), fill=BLANCO if i == act else (255, 255, 255, 110))


def titulo_abajo(L, tit, sub, y0=None):
    w, h = L.size; ft = f('InterDisplay-Black.ttf', 96); fs = f('Inter-Medium.ttf', 44)
    d = ImageDraw.Draw(L); lineas = 2 if d.textlength(tit, font=ft) > w - 140 else 1
    y = y0 or (h - 140 - lineas * 106 - 70)
    y = texto(L, (70, y), tit, ft, ancho=w - 140, inter=1.06); L.paste(degr(160, 10, GRAD), (72, y + 14)); texto(L, (70, y + 46), sub, fs, (220, 228, 255), ancho=w - 140)


# ---------- LUNES · carrusel ----------
W, H = 1080, 1350
s1 = cubrir(Image.open(M / '1021_014549_image.jpg'), W, H, 0.35); sombra_abajo(s1, 0.38); barra_marca(s1)
titulo_abajo(s1, 'Controla tu inventario hoy', 'Sin libreta, sin Excel, sin estrés'); puntos(s1, 4, 0); s1.save(OUT / 'lunes_1.jpg', quality=93)

s2 = degr(W, H, [(22, 34, 84), NAVY], vertical=True); producto(s2, M / 'image_08_10-20_1842.jpg', (240, 190, 600, 640), recorte=(40, 0, 504, 688)); barra_marca(s2)
titulo_abajo(s2, 'Escanea y vende en segundos', 'Precio y existencia al instante'); puntos(s2, 4, 1); s2.save(OUT / 'lunes_2.jpg', quality=93)

s3 = degr(W, H, [(22, 34, 84), NAVY], vertical=True)
pan = Image.open(M / 'doc_06.png').convert('RGB'); pan.thumbnail((940, 600), Image.LANCZOS)
marco = Image.new('RGB', (pan.width + 36, pan.height + 36), (8, 10, 22)); marco.paste(pan, (18, 18))
sm = Image.new('RGBA', (marco.width + 120, marco.height + 120)); ImageDraw.Draw(sm).rectangle((60, 80, marco.width + 60, marco.height + 80), fill=(0, 0, 0, 150)); sm = sm.filter(ImageFilter.GaussianBlur(30))
s3.paste(sm, ((W - sm.width) // 2, 230), sm); s3.paste(marco, ((W - marco.width) // 2, 260)); barra_marca(s3)
titulo_abajo(s3, 'Cortes de caja claros', 'Sabe lo que entró y lo que salió'); puntos(s3, 4, 2); s3.save(OUT / 'lunes_3.jpg', quality=93)

s4 = cubrir(Image.open(M / 'doc_02.png'), W, H, 0.55); sombra_abajo(s4, 0.42, 250); barra_marca(s4)
titulo_abajo(s4, 'Lo ves funcionando primero', 'Primero funciona, después pagas', y0=830); boton(s4, (70, 1190), 'Escríbeme por WhatsApp'); puntos(s4, 4, 3); s4.save(OUT / 'lunes_4.jpg', quality=93)

# ---------- MIÉRCOLES · portada del reel (9:16) ----------
W2, H2 = 1080, 1920
p = degr(W2, H2, [(40, 64, 150), NAVY], vertical=True); barra_marca(p); producto(p, M / 'image_04_10-20_1842.jpg', (140, 230, 800, 820), recorte=(0, 0, 545, 700))
ft = f('InterDisplay-Black.ttf', 112); y = texto(p, (70, 1150), 'La nevería que no controlaba gramos', ft, ancho=940, inter=1.04)
p.paste(degr(180, 12, GRAD), (72, y + 18)); texto(p, (70, y + 56), 'Ahora controla por vasos', f('Inter-Medium.ttf', 54), (220, 228, 255))
p.save(OUT / 'miercoles_portada_reel.jpg', quality=93)

# ---------- VIERNES · oferta ----------
v = degr(W, H, [(26, 42, 104), NAVY], vertical=True); barra_marca(v)
producto(v, M / 'image_05_10-20_1842.jpg', (400, 170, 620, 520))
producto(v, M / 'image_08_10-20_1842.jpg', (60, 230, 360, 460), recorte=(40, 0, 504, 688))
ft = f('InterDisplay-Black.ttf', 92); y = texto(v, (70, 730), 'Kit completo para tu negocio', ft, ancho=940, inter=1.05)
texto(v, (70, y + 6), 'Software + impresora + lector', f('Inter-SemiBold.ttf', 46), (220, 228, 255))
ImageDraw.Draw(v).text((70, y + 82), '$3,500', font=f('InterDisplay-Black.ttf', 120), fill=(250, 204, 21))
ImageDraw.Draw(v).text((520, y + 112), 'MXN + impuestos\n1 año + instalación\ny capacitación', font=f('Inter-Medium.ttf', 32), fill=BLANCO, spacing=10)
ImageDraw.Draw(v).text((70, y + 262), 'Primero lo tienes funcionando, después pagas.', font=f('Inter-Bold.ttf', 40), fill=BLANCO)
ImageDraw.Draw(v).text((70, 1250), 'Instalación en CDMX y Área Metropolitana · Requiere computadora', font=f('Inter-Regular.ttf', 27), fill=(190, 200, 235))
v.save(OUT / 'viernes_oferta.jpg', quality=93)

# ---------- HISTORIAS ----------
h1 = degr(W2, H2, [(59, 91, 219), (139, 92, 246), (236, 72, 153)], vertical=True); barra_marca(h1)
texto(h1, (80, 620), '¿Cómo llevas tus ventas hoy?', f('InterDisplay-Black.ttf', 118), ancho=920, inter=1.04)
d = ImageDraw.Draw(h1); d.rounded_rectangle((140, 1060, 940, 1340), radius=40, outline=(255, 255, 255), width=4)
d.text((540, 1200), '(aquí va la encuesta de Instagram:\n«Libreta / Excel» · «Sistema»)', font=f('Inter-Medium.ttf', 34), fill=(255, 255, 255), anchor='mm', align='center', spacing=10)
h1.save(OUT / 'martes_historia.jpg', quality=93)

h2 = cubrir(Image.open(M / '1023_015446_image.jpg'), W2, H2, 0.3); sombra_abajo(h2, 0.35, 240); barra_marca(h2)
y = texto(h2, (70, 1180), 'Instalamos en CDMX y Área Metropolitana', f('InterDisplay-Black.ttf', 96), ancho=940, inter=1.05)
texto(h2, (70, y + 30), 'Primero lo ves funcionando, después pagas.', f('Inter-SemiBold.ttf', 50), (220, 228, 255), ancho=940)
boton(h2, (70, 1680), 'Escríbeme por WhatsApp', 96)
h2.save(OUT / 'jueves_historia.jpg', quality=93)
print('ok', sorted(x.name for x in OUT.iterdir()))
