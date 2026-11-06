"""Lisbeth v9: GANCHO renovado (primeros ~8 s) al estilo del reel de referencia (cinelmobiliario: un terreno que «va tomando forma»).
Entrada más llamativa: arranca abierto con el pueblo de Tomatlán, la cámara vuela al terreno, el contorno se TRAZA, los lotes se delimitan con barrido
y se van «construyendo» (tierra → verde) uno tras otro. El resto del video, la voz y los datos son los de v8."""
import subprocess, sys
import numpy as np
import scipy.ndimage as nd
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
import multiprocessing as mp
from armar_v8 import *   # noqa  (v7/v6: render, cap, degradado, pin, etiqueta, efecto_lotes, MASK, PLANO, coef...)
import armar_v8 as v8

TMP = AQUI / 'tmp_v9'; TMP.mkdir(exist_ok=True)
TOMATLAN = (19.9381, -105.2492)       # pueblo de Tomatlán, Jal. (coordenada aproximada de la cabecera)
T_CONT, T_LIN, T_FIN = 2.2, 3.6, 8.6  # trazo del contorno · barrido de líneas · fin de la «construcción»

# ── regiones (lotes) del plano → etiquetas para pintarlos uno a uno ──
def regiones():
    lin = np.array(MASK) > 40
    lab, n = nd.label(~lin)
    h, w = lab.shape
    borde = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
    out = np.zeros((h, w), np.int32); info = []
    for i in range(1, n + 1):
        if i in borde: continue
        m = lab == i; a = int(m.sum())
        if a < 350 or a > 0.12 * h * w: continue
        ys, xs = np.nonzero(m); info.append((i, ys.mean() / h, xs.mean() / w))
    info.sort(key=lambda r: r[1] + 0.45 * r[2])
    for k, (i, cy, cx) in enumerate(info, 1): out[lab == i] = k
    return out, len(info)


REG, NREG = regiones()
REG_IMG = Image.fromarray(REG, mode='I')
INI = np.zeros(NREG + 1, np.float32); INI[1:] = T_LIN + 0.2 + (T_FIN - T_LIN - 2.6) * (np.arange(NREG) / max(1, NREG - 1)) ** 0.9
TIERRA = np.array([205, 126, 74], np.float32); VERDE = np.array([112, 168, 96], np.float32)


def rellena_lotes(img, pr, t):
    dst = [pr(la, lo) for lo, la in [POLIGONO[0], POLIGONO[1], POLIGONO[2], POLIGONO[3]]]
    c = coef(PLANO, dst)
    L = np.array(REG_IMG.transform((W, H), Image.PERSPECTIVE, c, Image.NEAREST)).astype(np.int32)
    u = (t - INI) / 0.9
    k1 = np.clip(u, 0, 1); k1 = k1 * k1 * (3 - 2 * k1)
    k2 = np.clip((u - 1.1) / 1.3, 0, 1); k2 = k2 * k2 * (3 - 2 * k2)
    k1[0] = 0
    a = (0.55 * k1)[L][..., None]
    col = (TIERRA[None] * (1 - k2[:, None]) + VERDE[None] * k2[:, None])[L]
    base = np.array(img.convert('RGB')).astype(np.float32)
    return Image.fromarray(np.clip(base * (1 - a) + col * a, 0, 255).astype(np.uint8))


def contorno(img, pr, t, ini, dur):
    """El perímetro del terreno se traza como un trazo luminoso (como el borde del reel de referencia)."""
    p = suave((t - ini) / dur)
    if p <= 0: return img
    pts = [pr(la, lo) for lo, la in POLIGONO]; pts = pts + [pts[0]]
    seg = [((pts[i + 1][0] - pts[i][0]) ** 2 + (pts[i + 1][1] - pts[i][1]) ** 2) ** .5 for i in range(4)]
    meta = sum(seg) * p
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    rec = 0; fin = pts[0]
    for i in range(4):
        if rec + seg[i] <= meta: d.line([pts[i], pts[i + 1]], fill=(255, 236, 170, 255), width=8); rec += seg[i]; fin = pts[i + 1]
        else:
            f = (meta - rec) / seg[i]; fin = (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f)
            d.line([pts[i], fin], fill=(255, 236, 170, 255), width=8); break
    if p < 1: d.ellipse((fin[0] - 15, fin[1] - 15, fin[0] + 15, fin[1] + 15), fill=(255, 255, 255, 255), outline=ORO, width=5)
    glow = capa.filter(ImageFilter.GaussianBlur(9))
    return Image.alpha_composite(Image.alpha_composite(img.convert('RGBA'), glow), capa).convert('RGB')


