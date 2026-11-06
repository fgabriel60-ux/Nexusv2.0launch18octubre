"""Anegocios ANTES y DESPUÉS (estilo motion graphics tipo Uriel): libreta -> Excel -> Punto de Venta Anegocios -> kit $3,500.
Frames PIL -> ffmpeg. Usa voz_ad/ (Fish, tiempos por whisper), clips_v3/M1,M2 (Modal) y metraje real de Fernando."""
import json, math, random, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg
sys.path.insert(0, str(Path(__file__).resolve().parent))
import intro_paquete as IP

A = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 720, 1280, 30
SALIDA = A / 'final' / 'Anegocios_v5A_paquete_antes_despues.mp4'
T = A / 'tmp_v5A'; T.mkdir(exist_ok=True)
FD = '/usr/share/fonts/truetype/dejavu/'
def fnt(s, b=True, mono=False):
    return ImageFont.truetype(FD + ('DejaVuSansMono-Bold.ttf' if mono else ('DejaVuSans-Bold.ttf' if b else 'DejaVuSans.ttf')), s)

BG = (238, 238, 236); NEGRO = (17, 17, 17); GRIS = (165, 165, 165); AZUL = (10, 84, 200); AZUL_CL = (96, 170, 255)
VERDE = (37, 170, 90); BLANCO = (255, 255, 255); ROJO = (205, 52, 52)

TI = json.loads((A / 'voz_v5a' / 'tiempos.json').read_text())
TXT = {'P': 'Software, lector, impresora, instalación y soporte, por tres mil quinientos pesos.',
       'H': 'Pago contra entrega. Pagas hasta recibir todo y estar capacitado.',
       'A': 'Notas a mano, tardado, ilegible, con errores.',
       'B': 'Con Excel: nunca está al día, recapturas, muchas fórmulas, no se comparte, y es un embudo.',
       'C': 'Ahora, con Anegocios: venta ágil, de anotar dos veces a registrar una sola vez, y todo en tiempo real.',
       'D': 'Todo por $3,500 MXN: un año de software, impresora, lector, instalación, capacitación y soporte.',
       'E': 'Confirma tu entrega en WhatsApp.'}
ORDEN = list('PHABCDE')
ini, t = {}, 0.2
for k in ORDEN:
    ini[k] = t; t += TI[k]['dur'] + (0.2 if k == 'C' else 0.05)
FIN = ini['E'] + TI['E']['dur'] + 1.1
T0 = ini['H'] - 0.2


def palabras_t(k):
    ws = TXT[k].split(); pw = TI[k]['palabras']
    a, b = ini[k] + pw[0][1], ini[k] + pw[-1][2]
    pausa = lambda w: 4 if w[-1] in ',.:?;' else 0
    pesos = [len(w) + pausa(w) for w in ws]; tot, acc, out = sum(pesos), 0, []
    for w, p in zip(ws, pesos):
        s0 = a + (b - a) * acc / tot; acc += p; out.append((w, s0, a + (b - a) * (acc - pausa(w)) / tot))
    return out
PAL = {k: palabras_t(k) for k in ORDEN}
def tw(k, inicio):
    for i, (w, a, b) in enumerate(PAL[k]):
        if w.lower().strip(',.:?;').startswith(inicio): return a
    raise KeyError(inicio)

ease = lambda x: 1 - (1 - min(max(x, 0), 1)) ** 3
clamp = lambda x: min(max(x, 0.0), 1.0)
pop = lambda x: 1 + 0.08 * math.sin(clamp(x) * math.pi) * (1 - clamp(x)) if x < 1 else 1


def sombra(capa, caja, r, op=70, blur=22, dy=14):
    s = Image.new('RGBA', capa.size, (0, 0, 0, 0)); ImageDraw.Draw(s).rounded_rectangle((caja[0], caja[1] + dy, caja[2], caja[3] + dy), r, fill=(0, 0, 0, op))
    capa.alpha_composite(s.filter(ImageFilter.GaussianBlur(blur)))
def tarjeta(capa, caja, r=34, color=BLANCO):
    sombra(capa, caja, r); ImageDraw.Draw(capa).rounded_rectangle(caja, r, fill=color)
