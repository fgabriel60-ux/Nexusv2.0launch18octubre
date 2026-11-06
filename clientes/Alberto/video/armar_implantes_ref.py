"""Veneers Dental (Dra. Ángeles) · reel de IMPLANTES con el lenguaje visual del reel dental de referencia (referencia_dental_encias.mp4):
doctora sentada a cámara en consultorio azul (tomas H3 con lip-sync), burbujas 3D arriba (sano / hueco / implante / anestesia) que entran con «pop»,
recuadro 3D sobre el pecho (hueso que se pierde, implante en el hueso), subtítulos palabra por palabra con la palabra clave en color
(rojo, amarillo, verde con brillo o caja azul), zooms de golpe, un pico de desenfoque con whoosh, música y cierre con logo/tarjeta de la clínica.
Composición cuadro a cuadro con PIL → ffmpeg. Uso: python3 armar_implantes_ref.py --version 1 [--tomas r1] [--prueba]"""
import argparse, math, re, subprocess, sys
from pathlib import Path
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageChops
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/XV')
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/_productor')
from armar_xv import fu

AQUI = Path(__file__).resolve().parent
R = AQUI / 'implantes_ref'
FOTOS = AQUI.parent / 'whatsapp' / 'del_cliente'
SFX = AQUI.parents[1] / 'Guillermo' / 'video' / 'sfx'
FF = imageio_ffmpeg.get_ffmpeg_exe()
TMP = Path('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/b4c6325f-3619-4737-92c5-2c71e199d91e/scratchpad/implantes'); TMP.mkdir(parents=True, exist_ok=True)
W, H, FPS = 1080, 1920, 30
TARJ = 3.4
WHATS, DIREC = '631 165 1910', 'Av. Álvaro Obregón 695 · Nogales, Son.'   # del anuncio real que mandó el cliente (doctora_3/4.jpg)

# Texto en pantalla por idea: «|» separa frases, «/» salto de línea; sufijos ^r rojo, ^y amarillo, ^g verde, ^b caja azul.
# Debe tener el mismo número de palabras que lo que dice la voz (las cifras se juntan en una).
TEXTO = {
    'S1': '¿Te falta / un diente?^r | No lo dejes / así.^y',
    'S2': 'Cuando pierdes / una pieza,^r | el hueso^r / de esa zona | puede irse / perdiendo^b | con el tiempo, | y los dientes / de al lado | se pueden / mover.^b',
    'S3': 'La solución es / un implante^g dental:^g | una raíz / de titanio^y | que se coloca / dentro del hueso, | como una / raíz^g nueva.^g',
    'S4': 'Se coloca con / anestesia^b local,^b | y la corona^y / va aparte.^y',
    'S5': 'Aquí en / Veneers^b Dental,^b | tu implante / va desde | $12,500^y / pesos.^y | Escríbenos / por WhatsApp^g | y agenda / tu valoración.',
}
ORDEN = list(TEXTO)
# Tomas: cuadro de zoom (centro x, y de la cara en fracción del cuadro) y golpes de zoom: [(palabra, zoom)]
ZOOMS = {'S1': [(0, 1.0), (5, 1.16)], 'S2': [(0, 1.0)], 'S3': [(0, 1.0)], 'S4': [(0, 1.0), (5, 1.13)], 'S5': [(0, 1.0)]}   # H3 ya mete su propio corte a plano cerrado en S2, S3 y S5
CARA = {s: (.5, .42) for s in TEXTO}
# Eventos por palabra: (toma, índice de palabra, qué, valor)
EVENTOS = [('S1', 0, 'izq', 'M1'), ('S1', 3, 'der', 'M2'),
           ('S2', 4, 'recuadro', 'M3'), ('S2', 14, 'recuadro', None),
           ('S3', 3, 'der', 'M5'), ('S3', 6, 'recuadro', 'M4'), ('S3', 13, 'recuadro', None),
           ('S4', 3, 'izq', 'M6'),
           ('S5', 0, 'izq', 'M1'), ('S5', 2, 'logo', True), ('S5', 7, 'logo', None), ('S5', 12, 'der', 'WA')]
BLUR_EN = 'S3'   # pico de desenfoque (y whoosh) al entrar a esta toma
MODELOS = {'M1': 'M1_r1', 'M2': 'M2a_r2', 'M3': 'M3_r1', 'M4': 'M4b_r2', 'M5': 'M5_r1', 'M6': 'M6_r1'}   # cuadros Qwen elegidos


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1800:])


