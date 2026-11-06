"""Anegocios v3 (estilo motion graphics tipo Uriel): proceso paso a paso, contadores, subtítulos palabra por palabra.
Genera frames con PIL -> ffmpeg. Requiere voz_v3/tiempos.json y clips_v3/M1..M3.mp4 (si faltan, usa tarjetas de color)."""
import json, math, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg

A = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 720, 1280, 30
SALIDA = A / 'final' / (sys.argv[1] if len(sys.argv) > 1 else 'Anegocios_kit_v3_estilo_uriel.mp4')
T = A / 'tmp_v3'; T.mkdir(exist_ok=True)
FD = '/usr/share/fonts/truetype/dejavu/'
def fnt(s, b=True, mono=False):
    return ImageFont.truetype(FD + ('DejaVuSansMono-Bold.ttf' if mono else ('DejaVuSans-Bold.ttf' if b else 'DejaVuSans.ttf')), s)

BG = (238, 238, 236); NEGRO = (17, 17, 17); GRIS = (165, 165, 165); AZUL = (10, 84, 200); AZUL_CL = (96, 170, 255)
VERDE = (37, 170, 90); BLANCO = (255, 255, 255)

# ---------------- tiempos ----------------
TI = json.loads((A / 'voz_v3' / 'tiempos.json').read_text())
TXT = {'A': '¿Todavía llevas las cuentas de tu tienda en una libreta o en Excel?',
       'B': 'Con Anegocios es así de fácil: escaneas el producto y sube al ticket al instante.',
       'C': 'Cobras e imprime el ticket para tu cliente.',
       'D': 'Al final del día, tu corte de caja compara lo vendido contra lo cobrado.',
       'E': 'Y en ruta, registras tus ventas desde tu celular Android.',
       'F': 'Todo por $3,500 MXN: un año de software, impresora, lector, instalación, capacitación y soporte. Pagas hasta que esté funcionando.',
       'G': 'Escríbenos por WhatsApp.'}
ORDEN = list('ABCDEFG')
GAP = 0.25
ini, t = {}, 0.35
for k in ORDEN:
    ini[k] = t; t += TI[k]['dur'] + (0.4 if k == 'F' else GAP)
FIN = ini['G'] + TI['G']['dur'] + 1.0


def palabras_t(k):
    """Palabras mostradas con tiempos absolutos (reparto proporcional dentro del tramo hablado según whisper)."""
    ws = TXT[k].split()
    pw = TI[k]['palabras']
    a, b = ini[k] + pw[0][1], ini[k] + pw[-1][2]
    pesos = [len(w) + (4 if w[-1] in ',.:?;' else 0) for w in ws]
    tot, acc, out = sum(pesos), 0, []
    for w, p in zip(ws, pesos):
        s0 = a + (b - a) * acc / tot; acc += p; s1 = a + (b - a) * (acc - (4 if w[-1] in ',.:?;' else 0)) / tot
        out.append((w, s0, s1))
    return out
PAL = {k: palabras_t(k) for k in ORDEN}


def tiempo_palabra(k, idx):
    return PAL[k][idx][1]


# anclas de escena (tiempos absolutos)
T_B_UI = ini['B'] + 1.9
T_P1 = tiempo_palabra('B', 6) - 0.1      # 'escaneas'
T_P2 = tiempo_palabra('B', 10) - 0.1     # 'sube'
T_P3 = ini['C'] - 0.05                   # 'Cobras'
T_P4 = tiempo_palabra('C', 2) - 0.1      # 'imprime'
T_P5 = ini['D'] - 0.05
T_E_UI = ini['E'] + 1.7
T_P6 = T_E_UI
T_F = ini['F'] - 0.05
T_G = ini['G'] - 0.1
print('duración', round(FIN, 2), {k: round(v, 2) for k, v in ini.items()})

# ---------------- utilidades ----------------
ease = lambda x: 1 - (1 - min(max(x, 0), 1)) ** 3
clamp = lambda x: min(max(x, 0.0), 1.0)
def pop(x):  # rebote suave
    x = clamp(x); return 1 + 0.08 * math.sin(x * math.pi) * (1 - x) if x < 1 else 1


