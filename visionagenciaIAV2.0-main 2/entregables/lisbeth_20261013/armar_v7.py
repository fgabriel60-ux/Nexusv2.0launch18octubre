"""Lisbeth v7: (1) los lotes se DIBUJAN sobre el terreno satelital con efecto de barrido (en vez de mostrar la hoja del plano),
(2) foto «imponente» del aeropuerto al llegar, (3) voz de Lisbeth con más punch (clonada en Fish, speed 1.1 + masterizado)."""
import subprocess, sys
import numpy as np
import scipy.ndimage as nd
from PIL import Image, ImageDraw, ImageFilter
from armar_v6 import *   # noqa: helpers (render, cap, degradado, pin, etiqueta, ventana, dibuja_poligono, suave, lerp, POLIGONO, CENTRO, AEROPUERTO, KM...)

TMP = AQUI / 'tmp_v7'; TMP.mkdir(exist_ok=True)
VOZ = AQUI / 'voz_real' / 'LISBETH_punch.wav'
T2, T3, T4, T5, TOTAL = 7.2, 13.0, 15.6, 20.5, 20.5
FOTO_AERO = AQUI / 'refs' / 'plusvalia' / 'aeropista_imponente.jpg'

# ── plano de lotes → máscara de líneas limpia (sin textos) ──
def mascara_lotes():
    a = np.array(Image.open(AQUI / 'lotes' / 'peniel_p1.png').convert('L'))[396:3663]
    lineas = a < 150
    lab, n = nd.label(lineas, structure=np.ones((3, 3)))
    sl = nd.find_objects(lab); keep = np.zeros(n + 1, bool)
    for i, s in enumerate(sl, 1):
        if max(s[0].stop - s[0].start, s[1].stop - s[1].start) >= 160: keep[i] = True   # las líneas largas; los textos/puntos son chicos
    lineas = keep[lab]
    lineas = nd.binary_dilation(lineas, iterations=3)
    im = Image.fromarray((lineas * 255).astype(np.uint8)).resize((1000, int(1000 * lineas.shape[0] / lineas.shape[1])), Image.LANCZOS)
    return im


MASK = mascara_lotes()
S = 1000 / 2640
# esquinas del plano (en la máscara) → esquinas del polígono del KMZ (P1→A, P4→B, P3→C, P2→D)
PLANO = [(39.6 * S, (1283 - 396) * S), (871 * S, (3277 - 396) * S), (2574 * S, (2574 - 396) * S), (1604 * S, (485 - 396) * S)]
GRAD = Image.fromarray(np.tile(np.linspace(0, 255, MASK.height).astype(np.uint8)[:, None], (1, MASK.width)))


def coef(src, dst):
    A, B = [], []
    for (u, v), (x, y) in zip(src, dst):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    return tuple(np.linalg.solve(A, B))


def efecto_lotes(img, pr, p):
    """Dibuja los lotes sobre el terreno: las líneas aparecen con un barrido luminoso a lo largo del plano."""
    dst = [pr(la, lo) for lo, la in [POLIGONO[0], POLIGONO[1], POLIGONO[2], POLIGONO[3]]]   # A, B, C, D
    c = coef(PLANO, dst)
    L = np.array(MASK.transform((W, H), Image.PERSPECTIVE, c, Image.BICUBIC)).astype(np.float32) / 255
    pm = Image.new('L', (W, H), 0); ImageDraw.Draw(pm).polygon(dst, fill=255); L = L * (np.array(pm).astype(np.float32) / 255)
    G = np.array(GRAD.transform((W, H), Image.PERSPECTIVE, c, Image.BICUBIC, fillcolor=255)).astype(np.float32)
    corte = p * 255 * 1.0
    vis = (G <= corte).astype(np.float32); vis = nd.gaussian_filter(vis, 2)
    borde = np.exp(-((G - corte) / 18) ** 2) * (L > 0.05)
    a_linea = L * vis
    glow = nd.gaussian_filter(borde * L, 10) * 2.2
    base = np.array(img.convert('RGB')).astype(np.float32)
    base *= (1 - 0.22 * np.clip(vis.max() * 0 + p, 0, 1))                      # oscurece un poco el mapa para que resalten las líneas
    oro = np.array([255, 226, 150], np.float32); blanco = np.array([255, 255, 255], np.float32)
    out = base * (1 - a_linea[..., None] * .95) + oro * a_linea[..., None] * .95
    out = out * (1 - np.clip(glow, 0, 1)[..., None] * .8) + blanco * np.clip(glow, 0, 1)[..., None] * .8
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def escena1(t):
    z = lerp(14.2, 19.0, suave(t / 2.8)) + 0.25 * max(0, (t - 2.8)) / (T2 - 2.8)
    im, pr = render(CENTRO[0], CENTRO[1], z, W, H); im = dibuja_poligono(im, pr, t, 0.9)
    p = suave((t - 3.0) / 3.4)
    if p > 0: im = efecto_lotes(im, pr, p)
    a = suave((t - 1.2) / 0.5) * suave((3.2 - t) / 0.3)
    if a > 0:
        capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa); x, y = pr(*CENTRO); pin(d, x, y - 10); etiqueta(d, x, y - 150, 'TU TERRENO')
        im = Image.alpha_composite(im.convert('RGBA'), capa).convert('RGB')
    im = cap(degradado(im), ['TERRENO DE', '30,000 m²'], t, 0.6, 3.0)
    return cap(im, ['LOTES DE', '400 A 600 m²'], t, 3.3, T2 - .1)