def sA9(t, limpio=False):
    # entrada: abierto sobre Tomatlán → vuelo al terreno (misma curva de zoom que v8 desde t≈2 s)
    k = suave(t / 6.0)
    z = lerp(13.4, 19.0, k) + 0.3 * max(0, t - 6.0) / (TA - 6.0)
    kc = suave(t / 3.6)
    la, lo = lerp(lerp(CENTRO[0], TOMATLAN[0], .72), CENTRO[0], kc), lerp(lerp(CENTRO[1], TOMATLAN[1], .72), CENTRO[1], kc)
    im, pr = render(la, lo, z, W, H)
    if t < 3.6:   # entrada más viva: color y contraste (el pueblo y el campo se ven más atractivos)
        g = suave((3.6 - t) / 1.2); im = ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(1 + .45 * g)).enhance(1 + .16 * g)
    # pueblo
    a = suave((t - 0.25) / 0.4) * suave((2.9 - t) / 0.4)
    if a > 0:
        capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa); x, y = pr(*TOMATLAN); r = 40 + 70 * ((t * 1.3) % 1); d.ellipse((x - r, y - r, x + r, y + r), outline=(255, 236, 170, int(230 * (1 - ((t * 1.3) % 1)))), width=6)
        pin(d, x, y - 6, (255, 255, 255), 16); etiqueta(d, x, y - 130, 'TOMATLÁN, JAL.', 30)
        capa.putalpha(capa.getchannel('A').point(lambda v: int(v * a))); im = Image.alpha_composite(im.convert('RGBA'), capa).convert('RGB')
    # construcción: lotes se pintan, líneas se delimitan, contorno se traza
    if t > T_LIN: im = rellena_lotes(im, pr, t)
    im = contorno(im, pr, t, T_CONT, 1.5)
    p = suave((t - T_LIN) / 3.4)
    if p > 0: im = efecto_lotes(im, pr, p)
    a2 = suave((t - 8.2) / 0.5) * suave((9.8 - t) / 0.4)
    if a2 > 0:
        capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa); x, y = pr(*CENTRO); pin(d, x, y - 10); etiqueta(d, x, y - 150, 'TU TERRENO')
        capa.putalpha(capa.getchannel('A').point(lambda v: int(v * a2))); im = Image.alpha_composite(im.convert('RGBA'), capa).convert('RGB')
    if limpio: return im
    # etiqueta superior del gancho (aparece al delimitar los lotes)
    b = suave((t - 4.0) / 0.4) * suave((8.4 - t) / 0.4)
    if b > 0:
        capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa); etiqueta(d, W / 2, 250, 'LOTES DELIMITADOS', 40)
        capa.putalpha(capa.getchannel('A').point(lambda v: int(v * b))); im = Image.alpha_composite(im.convert('RGBA'), capa).convert('RGB')
    im = degradado(im)
    im = cap(im, ['LISBETH', 'ASESORA INMOBILIARIA'], t, 0.4, 3.3)
    im = cap(im, ['ELEGIR DÓNDE CONSTRUIR', 'TU PATRIMONIO'], t, 3.6, 9.6)
    im = cap(im, ['TERRENO DE', '30,000 m²'], t, 9.9, 12.0)
    im = cap(im, ['LOTES DE', '400 A 600 m²'], t, 12.2, 13.5)
    return cap(im, ['A 20 MIN', 'DE LA PLAYA'], t, 13.6, TA - .1)


def sA9_tail(t):
    """Tras la construcción (t > T_FIN) los lotes quedan pintados y delimitados (estado final estático del gancho)."""
    return sA9(t)


ESC9 = [(0, TA, sA9)] + v8.ESC8[1:]


def frame9(t):
    for i, (a, b, f) in enumerate(ESC9):
        if t < b or i == len(ESC9) - 1:
            im = f(t)
            if i < len(ESC9) - 1 and b - t < 0.18: im = Image.blend(im, ESC9[i + 1][2](t), 0.5 * (1 - (b - t) / 0.18))
            return im


if __name__ == '__main__':
    solo = [float(x) for x in sys.argv[1:]]
    if solo:
        for s in solo: frame9(s).save(TMP / f'prueba_{s}.png'); print('ok', s)
        raise SystemExit
    sal = AQUI / 'final' / 'Lisbeth_terreno_v9.mp4'; hd = TMP / 'hd.mp4'
    p = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', str(VOZ),
                          '-map', '0:v', '-map', '1:a', '-t', f'{TOTAL:.2f}', '-c:v', 'libx264', '-profile:v', 'main', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p',
                          '-c:a', 'aac', '-ar', '44100', '-b:a', '160k', '-movflags', '+faststart', str(hd)], stdin=subprocess.PIPE)
    def f(n): return frame9(n / FPS).tobytes()
    with mp.get_context('fork').Pool(2) as pool:
        for n, b in enumerate(pool.imap(f, range(int(TOTAL * FPS)), chunksize=4)):
            p.stdin.write(b)
            if n % 90 == 0: print(f'{n / FPS:.1f}s', flush=True)
    p.stdin.close(); p.wait()
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(hd), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p',
                    '-crf', '21', '-c:a', 'copy', '-movflags', '+faststart', str(sal)], check=True)
    print(sal, sal.stat().st_size // 1024, 'KB')