def duracion(p):
    t = subprocess.run([FF, '-i', str(p)], capture_output=True, text=True).stderr.split('Duration: ')[1].split(',')[0].split(':')
    return int(t[0]) * 3600 + int(t[1]) * 60 + float(t[2])


_wm = None
def _norm(t):
    return re.sub(r'[^0-9a-záéíóúüñ]', '', t.lower())


def tiempos(wav, display):
    """Tiempos por palabra del texto en pantalla: Whisper da tokens con tiempo y se reparten por posición de letras
    (robusto a «a parte» vs «aparte», «12 ,500» vs «$12,500», «Vineyards» vs «Veneers»)."""
    global _wm
    if _wm is None:
        from faster_whisper import WhisperModel
        _wm = WhisperModel('medium', device='cpu', compute_type='int8')
    a = np.frombuffer(subprocess.run([FF, '-v', 'error', '-i', str(wav), '-f', 'f32le', '-ac', '1', '-ar', '16000', '-'], capture_output=True).stdout, np.float32)
    segs, _ = _wm.transcribe(a, language='es', word_timestamps=True)
    ws = [(_norm(w.word), w.start, w.end) for s in segs for w in s.words if _norm(w.word)]
    # posición relativa (0..1) de inicio y fin de cada token whisper en letras
    tot = sum(len(w[0]) for w in ws); acc = 0; marcas = []
    for w, a0, b0 in ws:
        marcas.append((acc / tot, (acc + len(w)) / tot, a0, b0)); acc += len(w)
    def t_en(u, fin=False):
        for m0, m1, a0, b0 in marcas:
            if u <= m1 + 1e-9:
                k = 0 if m1 == m0 else (u - m0) / (m1 - m0)
                return a0 + max(0, min(1, k)) * (b0 - a0)
        return marcas[-1][3]
    dn = [_norm(d) or 'x' for d in display]; dt = sum(len(d) for d in dn); acc = 0; out = []
    for d in dn:
        out.append((t_en(acc / dt + 1e-6), t_en((acc + len(d)) / dt))); acc += len(d)
    return out


# ---------- gráficos ----------
COLORES = {'r': (255, 64, 64), 'y': (255, 214, 10), 'g': (60, 240, 120)}
AZUL = (36, 99, 235)


def sprite_palabra(txt, est, tam=62):
    """RGBA de una palabra con sombra suave; clave en color con brillo (y contorno oscuro para leerse sobre manos) o en caja azul."""
    if '$' in txt: tam += 36
    f = fu(tam + (8 if est else 0), 'ExtraBold' if est else 'Bold')
    asc, desc = f.getmetrics(); w = int(f.getlength(txt)) + 60; h = asc + desc + 50
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    col = COLORES.get(est, (255, 255, 255))
    if est == 'b':
        d = ImageDraw.Draw(img); d.rounded_rectangle((14, 18, w - 14, h - 14), 12, fill=AZUL + (255,))
        col = (255, 255, 255)
    sh = Image.new('L', (w, h), 0); ImageDraw.Draw(sh).text((30, 25 + 4), txt, font=f, fill=210); sh = sh.filter(ImageFilter.GaussianBlur(7))
    if est in ('r', 'y', 'g'):
        gl = Image.new('L', (w, h), 0); ImageDraw.Draw(gl).text((30, 25), txt, font=f, fill=255); gl = gl.filter(ImageFilter.GaussianBlur(9))
        capa = Image.new('RGBA', (w, h), col + (0,)); capa.putalpha(gl.point(lambda v: min(255, int(v * 1.15))))
        s = Image.new('RGBA', (w, h), (0, 0, 0, 0)); s.putalpha(sh); img = Image.alpha_composite(s, img)
        img = Image.alpha_composite(img, capa)
    elif est != 'b':
        s = Image.new('RGBA', (w, h), (0, 0, 0, 0)); s.putalpha(sh); img = Image.alpha_composite(s, img)
    ImageDraw.Draw(img).text((30, 25), txt, font=f, fill=col + (255,), stroke_width=3 if est in ('r', 'y', 'g') else 0, stroke_fill=(20, 12, 10, 255))
    return img


def frases_de(texto):
    """[[ [ (palabra, estilo, índice) ...línea ], ...líneas ], ...frases]"""
    out, k = [], 0
    for fr in texto.split('|'):
        lineas = []
        for ln in fr.split('/'):
            ps = []
            for tok in ln.split():
                est = tok[-1] if re.search(r'\^[rygb]$', tok) else None
                ps.append((tok[:-2] if est else tok, est, k)); k += 1
            lineas.append(ps)
        out.append(lineas)
    return out


