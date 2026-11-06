"""Lisbeth v8: voz de ASESORA INMOBILIARIA (serena, empática, nada apurada) que menciona el aeropuerto de Chalacatepec y la presa Cajón de Peña.
Cada lugar se localiza en el mapa satelital, se traza la ruta con su distancia y SOLO al llegar al punto se abre su foto."""
import subprocess, sys
from PIL import Image, ImageDraw
from armar_v7 import *   # noqa
import armar_v7 as v7

TMP = AQUI / 'tmp_v8'; TMP.mkdir(exist_ok=True)
VOZ = AQUI / 'voz_real' / 'LISBETH_experta.wav'
PRESA = (20.018, -105.131)           # embalse de Cajón de Peña (ubicado a ojo en el satélite; la coordenada publicada es de baja precisión)
KM2 = haversine(CENTRO, PRESA)
VISTA = (19.6925, -105.205, 11.6)     # encuadre con terreno, aeropuerto y presa a la vez
FOTO_PRESA = PLUS / 'entorno.jpg'
TA, TB, TC, TD, TOTAL = 15.3, 22.4, 26.2, 31.6, 31.6


def sA(t):
    z = lerp(13.0, 19.0, suave(t / 6.0)) + 0.3 * max(0, t - 6.0) / (TA - 6.0)
    im, pr = render(CENTRO[0], CENTRO[1], z, W, H); im = dibuja_poligono(im, pr, t, 3.5)
    a = suave((t - 5.5) / 0.5) * suave((9.8 - t) / 0.4)
    if a > 0:
        capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa); x, y = pr(*CENTRO); pin(d, x, y - 10); etiqueta(d, x, y - 150, 'TU TERRENO')
        im = Image.alpha_composite(im.convert('RGBA'), capa).convert('RGB')
    p = suave((t - 10.0) / 3.6)
    if p > 0: im = efecto_lotes(im, pr, p)
    im = degradado(im)
    im = cap(im, ['LISBETH', 'ASESORA INMOBILIARIA'], t, 0.4, 3.3)
    im = cap(im, ['ELEGIR DÓNDE CONSTRUIR', 'TU PATRIMONIO'], t, 3.6, 9.6)
    im = cap(im, ['TERRENO DE', '30,000 m²'], t, 9.9, 12.0)
    im = cap(im, ['LOTES DE', '400 A 600 m²'], t, 12.2, 13.5)
    return cap(im, ['A 20 MIN', 'DE LA PLAYA'], t, 13.6, TA - .1)


def sB(t):
    u = t - TA; k = suave(u / 1.3)
    z = lerp(19.3, VISTA[2], k); la, lo = lerp(CENTRO[0], VISTA[0], k), lerp(CENTRO[1], VISTA[1], k)
    im, pr = render(la, lo, z, W, H)
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    x0, y0 = pr(*CENTRO); xa, ya = pr(*AEROPUERTO); xp, yp = pr(*PRESA)
    def ruta(x1, y1, prog):
        n = 60
        for i in range(int(n * prog)):
            if i % 2 == 0:
                a = (x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n); b = (x0 + (x1 - x0) * (i + 1) / n, y0 + (y1 - y0) * (i + 1) / n); d.line([a, b], fill=(255, 226, 150, 255), width=9)
        if 0 < prog < 1: px_, py_ = x0 + (x1 - x0) * prog, y0 + (y1 - y0) * prog; d.ellipse((px_ - 16, py_ - 16, px_ + 16, py_ + 16), fill=(255, 255, 255, 255), outline=ORO, width=6)
    p1 = suave((u - 1.3) / 1.1); p2 = suave((u - 3.0) / 1.1)
    if u > 1.3: ruta(xa, ya, p1)
    if u > 3.0: ruta(xp, yp, p2)
    pin(d, x0, y0 - 6, ORO, 16)
    if p1 > .98: pin(d, xa, ya - 6, (255, 255, 255), 18); etiqueta(d, xa, ya - 140, 'AEROPUERTO CHALACATEPEC', 28)
    if p2 > .98: pin(d, xp, yp - 6, (255, 255, 255), 18); etiqueta(d, xp, yp - 140, 'PRESA CAJÓN DE PEÑA', 28)
    if p1 > .35 and u < 2.8: etiqueta(d, (x0 + xa) / 2 + 120, (y0 + ya) / 2, f'≈ {KM:.0f} km', 44)
    if p2 > .35 and u < 5.2: etiqueta(d, (x0 + xp) / 2 + 140, (y0 + yp) / 2, f'≈ {KM2:.0f} km', 44)
    im = Image.alpha_composite(im.convert('RGBA'), capa).convert('RGB'); im = degradado(im, 1000, 150)
    if t < 19.5: im = ventana(im, FOTO_AERO, t, 17.7, 1010, 860)
    else: im = ventana(im, FOTO_PRESA, t, 19.5, 1010, 860)
    if t < 18.2: return cap(im, ['CERCA DEL AEROPUERTO', f'DE CHALACATEPEC · ≈ {KM:.0f} km'], t, TA + .5, 18.1, 1580, 54)
    return cap(im, ['PRESA CAJÓN DE PEÑA', f'≈ {KM2:.0f} km · ZONA CON POTENCIAL'], t, 18.3, TB - .1, 1580, 54)


