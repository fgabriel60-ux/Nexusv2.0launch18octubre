"""Anegocios · MOSTRADOR: escena fotorrealista de miscelánea (cuadros Qwen S0..S3 en Modal) + caja y rollos REALES del kit recortados y compuestos
con sombras de contacto; cámara en movimiento, etiquetas azules inclinadas con línea guía, destellos, barrido azul final. Voz Farid dick 2 (voz_showcase)."""
import json, math, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg

A = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 720, 1280, 30
SALIDA = A / 'final' / 'Anegocios_mostrador_v1.mp4'
T = A / 'tmp_mostrador'; T.mkdir(exist_ok=True)
FD = '/usr/share/fonts/truetype/dejavu/'
fnt = lambda s, b=True: ImageFont.truetype(FD + ('DejaVuSans-Bold.ttf' if b else 'DejaVuSans.ttf'), s)
NEGRO = (17, 17, 17); AZUL = (10, 84, 200); AZUL_CL = (96, 170, 255); BLANCO = (255, 255, 255); AMAR = (255, 230, 0); GRIS = (200, 200, 200)

TI = json.loads((A / 'voz_showcase' / 'tiempos.json').read_text())
ORDEN = list('ABCDEFG')
GAP = 0.3
ini, t = {}, 0.2
for k in ORDEN:
    ini[k] = t; t += TI[k]['dur'] + GAP
FIN = ini['G'] + TI['G']['dur'] + 2.9
TXT = {k: TI[k]['texto'] for k in ORDEN}
ease = lambda x: 1 - (1 - min(max(x, 0), 1)) ** 3
smooth = lambda x: (lambda u: u * u * (3 - 2 * u))(min(max(x, 0), 1))
clamp = lambda x: min(max(x, 0.0), 1.0)
nueva = lambda: Image.new('RGBA', (W, H), (0, 0, 0, 0))

def pop(x):  # rebote con sobreimpulso
    x = clamp(x)
    return 0 if x <= 0 else (1 - (1 - x) ** 3) * (1 + 0.12 * math.sin(x * math.pi))

def mover(capa, a, dx=0, dy=0):
    if a < 1:
        capa = capa.copy(); capa.putalpha(capa.getchannel('A').point(lambda v: int(v * a)))
    if dx or dy:
        n = Image.new('RGBA', capa.size, (0, 0, 0, 0)); n.alpha_composite(capa, (int(dx), int(dy))); capa = n
    return capa

# ---------- palabras (subtítulos) ----------
def palabras_t(k):
    ws = TXT[k].split(); pw = TI[k]['palabras']
    a, b = ini[k] + pw[0][1], ini[k] + pw[-1][2]
    pausa = lambda w: 4 if w[-1] in ',.:?;' else 0
    pesos = [len(w) + pausa(w) for w in ws]; tot, acc, out = sum(pesos), 0, []
    for w, p in zip(ws, pesos):
        s0 = a + (b - a) * acc / tot; acc += p; out.append((w, s0, a + (b - a) * (acc - pausa(w)) / tot))
    return out
PAL = {k: palabras_t(k) for k in ORDEN}

# ---------- mundo: escena del mostrador a 2x ----------
K2 = 2
def cargar(n): return Image.open(A / 'mostrador_cuadros_v2' / f'S{n}.png').convert('RGB').resize((W * K2, H * K2), Image.LANCZOS)
ESC = [cargar(i) for i in range(4)]
CAJA = Image.open(A / 'refs_mostrador' / 'corte_caja.png'); ROL = Image.open(A / 'refs_mostrador' / 'corte_rollos.png')
LOGO = Image.open(A / 'sitio' / 'logo_azul.png').convert('RGBA')
LOGO_B = Image.new('RGBA', LOGO.size, (255, 255, 255, 0)); LOGO_B.putalpha(LOGO.getchannel('A'))

def tono_cal(p, f=0.93):  # ajusta color a la luz cálida de la escena
    r, g, b, a = p.split()
    r = r.point(lambda v: int(v * f)); g = g.point(lambda v: int(v * f * 0.96)); b = b.point(lambda v: int(v * f * 0.88))
    return Image.merge('RGBA', (r, g, b, a))