class Subs:
    def __init__(self, texto, tws, t0, y=0.84, end=None):
        self.end = end
        self.items = []   # (sprite, x, y, t_ini, t_fin, es_clave)
        frs = frases_de(texto)
        inicios = [tws[fr[0][0][2]][0] for fr in frs]
        for i, fr in enumerate(frs):
            fin = (inicios[i + 1] - 0.04) if i + 1 < len(frs) else tws[fr[-1][-1][2]][1] + 0.5
            sprites = [[(sprite_palabra(p, e), p, e, k) for p, e, k in ln] for ln in fr]
            alto_l = [max(s[0].height for s in ln) - 30 for ln in sprites]
            top = H * y - sum(alto_l) / 2
            for ln, al in zip(sprites, alto_l):
                ancho = sum(s[0].width - 60 for s in ln) + 16 * (len(ln) - 1)
                x = (W - ancho) / 2
                for spr, p, e, k in ln:
                    self.items.append((spr, x - 30, top + (al - (spr.height - 30)) / 2 - 25, t0 + tws[k][0], t0 + fin, bool(e)))
                    x += spr.width - 60 + 16
                top += al

    def pintar(self, img, t):
        if self.end is not None and t >= self.end:
            return
        for spr, x, y, a, z, clave in self.items:
            if a <= t <= z:
                u = min(1, (t - a) / 0.12)
                s = spr
                if clave and t - a < 0.2:
                    k = 1.25 - 0.25 * min(1, (t - a) / 0.2)
                    s = spr.resize((int(spr.width * k), int(spr.height * k)), Image.BILINEAR)
                    x2, y2 = x - (s.width - spr.width) / 2, y - (s.height - spr.height) / 2
                else:
                    x2, y2 = x, y + 10 * (1 - u)
                if u < 1:
                    s = s.copy(); s.putalpha(s.getchannel('A').point(lambda v: int(v * u)))
                img.alpha_composite(s, (int(x2), int(y2)))


def burbuja(png, d=230):
    """Círculo con el render 3D, aro blanco brillante (como las esferas de la referencia)."""
    im = ImageOps.fit(Image.open(png).convert('RGB'), (d, d), Image.LANCZOS, centering=(.5, .5))
    m = Image.new('L', (d * 4, d * 4), 0); ImageDraw.Draw(m).ellipse((0, 0, d * 4 - 1, d * 4 - 1), fill=255); m = m.resize((d, d), Image.LANCZOS)
    P = 40; out = Image.new('RGBA', (d + 2 * P, d + 2 * P), (0, 0, 0, 0))
    gl = Image.new('L', out.size, 0); ImageDraw.Draw(gl).ellipse((P - 4, P - 4, P + d + 4, P + d + 4), outline=255, width=10); gl = gl.filter(ImageFilter.GaussianBlur(10))
    out.paste((235, 245, 255, 255), mask=gl)
    c = im.convert('RGBA'); c.putalpha(m); out.alpha_composite(c, (P, P))
    ImageDraw.Draw(out).ellipse((P - 2, P - 2, P + d + 2, P + d + 2), outline=(255, 255, 255, 255), width=5)
    return out


def burbuja_whatsapp(d=230):
    """Burbuja verde con globo de chat (dibujado, sin logo de marca)."""
    S = 4; D = d * S; im = Image.new('RGB', (D, D), (37, 211, 102)); dd = ImageDraw.Draw(im)
    dd.ellipse((D * .22, D * .2, D * .78, D * .76), outline=(255, 255, 255), width=int(D * .05))
    dd.polygon([(D * .27, D * .66), (D * .2, D * .82), (D * .38, D * .74)], fill=(255, 255, 255))
    for k in (-1, 0, 1):   # «escribiendo…»
        dd.ellipse((D * (.5 + .12 * k - .045), D * .435, D * (.5 + .12 * k + .045), D * .525), fill=(255, 255, 255))
    p = TMP / 'wa.png'; im.resize((d, d), Image.LANCZOS).save(p); return burbuja(p, d)