def sC(t):
    u = t - TB; k = suave(u / 1.2)
    z = lerp(VISTA[2], 18.6, k); la, lo = lerp(VISTA[0], CENTRO[0], k), lerp(VISTA[1], CENTRO[1], k)
    im, pr = render(la, lo, z, W, H); im = dibuja_poligono(im, pr, t, TB - 5)
    if k > .6: im = efecto_lotes(im, pr, 1.0)
    return cap(degradado(im), ['DOCUMENTOS', 'EN REGLA'], t, TB + .4, TC - .1)


FAM8 = None
def sD(t):
    global FAM8
    if FAM8 is None:
        import av
        c = av.open(str(AQUI / 'clips_v5' / 'P3.mp4')); FAM8 = [fr.to_image().convert('RGB').resize((W, H), Image.LANCZOS) for fr in c.decode(video=0)]
    u = (t - TC) / (TD - TC); im = degradado(FAM8[min(len(FAM8) - 1, int(u * len(FAM8)))], 1250, 200)
    im = cap(im, ['NO COMPRES', 'PROMESAS'], t, TC + .2, TC + 3.0, 1440, 66)
    return cap(im, ['ESCRÍBEME', 'POR WHATSAPP'], t, TC + 3.2, TD + 1, 1440, 66)


ESC8 = [(0, TA, sA), (TA, TB, sB), (TB, TC, sC), (TC, TD, sD)]


def frame8(t):
    for i, (a, b, f) in enumerate(ESC8):
        if t < b or i == len(ESC8) - 1:
            im = f(t)
            if i < len(ESC8) - 1 and b - t < 0.18: im = Image.blend(im, ESC8[i + 1][2](t), 0.5 * (1 - (b - t) / 0.18))
            return im


if __name__ == '__main__':
    solo = [float(x) for x in sys.argv[1:]]
    if solo:
        for s in solo: frame8(s).save(TMP / f'prueba_{s}.png'); print('ok', s)
        raise SystemExit
    sal = AQUI / 'final' / 'Lisbeth_terreno_v8.mp4'; hd = TMP / 'hd.mp4'
    p = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', str(VOZ),
                          '-map', '0:v', '-map', '1:a', '-t', f'{TOTAL:.2f}', '-c:v', 'libx264', '-profile:v', 'main', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p',
                          '-c:a', 'aac', '-ar', '44100', '-b:a', '160k', '-movflags', '+faststart', str(hd)], stdin=subprocess.PIPE)
    for n in range(int(TOTAL * FPS)):
        p.stdin.write(frame8(n / FPS).tobytes())
        if n % 90 == 0: print(f'{n / FPS:.1f}s', flush=True)
    p.stdin.close(); p.wait()
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(hd), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p',
                    '-crf', '21', '-c:a', 'copy', '-movflags', '+faststart', str(sal)], check=True)
    print(sal, sal.stat().st_size // 1024, 'KB')
