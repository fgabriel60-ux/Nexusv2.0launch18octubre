"""Mariano · marometa por CÓDIGO (31 oct, sin GPU): plano abierto fijo de su casa Salvia (fondo limpio de r5),
recortes reales de Mariano (rembg) animados: parado en la orilla del techo → se agacha → salto mortal hacia atrás
(vuelta completa con desenfoque) → cae creciendo hacia la cámara con su sombra → destello → corte al aterrizaje r4 y su gancho.
  python3 marometa.py  → codigo/marometa.mp4 (solo video, 720x1280, 30 fps)"""
import math, subprocess
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
from pathlib import Path
D = Path(__file__).parent
W, H, FPS = 720, 1280, 30
_f = Image.open(D / 'fondo.png').convert('RGB').resize((W, H)); ZF, CX0, CY0 = 1.0, 360, 640   # acerca la casa
_cw, _ch = W / ZF, H / ZF; FONDO = _f.crop((int(CX0 - _cw / 2), int(CY0 - _ch / 2), int(CX0 + _cw / 2), int(CY0 + _ch / 2))).resize((W, H), Image.LANCZOS)
SP = {n: Image.open(D / f'{n}.png').convert('RGBA') for n in ('parado', 'tuck', 'aire')}
# quita la sombra pegada al recorte «parado» (la parte de abajo a la derecha)
p = np.array(SP['parado']); h = p.shape[0]; p[int(h * .80):, int(p.shape[1] * .62):, 3] = 0; SP['parado'] = Image.fromarray(p)
TECHO_Y, X0 = 552, 300            # orilla del techo y posición inicial
T_PARADO, T_VUELTA, T_CAIDA = 0.55, 0.85, 0.80
TOTAL = T_PARADO + T_VUELTA + T_CAIDA


def ease_in(x): return x * x
def ease_out(x): return 1 - (1 - x) ** 2


def pegar(lienzo, spr, cx, pie_y, alto, rot=0, sx=1, sy=1, por_centro=False):
    k = alto / spr.height
    s = spr.resize((max(1, int(spr.width * k * sx)), max(1, int(spr.height * k * sy))), Image.LANCZOS)
    if rot: s = s.rotate(rot, resample=Image.BICUBIC, expand=True)
    x = int(cx - s.width / 2); y = int(pie_y - s.height / 2) if por_centro else int(pie_y - s.height)
    lienzo.alpha_composite(s, (x, y))


def sombra(lienzo, cx, y, ancho, alfa):
    if alfa <= 0: return
    c = Image.new('RGBA', lienzo.size, (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    d.ellipse((cx - ancho, y - ancho * .18, cx + ancho, y + ancho * .18), fill=(20, 20, 30, int(alfa)))
    lienzo.alpha_composite(c.filter(ImageFilter.GaussianBlur(max(2, ancho * .15))))


def estado(t, lienzo):
    if t < T_PARADO:                                   # parado, se balancea y se agacha
        k = t / T_PARADO; agacha = max(0, (k - .6) / .4)
        pegar(lienzo, SP['parado'], X0 + 2 * math.sin(t * 9), TECHO_Y, 88, sx=1 + .08 * agacha, sy=1 - .18 * agacha)
        return
    t -= T_PARADO
    if t < T_VUELTA:                                   # salto mortal hacia atrás: parábola + vuelta completa
        k = t / T_VUELTA
        cx = X0 + 90 * k; cy = TECHO_Y - 70 - 230 * (4 * k * (1 - k)) + 90 * k
        rot = 180 + 360 * ease_out(k)                  # «tuck» está de cabeza: 180° = cabeza arriba
        if k < .08: pegar(lienzo, SP['parado'], cx, TECHO_Y - 6, 124, sy=1.08)
        else: pegar(lienzo, SP['tuck'], cx, cy, 100 + 30 * k, rot=rot, por_centro=True)
        return
    t -= T_VUELTA                                      # cae hacia la cámara creciendo
    k = min(1, t / T_CAIDA); e = ease_in(k)
    alto = 150 + 950 * e; cx = X0 + 90 + (360 - X0 - 90) * e
    pie = TECHO_Y + 110 + (1430 - TECHO_Y - 110) * e
    suelo = 900 + (1250 - 900) * e
    sombra(lienzo, cx, suelo, 45 + 220 * e, 60 + 120 * e)
    pegar(lienzo, SP['aire'], cx, pie, alto)


def cuadro(n):
    acc = np.zeros((H, W, 3), np.float32); SUB = 4
    z = 1 + .035 * (n / (TOTAL * FPS))                 # zoom lento de cámara
    base = FONDO.resize((int(W * z), int(H * z)), Image.LANCZOS).crop((int(W * (z - 1) / 2), int(H * (z - 1) / 2), int(W * (z - 1) / 2) + W, int(H * (z - 1) / 2) + H)).convert('RGBA')
    for s in range(SUB):                                # desenfoque de movimiento
        lz = base.copy(); estado((n + s / SUB) / FPS, lz); acc += np.asarray(lz.convert('RGB'), np.float32)
    im = (acc / SUB).astype(np.uint8)
    t = n / FPS
    if t > TOTAL - .12:                                 # temblor justo antes del impacto
        dx, dy = np.random.randint(-10, 11, 2); im = np.roll(np.roll(im, dy, 0), dx, 1)
    return im


nf = int(TOTAL * FPS)
p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                      '-c:v', 'libx264', '-crf', '17', '-pix_fmt', 'yuv420p', str(D / 'marometa_abierto.mp4')], stdin=subprocess.PIPE)
for n in range(nf): p.stdin.write(cuadro(n).tobytes())
p.stdin.close(); p.wait(); print('listo', nf / FPS)
