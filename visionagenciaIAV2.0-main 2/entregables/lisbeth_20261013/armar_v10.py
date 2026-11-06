"""Lisbeth v10: GANCHO cinematográfico de hora dorada (como la referencia: un terreno que «va tomando forma») sobre el plano REAL de lotes de Lisbeth.
K1 (terreno con contorno → lotes de tierra y calles) + K2 (lotes de tierra → lotes verdes), generados en Modal (lisbeth_modal_v10.py).
Sustituye la escena satelital inicial (0 → TA); el resto del video, la voz y los datos son los de v8/v9."""
import subprocess, sys
import av
import multiprocessing as mp
from PIL import Image, ImageDraw
from armar_v9 import *   # noqa  (W, H, FPS, TA, TOTAL, VOZ, FF, cap, degradado, etiqueta, suave, TMP...)
import armar_v8 as v8

FPS_CLIP = 24.0
CLIPS = []
for n in ('K1', 'K2'):
    c = av.open(str(AQUI / 'clips_v10' / f'{n}.mp4'))
    CLIPS += [fr.to_image().convert('RGB') for fr in c.decode(video=0)]
T_CLIP = len(CLIPS) / FPS_CLIP        # ≈ 10.3 s


def sA10(t):
    k = min(len(CLIPS) - 1, int(t * FPS_CLIP))
    im = CLIPS[k]
    z = 1 + 0.035 * suave((t - T_CLIP) / (TA - T_CLIP)) if t > T_CLIP else 1 + 0.02 * suave(t / T_CLIP)   # empuje lento continuo
    im = im.resize((W, H), Image.LANCZOS)
    if z > 1:
        w2, h2 = int(W / z), int(H / z); x0, y0 = (W - w2) // 2, int((H - h2) * .45); im = im.crop((x0, y0, x0 + w2, y0 + h2)).resize((W, H), Image.LANCZOS)
    b = suave((t - 0.3) / 0.5) * suave((T_CLIP + 2.0 - t) / 0.5)      # etiqueta de honestidad: es una visualización del proyecto
    if b > 0:
        capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa); etiqueta(d, W / 2, 250, 'VISUALIZACIÓN DEL PROYECTO', 34)
        capa.putalpha(capa.getchannel('A').point(lambda v: int(v * b))); im = Image.alpha_composite(im.convert('RGBA'), capa).convert('RGB')
    im = degradado(im)
    im = cap(im, ['LISBETH', 'ASESORA INMOBILIARIA'], t, 0.4, 3.3)
    im = cap(im, ['ELEGIR DÓNDE CONSTRUIR', 'TU PATRIMONIO'], t, 3.6, 9.6)
    im = cap(im, ['TERRENO DE', '30,000 m²'], t, 9.9, 12.0)
    im = cap(im, ['LOTES DE', '400 A 600 m²'], t, 12.2, 13.5)
    return cap(im, ['A 20 MIN', 'DE LA PLAYA'], t, 13.6, TA - .1)


FAM = None
def sD10(t):
    """Igual que v8.sD pero con los cuadros en tamaño original (ahorra ~1.4 GB por proceso)."""
    global FAM
    if FAM is None:
        c = av.open(str(AQUI / 'clips_v5' / 'P3.mp4')); FAM = [fr.to_image().convert('RGB') for fr in c.decode(video=0)]
    TC, TD = v8.TC, v8.TD
    u = (t - TC) / (TD - TC); im = FAM[min(len(FAM) - 1, max(0, int(u * len(FAM))))].resize((W, H), Image.LANCZOS); im = degradado(im, 1250, 200)
    im = cap(im, ['NO COMPRES', 'PROMESAS'], t, TC + .2, TC + 3.0, 1440, 66)
    return cap(im, ['ESCRÍBEME', 'POR WHATSAPP'], t, TC + 3.2, TD + 1, 1440, 66)


ESC10 = [(0, TA, sA10)] + v8.ESC8[1:-1] + [(v8.TC, v8.TD, sD10)]


def frame10(t):
    for i, (a, b, f) in enumerate(ESC10):
        if t < b or i == len(ESC10) - 1:
            im = f(t)
            if i < len(ESC10) - 1 and b - t < 0.18: im = Image.blend(im, ESC10[i + 1][2](t), 0.5 * (1 - (b - t) / 0.18))
            return im


if __name__ == '__main__':
    solo = [float(x) for x in sys.argv[1:]]
    if solo:
        for s in solo: frame10(s).save(TMP / f'prueba10_{s}.png'); print('ok', s)
        raise SystemExit
    sD10(v8.TC + 1)    # precarga en el proceso padre (decodificar con av dentro de hijos fork se cuelga)
    sal = AQUI / 'final' / 'Lisbeth_terreno_v10_gancho_dorado.mp4'; hd = TMP / 'hd10.mp4'
    p = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', str(VOZ),
                          '-map', '0:v', '-map', '1:a', '-t', f'{TOTAL:.2f}', '-c:v', 'libx264', '-profile:v', 'main', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p',
                          '-c:a', 'aac', '-ar', '44100', '-b:a', '160k', '-movflags', '+faststart', str(hd)], stdin=subprocess.PIPE)
    def f(n): return frame10(n / FPS).tobytes()
    with mp.get_context('fork').Pool(2) as pool:
        for n, b in enumerate(pool.imap(f, range(int(TOTAL * FPS)), chunksize=4)):
            p.stdin.write(b)
            if n % 90 == 0: print(f'{n / FPS:.1f}s', flush=True)
    p.stdin.close(); p.wait()
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(hd), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p',
                    '-crf', '21', '-c:a', 'copy', '-movflags', '+faststart', str(sal)], check=True)
    print(sal, sal.stat().st_size // 1024, 'KB')
