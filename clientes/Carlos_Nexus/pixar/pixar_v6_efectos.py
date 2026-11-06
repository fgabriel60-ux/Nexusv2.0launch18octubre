#!/usr/bin/env python3
"""Pixar v6 de Carlos (Nexus): efectos del reel de referencia aplicados SOBRE el v5 terminado.

Uso:  python3 pixar_v6_efectos.py N      -> genera Pixar_v6_efectos_vN.mp4 en esta carpeta

Base: Pixar_v5_base.mp4 (voz clonada + lipsync + subtítulos de palabra activa + fuego).
No se toca el audio: se copia tal cual (AAC) y solo se agrega silencio al final por la tarjeta de cierre.

Línea de tiempo (s) — palabras de la voz sacadas de los subtítulos de v5:
  0.25–6.5   liquid-glass-graph: costo por mensaje $13.76 -> $5 (se quema con el fuego de v5)
  6.5–11.37  avatar limpio (lipsync)
  11.2–11.6  screen-push-digital en el corte de v5 + palabra LED «NEXUS»
  12.95–17.55 apple-ui-toggles: estrategia / volantes / primer video -> GRATIS en llamada de 10 min
  17.25–17.55 match-cut: la tarjeta se encoge exactamente a la pantalla del teléfono
  17.55–19.9 over-the-shoulder-zoom al teléfono con reportes reales de clientes en WhatsApp
  19.9–21.55 pov-carousel-spin sutil de las tarjetas de clientes
  21.55–22.45 las tarjetas se queman con el fuego de v5 y vuelve el avatar
  22.7–24.6  botón «Agendar llamada» (la voz dice «toca el botón y agenda tu llamada»)
  24.6–29.3  toggles de precio: llamada GRATIS + «$500 al mes si te gusta la estrategia»
  29.6–30.75 pastilla de cristal «Comenta VIDEO»
  30.75–fin  cierre con palabra clave (mosaico de escenas, como el reel de referencia)
"""
import sys, math, subprocess
from pathlib import Path
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

AQUI = Path(__file__).resolve().parent
SRC = AQUI / 'Pixar_v5_base.mp4'
VER = sys.argv[1] if len(sys.argv) > 1 else '1'
OUT = AQUI / f'Pixar_v6_efectos_v{VER}.mp4'
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 720, 1280, 30
SRC_DUR = 31.87
END_DUR = 34.2
FONTS = AQUI / 'fonts'
DEJAVU_B = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

_fc = {}
def F(name, size):
    k = (name, size)
    if k not in _fc:
        path = DEJAVU_B if name == 'dejavu' else str(FONTS / f'{name}.ttf')
        _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]

# ---------------------------------------------------------------- utilidades
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def prog(t, t0, t1): return clamp((t - t0) / (t1 - t0)) if t1 > t0 else float(t >= t1)
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_in(x): x = clamp(x); return x ** 3
def back_out(x, s=1.7):
    x = clamp(x) - 1; return x * x * ((s + 1) * x + s) + 1
def lerp(a, b, x): return a + (b - a) * x

def rr_mask(w, h, r, ss=3):
    m = Image.new('L', (w * ss, h * ss), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w * ss - 1, h * ss - 1], r * ss, fill=255)
    return m.resize((w, h), Image.LANCZOS)

def paste_rgba(base, im, x, y, alpha=1.0):
    if alpha <= 0.001: return
    if alpha < 0.999:
        a = im.getchannel('A').point(lambda v: int(v * alpha))
        im = im.copy(); im.putalpha(a)
    base.alpha_composite(im, (int(round(x)), int(round(y)))) if 0 <= x and 0 <= y and x + im.width <= base.width and y + im.height <= base.height else _paste_clip(base, im, int(round(x)), int(round(y)))

def _paste_clip(base, im, x, y):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(base.width, x + im.width), min(base.height, y + im.height)
    if x1 <= x0 or y1 <= y0: return
    crop = im.crop((x0 - x, y0 - y, x1 - x, y1 - y))
    base.alpha_composite(crop, (x0, y0))

