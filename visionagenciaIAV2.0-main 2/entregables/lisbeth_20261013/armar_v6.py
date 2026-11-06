"""Lisbeth v6 — estructura del reel de referencia: mapa satelital real (KMZ del terreno) → plano de lotes → ruta con la distancia al aeropuerto
→ la foto del lugar SOLO al llegar al punto → entorno → familia + CTA. Voz real de Lisbeth (LISBETH_2.ogg)."""
import math, subprocess, sys
from pathlib import Path
import av, imageio_ffmpeg, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from mapa_lib import render, haversine, centro_y_area, POLIGONO, AEROPUERTO

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
FUENTE = str(AQUI.parent / 'modelos_modal' / 'fuentes' / 'Montserrat.ttf')
W, H, FPS = 1080, 1920, 30
ORO, BLANCO, AZUL = (232, 190, 110), (255, 255, 255), (8, 24, 60)
TMP = AQUI / 'tmp_v6'; TMP.mkdir(exist_ok=True)
VOZ = AQUI / 'voz_real' / 'LISBETH_2.ogg'
CENTRO, AREA = centro_y_area(); KM = haversine(CENTRO, AEROPUERTO)
MEDIO = ((CENTRO[0] + AEROPUERTO[0]) / 2, (CENTRO[1] + AEROPUERTO[1]) / 2)
# límites de escena (s)
T1, T2, T3, T4, T5, TOTAL = 4.0, 8.0, 17.4, 20.5, 25.4, 25.4
PLUS = AQUI / 'refs' / 'plusvalia'


def fu(t, peso='Bold'):
    f = ImageFont.truetype(FUENTE, t); f.set_variation_by_name(peso); return f


def suave(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)


def lerp(a, b, k): return a + (b - a) * k


def cap(img, lineas, t, ini, fin, y=1440, tam=60):
    """Letrero del reel de referencia (abajo a la izquierda, barra dorada)."""
    a = suave((t - ini) / 0.3) * suave((fin - t) / 0.3)
    if a <= 0: return img
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    d.rectangle((70, y, 76, y + 2 * tam + 14), fill=(*ORO, int(255 * a)))
    for i, l in enumerate(lineas):
        f = fu(tam if i == 0 else int(tam * .78), 'Bold' if i == 0 else 'Medium')
        d.text((105, y + i * (tam + 8)), l, font=f, fill=(255, 255, 255, int(255 * a)), stroke_width=2, stroke_fill=(0, 0, 0, int(200 * a)))
    return Image.alpha_composite(img.convert('RGBA'), capa).convert('RGB')


def degradado(img, y0=1150, fuerza=210):
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    for y in range(y0, H): d.line([(0, y), (W, y)], fill=(4, 12, 30, int(fuerza * ((y - y0) / (H - y0)) ** 1.2)))
    return Image.alpha_composite(img.convert('RGBA'), capa).convert('RGB')


def pin(d, x, y, color=ORO, r=20):
    d.polygon([(x, y), (x - r * .75, y - r * 1.7), (x + r * .75, y - r * 1.7)], fill=color)
    d.ellipse((x - r, y - r * 3, x + r, y - r), fill=color); d.ellipse((x - r * .4, y - r * 2.4, x + r * .4, y - r * 1.6), fill=(20, 20, 20))


def etiqueta(d, x, y, txt, tam=34, ancla='c'):
    f = fu(tam, 'ExtraBold'); w = d.textlength(txt, font=f) + 44
    x0 = x - w / 2 if ancla == 'c' else x
    d.rounded_rectangle((x0, y, x0 + w, y + tam + 30), 16, fill=(8, 24, 60, 235), outline=ORO, width=3); d.text((x0 + 22, y + 13), txt, font=f, fill=BLANCO)


def ventana(img, foto, t, ini, y_final=760, ancho=960):
    """La foto del lugar se abre como ventana dentro del mapa (aparece desde abajo) — solo cuando la cámara llegó al punto."""
    k = suave((t - ini) / 0.6)
    if k <= 0: return img
    im = Image.open(foto).convert('RGB'); alto = int(ancho * im.height / im.width); alto = min(alto, 1000)
    zoom = 1 + 0.05 * (t - ini); im = im.resize((int(ancho * zoom), int(ancho * zoom * im.height / im.width)), Image.LANCZOS)
    cx, cy = (im.width - ancho) // 2, (im.height - alto) // 2; im = im.crop((cx, cy, cx + ancho, cy + alto))
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); m = Image.new('L', im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width, im.height), 30, fill=255)
    y = int(lerp(H + 20, y_final, k)); x = (W - ancho) // 2
    marco = ImageDraw.Draw(capa); marco.rounded_rectangle((x - 8, y - 8, x + ancho + 8, y + alto + 8), 36, fill=(*ORO, 255))
    capa.paste(im, (x, y), m)
    return Image.alpha_composite(img.convert('RGBA'), capa).convert('RGB')