def texto(d, xy, s, f, fill, anchor='la'): d.text(xy, s, font=f, fill=fill, anchor=anchor)
def nueva(): return Image.new('RGBA', (W, H), (0, 0, 0, 0))
def mover(capa, a, dx=0, dy=0):
    if a < 1:
        al = capa.getchannel('A').point(lambda v: int(v * a)); capa = capa.copy(); capa.putalpha(al)
    if dx or dy:
        n = Image.new('RGBA', capa.size, (0, 0, 0, 0)); n.alpha_composite(capa, (int(dx), int(dy))); capa = n
    return capa


def etiqueta(texto_, color, t, y=215):
    k = ease(t / 0.35); capa = nueva(); d = ImageDraw.Draw(capa); f = fnt(34)
    w = d.textlength(texto_, font=f) + 70
    sombra(capa, (W / 2 - w / 2, y - 36, W / 2 + w / 2, y + 36), 36, 60, 14, 8); d = ImageDraw.Draw(capa)
    d.rounded_rectangle((W / 2 - w / 2, y - 36, W / 2 + w / 2, y + 36), 36, fill=color); texto(d, (W // 2, y), texto_, f, BLANCO, 'mm')
    return mover(capa, k, 0, -(1 - k) * 40)


def pastilla(capa, y, texto_, color, icono, kk, oscuro=True):
    if kk <= 0: return
    c = nueva(); d = ImageDraw.Draw(c); f = fnt(36); w = d.textlength(texto_, font=f) + 110
    sombra(c, (W / 2 - w / 2, y - 40, W / 2 + w / 2, y + 40), 40, 70, 12, 8); d = ImageDraw.Draw(c)
    d.rounded_rectangle((W / 2 - w / 2, y - 40, W / 2 + w / 2, y + 40), 40, fill=NEGRO if oscuro else color)
    d.ellipse((W / 2 - w / 2 + 14, y - 26, W / 2 - w / 2 + 66, y + 26), fill=color); texto(d, (W / 2 - w / 2 + 40, y), icono, fnt(30), BLANCO, 'mm')
    texto(d, (W / 2 - w / 2 + 84, y), texto_, f, BLANCO, 'lm')
    capa.alpha_composite(mover(c, clamp(kk * 1.4), 0, (1 - clamp(kk)) * 30))


# ---------------- clips ----------------
def extraer(nombre, fuente, ss, dur, crop='', caja=False):
    d = T / nombre; d.mkdir(exist_ok=True)
    if not list(d.glob('*.jpg')):
        vf = (crop + ',' if crop else '') + f'fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}'
        if caja:
            vf = ('setpts=1.6*PTS,fps=%d,split[a][b];[a]scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d,boxblur=28[bg];[b]scale=%d:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2' % (FPS, W, H, W, H, W))
        subprocess.run([FF, '-v', 'error', '-y', '-ss', str(ss), '-t', str(dur), '-i', str(fuente), '-vf', vf, '-q:v', '3', str(d / '%04d.jpg')], check=True)
    return sorted(d.glob('*.jpg'))
F_M1 = extraer('M1', A / 'clips_v3' / 'M1.mp4', 0, 6)
F_M2 = extraer('M2', A / 'clips_v3' / 'M2.mp4', 0, 6)
F_PANT = extraer('pant', A / 'refs' / 'fernando_video.mp4', 17.2, 3, 'crop=608:1080:700:0')
F_IMP = extraer('imp', A / 'refs' / 'fernando_video.mp4', 42.5, 1.7, caja=True)
def fr(fs, t, largo=None):
    if largo and len(fs) / FPS > largo * 1.0: pass
    i = int(t * FPS); i = min(max(i, 0), len(fs) - 1)
    return Image.open(fs[i]).convert('RGBA')
def fr_estirado(fs, t, largo):
    """Estira el clip (hasta 0.8x) para cubrir la escena sin congelarse."""
    nat = len(fs) / FPS; v = max(nat / largo, 0.8) if largo > nat else 1.0
    return fr(fs, t * v)


# ---------------- subtítulos kinéticos ----------------
CHUNKS = []
for k in ORDEN:
    cur = []
    for i, (w, a, b) in enumerate(PAL[k]):
        cur.append((w, a, b))
        if w[-1] in ',.:?;' or len(cur) >= 4 or sum(len(x[0]) + 1 for x in cur) > 21 or i == len(PAL[k]) - 1:
            CHUNKS.append(cur); cur = []
def subtitulo(t, oscuro):
    ch = None
    for i, c in enumerate(CHUNKS):
        a0 = c[0][1] - 0.05; a1 = CHUNKS[i + 1][0][1] - 0.05 if i + 1 < len(CHUNKS) else c[-1][2] + 0.6
        if a0 <= t < a1: ch = c; kin = clamp((t - a0) / 0.14); break
    if not ch: return None
    capa = nueva(); d = ImageDraw.Draw(capa); f = fnt(58)
    ws = [w for w, _, _ in ch]; an = [d.textlength(w + ' ', font=f) for w in ws]; tot = sum(an) - d.textlength(' ', font=f)
    if tot > W - 70: f = fnt(int(58 * (W - 70) / tot)); an = [d.textlength(w + ' ', font=f) for w in ws]; tot = sum(an) - d.textlength(' ', font=f)
    y = 1000
    if oscuro: d.rounded_rectangle((W / 2 - tot / 2 - 28, y - 52, W / 2 + tot / 2 + 28, y + 52), 30, fill=(0, 0, 0, 150))
    x = W / 2 - tot / 2
    for (w, a, b), n in zip(ch, an):
        yy = y
        if a - 0.02 <= t < b + 0.02: col = AZUL_CL if oscuro else AZUL; yy = y - 5 * math.sin(clamp((t - a) / 0.16) * math.pi)
        elif t >= b: col = BLANCO if oscuro else NEGRO
        else: col = (200, 200, 200) if oscuro else (178, 178, 176)
        d.text((x, yy), w, font=f, fill=col, anchor='lm'); x += n
    return mover(capa, kin * 0.7 + 0.3, 0, (1 - kin) * 14)


# ---------------- INTRO: paquete ----------------
def _tw_opt(k, ini_):
    try: return tw(k, ini_)
    except KeyError: return None
_im = {'caja': _tw_opt('P', 'software'), 'lector': _tw_opt('P', 'lector'), 'impresora': _tw_opt('P', 'impresora'), 'chip0': _tw_opt('P', 'instalaci'), 'chip1': _tw_opt('P', 'soporte'), 'precio': _tw_opt('P', 'tres')}
for _k, _v in _im.items():
    if _v is not None: IP.INI[_k] = max(0.1, _v - 0.1)
IP.INI['rollos'] = IP.INI['impresora'] + 0.45
def escena_p(t): return IP.frame(min(t, ini['H'] - 0.05)).convert('RGBA')
def empuje(t):
    a = ini['H'] - 0.45; k = ease((t - a) / 0.45)
    p = escena_p(t); h_ = escena_h_comp(t); out = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    out.alpha_composite(p, (-int(k * W), 0)); out.alpha_composite(h_, (int((1 - k) * W), 0)); return out


# ---------------- ESCENA H: gancho ----------------
def escena_h(t):
    im = fr_estirado(F_M1, t - T0, ini['B'] - 0.05 - T0)
    v = nueva(); ImageDraw.Draw(v).rectangle((0, 0, W, H), fill=(0, 0, 0, 120)); im.alpha_composite(v)
    capa = nueva(); d = ImageDraw.Draw(capa); f = fnt(64)
    lineas, cur = [], []
    for it in PAL['H']:
        cur.append(it)
        if it[0][-1] == '.' or len(cur) >= 3: lineas.append(cur); cur = []
    if cur: lineas.append(cur)
    for li, ln in enumerate(lineas):
        y = 470 + li * 100; fl = fnt(74) if li == 0 else f; an = [d.textlength(w + ' ', font=fl) for w, _, _ in ln]; tot = sum(an) - d.textlength(' ', font=fl)
        if tot > W - 90: fl = fnt(int(fl.size * (W - 90) / tot)); an = [d.textlength(w + ' ', font=fl) for w, _, _ in ln]; tot = sum(an) - d.textlength(' ', font=fl)
        x = W / 2 - tot / 2
        for (w, a, b), n in zip(ln, an):
            if t >= b + 0.02: col = BLANCO
            elif t >= a - 0.02: col = AZUL_CL
            else: col = (150, 150, 150)
            yy = y - (8 * math.sin(clamp((t - a) / 0.2) * math.pi) if t >= a else 0)
            d.text((x, yy), w, font=fl, fill=col, anchor='lm', stroke_width=3, stroke_fill=(0, 0, 0)); x += n
    return im, capa


def escena_h_comp(t):
    im, hook = escena_h(t); im.alpha_composite(hook); return im


# ---------------- ESCENA A: ANTES, libreta ----------------
TAGS_A = [('notas', 'Notas a mano', '✕'), ('tardado', 'Tardado', '!'), ('ilegible', 'Ilegible', '?'), ('errores', 'Errores de escritura y precio', '✕')]
def escena_a(t):
    im = fr_estirado(F_M1, t - T0, ini['B'] - 0.05 - T0)
    v = nueva(); ImageDraw.Draw(v).rectangle((0, 0, W, 330), fill=(0, 0, 0, 90)); ImageDraw.Draw(v).rectangle((0, H - 560, W, H), fill=(0, 0, 0, 80))
    im.alpha_composite(v.filter(ImageFilter.GaussianBlur(50)))
    im.alpha_composite(etiqueta('ANTES · LIBRETA', ROJO, t - ini['A'] + 0.1))
    capa = nueva()
    for i, (clave, et, ic) in enumerate(TAGS_A):
        pastilla(capa, 700 + i * 0 if False else 560 + i * 0, '', ROJO, ic, 0)
    # solo la pastilla vigente (cada una sustituye a la anterior para no tapar la cara)
    act = None
    for i, (clave, et, ic) in enumerate(TAGS_A):
        t0 = tw('A', clave)
        if t >= t0 - 0.05: act = (et, ic, (t - t0 + 0.05) / 0.3)
    if act: pastilla(capa, 860, act[0], ROJO, act[1], act[2])
    im.alpha_composite(capa)
    return im


# ---------------- ESCENA B: ANTES, Excel ----------------
def celdas(capa, t):
    d = ImageDraw.Draw(capa); x0, y0, cw, ch = 80, 430, 100, 38; rnd = random.Random(11)
    cols = ['A', 'B', 'C', 'D', 'E']
    d.rectangle((x0, y0 - ch, x0 + cw * 5, y0), fill=(33, 115, 70))
    for j, c in enumerate(cols): texto(d, (x0 + j * cw + cw // 2, y0 - ch // 2), c, fnt(22), BLANCO, 'mm')
    errores = [(2, 1, '#¡REF!'), (4, 3, '#VALOR!'), (6, 0, '#¿NOMBRE?'), (3, 4, '#¡DIV/0!'), (7, 2, '#¡REF!')]
    for i in range(8):
        for j in range(5):
            xx, yy = x0 + j * cw, y0 + i * ch
            d.rectangle((xx, yy, xx + cw, yy + ch), outline=(205, 205, 205), fill=(250, 250, 250))
            v = rnd.choice(['$54', '$36.5', '12', '$180', '8', '$22', '0', '$75'])
            texto(d, (xx + cw - 8, yy + ch // 2), v, fnt(20, mono=True), (90, 90, 90), 'rm')
    prog = clamp((t - 0.6) / 4.0)
    for n, (i, j, e) in enumerate(errores):
        if prog * len(errores) > n:
            xx, yy = x0 + j * cw, y0 + i * ch; d.rectangle((xx, yy, xx + cw, yy + ch), fill=(255, 220, 220), outline=ROJO, width=3)
            texto(d, (xx + cw // 2, yy + ch // 2), e, fnt(15, mono=True), ROJO, 'mm')
    texto(d, (x0, y0 + 8 * ch + 34), '=SI(Y(B2>0;C3<>"");SUMA(B2:B40)*0.16;BUSCARV(D5;Hoja2!A:C;3;0))', fnt(14, mono=True), (60, 60, 60), 'lm')


TAGS_B = [('nunca', 'Nunca está al día', '!'), ('recaptur', 'Recapturar de la libreta', '↻'), ('muchas', 'Muchas fórmulas', 'ƒ'), ('no', 'No se comparte', '✕'), ('embudo', 'Un embudo de trabajo', '▼')]
def escena_b(t0_abs):
    t = t0_abs - (ini['B'] - 0.05)
    capa = nueva(); tarjeta(capa, (50, 340, W - 50, 800), 28); celdas(capa, t)
    d = ImageDraw.Draw(capa); texto(d, (80, 365), 'Excel · Ventas.xlsx', fnt(22, False), GRIS, 'lm')
    # embudo al final
    kf = clamp((t0_abs - tw('B', 'embudo')) / 1.2)
    if kf > 0:
        ov = nueva(); od = ImageDraw.Draw(ov); od.rounded_rectangle((50, 340, W - 50, 800), 28, fill=(240, 240, 238, int(235 * ease(kf))))
        capa.alpha_composite(ov); d = ImageDraw.Draw(capa)
        cx = W / 2
        pts = [(cx - 230, 420), (cx + 230, 420), (cx + 40, 660), (cx + 40, 790), (cx - 40, 790), (cx - 230 + 190, 660)]
        pts = [(cx - 230, 420), (cx + 230, 420), (cx + 36, 630), (cx + 36, 770), (cx - 36, 770), (cx - 36, 630)]
        d.polygon(pts, fill=tuple(int(c * ease(kf) + 238 * (1 - ease(kf))) for c in (60, 60, 66)))
        for i in range(7):
            yy = 440 + ((t0_abs * 140 + i * 70) % 330); xx = cx + math.sin(i * 2.1 + t0_abs * 3) * (210 - (yy - 420) * 0.6)
            d.rounded_rectangle((xx - 22, yy - 14, xx + 22, yy + 14), 6, fill=(255, 232, 0) if i % 2 else BLANCO)
    base = nueva(); base.alpha_composite(capa)
    act = None
    for clave, et, ic in TAGS_B:
        tt = tw('B', clave)
        if t0_abs >= tt - 0.05: act = (et, ic, (t0_abs - tt + 0.05) / 0.3)
    if act: pastilla(base, 870, act[0], ROJO, act[1], act[2])
    return base


# ---------------- ESCENA C: DESPUÉS ----------------
TAGS_C = [('venta', 'Venta ágil', '✓'), ('anotar', 'De 2 anotaciones a 1 sola', '✓'), ('tiempo', 'Información en tiempo real', '✓')]
def escena_c(t):
    tl = t - ini['C']; largo = ini['D'] - ini['C']
    if tl < 1.8: im = fr(F_M2, tl + 0.2)
    elif tl < 4.2: im = fr(F_PANT, tl - 1.8)
    else: im = fr(F_IMP, tl - 4.2)
    v = nueva(); ImageDraw.Draw(v).rectangle((0, 0, W, 330), fill=(0, 0, 0, 90)); ImageDraw.Draw(v).rectangle((0, H - 560, W, H), fill=(0, 0, 0, 80))
    im.alpha_composite(v.filter(ImageFilter.GaussianBlur(50)))
    im.alpha_composite(etiqueta('DESPUÉS · ANEGOCIOS', AZUL, tl + 0.2))
    capa = nueva(); act = None
    for clave, et, ic in TAGS_C:
        t0 = tw('C', clave)
        if t >= t0 - 0.05: act = (et, ic, (t - t0 + 0.05) / 0.3)
    if act: pastilla(capa, 860, act[0], VERDE, act[1], act[2])
    im.alpha_composite(capa)
    return im


def transicion(t):
    """Barrido azul 'DESPUÉS' justo antes de la escena C."""
    a = ini['C'] - 0.55; b = ini['C'] + 0.05
    if not (a <= t < b): return None
    k = (t - a) / (b - a)
    capa = nueva(); d = ImageDraw.Draw(capa)
    x = -W + (W * 2) * ease(k) if k < 0.5 else 0
    if k < 0.5: xx = -W + W * ease(k * 2); d.rectangle((xx, 0, xx + W, H), fill=AZUL)
    else: xx = W * ease((k - 0.5) * 2); d.rectangle((xx - W + W, 0, W - xx + 0, H), fill=AZUL) if False else d.rectangle((0, 0, W, H), fill=AZUL)
    if 0.25 < k < 0.8: texto(d, (W // 2, H // 2), 'AHORA', fnt(120), BLANCO, 'mm'); texto(d, (W // 2, H // 2 + 110), 'con Anegocios', fnt(46, False), BLANCO, 'mm')
    if k >= 0.5:
        out = ease((k - 0.5) / 0.5); capa = mover(capa, 1 - out)
    return capa


# ---------------- ESCENA D: precio ----------------
ITEMS = [('año', '1 año de software'), ('impresora', 'Impresora de tickets'), ('lector', 'Lector de códigos'), ('instalaci', 'Instalación'), ('capacitaci', 'Capacitación'), ('soporte', 'Soporte por 1 año')]
def escena_d(t):
    capa = nueva(); d = ImageDraw.Draw(capa); t0 = t - (ini['D'] - 0.05)
    k = ease(t0 / 1.3); v = 3500 * k; esc = pop(t0 / 1.3)
    pw, ph = 560 * esc, 190 * esc
    sombra(capa, (W / 2 - pw / 2, 300 - ph / 2, W / 2 + pw / 2, 300 + ph / 2), 90, 70, 30, 24); d = ImageDraw.Draw(capa)
    d.rounded_rectangle((W / 2 - pw / 2, 300 - ph / 2, W / 2 + pw / 2, 300 + ph / 2), 90, fill=NEGRO)
    texto(d, (W // 2, 288), f'${v:,.0f}', fnt(108, mono=True), BLANCO, 'mm'); texto(d, (W // 2, 356), 'MXN · todo incluido', fnt(24, False), (200, 200, 200), 'mm')
    tarjeta(capa, (60, 460, W - 60, 940)); d = ImageDraw.Draw(capa)
    for i, (clave, et) in enumerate(ITEMS):
        kk = ease((t - tw('D', clave) + 0.05) / 0.3); y = 490 + i * 68
        if kk <= 0: continue
        c = nueva(); cd = ImageDraw.Draw(c)
        cd.ellipse((92, y + 8, 132, y + 48), fill=AZUL); texto(cd, (112, y + 28), '✓', fnt(26), BLANCO, 'mm'); texto(cd, (152, y + 28), et, fnt(31), NEGRO, 'lm')
        capa.alpha_composite(mover(c, kk, (1 - kk) * 70, 0))
    return capa


T_E = ini['E'] - 0.6
def escena_e(t):
    tl = t - T_E; k = ease(tl / 0.45); esc = pop(tl / 0.45)
    capa = nueva(); d = ImageDraw.Draw(capa)
    d.ellipse((W // 2 - 44, 190, W // 2 + 44, 278), fill=AZUL); texto(d, (W // 2, 234), '✓', fnt(58), BLANCO, 'mm')
    texto(d, (W // 2, 340), 'Pago contra entrega', fnt(52), AZUL, 'mm')
    for i, l in enumerate(['Pagas hasta recibir tu', 'impresora, lector y estar', 'capacitado.']): texto(d, (W // 2, 430 + i * 56), l, fnt(42), NEGRO, 'mm')
    bw, bh = 620 * esc, 130 * esc
    sombra(capa, (W / 2 - bw / 2, 700 - bh / 2, W / 2 + bw / 2, 700 + bh / 2), 60); d = ImageDraw.Draw(capa)
    d.rounded_rectangle((W / 2 - bw / 2, 700 - bh / 2, W / 2 + bw / 2, 700 + bh / 2), 60, fill=(37, 211, 102)); texto(d, (W // 2, 700), 'Confirma tu entrega en WhatsApp', fnt(30), BLANCO, 'mm')
    texto(d, (W // 2, 860), 'Anegocios', fnt(70), AZUL, 'mm'); texto(d, (W // 2, 920), 'anegocios.com', fnt(34, False), (90, 90, 90), 'mm')
    return mover(capa, k, 0, (1 - k) * 30)


def componer(t):
    if t < ini['H'] - 0.45:
        im = escena_p(t); s = subtitulo(t, True)
    elif t < ini['H'] - 0.0:
        im = empuje(t); s = None
    elif t < ini['A'] - 0.05:
        im, hook = escena_h(t); im.alpha_composite(hook); s = None
    elif t < ini['B'] - 0.05:
        im = escena_a(t); s = subtitulo(t, True)
    elif t < ini['C'] - 0.05:
        im = Image.new('RGBA', (W, H), BG + (255,)); im.alpha_composite(escena_b(t))
        im.alpha_composite(etiqueta('ANTES · EXCEL', ROJO, t - (ini['B'] - 0.05))); s = subtitulo(t, False)
    elif t < ini['D'] - 0.05:
        im = escena_c(t); s = subtitulo(t, True)
    elif t < T_E:
        im = Image.new('RGBA', (W, H), BG + (255,)); im.alpha_composite(escena_d(t)); s = subtitulo(t, False)
    else:
        im = Image.new('RGBA', (W, H), BG + (255,)); im.alpha_composite(escena_e(t)); s = subtitulo(t, False)
    if s: im.alpha_composite(s)
    tr = transicion(t)
    if tr: im.alpha_composite(tr)
    return im.convert('RGB')


def musica():
    """Cama musical suave generada por código (acordes Am-F-C-G, 84 bpm) para mezclar muy baja; sin música los primeros 3 s (fundido en la mezcla)."""
    import numpy as np, wave
    sr = 44100; n = int((FIN + 1) * sr); tt = np.arange(n) / sr; bpm = 84; beat = 60 / bpm
    acordes = [(220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (261.63, 329.63, 392.0), (196.0, 246.94, 293.66)]
    y = np.zeros(n)
    for i in range(int((FIN + 1) / (beat * 4)) + 1):
        a, b = int(i * beat * 4 * sr), min(n, int((i + 1) * beat * 4 * sr))
        if a >= n: break
        seg = tt[a:b] - tt[a]; env = np.minimum(1, seg / 0.4) * np.minimum(1, (tt[b - 1] - tt[a:b] + 0.001) / 0.5)
        for f0 in acordes[i % 4]:
            y[a:b] += env * (np.sin(2 * np.pi * f0 * seg) + 0.5 * np.sin(2 * np.pi * (f0 * 1.003) * seg)) * 0.12
        for j in range(8):
            s0 = int(a + j * beat / 2 * sr)
            if s0 >= n: break
            m = min(int(0.5 * sr), n - s0); ts = np.arange(m) / sr; f0 = acordes[i % 4][j % 3] * 2
            y[s0:s0 + m] += np.sin(2 * np.pi * f0 * ts) * np.exp(-ts * 6) * 0.10
    y = y / (np.abs(y).max() + 1e-9) * 0.8
    with wave.open(str(T / 'musica.wav'), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((y * 32767).astype('<i2').tobytes())


def main():
    N = int(FIN * FPS); mudo = T / 'mudo.mp4'
    p = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'fast', str(mudo)], stdin=subprocess.PIPE)
    for i in range(N):
        p.stdin.write(componer(i / FPS).tobytes())
        if i % 150 == 0: print('frame', i, '/', N, flush=True)
    p.stdin.close(); p.wait()
    musica(); fa = ''.join(f'[{i + 1}:a]adelay={int(ini[k] * 1000)}|{int(ini[k] * 1000)}[a{i}];' for i, k in enumerate(ORDEN))
    ins = sum([['-i', str(A / 'voz_v5a' / f'{k}.wav')] for k in ORDEN], []) + ['-i', str(T / 'musica.wav')]
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(mudo), *ins, '-filter_complex', fa + ''.join(f'[a{i}]' for i in range(len(ORDEN))) + f'amix=inputs={len(ORDEN)}:normalize=0:duration=longest,volume=1.6[aud]'.replace('[aud]', '[mix]') + f';[{len(ORDEN) + 1}:a]afade=t=in:st=3:d=1.5,afade=t=out:st={FIN - 1.5:.2f}:d=1.5,volume=0.1[mus];[mix][mus]amix=inputs=2:normalize=0[aud]',
                    '-map', '0:v', '-map', '[aud]', '-t', f'{FIN:.2f}', '-c:v', 'libx264', '-profile:v', 'main', '-level', '4.0', '-pix_fmt', 'yuv420p', '-crf', '23', '-preset', 'medium',
                    '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(SALIDA)], check=True)
    print('listo', SALIDA, round(SALIDA.stat().st_size / 1e6, 1), 'MB', round(FIN, 1), 's')


if __name__ == '__main__':
    print('inicios', {k: round(v, 2) for k, v in ini.items()}, 'fin', round(FIN, 2))
    if '--prueba' in sys.argv:
        puntos = [('p0', 1.0), ('p1', 2.2), ('p2', 3.4), ('p3', ini['H'] - 0.25), ('h1', ini['H'] + 2.5), ('a1', ini['A'] + 1.2), ('a2', ini['A'] + 3.5), ('b1', ini['B'] + 1.6), ('b2', ini['B'] + 4.8), ('tr', ini['C'] - 0.3), ('c1', ini['C'] + 1.0), ('c2', ini['C'] + 2.9), ('d', ini['D'] + 5.0), ('e', ini['E'] + 0.8)]
        for n, tt in puntos: componer(tt).save(T / f'{n}.png')
        hoja = Image.new('RGB', (5 * 360, 3 * 640))
        for i, (n, _) in enumerate(puntos): hoja.paste(Image.open(T / f'{n}.png').resize((360, 640)), ((i % 5) * 360, (i // 5) * 640))
        hoja.save(T / 'hoja.jpg', quality=85); print('pruebas listas')
    else:
        main()