def shadow_layer(w, h, r, blur=26, off=14, alpha=150, pad=60):
    sh = Image.new('RGBA', (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    m = Image.new('L', sh.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([pad, pad + off, pad + w, pad + h + off], r, fill=alpha)
    sh.putalpha(m.filter(ImageFilter.GaussianBlur(blur)))
    return sh, pad

class OverDraw:
    """Dibuja con alfa MEZCLADO sobre una imagen RGBA (ImageDraw solo reemplaza el alfa)."""
    def __init__(self, img):
        self.img = img; self.ov = Image.new('RGBA', img.size, (0, 0, 0, 0)); self.d = ImageDraw.Draw(self.ov)
    def __getattr__(self, k): return getattr(self.d, k)
    def flush(self):
        self.img.alpha_composite(self.ov); self.ov = Image.new('RGBA', self.img.size, (0, 0, 0, 0)); self.d = ImageDraw.Draw(self.ov)

def text_w(font, s): b = font.getbbox(s); return b[2] - b[0]

def draw_spaced(d, xy, s, font, fill, spacing=2.0):
    x, y = xy
    for ch in s:
        d.text((x, y), ch, font=font, fill=fill)
        x += font.getlength(ch) + spacing
    return x

def spaced_w(s, font, spacing=2.0): return sum(font.getlength(c) + spacing for c in s) - spacing

# patrón LED (subpíxeles RGB) para el efecto screen-push-digital
def led_pattern(cell=6):
    p = np.zeros((cell, cell, 3), np.float32)
    w = cell // 3
    for i in range(3):
        p[:cell - 1, i * w:(i + 1) * w - (1 if w > 1 else 0), i] = 1.0
    return np.tile(p, (H // cell + 1, W // cell + 1, 1))[:H, :W]
LED = led_pattern(6)

def digital(img, k):
    """k 0..1: pixelado + rejilla LED + separación RGB (pantalla digital)."""
    if k <= 0.01: return img
    a = img.convert('RGB')
    blk = int(1 + k * 13)
    if blk > 1:
        a = a.resize((max(1, W // blk), max(1, H // blk)), Image.BILINEAR).resize((W, H), Image.NEAREST)
    arr = np.asarray(a).astype(np.float32)
    sh = int(k * 8)
    if sh:
        arr[:, :, 0] = np.roll(arr[:, :, 0], sh, axis=1)
        arr[:, :, 2] = np.roll(arr[:, :, 2], -sh, axis=1)
    led = arr * LED * 2.1
    out = arr * (1 - k * 0.85) + led * (k * 0.85)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert('RGBA')

def zoom(img, s, cx=W / 2, cy=H / 2):
    if abs(s - 1) < 1e-3: return img
    w, h = img.size
    nw, nh = w / s, h / s
    x0, y0 = cx - nw * cx / w, cy - nh * cy / h
    return img.transform((w, h), Image.EXTENT, (x0, y0, x0 + nw, y0 + nh), Image.BICUBIC)

# ---------------------------------------------------------------- subtítulos (mismo estilo que v5)
YELLOW = (250, 214, 72)
def subtitle_layer(word, yellow=False, base=None):
    f = F('dejavu', 75)
    lay = Image.new('RGBA', (W, 260), (0, 0, 0, 0))
    sh = Image.new('RGBA', (W, 260), (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((W / 2 + 3, 147 + 4), word, font=f, anchor='ms', fill=(0, 0, 0, 170), stroke_width=4, stroke_fill=(0, 0, 0, 170))
    lay.alpha_composite(sh.filter(ImageFilter.GaussianBlur(4)))
    ImageDraw.Draw(lay).text((W / 2, 147), word, font=f, anchor='ms', fill=YELLOW if yellow else (255, 255, 255), stroke_width=3, stroke_fill=(48, 36, 30))
    return lay  # se pega en y=900 (línea base en 1047, como v5)

# Palabras de la voz (inicio, fin, palabra, amarilla) en los tramos donde reemplazo la imagen
WORDS = [
    (12.43, 13.13, 'estrategia', True), (13.37, 13.47, 'tus', False), (13.47, 13.97, 'volantes', False),
    (13.97, 14.30, 'y', False), (14.30, 14.43, 'tu', False), (14.43, 14.70, 'primer', False),
    (14.70, 15.00, 'video', False), (15.00, 15.47, 'gratis', True), (15.47, 15.87, 'en', False),
    (15.87, 16.03, 'una', False), (16.03, 16.37, 'llamada', False), (16.37, 16.60, 'de', False),
    (16.60, 16.83, 'diez', False), (16.83, 17.40, 'minutos', False),
    (17.67, 17.87, 'ya', False), (17.87, 18.27, 'ayudamos', False), (18.27, 18.47, 'a', False),
    (18.47, 18.77, 'otros', False), (18.77, 18.97, 'a', False), (18.97, 19.33, 'bajar', False),
    (19.33, 19.53, 'sus', False), (19.53, 20.17, 'costos', False), (20.17, 20.43, 'de', False),
    (20.43, 20.87, 'mensajes', True), (20.87, 21.55, 'drásticamente', False),
    (22.27, 22.63, 'toca', False),
    (24.10, 24.83, 'llamada', False), (24.83, 25.03, 'el', False), (25.03, 25.53, 'costo', False),
    (25.53, 25.83, 'es', False), (25.83, 26.07, '$500', True), (26.07, 26.63, 'pesos', True),
    (27.10, 27.43, 'el', False), (27.43, 27.77, 'precio', False), (27.77, 28.30, 'por', False),
    (28.30, 28.60, 'dejar', False), (28.60, 28.77, 'de', False), (28.77, 29.17, 'adivinar', False),
    (29.17, 29.83, 'y', False),
]
_subc = {}
def word_at(t):
    for a, b, w, y in WORDS:
        if a <= t < b:
            k = (w, y)
            if k not in _subc: _subc[k] = subtitle_layer(w, y)
            return _subc[k]
    return None

# ---------------------------------------------------------------- lectura de v5
def grab(ts):
    r = imageio_ffmpeg.read_frames(str(SRC)); next(r)
    want = {int(round(t * FPS)): t for t in ts}; got = {}
    for i, fr in enumerate(r):
        if i in want: got[want[i]] = Image.frombuffer('RGB', (W, H), fr).convert('RGBA')
        if i >= max(want): break
    return got

print('cuadros de referencia…')
REF = grab([0.20, 5.40, 8.0, 12.90, 21.50, 24.60, 29.50])
CLEAN0 = REF[0.20]
REF540 = np.asarray(REF[5.40].convert('RGB')).astype(np.int16)
REF2150 = np.asarray(REF[21.50].convert('RGB')).astype(np.int16)

def card_region_mask(ref):
    """Zonas de tarjeta azul marino / borde amarillo de v5 en un cuadro de referencia."""
    a = ref.astype(np.int16)
    navy = (a[:, :, 0] < 60) & (a[:, :, 1] < 66) & (a[:, :, 2] < 80) & (a[:, :, 2] >= a[:, :, 0] - 4)
    m = Image.fromarray((navy * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(5))
    return np.asarray(m) > 128

V5CARD_A = np.zeros((H, W), bool); V5CARD_A[66:340, 24:672] = True  # tarjeta de inicio de v5
V5CARD_C = card_region_mask(REF2150)
V5CARD_C[:330] = False

def fire_and_intact(frame_np, ref_np, region):
    """De v5: llamas (para pegarlas encima) y la parte de la tarjeta que sigue sin quemarse
    (detectada por el azul marino de la tarjeta, cerrando huecos del texto)."""
    a = frame_np.astype(np.int16)
    diff = np.abs(a - ref_np).sum(axis=2)
    navy = (a[:, :, 0] < 62) & (a[:, :, 1] < 68) & (a[:, :, 2] < 84) & (a[:, :, 2] >= a[:, :, 0] - 4)
    q = Image.fromarray((navy * 255).astype(np.uint8)).resize((W // 4, H // 4), Image.BOX).point(lambda v: 255 if v > 90 else 0)
    q = q.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.MinFilter(7))
    intact = region & (np.asarray(q.resize((W, H), Image.BILINEAR)) > 128)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    firec = (r > 170) & (r - b > 110) & (g < r - 25) & (diff > 70)
    soot = region & (diff > 60) & (a.max(axis=2) < 70)
    fm = Image.fromarray((firec * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
    im = Image.fromarray((intact * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(2.5))
    sm = Image.fromarray((soot * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))
    return fm, im, sm

# ---------------------------------------------------------------- vidrio esmerilado
def glass(bg, box, r=34, blur=22, tint=(14, 16, 22, 120), bright=1.0):
    x0, y0, x1, y1 = [int(v) for v in box]
    w, h = x1 - x0, y1 - y0
    pad = blur * 2
    crop = bg.crop((x0 - pad, y0 - pad, x1 + pad, y1 + pad)).convert('RGB').filter(ImageFilter.GaussianBlur(blur))
    crop = crop.crop((pad, pad, pad + w, pad + h))
    if bright != 1.0:
        crop = Image.fromarray(np.clip(np.asarray(crop).astype(np.float32) * bright, 0, 255).astype(np.uint8))
    g = crop.convert('RGBA')
    g.alpha_composite(Image.new('RGBA', (w, h), tint))
    # brillo superior (sheen)
    sheen = Image.new('L', (w, h), 0)
    sd = ImageDraw.Draw(sheen)
    for yy in range(h):
        sd.line([(0, yy), (w, yy)], fill=int(34 * max(0, 1 - yy / (h * 0.55))))
    g.alpha_composite(Image.merge('RGBA', (Image.new('L', (w, h), 255),) * 3 + (sheen,)))
    m = rr_mask(w, h, r)
    g.putalpha(m)
    # borde fino luminoso
    bd = Image.new('RGBA', (w * 3, h * 3), (0, 0, 0, 0))
    ImageDraw.Draw(bd).rounded_rectangle([1, 1, w * 3 - 2, h * 3 - 2], r * 3, outline=(255, 255, 255, 95), width=4)
    g.alpha_composite(bd.resize((w, h), Image.LANCZOS))
    return g

# ---------------------------------------------------------------- 1) liquid glass graph
GBOX = (22, 46, 698, 352)
def graph_card(bg, t):
    x0, y0, x1, y1 = GBOX; w, h = x1 - x0, y1 - y0
    g = glass(bg, GBOX, r=36, blur=24, tint=(10, 12, 18, 150), bright=0.85)
    d = OverDraw(g)
    draw_spaced(d, (34, 28), 'COSTO POR MENSAJE', F('Inter-SemiBold', 21), (255, 255, 255, 200), 2.6)
    d.text((34, 58), 'Resultado real · mis campañas', font=F('Inter-Medium', 21), fill=(255, 255, 255, 140))
    p = ease(prog(t, 0.85, 3.05))
    val = lerp(13.76, 5.0, p)
    col = tuple(int(lerp(a, b, ease(prog(t, 1.6, 3.05)))) for a, b in zip((255, 120, 108), (88, 226, 140)))
    s = f'${val:.2f}'
    fbig = F('Inter-Bold', 66)
    d.text((w - 34, 22), s, font=fbig, fill=col + (255,), anchor='ra')
    d.text((w - 36, 98), 'por mensaje', font=F('Inter-Medium', 19), fill=(255, 255, 255, 150), anchor='ra')
    # gráfica: solo dos puntos reales (antes y ahora) unidos por una curva suave
    gx0, gx1, gyt, gyb = 44, w - 70, 150, h - 58
    def curve(u):
        yv = lerp(13.76, 5.0, ease(u))
        return gx0 + (gx1 - gx0) * u, gyb - (yv - 3.5) / (14.5 - 3.5) * (gyb - gyt)
    # cuadrícula tenue
    for k in range(4):
        yy = gyt + (gyb - gyt) * k / 3
        d.line([(gx0, yy), (gx1, yy)], fill=(255, 255, 255, 22), width=1)
    n = 80
    pts = [curve(i / n) for i in range(int(n * p) + 1)]
    if p > 0 and len(pts) >= 2:
        # relleno degradado bajo la línea
        d.flush()
        fill = Image.new('L', (w, h), 0)
        ImageDraw.Draw(fill).polygon(pts + [(pts[-1][0], gyb + 30), (pts[0][0], gyb + 30)], fill=70)
        grad = Image.new('L', (w, h), 0)
        gd = ImageDraw.Draw(grad)
        for yy in range(h):
            gd.line([(0, yy), (w, yy)], fill=int(255 * clamp(1 - (yy - gyt) / (gyb - gyt + 30))))
        fa = ImageChops.multiply(fill, grad)
        g.alpha_composite(Image.merge('RGBA', (Image.new('L', (w, h), 70), Image.new('L', (w, h), 220), Image.new('L', (w, h), 130), fa)))
        glow = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(glow).line(pts, fill=(80, 235, 140, 200), width=12, joint='curve')
        g.alpha_composite(glow.filter(ImageFilter.GaussianBlur(7)))
        d.line(pts, fill=(96, 240, 150, 255), width=5, joint='curve')
        hx, hy = pts[-1]
        d.ellipse([hx - 9, hy - 9, hx + 9, hy + 9], fill=(255, 255, 255, 255))
        d.ellipse([hx - 16, hy - 16, hx + 16, hy + 16], outline=(96, 240, 150, 160), width=3)
    # etiquetas antes / ahora
    sx, sy = curve(0)
    d.ellipse([sx - 7, sy - 7, sx + 7, sy + 7], fill=(255, 120, 108, 255))
    d.text((sx + 14, sy - 30), 'ANTES  $13.76', font=F('Inter-Bold', 22), fill=(255, 150, 140, 235))
    a_now = ease(prog(t, 3.0, 3.35))
    if a_now > 0:
        ex, ey = curve(1)
        d.text((ex - 6, ey - 40), 'AHORA  $5', font=F('Inter-Bold', 24), fill=(120, 245, 165, int(255 * a_now)), anchor='rs')
        chip = '−64%'
        cf = F('Inter-Bold', 24)
        cw = text_w(cf, chip) + 28
        cx1 = w - 34; cx0 = cx1 - cw; cy0 = 126
        sc = back_out(prog(t, 3.0, 3.4))
        if sc > 0.05:
            ch = Image.new('RGBA', (cw, 40), (0, 0, 0, 0))
            cd = ImageDraw.Draw(ch)
            cd.rounded_rectangle([0, 0, cw - 1, 39], 20, fill=(52, 199, 89, 235))
            cd.text((cw / 2, 20), chip, font=cf, fill=(255, 255, 255), anchor='mm')
            ch = ch.resize((max(1, int(cw * sc)), max(1, int(40 * sc))), Image.LANCZOS)
            d.ov.alpha_composite(ch, (int(cx1 - ch.width), int(cy0 + (40 - ch.height) / 2)))
    d.flush()
    return g

# ---------------------------------------------------------------- 2) toggles estilo iOS
GREEN = (52, 199, 89)
def switch(on_k, w=96, h=58):
    ss = 3
    im = Image.new('RGBA', (w * ss, h * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    off = (226, 226, 231)
    col = tuple(int(lerp(a, b, on_k)) for a, b in zip(off, GREEN))
    d.rounded_rectangle([0, 0, w * ss - 1, h * ss - 1], h * ss // 2, fill=col + (255,))
    kr = (h - 8) * ss // 2
    kx = lerp(4 * ss + kr, w * ss - 4 * ss - kr, ease(on_k))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([kx - kr, h * ss / 2 - kr + 4, kx + kr, h * ss / 2 + kr + 4], fill=(0, 0, 0, 60))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    ImageDraw.Draw(im).ellipse([kx - kr, h * ss / 2 - kr, kx + kr, h * ss / 2 + kr], fill=(255, 255, 255, 255))
    return im.resize((w, h), Image.LANCZOS)

def ios_card(w, header, rows, footer=None, foot_k=0.0, r=40):
    """rows: lista de (texto, on_k, aparecer_k, extra_derecha)"""
    rh = 104
    hh = 70 if header else 24
    fh = 0
    if footer: fh = int(150 * ease(foot_k))
    h = hh + rh * len(rows) + 20 + fh
    c = Image.new('RGBA', (w, h), (255, 255, 255, 255))
    d = OverDraw(c)
    if header:
        draw_spaced(d, (36, 30), header.upper(), F('Inter-SemiBold', 20), (142, 142, 147), 2.2)
    y = hh
    for i, (txt, on_k, ap, extra) in enumerate(rows):
        if ap <= 0: y += rh; continue
        a = int(255 * ap)
        fnt = F('Inter-SemiBold', 38) if len(txt) < 22 else F('Inter-SemiBold', 31)
        available = w - 72 - 96 - 18 - (F('Inter-Bold', 30).getlength(extra) + 16 if extra else 0)
        size = fnt.size
        while fnt.getlength(txt) > available and size > 18:
            size -= 1
            fnt = F('Inter-SemiBold', size)
        d.text((36, y + rh / 2), txt, font=fnt, fill=(17, 17, 20, a), anchor='lm')
        sw = switch(on_k)
        sw.putalpha(sw.getchannel('A').point(lambda v: int(v * ap)))
        d.ov.alpha_composite(sw, (w - 36 - sw.width, int(y + (rh - sw.height) / 2)))
        if extra:
            d.text((w - 36 - sw.width - 18, y + rh / 2), extra, font=F('Inter-Bold', 30), fill=GREEN + (a,), anchor='rm')
        if i < len(rows) - 1:
            d.line([(36, y + rh), (w, y + rh)], fill=(229, 229, 234, a), width=2)
        y += rh
    if footer and fh > 20:
        fy = y + 10
        band = Image.new('RGBA', (w - 40, fh - 20), (0, 0, 0, 0))
        bd = ImageDraw.Draw(band)
        bd.rounded_rectangle([0, 0, band.width - 1, band.height - 1], 26, fill=GREEN + (255,))
        bdo = OverDraw(band); footer(bdo, foot_k); bdo.flush()
        d.ov.alpha_composite(band, (20, fy))
    d.flush()
    c.putalpha(ImageChops.multiply(c.getchannel('A'), rr_mask(w, h, r)))
    return c

def footer_gratis_factory(t):
    def f(d, k):
        bw, bh = d.img.size
        if bh < 60: return
        s = back_out(prog(t, 15.0, 15.35))
        fb = F('Inter-Black', int(max(10, 66 * s)))
        d.text((bw / 2, bh * 0.40), 'GRATIS', font=fb, fill=(255, 255, 255), anchor='mm')
        a2 = ease(prog(t, 16.0, 16.35))
        if a2 > 0:
            d.text((bw / 2, bh * 0.80), 'en una llamada de 10 min', font=F('Inter-SemiBold', 27), fill=(255, 255, 255, int(255 * a2)), anchor='mm')
    return f

def footer_precio_factory(t):
    def f(d, k):
        bw, bh = d.img.size
        if bh < 60: return
        p = ease_out(prog(t, 25.83, 26.25))
        val = int(round(500 * p))
        d.text((bw / 2 - 6, bh * 0.44), f'${val}', font=F('Inter-Black', 72), fill=(255, 255, 255), anchor='rm')
        d.text((bw / 2 + 6, bh * 0.44 + 8), 'pesos al mes', font=F('Inter-Bold', 32), fill=(255, 255, 255, 235), anchor='lm')
        d.text((bw / 2, bh * 0.83), 'solo si te gusta la estrategia', font=F('Inter-SemiBold', 25), fill=(255, 255, 255, 230), anchor='mm')
    return f

# ---------------------------------------------------------------- 3) teléfono con WhatsApp
PH_W, PH_H = 360, 740
SCR_PAD = 14
def phone_screen(t, sw, sh):
    """Pantalla tipo WhatsApp con reportes reales (no testimonios)."""
    s = Image.new('RGBA', (sw, sh), (239, 234, 226, 255))
    d = ImageDraw.Draw(s)
    # textura sutil
    rng = np.random.default_rng(3)
    for _ in range(60):
        x, y = rng.integers(0, sw), rng.integers(110, sh)
        d.ellipse([x, y, x + 6, y + 6], outline=(226, 220, 210, 255))
    # barra de estado + encabezado
    d.rectangle([0, 0, sw, 104], fill=(0, 128, 105))
    d.text((24, 14), '10:28', font=F('Inter-SemiBold', 17), fill=(255, 255, 255))
    d.ellipse([18, 48, 62, 92], fill=(255, 255, 255))
    d.text((40, 70), 'N', font=F('Inter-Black', 24), fill=(0, 128, 105), anchor='mm')
    d.text((74, 50), 'Nexus · Reportes', font=F('Inter-Bold', 21), fill=(255, 255, 255))
    d.text((74, 76), 'resultados de campañas', font=F('Inter-Regular', 16), fill=(220, 248, 240))
    msgs = [
        (17.85, 'Grupo JR · Puebla', '80 mensajes', '$6.43 por conversación · CTR 3.91%'),
        (18.75, 'Servilin', '6 conversaciones', '$2.21 por conversación'),
        (19.55, 'Mis campañas', '$13.76 → $5', 'costo por mensaje'),
    ]
    y = 124
    bubbles = []
    for t0, a, b, c in msgs:
        k = prog(t, t0, t0 + 0.28)
        if k <= 0: continue
        bw, bh = sw - 28, 126
        bub = Image.new('RGBA', (bw, bh), (0, 0, 0, 0))
        bd = ImageDraw.Draw(bub)
        bd.rounded_rectangle([0, 0, bw - 1, bh - 1], 18, fill=(255, 255, 255, 255))
        bd.text((16, 12), a, font=F('Inter-Bold', 18), fill=(0, 128, 105))
        bd.text((16, 38), b, font=F('Inter-ExtraBold', 28), fill=(17, 27, 33))
        bd.text((16, 80), c, font=F('Inter-Medium', 15), fill=(84, 101, 111))
        sc = lerp(0.85, 1.0, back_out(k))
        bb = bub.resize((max(1, int(bw * sc)), max(1, int(bh * sc))), Image.LANCZOS)
        bb.putalpha(bb.getchannel('A').point(lambda v: int(v * clamp(k * 1.6))))
        sh_, pd = shadow_layer(bb.width, bb.height, 18, blur=6, off=3, alpha=50, pad=14)
        s.alpha_composite(sh_, (14 - pd, int(y + (bh - bb.height) / 2) - pd))
        s.alpha_composite(bb, (14, int(y + (bh - bb.height) / 2)))
        bubbles.append((14, y, bw, bh))
        y += bh + 16
    # notificación entrante (banner) cuando llega cada mensaje
    for t0, a, b, c in msgs:
        k = prog(t, t0 - 0.05, t0 + 0.55)
        if 0 < k < 1:
            yy = lerp(-70, 8, ease_out(prog(t, t0 - 0.05, t0 + 0.15))) - 80 * ease_in(prog(t, t0 + 0.4, t0 + 0.55))
            n = Image.new('RGBA', (sw - 20, 62), (0, 0, 0, 0))
            nd = ImageDraw.Draw(n)
            nd.rounded_rectangle([0, 0, n.width - 1, 61], 16, fill=(250, 250, 250, 240))
            nd.ellipse([10, 13, 46, 49], fill=(37, 211, 102))
            nd.text((56, 10), 'WhatsApp · Nexus', font=F('Inter-SemiBold', 14), fill=(110, 110, 115))
            nd.text((56, 30), f'{a}: {b}', font=F('Inter-Bold', 17), fill=(20, 20, 20))
            s.alpha_composite(n, (10, int(yy)))
    return s

def bubble_card(a, b, c, w=440, h=200):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 30, fill=(255, 255, 255, 255))
    d.ellipse([26, 26, 58, 58], fill=(37, 211, 102))
    d.text((70, 30), a, font=F('Inter-Bold', 24), fill=(0, 128, 105))
    d.text((26, 74), b, font=F('Inter-ExtraBold', 50), fill=(17, 27, 33))
    d.text((26, 146), c, font=F('Inter-Medium', 22), fill=(84, 101, 111))
    return im

CAROUSEL = [
    bubble_card('Grupo JR · Puebla', '80 mensajes', '$6.43 por conversación · CTR 3.91%'),
    bubble_card('Servilin', '6 conversaciones', '$2.21 por conversación'),
    bubble_card('Mis campañas', '$13.76 → $5', 'costo por mensaje'),
]

def persp(img, quad):
    """Deforma img al cuadrilátero quad=[(x,y)x4: tl,tr,br,bl] en un lienzo W×H."""
    w, h = img.size
    src = [(0, 0), (w, 0), (w, h), (0, h)]
    A = []; B = []
    for (x, y), (u, v) in zip(quad, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    coef = np.linalg.solve(np.array(A, float), np.array(B, float))
    return img.transform((W, H), Image.PERSPECTIVE, tuple(coef), Image.BICUBIC)

def carousel(t, base):
    k = ease_out(prog(t, 19.85, 21.5))
    ang0 = math.radians(-120 * 2) + math.radians(240) * k  # termina con «$13.76 → $5» al frente
    R, cx, cy, fz = 210, W / 2, 620, 1100
    items = []
    for i, im in enumerate(CAROUSEL):
        th = ang0 + math.radians(120 * i)
        items.append((math.cos(th), th, im))
    items.sort(key=lambda z: z[0])
    for cz, th, im in items:
        if cz <= 0.05:
            continue  # El reverso de la tarjeta no muestra texto reflejado.
        w, h = im.size
        pts = []
        for dx, dy in [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]:
            X = R * math.sin(th) + dx * math.cos(th)
            Z = R * math.cos(th) - dx * math.sin(th)
            sc = fz / (fz - Z)
            pts.append((cx + X * sc, cy + dy * sc))
        lay = persp(im, pts)
        dim = 0.35 + 0.65 * (cz + 1) / 2
        a = lay.getchannel('A').point(lambda v: int(v * (0.55 + 0.45 * (cz + 1) / 2)))
        rgb = Image.fromarray((np.asarray(lay.convert('RGB')).astype(np.float32) * dim).astype(np.uint8)).convert('RGBA')
        rgb.putalpha(a)
        base.alpha_composite(rgb)

# ---------------------------------------------------------------- fondos
def blurred(img, r=26, dark=0.62):
    b = img.convert('RGB').filter(ImageFilter.GaussianBlur(r))
    return Image.fromarray((np.asarray(b).astype(np.float32) * dark).astype(np.uint8)).convert('RGBA')

BG_TOG = blurred(REF[12.90], 26, 0.55)
BG_PRICE = blurred(REF[24.60], 26, 0.55)
# hombro desenfocado (primer plano) tomado del propio avatar
_tex = REF[8.0].crop((420, 1000, 700, 1260)).resize((700, 700), Image.BICUBIC).filter(ImageFilter.GaussianBlur(22))
_tex = Image.fromarray((np.asarray(_tex.convert('RGB')).astype(np.float32) * 0.8).astype(np.uint8)).convert('RGBA')
_shm = Image.new('L', (700, 700), 0)
ImageDraw.Draw(_shm).ellipse([60, 120, 1100, 1300], fill=255)   # curva del hombro
_tex.putalpha(_shm.filter(ImageFilter.GaussianBlur(30)))
_sh = _tex
SHOULDER = _sh

PHONE_RECT0 = (180, 300, 180 + PH_W, 300 + PH_H)  # rectángulo del teléfono en el match-cut
TOG_RECT = (60, 330, 660, 0)

def phone_scene(t):
    base = BG_TOG.copy()
    z = lerp(1.0, 1.42, ease(prog(t, 17.55, 19.85)))
    pcx, pcy = (PHONE_RECT0[0] + PHONE_RECT0[2]) / 2, (PHONE_RECT0[1] + PHONE_RECT0[3]) / 2
    # fondo con leve paralaje
    base = zoom(base, 1 + (z - 1) * 0.35)
    # teléfono
    pw, ph = int(PH_W * z), int(PH_H * z)
    tcx, tcy = lerp(pcx, W / 2, ease(prog(t, 17.55, 19.85))), lerp(pcy, 590, ease(prog(t, 17.55, 19.85)))
    phone = Image.new('RGBA', (PH_W, PH_H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(phone)
    pd.rounded_rectangle([0, 0, PH_W - 1, PH_H - 1], 52, fill=(18, 18, 20, 255))
    pd.rounded_rectangle([2, 2, PH_W - 3, PH_H - 3], 50, outline=(90, 90, 96, 255), width=2)
    scr = phone_screen(t, PH_W - 2 * SCR_PAD, PH_H - 2 * SCR_PAD)
    scr.putalpha(rr_mask(scr.width, scr.height, 40))
    phone.alpha_composite(scr, (SCR_PAD, SCR_PAD))
    pd.rounded_rectangle([PH_W / 2 - 50, SCR_PAD + 8, PH_W / 2 + 50, SCR_PAD + 34], 13, fill=(10, 10, 12, 255))
    phone = phone.resize((pw, ph), Image.LANCZOS)
    sh, pad = shadow_layer(pw, ph, 52, blur=30, off=24, alpha=170, pad=80)
    base.alpha_composite(sh, (int(tcx - pw / 2 - pad), int(tcy - ph / 2 - pad)))
    base.alpha_composite(phone, (int(tcx - pw / 2), int(tcy - ph / 2)))
    # hombro en primer plano: se sale de cuadro al acercarse (paralaje mayor)
    zs = lerp(1.0, 1.7, ease(prog(t, 17.55, 19.85)))
    shp = SHOULDER.resize((int(SHOULDER.width * zs), int(SHOULDER.height * zs)), Image.BILINEAR)
    sx = lerp(-330, -900, ease(prog(t, 17.55, 19.85)))
    sy = lerp(760, 1000, ease(prog(t, 17.55, 19.85)))
    paste_rgba(base, shp, sx, sy, 1.0)
    # carrusel
    kc = ease(prog(t, 19.7, 20.1))
    if kc > 0:
        veil = Image.new('RGBA', (W, H), (8, 10, 14, int(150 * kc)))
        base.alpha_composite(veil)
        if kc < 1:
            base = Image.blend(base, base.filter(ImageFilter.GaussianBlur(8)), kc)
        else:
            base = base.filter(ImageFilter.GaussianBlur(8))
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        carousel(t, lay)
        lay.putalpha(lay.getchannel('A').point(lambda v: int(v * kc)))
        base.alpha_composite(lay)
    # leyenda arriba
    la = ease(prog(t, 19.8, 20.1))
    if la > 0:
        cap = 'Reportes reales de mis clientes'
        lb = Image.new('RGBA', (W, 80), (0, 0, 0, 0))
        ImageDraw.Draw(lb).text((W / 2, 40), cap, font=F('Inter-Bold', 30), fill=(255, 255, 255, int(235 * la)), anchor='mm', stroke_width=2, stroke_fill=(0, 0, 0, int(120 * la)))
        base.alpha_composite(lb, (0, 300))
    return base

def toggles_scene(t):
    s = lerp(1.0, 1.06, prog(t, 12.95, 17.55))
    base = zoom(BG_TOG, s)
    rows = [
        ('Tu estrategia', ease(prog(t, 13.15, 13.35)), 1.0, None),
        ('Tus volantes', ease(prog(t, 13.55, 13.75)), 1.0, None),
        ('Tu primer video', ease(prog(t, 14.5, 14.7)), 1.0, None),
    ]
    card = ios_card(600, 'Lo que te armamos', rows, footer=footer_gratis_factory(t), foot_k=prog(t, 14.95, 15.15))
    return base, card

def price_scene(t):
    s = lerp(1.0, 1.05, prog(t, 24.6, 29.3))
    base = zoom(BG_PRICE, s)
    rows = [
        ('Llamada de 10 min', 1.0, 1.0, 'GRATIS'),
        ('Estrategia + volantes + video', 1.0, 1.0, None),
    ]
    card = ios_card(600, 'Si te gusta la estrategia', rows, footer=footer_precio_factory(t), foot_k=prog(t, 25.6, 25.85))
    return base, card

def place_card(base, card, t, t_in, cy=640, t_out=None, out_k=0.0):
    k = back_out(prog(t, t_in, t_in + 0.35))
    sc = lerp(0.82, 1.0, k)
    a = clamp(prog(t, t_in, t_in + 0.2))
    c = card.resize((max(1, int(card.width * sc)), max(1, int(card.height * sc))), Image.LANCZOS)
    x, y = W / 2 - c.width / 2, cy - c.height / 2
    sh, pad = shadow_layer(c.width, c.height, 40, blur=30, off=20, alpha=int(150 * a), pad=80)
    base.alpha_composite(sh, (int(x - pad), int(y - pad)))
    paste_rgba(base, c, x, y, a)
    return (x, y, c.width, c.height)

# ---------------------------------------------------------------- LED «NEXUS» (screen-push-digital)
def led_word(word, t, t0, t1):
    k_in = ease_out(prog(t, t0, t0 + 0.45))
    k_out = ease_in(prog(t, t1 - 0.25, t1))
    if k_in <= 0 or k_out >= 1: return None
    f = F('Inter-Black', 150)
    lay = Image.new('RGB', (W, 300), (0, 0, 0))
    ImageDraw.Draw(lay).text((W / 2, 150), word, font=f, fill=(255, 255, 255), anchor='mm')
    sc = lerp(2.6, 1.0, k_in) * lerp(1.0, 0.7, k_out)
    lay = zoom(lay.convert('RGBA'), sc, W / 2, 150).convert('RGB')
    blk = 5
    small = lay.resize((W // blk, 300 // blk), Image.BILINEAR)
    lay = small.resize((W, 300), Image.NEAREST)
    arr = np.asarray(lay).astype(np.float32) / 255
    led = arr * LED[:300] * 2.4 + arr * 0.55
    a = np.clip(arr.max(axis=2) * 1.0, 0, 1)
    glow = Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(14))
    col = np.clip(led * np.array([1.0, 0.9, 0.42]), 0, 1)  # tono ámbar como el «nexus» amarillo
    rgba = np.dstack([col * 255, np.clip(a * 255 * (1 - k_out) * clamp(k_in * 1.5), 0, 255)]).astype(np.uint8)
    out = Image.new('RGBA', (W, 300), (0, 0, 0, 0))
    gl = Image.new('RGBA', (W, 300), (255, 200, 60, 0)); gl.putalpha(glow.point(lambda v: int(v * 0.55 * (1 - k_out))))
    out.alpha_composite(gl)
    out.alpha_composite(Image.fromarray(rgba, 'RGBA'))
    return out

# ---------------------------------------------------------------- botón «Agendar llamada»
def button(t):
    a = ease(prog(t, 22.7, 22.95)) * (1 - ease(prog(t, 24.45, 24.65)))
    if a <= 0: return None
    press = 1 - 0.06 * math.sin(math.pi * prog(t, 23.25, 23.55))
    w, h = 400, 84
    b = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(b)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 42, fill=(37, 211, 102, 255))
    # icono de calendario
    d.rounded_rectangle([34, 22, 74, 62], 7, outline=(255, 255, 255), width=4)
    d.line([(34, 34), (74, 34)], fill=(255, 255, 255), width=4)
    d.line([(44, 16), (44, 26)], fill=(255, 255, 255), width=4); d.line([(64, 16), (64, 26)], fill=(255, 255, 255), width=4)
    d.text((92, h / 2), 'Agendar llamada', font=F('Inter-Bold', 34), fill=(255, 255, 255), anchor='lm')
    b = b.resize((int(w * press), int(h * press)), Image.LANCZOS)
    b.putalpha(b.getchannel('A').point(lambda v: int(v * a)))
    return b

# ---------------------------------------------------------------- CTA
def cta_pill(bg, t):
    a = ease_out(prog(t, 29.6, 29.95))
    if a <= 0: return None, 0
    box = (40, 70, 680, 270)
    g = glass(bg, box, r=40, blur=22, tint=(12, 12, 16, 140), bright=0.85)
    d = ImageDraw.Draw(g)
    w = box[2] - box[0]
    d.text((w / 2, 74), 'Comenta «VIDEO»', font=F('Inter-Black', 62), fill=(255, 255, 255), anchor='mm')
    d.text((w / 2, 146), 'y te mando el link de tu llamada gratis', font=F('Inter-SemiBold', 27), fill=(255, 214, 72), anchor='mm')
    return g, a

THUMBS = {}
THUMB_T = [1.6, 3.4, 8.6, 12.2, 13.9, 15.6, 18.3, 19.9, 20.8, 23.2, 26.6, 29.9]
def end_card(t, live):
    k = ease(prog(t, 30.52, 30.80))
    base = Image.new('RGBA', (W, H), (18, 16, 20, 255))
    d = OverDraw(base)
    ta = ease(prog(t, 30.6, 30.95))
    d.text((W / 2, 150), 'Comenta «VIDEO»', font=F('Inter-Black', 66), fill=(255, 255, 255, int(255 * ta)), anchor='mm')
    d.flush()
    pa = back_out(prog(t, 30.85, 31.2))
    if pa > 0.02:
        txt = 'y te mando el link de tu llamada gratis'
        f = F('Inter-Bold', 29)
        pw = text_w(f, txt) + 44
        pill = Image.new('RGBA', (pw, 62), (0, 0, 0, 0))
        pdd = ImageDraw.Draw(pill)
        pdd.rounded_rectangle([0, 0, pw - 1, 61], 18, fill=(214, 96, 46, 255))
        pdd.text((pw / 2, 31), txt, font=f, fill=(255, 255, 255), anchor='mm')
        pill = pill.resize((max(1, int(pw * pa)), max(1, int(62 * pa))), Image.LANCZOS)
        base.alpha_composite(pill, (int(W / 2 - pill.width / 2), int(232 - pill.height / 2)))
    # mosaico 4×3 de escenas del propio video (como el cierre del reel de referencia)
    cols, rows = 4, 3
    tw, th = 152, 270
    gx, gy = (W - cols * tw - (cols - 1) * 10) / 2, 300
    for i, tt in enumerate(THUMB_T):
        r_, c_ = divmod(i, cols)
        kk = ease_out(prog(t, 30.7 + 0.04 * i, 31.1 + 0.04 * i))
        if kk <= 0: continue
        src = live if i == 5 else THUMBS.get(tt)
        if src is None: continue
        im = src.convert('RGB').resize((tw, th), Image.LANCZOS)
        im = im.convert('RGBA'); im.putalpha(rr_mask(tw, th, 14))
        x = gx + c_ * (tw + 10); y = gy + r_ * (th + 10) + 40 * (1 - kk)
        paste_rgba(base, im, x, y, kk)
    ba = ease(prog(t, 31.6, 31.9))
    if ba > 0:
        d = OverDraw(base)
        d.text((W / 2, 1185), 'o toca el botón y agenda tu llamada', font=F('Inter-SemiBold', 28), fill=(200, 200, 205, int(255 * ba)), anchor='mm')
        d.flush()
    return base, k

# ---------------------------------------------------------------- render
def render():
    tmp = OUT.with_suffix('.video.mp4')
    enc = subprocess.Popen([FFMPEG, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-profile:v', 'main', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(tmp)],
                           stdin=subprocess.PIPE)
    reader = imageio_ffmpeg.read_frames(str(SRC)); next(reader)
    n_total = int(round(END_DUR * FPS))
    last = None
    for i in range(n_total):
        t = i / FPS
        fr = next(reader, None)
        if fr is not None:
            last = fr
        src_np = np.frombuffer(last, np.uint8).reshape(H, W, 3)
        v5 = Image.fromarray(src_np).convert('RGBA')
        out = v5.copy()

        # --- 1) liquid glass graph, se quema con el fuego de v5
        if 0.25 <= t < 6.6:
            gbg = v5.copy()
            gbg.paste(CLEAN0.crop((0, 0, W, 380)), (0, 0))  # fondo limpio sin la tarjeta de v5
            card = graph_card(gbg, t)
            a_in = ease_out(prog(t, 0.25, 0.55))
            sc = lerp(0.9, 1.0, back_out(prog(t, 0.25, 0.6)))
            if t >= 5.42:
                fm, im_, sm = fire_and_intact(src_np, REF540, V5CARD_A)
                cm = im_.crop(GBOX)
                outside = Image.new('L', cm.size, int(255 * (1 - ease(prog(t, 5.5, 6.1)))))
                inside = Image.fromarray(V5CARD_A[GBOX[1]:GBOX[3], GBOX[0]:GBOX[2]].astype(np.uint8) * 255)
                m = Image.composite(cm, outside, inside)
                card.putalpha(ImageChops.multiply(card.getchannel('A'), m))
                char = Image.new('RGBA', card.size, (25, 12, 4, 0))
                edge = ImageChops.subtract(m.filter(ImageFilter.MaxFilter(9)), m)
                char.putalpha(edge.point(lambda v: min(255, v * 2)))
                card.alpha_composite(char)
            c2 = card.resize((int(card.width * sc), int(card.height * sc)), Image.LANCZOS) if sc < 0.999 else card
            cx, cy = (GBOX[0] + GBOX[2]) / 2, (GBOX[1] + GBOX[3]) / 2
            if t < 0.47 or a_in >= 0.999:
                paste_rgba(out, c2, cx - c2.width / 2, cy - c2.height / 2, a_in)
            else:
                paste_rgba(out, c2, cx - c2.width / 2, cy - c2.height / 2, a_in)
            if t >= 5.42:
                fire = Image.fromarray(src_np).convert('RGBA'); fire.putalpha(fm)
                out.alpha_composite(fire)

        # --- screen-push-digital en el corte de v5 (11.37)
        if 11.17 <= t < 11.37:
            k = ease_in(prog(t, 11.17, 11.37))
            out = digital(zoom(out, 1 + 0.18 * k), k)
        elif 11.37 <= t < 11.62:
            k = 1 - ease_out(prog(t, 11.37, 11.62))
            out = digital(zoom(out, 1 + 0.18 * k), k)
        led = led_word('NEXUS', t, 11.40, 12.98)
        if led is not None:
            out.alpha_composite(led, (0, 70))

        # --- 2) toggles (estrategia, volantes, video, GRATIS) + match-cut al teléfono
        if 12.95 <= t < 17.55:
            base, card = toggles_scene(t)
            kin = ease(prog(t, 12.95, 13.12))
            if kin < 1:
                bgmix = Image.blend(v5, base, kin)
                base = bgmix
            if t < 17.25:
                place_card(base, card, t, 12.97, cy=600)
            else:
                # match-cut: la tarjeta se encoge exactamente al rectángulo de la pantalla del teléfono
                m = ease(prog(t, 17.25, 17.55))
                x0, y0, x1, y1 = PHONE_RECT0
                x0 += SCR_PAD; y0 += SCR_PAD; x1 -= SCR_PAD; y1 -= SCR_PAD
                tw_ = lerp(card.width, x1 - x0, m); th_ = lerp(card.height, y1 - y0, m)
                c = card.resize((int(tw_), int(th_)), Image.LANCZOS)
                plain = Image.new('RGBA', c.size, (239, 234, 226, 255))
                c = Image.blend(c, plain, ease(prog(t, 17.3, 17.52)))
                rmask = rr_mask(c.width, c.height, int(lerp(40, 52, m)))
                c.putalpha(ImageChops.multiply(c.getchannel('A'), rmask))
                cx = lerp(W / 2, (x0 + x1) / 2, m); cy = lerp(600, (y0 + y1) / 2, m)
                sh, pad = shadow_layer(c.width, c.height, 44, blur=30, off=20, alpha=150, pad=80)
                base.alpha_composite(sh, (int(cx - c.width / 2 - pad), int(cy - c.height / 2 - pad)))
                paste_rgba(base, c, cx - c.width / 2, cy - c.height / 2, 1.0)
            out = base

        # --- 3) over-the-shoulder al teléfono + carrusel; se quema con el fuego de v5
        if 17.55 <= t < 22.45:
            scene = phone_scene(t)
            if t >= 21.5:
                fm, im_, sm = fire_and_intact(src_np, REF2150, V5CARD_C)
                outside = Image.new('L', (W, H), int(255 * (1 - ease(prog(t, 21.6, 22.25)))))
                inside = Image.fromarray(V5CARD_C.astype(np.uint8) * 255)
                m = Image.composite(im_, outside, inside)
                scene.putalpha(m)
                o2 = v5.copy(); o2.alpha_composite(scene)
                fire = Image.fromarray(src_np).convert('RGBA'); fire.putalpha(fm)
                o2.alpha_composite(fire)
                out = o2
            else:
                out = scene

        # --- botón «Agendar llamada»
        b = button(t)
        if b is not None:
            out.alpha_composite(b, (int(W / 2 - b.width / 2), int(1168 - b.height / 2)))

        # --- 4) toggles de precio
        if 24.6 <= t < 29.42:
            base, card = price_scene(t)
            kin = ease(prog(t, 24.6, 24.74))
            if kin < 1: base = Image.blend(v5, base, kin)
            place_card(base, card, t, 24.62, cy=600)
            out = base
            if t >= 29.2:
                if t < 29.27:
                    out = digital(zoom(out, 1 + 0.15 * ease_in(prog(t, 29.2, 29.27))), ease_in(prog(t, 29.2, 29.27)))
                else:
                    k = 1 - ease_out(prog(t, 29.27, 29.42))
                    out = digital(zoom(v5.copy(), 1 + 0.15 * k), k)

        # --- subtítulos re-dibujados donde reemplacé la imagen
        if (12.95 <= t < 22.45) or (24.6 <= t < 29.42):
            if not (21.55 <= t < 22.27):
                sl = word_at(t)
                if sl is not None:
                    out.alpha_composite(sl, (0, 900))

        # --- pastilla de cristal «Comenta VIDEO»
        if 29.6 <= t < 30.85:
            g, a = cta_pill(v5, t)
            if g is not None:
                yoff = lerp(-40, 0, a)
                paste_rgba(out, g, 40, 70 + yoff, a)

        # guardar miniaturas para el mosaico final
        for tt in THUMB_T:
            if abs(t - tt) < 0.5 / FPS: THUMBS[tt] = out.copy()

        # --- cierre
        if t >= 30.52:
            ec, k = end_card(t, v5)
            if k < 1:
                # screen-push-digital hacia el cierre
                o1 = digital(zoom(out, 1 + 0.2 * k), k)
                out = Image.blend(o1, ec, k)
            else:
                out = ec

        enc.stdin.write(np.asarray(out.convert('RGB')).tobytes())
        if i % 60 == 0: print(f'  {t:5.1f}s', flush=True)
    enc.stdin.close(); enc.wait()
    # audio: copia exacta del AAC de v5 (sin recodificar)
    subprocess.run([FFMPEG, '-y', '-loglevel', 'error', '-i', str(tmp), '-i', str(SRC), '-map', '0:v', '-map', '1:a', '-c', 'copy', '-movflags', '+faststart', str(OUT)], check=True)
    tmp.unlink()
    print('listo:', OUT, f'{OUT.stat().st_size / 1e6:.1f} MB')

if __name__ == '__main__':
    render()