CAJA_T, ROL_T = tono_cal(CAJA, 0.96), tono_cal(ROL, 0.9)

def pieza(base, p, altura, cx, by, e, sombra=True):
    """pega la pieza (coordenadas del mundo 720x1280) con rebote e y sombra de contacto."""
    if e <= 0: return
    h = max(2, int(altura * K2 * e)); w = max(2, int(p.width * h / p.height))
    pp = p.resize((w, h), Image.LANCZOS); X = int(cx * K2 - w / 2); Y = int(by * K2 - h)
    if sombra:
        sh = Image.new('RGBA', base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(sh)
        d.ellipse((cx * K2 - w * 0.55, by * K2 - 16 * K2, cx * K2 + w * 0.55 + 30 * K2, by * K2 + 16 * K2), fill=(0, 0, 0, int(150 * min(e, 1))))
        base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10 * K2)))
    if e < 1:
        pp = pp.copy(); pp.putalpha(pp.getchannel('A').point(lambda v: int(v * clamp(e * 1.5))))
    base.alpha_composite(pp, (X, Y))

# tiempos de aparición (relativos al inicio de A)
a0 = ini['A']
REV = {'S1': a0 + 0.35, 'S2': a0 + 0.85, 'S3': a0 + 1.35, 'caja': a0 + 1.85, 'rollos': a0 + 2.3}
# posición en el mundo (720x1280) de cada pieza para destellos y líneas guía
POS = {'laptop': (360, 665), 'lector': (140, 860), 'impresora': (610, 880), 'caja': (330, 965), 'rollos': (575, 1055), 'todo': (360, 780)}

def mundo(t):
    estado = 0
    base = ESC[0]
    for n, clave in ((1, 'S1'), (2, 'S2'), (3, 'S3')):
        x = (t - REV[clave]) / 0.3
        if x > 0: base = Image.blend(base, ESC[n], ease(x)) if x < 1 else ESC[n]
    base = base.convert('RGBA'); base = base.copy()
    # caja y rollos: aparecen en el plano general (A), se retiran en los primeros planos (B-D) y vuelven en E-F
    t_out = ini['B'] - 0.15; t_back = ini['E'] - 0.05
    if t < t_out + 0.3:
        f = 1 - ease((t - t_out) / 0.3); ec = pop((t - REV['caja']) / 0.5) * f; er = pop((t - REV['rollos']) / 0.5) * f
    elif t >= t_back:
        ec = pop((t - t_back) / 0.5); er = pop((t - t_back - 0.2) / 0.5)
    else:
        ec = er = 0
    pieza(base, CAJA_T, 330, 330, 1130, ec)
    pieza(base, ROL_T, 190, 575, 1150, er)
    return base

# ---------- cámara ----------
WP = [(0.0, 360, 640, 1.0), (ini['B'], 360, 690, 1.12), (ini['B'] + 1.9, 360, 665, 1.75), (ini['C'] + 0.15, 360, 665, 1.75),
      (ini['C'] + 0.95, 150, 860, 1.7), (ini['D'] + 0.15, 150, 860, 1.7), (ini['D'] + 0.95, 600, 880, 1.7),
      (ini['E'] + 0.05, 600, 880, 1.7), (ini['E'] + 1.0, 360, 780, 1.0), (ini['F'], 360, 780, 1.0), (FIN, 360, 780, 1.1)]
def camara(t):
    if t <= WP[0][0]: return WP[0][1:]
    for (t0, x0, y0, z0), (t1, x1, y1, z1) in zip(WP, WP[1:]):
        if t0 <= t < t1:
            u = smooth((t - t0) / (t1 - t0)); return x0 + (x1 - x0) * u, y0 + (y1 - y0) * u, z0 + (z1 - z0) * u
    return WP[-1][1:]
def a_pantalla(wx, wy, cam):
    cx, cy, z = cam; return (wx - cx) * z + W / 2, (wy - cy) * z + H / 2