def recuadro(png, w=700):
    im = Image.open(png).convert('RGB'); h = int(w * im.height / im.width)
    im = im.resize((w, h), Image.LANCZOS).convert('RGBA')
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 42, fill=255); im.putalpha(m)
    P = 40; out = Image.new('RGBA', (w + 2 * P, h + 2 * P), (0, 0, 0, 0))
    sh = Image.new('L', out.size, 0); ImageDraw.Draw(sh).rounded_rectangle((P, P + 14, P + w, P + h + 14), 42, fill=170); sh = sh.filter(ImageFilter.GaussianBlur(18))
    out.paste((0, 0, 0, 255), mask=sh); out.alpha_composite(im, (P, P))
    return out


def logo_vd():
    """Logo real (VD Veneers Dental) recortado del anuncio del cliente: blanco sobre negro → alfa por luminancia."""
    if (AQUI / 'implantes_ref' / 'logo_vd_blanco.png').exists():  # el anuncio original ya no se puede bajar de WhatsApp: logo recortado de la tarjeta del v4
        c = Image.open(AQUI / 'implantes_ref' / 'logo_vd_blanco.png').convert('L')
    else:
        im = Image.open(FOTOS / 'doctora_4.jpg').convert('L'); w, h = im.size
        c = im.crop((int(w * .17), int(h * .012), int(w * .447), int(h * .138)))
    a = c.point(lambda v: max(0, min(255, int((v - 40) * 1.6))))
    out = Image.new('RGBA', c.size, (255, 255, 255, 0)); out.putalpha(a); return out


def sello_logo(d=330):
    """Círculo blanco con el logo y palomita (como el sello de la clínica de la referencia)."""
    lg = logo_vd(); lg = lg.resize((int(d * .8), int(d * .8 * lg.height / lg.width)), Image.LANCZOS)
    negro = Image.new('RGBA', lg.size, (18, 18, 22, 255)); negro.putalpha(lg.getchannel('A'))
    P = 50; out = Image.new('RGBA', (d + 2 * P, d + 2 * P + 40), (0, 0, 0, 0))
    gl = Image.new('L', out.size, 0); ImageDraw.Draw(gl).ellipse((P - 10, P - 10, P + d + 10, P + d + 10), fill=255); gl = gl.filter(ImageFilter.GaussianBlur(22))
    out.paste((255, 255, 255, 180), mask=gl)
    ImageDraw.Draw(out).ellipse((P, P, P + d, P + d), fill=(255, 255, 255, 255))
    out.alpha_composite(negro, (P + (d - lg.width) // 2, P + (d - lg.height) // 2))
    dd = ImageDraw.Draw(out); cx, cy, r = P + d // 2, P + d - 6, 30
    dd.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 255, 255)); dd.ellipse((cx - r + 5, cy - r + 5, cx + r - 5, cy + r - 5), fill=(225, 40, 60, 255))
    dd.line([(cx - 13, cy), (cx - 3, cy + 10), (cx + 14, cy - 10)], fill=(255, 255, 255, 255), width=6)
    return out


def ease_back(u):
    u = max(0, min(1, u)); c = 1.9; return 1 + (c + 1) * (u - 1) ** 3 + c * (u - 1) ** 2


def pegar_pop(img, spr, cx, cy, t, a, z, bob=0.0):
    """Entra con rebote (0.35 s), flota leve y sale encogiéndose (0.2 s)."""
    if t < a or t > z: return
    k = ease_back((t - a) / 0.35)
    if z - t < 0.2: k *= max(0, (z - t) / 0.2)
    if k <= 0.02: return
    s = spr.resize((max(1, int(spr.width * k)), max(1, int(spr.height * k))), Image.BILINEAR) if abs(k - 1) > 0.01 else spr
    dy = bob * math.sin(2 * math.pi * (t - a) / 2.6)
    img.alpha_composite(s, (int(cx - s.width / 2), int(cy - s.height / 2 + dy)))