def dibuja_poligono(img, proj, t, ini):
    a = suave((t - ini) / 0.6)
    if a <= 0: return img
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    pts = [proj(la, lo) for lo, la in POLIGONO]
    d.polygon(pts, fill=(255, 214, 120, int(70 * a))); d.line(pts + [pts[0]], fill=(255, 226, 150, int(255 * a)), width=7, joint='curve')
    return Image.alpha_composite(img.convert('RGBA'), capa).convert('RGB')


# ───────── escenas ─────────
def escena1(t):
    k = suave(t / T1); z = lerp(14.2, 17.0, k)
    im, pr = render(CENTRO[0], CENTRO[1], z, W, H); im = dibuja_poligono(im, pr, t, 1.0)
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    x, y = pr(*CENTRO); a = suave((t - 1.4) / 0.5)
    if a > 0: pin(d, x, y - 10); etiqueta(d, x, y - 150, 'TU TERRENO')
    im = Image.alpha_composite(im.convert('RGBA'), capa).convert('RGB')
    return cap(degradado(im), ['TERRENO DE', '30,000 m²'], t, 0.8, T1 - 0.1)


PLAN = None
def escena2(t):
    global PLAN
    if PLAN is None:
        p = Image.open(AQUI / 'lotes' / 'peniel_p1.png').convert('RGB'); p = p.crop((0, 396, p.width, 3663)); p = p.resize((960, int(960 * p.height / p.width)), Image.LANCZOS)
        PLAN = p
    fondo = Image.new('RGB', (W, H)); d = ImageDraw.Draw(fondo)
    for y in range(H): d.line([(0, y), (W, y)], fill=tuple(int(AZUL[i] * (1 - y / H * .6)) for i in range(3)))
    z = 1 + 0.06 * (t - T1) / (T2 - T1); p = PLAN.resize((int(PLAN.width * z), int(PLAN.height * z)), Image.LANCZOS)
    m = Image.new('L', p.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, p.width, p.height), 28, fill=255)
    fondo.paste(p, ((W - p.width) // 2, 230 - (p.height - PLAN.height) // 2), m)
    return cap(degradado(fondo, 1300, 170), ['LOTES DE', '400 A 600 m²'], t, T1 + .3, T2 - .1, 1500)


def escena3(t):
    u = t - T2; dur = T3 - T2
    # 0-2.2 s: alejar del terreno · 2.2-4.8: ruta · 4.8-5.9: vuelo al aeropuerto · luego foto
    k1 = suave(u / 2.4); k3 = suave((u - 4.9) / 1.2)
    z = lerp(16.4, 12.25, k1); la, lo = lerp(CENTRO[0], MEDIO[0], k1), lerp(CENTRO[1], MEDIO[1], k1)
    if u > 4.9: z = lerp(12.25, 15.0, k3); la, lo = lerp(MEDIO[0], AEROPUERTO[0], k3), lerp(MEDIO[1], AEROPUERTO[1], k3)
    im, pr = render(la, lo, z, W, H); im = dibuja_poligono(im, pr, t, T2 - 1)
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    x0, y0 = pr(*CENTRO); x1, y1 = pr(*AEROPUERTO); prog = suave((u - 2.4) / 2.2)
    if prog > 0:
        n = 60
        for i in range(int(n * prog)):
            if i % 2 == 0:
                a = (x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n); b = (x0 + (x1 - x0) * (i + 1) / n, y0 + (y1 - y0) * (i + 1) / n)
                d.line([a, b], fill=(255, 226, 150, 255), width=9)
        px_, py_ = x0 + (x1 - x0) * prog, y0 + (y1 - y0) * prog; d.ellipse((px_ - 16, py_ - 16, px_ + 16, py_ + 16), fill=(255, 255, 255, 255), outline=ORO, width=6)
        if prog > .35 and u < 6.2: etiqueta(d, (x0 + x1) / 2 + 110, (y0 + y1) / 2 - 40, f'≈ {KM:.0f} km', 46)
    pin(d, x0, y0 - 6, ORO, 16)
    if prog > .98: pin(d, x1, y1 - 6, (255, 255, 255), 18); etiqueta(d, x1, y1 - 140, 'AEROPUERTO CHALACATEPEC', 28)
    im = Image.alpha_composite(im.convert('RGBA'), capa).convert('RGB')
    im = ventana(degradado(im, 700, 120) if u > 5.9 else im, PLUS / 'aeropuerto.jpg', t, T2 + 6.0, 560, 960)
    im = cap(degradado(im, 1300, 200) if u <= 5.9 else im, ['A 20 MIN', 'DE LA PLAYA'], t, T2 + .2, T2 + 2.2)
    im = cap(im, [f'A {KM:.0f} KM DEL', 'AEROPUERTO DE CHALACATEPEC'], t, T2 + 2.6, T2 + 5.8, 1440)
    return cap(im, ['NUEVO AEROPUERTO', 'ZONA CON PLUSVALÍA'], t, T2 + 6.3, T3 - .1, 1440)


def escena4(t):
    u = t - T3; k = suave(u / 1.0)
    im, pr = render(AEROPUERTO[0] + 0.012 * u / 3, AEROPUERTO[1] - 0.004 * u / 3, 14.6, W, H)
    im = Image.blend(im, Image.new('RGB', (W, H), AZUL), 0.35)
    im = ventana(im, PLUS / 'entorno.jpg', t, T3 + .2, 520, 960)
    return cap(degradado(im, 1100, 200), ['ENTORNO', 'NATURAL'], t, T3 + .5, T4 - .1, 1440)


FAM = None
def escena5(t):
    global FAM
    if FAM is None:
        c = av.open(str(AQUI / 'clips_v5' / 'P3.mp4')); FAM = [fr.to_image().convert('RGB').resize((W, H), Image.LANCZOS) for fr in c.decode(video=0)]
    u = (t - T4) / (T5 - T4); im = FAM[min(len(FAM) - 1, int(u * len(FAM) * 1.0))]
    im = degradado(im, 1250, 200)
    im = cap(im, ['TU FAMILIA', 'SE LO MERECE'], t, T4 + .2, T5 - 2.7)
    return cap(im, ['NO COMPRES PROMESA', 'INFORMACIÓN POR WHATSAPP'], t, T5 - 2.5, T5 + 1, 1440, 54)


ESC = [(0, T1, escena1), (T1, T2, escena2), (T2, T3, escena3), (T3, T4, escena4), (T4, T5, escena5)]


def frame(t):
    for i, (a, b, f) in enumerate(ESC):
        if t < b or i == len(ESC) - 1:
            im = f(t)
            if i < len(ESC) - 1 and b - t < 0.18:   # fundido corto a la siguiente
                im = Image.blend(im, ESC[i + 1][2](t), 1 - (b - t) / 0.18 * 1.0 if False else 0.5 * (1 - (b - t) / 0.18))
            return im


if __name__ == '__main__':
    solo = [float(x) for x in sys.argv[1:]]
    if solo:
        for s in solo: frame(s).save(TMP / f'prueba_{s}.png'); print('ok', s)
        raise SystemExit
    sal = AQUI / 'final' / 'Lisbeth_terreno_v6.mp4'; hd = TMP / 'hd.mp4'
    p = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', str(VOZ),
                          '-filter_complex', '[1:a]adelay=300|300,loudnorm=I=-15:TP=-1.5,apad[a]', '-map', '0:v', '-map', '[a]', '-t', f'{TOTAL:.2f}',
                          '-c:v', 'libx264', '-profile:v', 'main', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', '44100', '-b:a', '128k',
                          '-movflags', '+faststart', str(hd)], stdin=subprocess.PIPE)
    for n in range(int(TOTAL * FPS)):
        p.stdin.write(frame(n / FPS).tobytes())
        if n % 60 == 0: print(f'{n / FPS:.1f}s', flush=True)
    p.stdin.close(); p.wait()
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(hd), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p',
                    '-crf', '21', '-c:a', 'copy', '-movflags', '+faststart', str(sal)], check=True)
    print(sal, sal.stat().st_size // 1024, 'KB')