def escena3(t):
    u = t - T2
    k1 = suave(u / 1.5); k3 = suave((u - 3.0) / 0.8)
    z = lerp(19.25, 12.25, k1); la, lo = lerp(CENTRO[0], MEDIO[0], k1), lerp(CENTRO[1], MEDIO[1], k1)
    if u > 3.0: z = lerp(12.25, 15.0, k3); la, lo = lerp(MEDIO[0], AEROPUERTO[0], k3), lerp(MEDIO[1], AEROPUERTO[1], k3)
    im, pr = render(la, lo, z, W, H); im = dibuja_poligono(im, pr, t, T2 - 1)
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    x0, y0 = pr(*CENTRO); x1, y1 = pr(*AEROPUERTO); prog = suave((u - 1.5) / 1.5)
    if prog > 0:
        n = 60
        for i in range(int(n * prog)):
            if i % 2 == 0:
                a = (x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n); b = (x0 + (x1 - x0) * (i + 1) / n, y0 + (y1 - y0) * (i + 1) / n)
                d.line([a, b], fill=(255, 226, 150, 255), width=9)
        px_, py_ = x0 + (x1 - x0) * prog, y0 + (y1 - y0) * prog; d.ellipse((px_ - 16, py_ - 16, px_ + 16, py_ + 16), fill=(255, 255, 255, 255), outline=ORO, width=6)
        if prog > .35 and u < 3.9: etiqueta(d, (x0 + x1) / 2 + 110, (y0 + y1) / 2 - 40, f'≈ {KM:.0f} km', 46)
    pin(d, x0, y0 - 6, ORO, 16)
    if prog > .98: pin(d, x1, y1 - 6, (255, 255, 255), 18); etiqueta(d, x1, y1 - 140, 'AEROPUERTO CHALACATEPEC', 28)
    im = Image.alpha_composite(im.convert('RGBA'), capa).convert('RGB')
    im = degradado(im, 1250, 200)
    im = ventana(im, FOTO_AERO, t, T2 + 3.7, 520, 980)
    im = cap(im, ['A 20 MIN', 'DE LA PLAYA'], t, T2 + .1, T2 + 1.7)
    im = cap(im, [f'A {KM:.0f} KM DEL', 'AEROPUERTO DE CHALACATEPEC'], t, T2 + 1.9, T2 + 3.7, 1440)
    return cap(im, ['NUEVO AEROPUERTO', 'ZONA CON PLUSVALÍA'], t, T2 + 4.0, T3 - .1, 1440)


def escena4(t):
    u = t - T3
    im, pr = render(AEROPUERTO[0] + 0.012 * u / 3, AEROPUERTO[1] - 0.004 * u / 3, 14.6, W, H)
    im = Image.blend(im, Image.new('RGB', (W, H), AZUL), 0.35)
    im = ventana(im, PLUS / 'entorno.jpg', t, T3 + .1, 520, 960)
    return cap(degradado(im, 1100, 200), ['TU FAMILIA', 'SE LO MERECE'], t, T3 + .3, T4 - .1, 1440)


FAM = None
def escena5(t):
    global FAM
    if FAM is None:
        import av
        c = av.open(str(AQUI / 'clips_v5' / 'P3.mp4')); FAM = [fr.to_image().convert('RGB').resize((W, H), Image.LANCZOS) for fr in c.decode(video=0)]
    u = (t - T4) / (T5 - T4); im = degradado(FAM[min(len(FAM) - 1, int(u * len(FAM)))], 1250, 200)
    im = cap(im, ['NO COMPRES', 'PROMESAS'], t, T4 + .1, T4 + 2.0, 1440, 66)
    return cap(im, ['ESCRÍBEME', 'POR WHATSAPP'], t, T4 + 2.1, T5 + 1, 1440, 66)


ESC = [(0, T2, escena1), (T2, T3, escena3), (T3, T4, escena4), (T4, T5, escena5)]


def frame(t):
    for i, (a, b, f) in enumerate(ESC):
        if t < b or i == len(ESC) - 1:
            im = f(t)
            if i < len(ESC) - 1 and b - t < 0.18: im = Image.blend(im, ESC[i + 1][2](t), 0.5 * (1 - (b - t) / 0.18))
            return im


if __name__ == '__main__':
    solo = [float(x) for x in sys.argv[1:]]
    if solo:
        for s in solo: frame(s).save(TMP / f'prueba_{s}.png'); print('ok', s)
        raise SystemExit
    sal = AQUI / 'final' / 'Lisbeth_terreno_v7.mp4'; hd = TMP / 'hd.mp4'
    p = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', str(VOZ),
                          '-map', '0:v', '-map', '1:a', '-t', f'{TOTAL:.2f}', '-c:v', 'libx264', '-profile:v', 'main', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p',
                          '-c:a', 'aac', '-ar', '44100', '-b:a', '160k', '-movflags', '+faststart', str(hd)], stdin=subprocess.PIPE)
    for n in range(int(TOTAL * FPS)):
        p.stdin.write(frame(n / FPS).tobytes())
        if n % 60 == 0: print(f'{n / FPS:.1f}s', flush=True)
    p.stdin.close(); p.wait()
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(hd), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p',
                    '-crf', '21', '-c:a', 'copy', '-movflags', '+faststart', str(sal)], check=True)
    print(sal, sal.stat().st_size // 1024, 'KB')