def tarjeta(fondo, t):
    """Cierre: último cuadro desenfocado + sello del logo + precio + WhatsApp + dirección, con entradas escalonadas."""
    img = fondo.copy()
    capa = Image.new('RGBA', (W, H), (6, 14, 40, 170)); img.alpha_composite(capa)
    pegar_pop(img, SELLO_G, W / 2, 560, t, 0.0, 99)
    d = ImageDraw.Draw(img)
    def c(txt, y, tam, col, peso, desde):
        if t < desde: return
        u = min(1, (t - desde) / 0.25)
        f = fu(tam, peso); x = (W - d.textlength(txt, font=f)) / 2
        lay = Image.new('RGBA', (W, tam + 40), (0, 0, 0, 0)); ImageDraw.Draw(lay).text((x, 10), txt, font=f, fill=col + (int(255 * u),))
        img.alpha_composite(lay, (0, int(y + 20 * (1 - u))))
    c('IMPLANTE DENTAL', 880, 84, (255, 255, 255), 'Black', 0.25)
    c('Raíz de titanio · anestesia local', 990, 44, (200, 220, 255), 'SemiBold', 0.4)
    c('DESDE $12,500 MXN', 1080, 92, COLORES['y'], 'Black', 0.6)
    c('La corona va aparte', 1200, 44, (255, 255, 255), 'SemiBold', 0.75)
    if t >= 0.95:
        u = ease_back((t - 0.95) / 0.35)
        txt = f'WhatsApp  {WHATS}'; f = fu(54, 'ExtraBold'); a = d.textlength(txt, font=f) + 120
        pill = Image.new('RGBA', (int(a) + 40, 180), (0, 0, 0, 0)); pd = ImageDraw.Draw(pill)
        pd.rounded_rectangle((20, 20, a + 20, 150), 65, fill=(37, 211, 102, 255)); pd.text((80, 50), txt, font=f, fill=(255, 255, 255, 255))
        s = pill.resize((max(1, int(pill.width * u)), max(1, int(pill.height * u))), Image.BILINEAR)
        img.alpha_composite(s, (int(W / 2 - s.width / 2), int(1395 - s.height / 2)))
    c(DIREC, 1520, 40, (220, 230, 255), 'SemiBold', 1.2)
    return img


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--version', default='1'); ap.add_argument('--tomas', default='r1'); ap.add_argument('--prueba', action='store_true')
    ap.add_argument('--musica', default=str(R / 'musica.wav'))
    arg = ap.parse_args()
    global SELLO_G
    SELLO_G = sello_logo(360)
    # tiempos de cada toma = duración de su voz (la toma H3 dura un poco más)
    durs = {s: duracion(AQUI / 'voz' / f'ref_{s}_44.wav') for s in ORDEN}
    ini, t = {}, 0.0
    for s in ORDEN: ini[s] = t; t += durs[s]
    T_HABLA = t; TOTAL = T_HABLA + TARJ
    tws = {s: tiempos(AQUI / 'voz' / f'ref_{s}_44.wav', [re.sub(r'\^[rygb]$', '', x) for x in TEXTO[s].replace('|', ' ').replace('/', ' ').split()]) for s in ORDEN}
    subs = [Subs(TEXTO[s], tws[s], ini[s], end=ini[s] + durs[s]) for s in ORDEN]
    # cuadros de cada toma (24 fps)
    clips = {}
    for s in ORDEN:
        rd = imageio_ffmpeg.read_frames(str(R / 'tomas' / f'{s}_{arg.tomas}.mp4'))
        meta = next(rd); ws, hs = meta['size']
        clips[s] = [np.frombuffer(fr, np.uint8).reshape(hs, ws, 3) for fr in rd]
    # sprites 3D
    C = R / 'cuadros'
    esc = {m: burbuja(C / f'{MODELOS[m]}.png') for m in ('M1', 'M2', 'M5', 'M6')}
    esc['WA'] = burbuja_whatsapp()
    rec = {m: recuadro(C / f'{MODELOS[m]}.png') for m in ('M3', 'M4')}
    sello = sello_logo(300)
    # línea de tiempo de capas: pos → [(ini, fin, sprite)]
    capas = {'izq': [], 'der': [], 'recuadro': [], 'logo': []}
    sfx_pop = []
    for s, k, que, val in EVENTOS:
        tt = ini[s] + tws[s][k][0]
        if capas[que] and capas[que][-1][1] is None: capas[que][-1][1] = tt
        if val:
            spr = sello if que == 'logo' else (rec[val] if que == 'recuadro' else esc[val])
            capas[que].append([tt, None, spr]); sfx_pop.append(tt)
    for q in capas:
        if capas[q] and capas[q][-1][1] is None: capas[q][-1][1] = T_HABLA - 0.05
    POS = {'izq': (170, 390), 'der': (910, 390), 'recuadro': (W / 2, 1290), 'logo': (W / 2, 1290)}   # recuadro bajo la barbilla aun en planos cerrados
    t_blur = ini[BLUR_EN]

    def zoom_de(s, tl):
        z = 1.0
        for k, zz in ZOOMS[s]:
            if tl >= tws[s][k][0] - (0.0 if k else 1.0): z = zz
        # golpe: los primeros 0.3 s de la toma vienen de un poco más cerca y asientan
        return z * (1 + 0.06 * max(0, 1 - tl / 0.3))

    sal_hd = TMP / f'hd_v{arg.version}.mp4'
    n_fr = int(TOTAL * FPS) if not arg.prueba else int(6 * FPS)
    enc = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', str(sal_hd)], stdin=subprocess.PIPE)
    fondo_tarj = None
    for i in range(n_fr):
        t = i / FPS
        if t < T_HABLA:
            s = max(x for x in ORDEN if ini[x] <= t + 1e-6); tl = t - ini[s]
            fr = clips[s][min(len(clips[s]) - 1, int(tl * 24))]
            hs, ws = fr.shape[:2]
            z = zoom_de(s, tl); cx, cy = CARA[s]
            cw, ch = ws / z, hs / z
            x0 = min(max(0, cx * ws - cw / 2), ws - cw); y0 = min(max(0, cy * hs - ch * cy), hs - ch)
            img = Image.fromarray(fr).resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))
            img = img.filter(ImageFilter.UnsharpMask(2, 60, 2))
            db = abs(t - t_blur)
            if db < 0.28:
                img = img.filter(ImageFilter.GaussianBlur(26 * (1 - db / 0.28)))
            img = img.convert('RGBA')
            for q, lst in capas.items():
                for a, z2, spr in lst:
                    pegar_pop(img, spr, *POS[q], t, a, z2, bob=6 if q in ('izq', 'der') else 0)
            for sb in subs: sb.pintar(img, t)
        else:
            if fondo_tarj is None:
                ult = Image.fromarray(clips[ORDEN[-1]][-1]).resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(22))
                fondo_tarj = ult.convert('RGBA')
            img = tarjeta(fondo_tarj, t - T_HABLA)
        enc.stdin.write(img.convert('RGB').tobytes())
    enc.stdin.close(); enc.wait()
    # audio: voz por tomas + música + pops + whoosh
    voz = TMP / 'voz.wav'
    ff([x for s in ORDEN for x in ('-i', str(AQUI / 'voz' / f'ref_{s}_44.wav'))] + ['-filter_complex',
       ''.join(f'[{i}:a]aresample=48000,aformat=channel_layouts=mono[a{i}];' for i in range(len(ORDEN))) + ''.join(f'[a{i}]' for i in range(len(ORDEN))) +
       f'concat=n={len(ORDEN)}:v=0:a=1[v]', '-map', '[v]', str(voz)])
    ent = ['-i', str(voz), '-i', arg.musica]
    # v6b: la música se agacha cuando habla la doctora (Glimmer oía «a quién venir dental» y «amistecía» por la música encima)
    fl = (f"[0:a]aresample=48000,apad=whole_dur={TOTAL:.2f},asplit[vz][vzk];[1:a]aresample=48000,aloop=loop=-1:size=2147483647,atrim=0:{TOTAL:.2f},volume=0.16,"
          f"afade=t=in:st=0:d=0.3,afade=t=out:st={TOTAL - 1.0:.2f}:d=1.0[mu0];[mu0][vzk]sidechaincompress=threshold=0.015:ratio=10:attack=15:release=350[mu];")
    mix = ['[vz]', '[mu]']
    efectos = [(SFX / 'whoosh.wav', t_blur - 0.2, 0.55), (SFX / 'boom.wav', T_HABLA, 0.35)] + [(SFX / 'clic.wav', tt, 0.5) for tt in sfx_pop]
    for j, (p, tt, vol) in enumerate(efectos):
        ent += ['-i', str(p)]; ms = max(0, int(tt * 1000))
        fl += f'[{j + 2}:a]aresample=48000,volume={vol},adelay={ms}|{ms}[e{j}];'; mix.append(f'[e{j}]')
    fl += ''.join(mix) + f'amix=inputs={len(mix)}:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]'
    aud = TMP / 'audio.wav'
    ff(ent + ['-filter_complex', fl, '-map', '[a]', '-t', f'{TOTAL:.2f}', str(aud)])
    sal = AQUI / f'Veneers_Dra_Angeles_implantes_estilo_ref_v{arg.version}.mp4'
    if arg.prueba: sal = TMP / 'prueba.mp4'
    ff(['-i', str(sal_hd), '-i', str(aud), '-map', '0:v', '-map', '1:a', '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1',
        '-pix_fmt', 'yuv420p', '-crf', '21', '-preset', 'slow', '-c:a', 'aac', '-b:a', '128k', '-shortest', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB', f'{TOTAL:.1f}s')


if __name__ == '__main__':
    main()