def encuadre(m, cam):
    cx, cy, z = cam; w, h = W / z, H / z
    x0 = min(max(cx - w / 2, 0), W - w); y0 = min(max(cy - h / 2, 0), H - h)
    return m.crop((int(x0 * K2), int(y0 * K2), int((x0 + w) * K2), int((y0 + h) * K2))).resize((W, H), Image.LANCZOS)

# ---------- motion graphics ----------
def sombra(capa, poly, op=90, blur=14, dy=8):
    s = Image.new('RGBA', capa.size, (0, 0, 0, 0)); ImageDraw.Draw(s).polygon([(x, y + dy) for x, y in poly], fill=(0, 0, 0, op))
    capa.alpha_composite(s.filter(ImageFilter.GaussianBlur(blur)))

def etiqueta(t_rel, titulo, spec, y=190, objetivo=None, salida_t=None):
    k = ease(t_rel / 0.4)
    if salida_t is not None: k *= 1 - ease((t_rel - salida_t) / 0.3)
    if k <= 0: return nueva()
    capa = nueva(); d = ImageDraw.Draw(capa)
    ft, fs = fnt(40), fnt(26, False)
    w = max(d.textlength(titulo, font=ft), d.textlength(spec, font=fs)) + 90; h = 118; sk = 26
    x0 = -w + (w + 24) * k
    poly = [(x0 + sk, y), (x0 + w + sk, y), (x0 + w, y + h), (x0, y + h)]
    sombra(capa, poly); d = ImageDraw.Draw(capa)
    d.polygon(poly, fill=AZUL); d.polygon([(x0 + sk, y), (x0 + sk + 10, y), (x0 + 10, y + h), (x0, y + h)], fill=AZUL_CL)
    d.text((x0 + 46, y + 38), titulo, font=ft, fill=BLANCO, anchor='lm'); d.text((x0 + 46, y + 86), spec, font=fs, fill=(205, 225, 255), anchor='lm')
    if objetivo is not None and k > 0.9:   # línea guía hacia la pieza
        g = ease((t_rel - 0.35) / 0.4); sx, sy = x0 + w * 0.5, y + h
        ex, ey = sx + (objetivo[0] - sx) * g, sy + (objetivo[1] - sy) * g
        d.line((sx, sy, ex, ey), fill=AZUL_CL, width=4); d.ellipse((ex - 9, ey - 9, ex + 9, ey + 9), fill=BLANCO, outline=AZUL, width=4)
    return capa

def etiqueta3(t, ts, spec, y=150, objetivo=None):
    """título fijo arriba (hecho por código): 'Punto de Venta' pequeño + 'Anegocios' grande; la 3ª línea cambia según la pieza.
    t = tiempo absoluto (entrada una sola vez); ts = tiempo desde que empezó la escena actual (cambio de subtítulo)."""
    k = ease((t - a0 - 0.1) / 0.4)
    if k <= 0: return nueva()
    capa = nueva(); d = ImageDraw.Draw(capa)
    f1, f2, f3 = fnt(30, False), fnt(58), fnt(27 if len(spec) < 34 else 22)
    w, h, sk = 610, 160, 28
    x0 = -w + (w + 22) * k
    poly = [(x0 + sk, y), (x0 + w + sk, y), (x0 + w, y + h), (x0, y + h)]
    sombra(capa, poly); d = ImageDraw.Draw(capa)
    d.polygon(poly, fill=AZUL); d.polygon([(x0 + sk, y), (x0 + sk + 10, y), (x0 + 10, y + h), (x0, y + h)], fill=AZUL_CL)
    d.text((x0 + 48, y + 30), 'Punto de Venta', font=f1, fill=(205, 225, 255), anchor='lm')
    d.text((x0 + 48, y + 80), 'Anegocios', font=f2, fill=BLANCO, anchor='lm')
    u = ease(ts / 0.3)
    s = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(s)
    ds.text((x0 + 48, y + 130 + (1 - u) * 16), spec, font=f3, fill=(255, 255, 255, int(255 * u)), anchor='lm')
    capa.alpha_composite(s)
    if objetivo is not None and k > 0.9:   # línea guía hacia la pieza
        g = ease((ts - 0.35) / 0.4); sx, sy = x0 + w * 0.55, y + h
        ex, ey = sx + (objetivo[0] - sx) * g, sy + (objetivo[1] - sy) * g
        d = ImageDraw.Draw(capa); d.line((sx, sy, ex, ey), fill=AZUL_CL, width=4); d.ellipse((ex - 9, ey - 9, ex + 9, ey + 9), fill=BLANCO, outline=AZUL, width=4)
    return capa