def sombra(capa, caja, r, op=70, blur=22, dy=14):
    s = Image.new('RGBA', capa.size, (0, 0, 0, 0)); d = ImageDraw.Draw(s)
    d.rounded_rectangle((caja[0], caja[1] + dy, caja[2], caja[3] + dy), r, fill=(0, 0, 0, op))
    capa.alpha_composite(s.filter(ImageFilter.GaussianBlur(blur)))


def tarjeta(capa, caja, r=34, color=BLANCO):
    sombra(capa, caja, r); ImageDraw.Draw(capa).rounded_rectangle(caja, r, fill=color)


def texto(d, xy, s, f, fill, anchor='la'):
    d.text(xy, s, font=f, fill=fill, anchor=anchor)


def mover(capa, a, dx=0, dy=0):
    """Aplica alfa y desplazamiento a una capa RGBA."""
    if a < 1:
        al = capa.getchannel('A').point(lambda v: int(v * a)); capa = capa.copy(); capa.putalpha(al)
    if dx or dy:
        n = Image.new('RGBA', capa.size, (0, 0, 0, 0)); n.alpha_composite(capa, (int(dx), int(dy))); capa = n
    return capa


def titulo(d, l1, l2, a):
    f = fnt(54)
    c1 = tuple(int(NEGRO[i] * a + BG[i] * (1 - a)) for i in range(3)); c2 = tuple(int(GRIS[i] * a + BG[i] * (1 - a)) for i in range(3))
    texto(d, (W // 2, 205), l1, f, c1, 'mm'); texto(d, (W // 2, 270), l2, f, c2, 'mm')


def riel(d, paso):
    xs = [W // 2 + (i - 2.5) * 62 for i in range(6)]
    for i, x in enumerate(xs):
        act = i + 1 == paso; hecho = i + 1 < paso
        col = AZUL if act else ((90, 110, 150) if hecho else (205, 205, 203))
        r = 22 if act else 15
        d.ellipse((x - r, 96 - r, x + r, 96 + r), fill=col)
        if act: texto(d, (x, 96), str(i + 1), fnt(24), BLANCO, 'mm')
        elif hecho: texto(d, (x, 96), '✓', fnt(18), BLANCO, 'mm')


# ---------------- tarjetas por paso ----------------
def cuadro_barras(d, x, y, w, h, fase):
    import random
    rnd = random.Random(7); xx = x
    while xx < x + w - 6:
        ww = rnd.choice([3, 3, 5, 7]); d.rectangle((xx, y, xx + ww, y + h), fill=NEGRO); xx += ww + rnd.choice([3, 4, 6])


def paso1(t, base):  # escanear
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    caja = (60, 340, W - 60, 880); tarjeta(capa, caja)
    texto(d, (90, 372), 'PUNTO DE VENTA', fnt(24), GRIS)
    # producto con código
    d.rounded_rectangle((120, 450, W - 120, 700), 26, fill=(246, 246, 244), outline=(225, 225, 222), width=3)
    cuadro_barras(d, 175, 480, W - 350, 150, 0)
    texto(d, (W // 2, 668), '7 501055 300716', fnt(26, mono=True), (90, 90, 90), 'mm')
    # láser
    y = 470 + (math.sin(t * 7) * 0.5 + 0.5) * 190
    d.rectangle((135, y - 3, W - 135, y + 3), fill=(235, 40, 40))
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov); od.rectangle((135, y - 16, W - 135, y + 16), fill=(235, 40, 40, 50)); capa.alpha_composite(ov)
    # chip de producto leído
    k = ease((t - 1.1) / 0.5)
    if k > 0:
        c = Image.new('RGBA', (W, H), (0, 0, 0, 0)); cd = ImageDraw.Draw(c)
        cd.rounded_rectangle((90, 740, W - 90, 835), 22, fill=NEGRO)
        texto(cd, (122, 788), 'Salsa 250 g', fnt(32), BLANCO, 'lm'); texto(cd, (W - 122, 788), '$54.00', fnt(34, mono=True), (255, 232, 0), 'rm')
        capa.alpha_composite(mover(c, k, 0, (1 - k) * 40))
    return capa


FILAS = [('Salsa 250 g', 1, 54.0), ('Refresco 600 ml', 2, 36.0), ('Galletas', 1, 22.0), ('Jabón', 1, 18.0)]


def paso2(t, base):  # sube al ticket
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    tarjeta(capa, (60, 340, W - 60, 880))
    texto(d, (W // 2, 385), 'COMPRA TOTAL', fnt(26), GRIS, 'mm'); d.line((90, 420, W - 90, 420), fill=(225, 225, 222), width=3)
    tot = 0
    for i, (n, q, p) in enumerate(FILAS):
        k = ease((t - 0.15 - i * 0.45) / 0.35)
        if k <= 0: continue
        y = 450 + i * 74
        c = Image.new('RGBA', (W, H), (0, 0, 0, 0)); cd = ImageDraw.Draw(c)
        cd.rounded_rectangle((90, y, W - 90, y + 60), 14, fill=(246, 246, 244))
        texto(cd, (112, y + 30), f'{q} × {n}', fnt(27), NEGRO, 'lm'); texto(cd, (W - 112, y + 30), f'${q * p:,.2f}', fnt(28, mono=True), NEGRO, 'rm')
        capa.alpha_composite(mover(c, k, (1 - k) * 90, 0)); tot += q * p * k
    d.rounded_rectangle((90, 770, W - 90, 850), 20, fill=AZUL)
    texto(d, (122, 810), 'TOTAL', fnt(30), BLANCO, 'lm'); texto(d, (W - 122, 810), f'${tot:,.2f}', fnt(44, mono=True), (255, 232, 0), 'rm')
    return capa


def paso3(t, base):  # cobra
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    tarjeta(capa, (60, 340, W - 60, 880))
    texto(d, (W // 2, 400), 'TOTAL A COBRAR', fnt(26), GRIS, 'mm')
    v = 164.0 * ease(t / 0.2)
    texto(d, (W // 2, 520), f'${v:,.2f}', fnt(96, mono=True), NEGRO, 'mm')
    pagado = t > 0.5
    esc = 1.0 - 0.06 * math.sin(clamp((t - 0.3) / 0.2) * math.pi)
    bw, bh = 520 * esc, 120 * esc
    d.rounded_rectangle((W / 2 - bw / 2, 700 - bh / 2, W / 2 + bw / 2, 700 + bh / 2), 40, fill=VERDE if pagado else AZUL)
    texto(d, (W // 2, 700), 'Pagado ✓' if pagado else 'COBRAR', fnt(46), BLANCO, 'mm')
    texto(d, (W // 2, 810), 'Efectivo · Tarjeta · Transferencia', fnt(24, False), GRIS, 'mm')
    return capa


def paso4(t, base):  # imprime ticket
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    # papel sale de la impresora
    k = ease(t / 1.4); alto = 80 + 330 * k
    px0, px1, base_y = 210, W - 210, 720
    sombra(capa, (px0, base_y - alto, px1, base_y), 6, 60, 14, 8)
    d = ImageDraw.Draw(capa)
    d.rectangle((px0, base_y - alto, px1, base_y), fill=BLANCO)
    texto(d, (W // 2, base_y - alto + 28), 'ANEGOCIOS', fnt(22), NEGRO, 'mm')
    for i in range(6):
        yy = base_y - alto + 62 + i * 34
        if yy < base_y - 20:
            d.line((px0 + 22, yy, px0 + 22 + [150, 110, 140, 90, 130, 100][i], yy), fill=(150, 150, 150), width=4); d.line((px1 - 62, yy, px1 - 22, yy), fill=(150, 150, 150), width=4)
    if k > 0.85: texto(d, (W // 2, base_y - 28), 'TOTAL $164.00', fnt(24, mono=True), NEGRO, 'mm')
    # impresora
    sombra(capa, (150, 700, W - 150, 880), 28)
    d = ImageDraw.Draw(capa)
    d.rounded_rectangle((150, 700, W - 150, 880), 28, fill=(34, 34, 38)); d.rounded_rectangle((180, 722, W - 180, 740), 8, fill=(10, 10, 12))
    d.ellipse((W - 235, 808, W - 215, 828), fill=(80, 220, 120)); texto(d, (230, 818), 'Anegocios', fnt(24), (150, 160, 190), 'lm')
    return capa


def paso5(t, base):  # corte de caja
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    tarjeta(capa, (60, 340, W - 60, 880))
    texto(d, (90, 372), 'CORTE DE CAJA · HOY', fnt(24), GRIS)
    k1, k2 = ease(t / 0.9), ease((t - 0.5) / 0.9)
    for i, (nom, col, kk) in enumerate([('Vendido', AZUL, k1), ('Cobrado', (30, 30, 34), k2)]):
        y = 450 + i * 150
        texto(d, (90, y), nom, fnt(30), NEGRO); texto(d, (W - 90, y), f'${4820 * kk:,.0f}', fnt(40, mono=True), NEGRO, 'ra')
        d.rounded_rectangle((90, y + 62, W - 90, y + 92), 15, fill=(232, 232, 230)); d.rounded_rectangle((90, y + 62, 90 + (W - 180) * kk, y + 92), 15, fill=col)
    if t > 1.7:
        k = ease((t - 1.7) / 0.35); r = 60 * pop(k)
        d.rounded_rectangle((90, 770, W - 90, 850), 24, fill=VERDE if k > 0 else BG); texto(d, (W // 2, 810), '✓ Cuadra: sin diferencia', fnt(34), BLANCO, 'mm')
    return capa


def paso6(t, base):  # app android en ruta
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    x0, x1, y0, y1 = 190, W - 190, 320, 900
    sombra(capa, (x0, y0, x1, y1), 56); d = ImageDraw.Draw(capa)
    d.rounded_rectangle((x0, y0, x1, y1), 56, fill=(24, 24, 28)); d.rounded_rectangle((x0 + 12, y0 + 12, x1 - 12, y1 - 12), 46, fill=BLANCO)
    d.rounded_rectangle((W // 2 - 40, y0 + 22, W // 2 + 40, y0 + 34), 6, fill=(24, 24, 28))
    d.rectangle((x0 + 12, y0 + 62, x1 - 12, y0 + 128), fill=AZUL); texto(d, (W // 2, y0 + 95), 'Ruta · Anegocios', fnt(26), BLANCO, 'mm')
    ventas = [('Abarrotes La Paz', 320.0), ('Tienda Lupita', 185.5), ('Miscelánea Sol', 440.0)]
    for i, (n, v) in enumerate(ventas):
        k = ease((t - 0.2 - i * 0.55) / 0.35)
        if k <= 0: continue
        y = y0 + 160 + i * 112
        c = Image.new('RGBA', (W, H), (0, 0, 0, 0)); cd = ImageDraw.Draw(c)
        cd.rounded_rectangle((x0 + 30, y, x1 - 30, y + 92), 16, fill=(244, 244, 242))
        texto(cd, (x0 + 50, y + 30), n, fnt(21), NEGRO, 'lm'); texto(cd, (x0 + 50, y + 62), 'Venta registrada', fnt(17, False), GRIS, 'lm'); texto(cd, (x1 - 50, y + 46), f'${v:,.0f}', fnt(24, mono=True), AZUL, 'rm')
        capa.alpha_composite(mover(c, k, 0, (1 - k) * 36))
    if t > 2.0:
        k = ease((t - 2.0) / 0.4)
        c = Image.new('RGBA', (W, H), (0, 0, 0, 0)); cd = ImageDraw.Draw(c)
        cd.rounded_rectangle((x0 + 30, y1 - 120, x1 - 30, y1 - 50), 20, fill=VERDE); texto(cd, (W // 2, y1 - 85), 'Se envía con internet ✓', fnt(21), BLANCO, 'mm')
        capa.alpha_composite(mover(c, k, 0, (1 - k) * 20))
    return capa


PASOS = [(1, paso1, 'Escanea', 'el producto'), (2, paso2, 'Sube al ticket', 'al instante'), (3, paso3, 'Cobra', 'en segundos'),
         (4, paso4, 'Imprime', 'el ticket'), (5, paso5, 'Corte de caja', 'vendido vs cobrado'), (6, paso6, 'App Android', 'en ruta de venta')]
RANGOS = {1: (T_P1, T_P2), 2: (T_P2, T_P3), 3: (T_P3, T_P4), 4: (T_P4, T_P5), 5: (T_P5, T_E_UI - 1.7 + 0 + (ini['E'] - T_P5) * 0 + 99), 6: (T_E_UI, T_F)}
RANGOS[5] = (T_P5, ini['E'] - 0.05)
# paso1 empieza antes de su rango para cubrir la entrada tras el clip M2
RANGOS[1] = (T_B_UI, T_P2)


# ---------------- precio y cierre ----------------
ITEMS = [(10, '1 año de software'), (11, 'Impresora de tickets'), (12, 'Lector de códigos'), (13, 'Instalación'), (14, 'Capacitación'), (15, 'Soporte por 1 año')]
IT_IDX = {'F': {}}
def idx_f(pal):
    ws = [w for w, _, _ in PAL['F']]
    def find(s, desde=0):
        for i in range(desde, len(ws)):
            if ws[i].lower().startswith(s): return i
        return None
    return [find('año'), find('impresora'), find('lector'), find('instalaci'), find('capacitaci'), find('soporte')]
IDX_F = idx_f(PAL['F'])


def escena_precio(t):
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    k = ease(t / 1.3); v = 3500 * k; esc = pop(t / 1.3)
    pw, ph = 560 * esc, 190 * esc
    sombra(capa, (W / 2 - pw / 2, 180 - ph / 2 + 60, W / 2 + pw / 2, 180 + ph / 2 + 60), 80, 80); d = ImageDraw.Draw(capa)
    d.rounded_rectangle((W / 2 - pw / 2, 240 - ph / 2, W / 2 + pw / 2, 240 + ph / 2), 90, fill=NEGRO)
    texto(d, (W // 2, 228), f'${v:,.0f}', fnt(108, mono=True), BLANCO, 'mm'); texto(d, (W // 2, 296), 'MXN · todo incluido', fnt(24, False), (200, 200, 200), 'mm')
    tarjeta(capa, (60, 410, W - 60, 900)); d = ImageDraw.Draw(capa)
    for i, (idx, et) in enumerate(ITEMS):
        t0 = (PAL['F'][IDX_F[i]][1] - T_F) if IDX_F[i] is not None else 1.5 + i * 0.8
        kk = ease((t - t0 + 0.1) / 0.3)
        y = 440 + i * 70
        if kk <= 0: continue
        c = Image.new('RGBA', (W, H), (0, 0, 0, 0)); cd = ImageDraw.Draw(c)
        cd.ellipse((92, y + 8, 132, y + 48), fill=AZUL); texto(cd, (112, y + 28), '✓', fnt(26), BLANCO, 'mm'); texto(cd, (152, y + 28), et, fnt(31), NEGRO, 'lm')
        capa.alpha_composite(mover(c, kk, (1 - kk) * 70, 0))
    return capa


def escena_cierre(t):
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    k = ease(t / 0.45); esc = pop(t / 0.45)
    texto(d, (W // 2, 300), 'Pagas hasta que', fnt(54), NEGRO, 'mm'); texto(d, (W // 2, 366), 'esté funcionando.', fnt(54), AZUL, 'mm')
    bw, bh = 560 * esc, 130 * esc
    sombra(capa, (W / 2 - bw / 2, 560 - bh / 2, W / 2 + bw / 2, 560 + bh / 2), 60); d = ImageDraw.Draw(capa)
    d.rounded_rectangle((W / 2 - bw / 2, 560 - bh / 2, W / 2 + bw / 2, 560 + bh / 2), 60, fill=(37, 211, 102))
    texto(d, (W // 2, 560), 'Escríbenos por WhatsApp', fnt(33), BLANCO, 'mm')
    d.ellipse((W // 2 - 34, 690, W // 2 + 34, 758), fill=AZUL); texto(d, (W // 2, 724), '✓', fnt(44), BLANCO, 'mm')
    texto(d, (W // 2, 840), 'Anegocios', fnt(70), AZUL, 'mm'); texto(d, (W // 2, 900), 'anegocios.com', fnt(34, False), (90, 90, 90), 'mm')
    return mover(capa, k, 0, (1 - k) * 30)


# ---------------- subtítulos kinéticos ----------------
CHUNKS = []
for k in ORDEN:
    ws = PAL[k]; cur = []
    for i, (w, a, b) in enumerate(ws):
        cur.append((w, a, b))
        corte = w[-1] in ',.:?;' or len(cur) >= 4 or sum(len(x[0]) + 1 for x in cur) > 21
        if corte or i == len(ws) - 1:
            CHUNKS.append(cur); cur = []
FS = 58
def subtitulo(t, sobre_video):
    ch = None
    for i, c in enumerate(CHUNKS):
        a0 = c[0][1] - 0.05; a1 = CHUNKS[i + 1][0][1] - 0.05 if i + 1 < len(CHUNKS) else c[-1][2] + 0.6
        if a0 <= t < a1: ch = c; kin = clamp((t - a0) / 0.14); break
    if not ch: return None
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa); f = fnt(FS)
    ws = [w for w, _, _ in ch]; anch = [d.textlength(w + ' ', font=f) for w in ws]; tot = sum(anch) - d.textlength(' ', font=f)
    if tot > W - 70: f = fnt(int(FS * (W - 70) / tot)); anch = [d.textlength(w + ' ', font=f) for w in ws]; tot = sum(anch) - d.textlength(' ', font=f)
    y = 985
    if sobre_video: d.rounded_rectangle((W / 2 - tot / 2 - 28, y - 52, W / 2 + tot / 2 + 28, y + 52), 30, fill=(0, 0, 0, 150))
    x = W / 2 - tot / 2
    for (w, a, b), an in zip(ch, anch):
        if t >= a - 0.02 and t < b + 0.02: col = AZUL_CL if sobre_video else AZUL; yy = y - 5 * math.sin(clamp((t - a) / 0.16) * math.pi)
        elif t >= b: col = BLANCO if sobre_video else NEGRO; yy = y
        else: col = (200, 200, 200) if sobre_video else (178, 178, 176); yy = y
        d.text((x, yy), w, font=f, fill=col, anchor='lm'); x += an
    return mover(capa, kin * 0.7 + 0.3, 0, (1 - kin) * 14)


# ---------------- video de fondo (clips Modal) ----------------
def frames_clip(n):
    ruta = A / 'clips_v3' / f'{n}.mp4'; d = T / n; d.mkdir(exist_ok=True)
    if ruta.exists() and not list(d.glob('*.jpg')):
        subprocess.run([FF, '-v', 'error', '-y', '-i', str(ruta), '-vf', f'fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}', '-q:v', '3', str(d / '%04d.jpg')], check=True)
    return sorted(d.glob('*.jpg'))
CL = {n: frames_clip(n) for n in ('M1', 'M2', 'M3')}
def frame_clip(n, t):
    fs = CL[n]
    if not fs: return Image.new('RGBA', (W, H), (30, 60, 120, 255))
    return Image.open(fs[min(int(t * FPS), len(fs) - 1)]).convert('RGBA')


def zona_video(t):
    """Devuelve (frame de clip, alfa) si el tiempo cae en una toma de video."""
    if t < ini['B'] - 0.05: return 'M1', t, 1.0
    if ini['B'] - 0.05 <= t < T_B_UI + 0.15: return 'M2', t - (ini['B'] - 0.05), 1.0
    if ini['E'] - 0.05 <= t < T_E_UI + 0.15: return 'M3', t - (ini['E'] - 0.05), 1.0
    return None


# ---------------- composición ----------------
def componer(t):
    z = zona_video(t)
    if z:
        n, tl, _ = z
        im = frame_clip(n, tl)
        # fundido al pasar a la interfaz
        fin_clip = {'M1': ini['B'] - 0.05, 'M2': T_B_UI + 0.15, 'M3': T_E_UI + 0.15}[n]
        rest = fin_clip - t
        base = Image.new('RGBA', (W, H), BG + (255,))
        if rest < 0.15: im.putalpha(int(255 * clamp(rest / 0.15))); base.alpha_composite(im); im = base
        else:
            vig = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(vig).rectangle((0, H - 420, W, H), fill=(0, 0, 0, 70)); im.alpha_composite(vig.filter(ImageFilter.GaussianBlur(60)))
        if n in ('M2', 'M3') and t < ini['B'] + 0.2 and False: pass
        s = subtitulo(t, True)
        if s: im.alpha_composite(s)
        return im.convert('RGB')
    base = Image.new('RGBA', (W, H), BG + (255,))
    d = ImageDraw.Draw(base)
    paso = None
    for n, fn, l1, l2 in PASOS:
        a, b = RANGOS[n]
        if a - 0.05 <= t < b + 0.05: paso = (n, fn, l1, l2, a); break
    if t >= T_G:
        base.alpha_composite(escena_cierre(t - T_G))
    elif t >= T_F:
        capa = escena_precio(t - T_F); base.alpha_composite(mover(capa, ease((t - T_F) / 0.3), 0, 0))
    elif paso:
        n, fn, l1, l2, a = paso; tl = t - a; k = ease((tl + 0.05) / 0.35)
        riel(ImageDraw.Draw(base), n); titulo(d, l1, l2, k)
        base.alpha_composite(mover(fn(max(tl, 0), base), k, 0, (1 - k) * 40))
    s = subtitulo(t, False)
    if s: base.alpha_composite(s)
    return base.convert('RGB')


def main():
    N = int(FIN * FPS)
    mudo = T / 'mudo_v3.mp4'
    p = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'fast', str(mudo)], stdin=subprocess.PIPE)
    for i in range(N):
        p.stdin.write(componer(i / FPS).tobytes())
        if i % 150 == 0: print('frame', i, '/', N, flush=True)
    p.stdin.close(); p.wait()
    fa = ''.join(f'[{i + 1}:a]adelay={int(ini[k] * 1000)}|{int(ini[k] * 1000)}[a{i}];' for i, k in enumerate(ORDEN))
    ins = sum([['-i', str(A / 'voz_v3' / f'{k}.wav')] for k in ORDEN], [])
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(mudo), *ins, '-filter_complex', fa + ''.join(f'[a{i}]' for i in range(7)) + 'amix=inputs=7:normalize=0,volume=1.6[aud]',
                    '-map', '0:v', '-map', '[aud]', '-t', f'{FIN:.2f}', '-c:v', 'libx264', '-profile:v', 'main', '-level', '4.0', '-pix_fmt', 'yuv420p', '-crf', '23', '-preset', 'medium',
                    '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(SALIDA)], check=True)
    print('listo', SALIDA, round(SALIDA.stat().st_size / 1e6, 1), 'MB')


if __name__ == '__main__':
    if '--prueba' in sys.argv:
        for nombre, tt in [('p1', T_P1 + 0.9), ('p2', T_P2 + 1.5), ('p3', T_P3 + 1.4), ('p4', T_P4 + 1.2), ('p5', T_P5 + 2.0), ('p6', T_E_UI + 2.4), ('pf', T_F + 5.0), ('pg', T_G + 0.8)]:
            componer(tt).save(T / f'{nombre}.png')
        print('pruebas listas')
    else:
        main()