def destello(capa_base, x, y, tr, radio=140):
    """anillo + brillo que aparece cuando entra una pieza."""
    if tr < 0 or tr > 0.7: return
    u = tr / 0.7; r = radio * (0.4 + 0.9 * ease(u)); a = int(220 * (1 - u))
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    d.ellipse((x - r, y - r, x + r, y + r), outline=(150, 200, 255, a), width=6)
    d.ellipse((x - r * 0.5, y - r * 0.5, x + r * 0.5, y + r * 0.5), fill=(255, 255, 255, int(a * 0.35)))
    capa_base.alpha_composite(c.filter(ImageFilter.GaussianBlur(2)))

def viñeta(im):
    v = Image.new('L', (W, H), 0); d = ImageDraw.Draw(v); d.ellipse((-W * 0.25, -H * 0.1, W * 1.25, H * 1.1), fill=255)
    v = v.filter(ImageFilter.GaussianBlur(120)); osc = Image.new('RGBA', (W, H), (0, 0, 0, 120)); osc.putalpha(v.point(lambda p: int(120 * (1 - p / 255))))
    im.alpha_composite(osc); return im

def laser(t_rel):
    c = nueva(); d = ImageDraw.Draw(c)
    return c

def chip(capa, cx, cy, txt, k):
    if k <= 0: return
    f = fnt(34); d = ImageDraw.Draw(capa); w = d.textlength(txt, font=f) + 80; h = 74; e = pop(k)
    ww, hh = w * e, h * e; x0, y0 = cx - ww / 2, cy - hh / 2
    poly = [(x0 + 18, y0), (x0 + ww + 18, y0), (x0 + ww, y0 + hh), (x0, y0 + hh)]
    sombra(capa, poly, 100, 10, 6); d = ImageDraw.Draw(capa); d.polygon(poly, fill=AZUL)
    d.ellipse((x0 + 14, cy - 17, x0 + 48, cy + 17), fill=AMAR); d.text((x0 + 31, cy), '✓', font=fnt(24), fill=NEGRO, anchor='mm')
    if e > 0.85: d.text((x0 + 62, cy), txt, font=f, fill=BLANCO, anchor='lm')

# ---------- subtítulos ----------
CHUNKS = []
for k in ORDEN:
    cur = []
    for i, (w, a, b) in enumerate(PAL[k]):
        cur.append((w, a, b))
        if w[-1] in ',.:?;' or len(cur) >= 4 or sum(len(x[0]) + 1 for x in cur) > 21 or i == len(PAL[k]) - 1:
            CHUNKS.append(cur); cur = []
def subtitulo(t):
    ch = None
    for i, c in enumerate(CHUNKS):
        a0_ = c[0][1] - 0.05; a1 = CHUNKS[i + 1][0][1] - 0.05 if i + 1 < len(CHUNKS) else c[-1][2] + 0.6
        if a0_ <= t < a1: ch = c; kin = clamp((t - a0_) / 0.14); break
    if not ch: return None
    capa = nueva(); d = ImageDraw.Draw(capa); f = fnt(58)
    ws = [w for w, _, _ in ch]; an = [d.textlength(w + ' ', font=f) for w in ws]; tot = sum(an) - d.textlength(' ', font=f)
    if tot > W - 70: f = fnt(int(58 * (W - 70) / tot)); an = [d.textlength(w + ' ', font=f) for w in ws]; tot = sum(an) - d.textlength(' ', font=f)
    y = 1010
    d.rounded_rectangle((W / 2 - tot / 2 - 28, y - 52, W / 2 + tot / 2 + 28, y + 52), 30, fill=(0, 0, 0, 150))
    x = W / 2 - tot / 2
    for (w, a, b), n in zip(ch, an):
        yy = y
        if a - 0.02 <= t < b + 0.02: col = AZUL_CL; yy = y - 5 * math.sin(clamp((t - a) / 0.16) * math.pi)
        elif t >= b: col = BLANCO
        else: col = GRIS
        d.text((x, yy), w, font=f, fill=col, anchor='lm'); x += n
    return mover(capa, kin * 0.7 + 0.3, 0, (1 - kin) * 14)

# ---------- composición ----------
T_G = ini['G'] - 0.4
def cierre(t):
    """barrido azul inclinado desde la derecha y tarjeta final (logo blanco, botón de WhatsApp, anegocios.com)."""
    tl = t - T_G
    im = Image.new('RGBA', (W, H), (10, 84, 200, 255)); capa = nueva(); d = ImageDraw.Draw(capa)
    for y in range(0, H, 4):  # degradado sutil
        cc = int(40 * y / H); d.rectangle((0, y, W, y + 4), fill=(max(10 - cc // 3, 0), max(84 - cc, 0), max(200 - cc, 0), 255))
    im.alpha_composite(capa); capa = nueva(); d = ImageDraw.Draw(capa)
    e = ease(tl / 0.5)
    lg = LOGO_B.resize((460, int(460 * LOGO_B.height / LOGO_B.width)), Image.LANCZOS)
    capa.alpha_composite(mover(lg_to_layer(lg, 420), e, 0, (1 - e) * 30))
    c2 = nueva(); d = ImageDraw.Draw(c2); bw = 620 * pop((tl - 0.3) / 0.45) if tl > 0.3 else 0; bh = bw * 130 / 620
    if bw > 2:
        d.rounded_rectangle((W / 2 - bw / 2, 600 - bh / 2, W / 2 + bw / 2, 600 + bh / 2), 60, fill=(37, 211, 102))
        if bw > 540: d.text((W // 2, 600), 'Confirma tu entrega en WhatsApp', font=fnt(30), fill=BLANCO, anchor='mm')
    d.text((W // 2, 740), 'Pago contra entrega', font=fnt(40), fill=AMAR, anchor='mm') if tl > 0.7 else None
    d.text((W // 2, 800), 'Pagas hasta recibir todo y estar capacitado', font=fnt(26, False), fill=BLANCO, anchor='mm') if tl > 0.8 else None
    d.text((W // 2, 900), 'anegocios.com', font=fnt(40, False), fill=BLANCO, anchor='mm') if tl > 0.9 else None
    capa.alpha_composite(c2); im.alpha_composite(capa); return im

def lg_to_layer(lg, y):
    c = nueva(); c.alpha_composite(lg, (W // 2 - lg.width // 2, y)); return c

def barrido(t, t0):
    """panel azul inclinado que cruza la pantalla de derecha a izquierda (como el cierre del reel)."""
    u = (t - t0) / 0.55
    if u <= 0 or u >= 1: return None
    c = nueva(); d = ImageDraw.Draw(c); x = W + 260 - (W + 520) * smooth(u); sk = 200
    d.polygon([(x + sk, 0), (x + sk + 520, 0), (x + 520, H), (x, H)], fill=(10, 84, 200, 255)); return c

def componer(t):
    cam = camara(t)
    m = mundo(t); im = encuadre(m, cam)
    if ini['F'] - 0.05 <= t < T_G:
        osc = Image.new('RGBA', (W, H), (0, 0, 0, int(150 * ease((t - ini['F']) / 0.5)))); im.alpha_composite(osc)
    im = viñeta(im)
    # destellos al entrar cada pieza (en pantalla, siguiendo la cámara)
    for clave, nom in (('S1', 'laptop'), ('S2', 'lector'), ('S3', 'impresora'), ('caja', 'caja'), ('rollos', 'rollos')):
        sx, sy = a_pantalla(*POS[nom], cam); destello(im, sx, sy, t - REV[clave] - 0.05)
    capa = nueva()
    # etiquetas por escena
    if t < ini['B'] - 0.05: im.alpha_composite(etiqueta3(t, t - a0, 'Kit completo'))
    elif t < ini['C'] - 0.05:
        tr = t - ini['B']; im.alpha_composite(etiqueta3(t, tr, 'Software · 1 año', objetivo=a_pantalla(*POS['laptop'], cam)))
    elif t < ini['D'] - 0.05:
        tr = t - ini['C']; im.alpha_composite(etiqueta3(t, tr, 'Lector de códigos', objetivo=a_pantalla(110, 790, cam)))
        # rayo láser rojo animado en la cabeza del lector
        hx, hy = a_pantalla(110, 790, cam); k = clamp((tr - 0.7) / 0.2); c = nueva(); d = ImageDraw.Draw(c)
        if k > 0:
            fl = 0.6 + 0.4 * math.sin(tr * 28); ln = 260 * k
            d.polygon([(hx, hy), (hx + ln, hy - 70 * k), (hx + ln, hy + 90 * k)], fill=(255, 40, 40, int(70 * fl)))
            d.line((hx, hy, hx + ln, hy + 10), fill=(255, 60, 60, int(230 * fl)), width=4)
            im.alpha_composite(c.filter(ImageFilter.GaussianBlur(1.5)))
    elif t < ini['E'] - 0.05:
        tr = t - ini['D']; im.alpha_composite(etiqueta3(t, tr, 'Impresora de tickets', objetivo=a_pantalla(*POS['impresora'], cam)))
    elif t < ini['F'] - 0.05:
        tr = t - ini['E']; im.alpha_composite(etiqueta3(t, tr, 'Instalación · Capacitación · Soporte 1 año'))
        c = nueva()
        for i, txt in enumerate(['Instalación', 'Capacitación', 'Soporte 1 año']):
            chip(c, 360, 470 + i * 100, txt, (tr - 0.35 - i * 0.4) / 0.45)
        im.alpha_composite(c)
    elif t < T_G:
        tr = t - ini['F']; c = nueva(); d = ImageDraw.Draw(c); tp = tr - 0.2
        if tp >= 0:
            e = pop(tp / 0.5) * (1 + 0.04 * math.sin(max(tp - 0.5, 0) * 8)); pw, ph = 520 * e, 150 * e
            d.rounded_rectangle((W / 2 - pw / 2, 500 - ph / 2, W / 2 + pw / 2, 500 + ph / 2), int(ph / 2), fill=AMAR)
            d.text((W / 2, 500), '$3,500', font=fnt(max(10, int(104 * e))), fill=NEGRO, anchor='mm')
        k = ease((tr - 1.1) / 0.4)
        if k > 0:
            c2 = nueva(); d2 = ImageDraw.Draw(c2)
            poly = [(80 + 22, 650), (W - 80 + 22, 650), (W - 80, 840), (80, 840)]; sombra(c2, poly); d2 = ImageDraw.Draw(c2); d2.polygon(poly, fill=AZUL)
            d2.text((W // 2, 705), 'Pago contra entrega', font=fnt(44), fill=BLANCO, anchor='mm')
            for i, l in enumerate(['Pagas hasta recibir todo', 'y estar capacitado']): d2.text((W // 2, 765 + i * 40), l, font=fnt(32, False), fill=(215, 232, 255), anchor='mm')
            c.alpha_composite(mover(c2, k, 0, (1 - k) * 30))
        im.alpha_composite(c); im.alpha_composite(etiqueta3(t, tr, 'Precio del kit · pago contra entrega'))
    if t >= T_G - 0.1:
        im2 = cierre(t)
        bw = barrido(t, T_G - 0.1)
        if t >= T_G + 0.2: im = im2
        else:
            u = (t - (T_G - 0.1)) / 0.55
            if bw is not None:
                im.alpha_composite(bw)
                if u > 0.45: im.alpha_composite(Image.new('RGBA', (W, H), (10, 84, 200, int(255 * ease((u - 0.45) / 0.55)))))
    s = subtitulo(t)
    if s and t < T_G + 0.15: im.alpha_composite(s)
    return im.convert('RGB')

def musica():
    import numpy as np, wave
    sr = 44100; n = int((FIN + 1) * sr); tt = np.arange(n) / sr; bpm = 92; beat = 60 / bpm
    acordes = [(220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (261.63, 329.63, 392.0), (196.0, 246.94, 293.66)]
    y = np.zeros(n)
    for i in range(int((FIN + 1) / (beat * 4)) + 1):
        a, b = int(i * beat * 4 * sr), min(n, int((i + 1) * beat * 4 * sr))
        if a >= n: break
        seg = tt[a:b] - tt[a]; env = np.minimum(1, seg / 0.4) * np.minimum(1, (tt[b - 1] - tt[a:b] + 0.001) / 0.5)
        for f0 in acordes[i % 4]: y[a:b] += env * (np.sin(2 * np.pi * f0 * seg) + 0.5 * np.sin(2 * np.pi * (f0 * 1.003) * seg)) * 0.12
        for j in range(8):
            s0 = int(a + j * beat / 2 * sr)
            if s0 >= n: break
            m = min(int(0.5 * sr), n - s0); ts = np.arange(m) / sr; f0 = acordes[i % 4][j % 3] * 2
            y[s0:s0 + m] += np.sin(2 * np.pi * f0 * ts) * np.exp(-ts * 6) * 0.10
    y = y / (np.abs(y).max() + 1e-9) * 0.8
    with wave.open(str(T / 'musica_m.wav'), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((y * 32767).astype('<i2').tobytes())

def main():
    N = int(FIN * FPS); mudo = T / 'mudo_m.mp4'
    p = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'fast', str(mudo)], stdin=subprocess.PIPE)
    for i in range(N):
        p.stdin.write(componer(i / FPS).tobytes())
        if i % 150 == 0: print('frame', i, '/', N, flush=True)
    p.stdin.close(); p.wait(); musica()
    n = len(ORDEN); fa = ''.join(f'[{i + 1}:a]adelay={int(ini[k] * 1000)}|{int(ini[k] * 1000)}[a{i}];' for i, k in enumerate(ORDEN))
    ins = sum([['-i', str(A / 'voz_showcase' / f'{k}.wav')] for k in ORDEN], []) + ['-i', str(T / 'musica_m.wav')]
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(mudo), *ins, '-filter_complex', fa + ''.join(f'[a{i}]' for i in range(n)) + f'amix=inputs={n}:normalize=0:duration=longest,volume=1.6[mix];[{n + 1}:a]afade=t=in:st=3:d=1.5,afade=t=out:st={FIN - 1.5:.2f}:d=1.5,volume=0.1[mus];[mix][mus]amix=inputs=2:normalize=0[aud]',
                    '-map', '0:v', '-map', '[aud]', '-t', f'{FIN:.2f}', '-c:v', 'libx264', '-profile:v', 'main', '-level', '4.0', '-pix_fmt', 'yuv420p', '-crf', '23', '-preset', 'medium',
                    '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(SALIDA)], check=True)
    print('listo', SALIDA, round(SALIDA.stat().st_size / 1e6, 1), 'MB', round(FIN, 1), 's')

if __name__ == '__main__':
    print('inicios', {k: round(v, 2) for k, v in ini.items()}, 'fin', round(FIN, 2))
    if '--prueba' in sys.argv:
        puntos = [('0', a0 + 0.2), ('1', a0 + 1.1), ('2', a0 + 2.4), ('3', ini['B'] + 1.8), ('4', ini['C'] + 1.7), ('5', ini['D'] + 1.7),
                  ('6', ini['E'] + 2.2), ('7', ini['F'] + 1.0), ('8', ini['F'] + 3.0), ('9', T_G + 0.25), ('10', ini['G'] + 1.5), ('11', FIN - 0.3)]
        for n, tt in puntos: componer(tt).save(T / f'pm_{n}.png')
        hoja = Image.new('RGB', (6 * 300, 2 * 533))
        for i, (n, _) in enumerate(puntos): hoja.paste(Image.open(T / f'pm_{n}.png').resize((300, 533)), ((i % 6) * 300, (i // 6) * 533))
        hoja.save(T / 'hoja_mostrador.jpg', quality=85); print('pruebas listas')
    else:
        main()
