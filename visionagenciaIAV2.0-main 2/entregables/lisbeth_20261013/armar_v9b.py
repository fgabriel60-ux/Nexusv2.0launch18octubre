"""Lisbeth v9b: v9 (gancho por código) + clip MiniMax H3 de una casa que se CONSTRUYE sobre un lote delimitado (t=8.1 s en adelante).
La cámara del clip es la misma del cuadro base de v9 en t=8.1 s, así el empalme es invisible. Etiqueta «ILUSTRACIÓN» (la casa es una visualización)."""
import subprocess, sys
import av
import multiprocessing as mp
from PIL import Image, ImageDraw
from armar_v9 import *   # noqa
import armar_v9 as v9
import armar_v8 as v8

T_CLIP = 8.1
_c = av.open(str(AQUI / 'clips_v9' / 'K.mp4'))
CLIP = [fr.to_image().convert('RGB').resize((W, H), Image.LANCZOS) for fr in _c.decode(video=0)]
FPS_CLIP = 24.0


def sA9b(t):
    if t < T_CLIP: return v9.sA9(t)
    live = v9.sA9(t, limpio=True)
    k = min(len(CLIP) - 1, int((t - T_CLIP) * FPS_CLIP))
    zoom = 1 + 0.012 * max(0, t - T_CLIP - 5.1)           # tras el clip, la última imagen se queda con un acercamiento muy lento
    im = CLIP[k]
    if zoom > 1:
        w2, h2 = int(W / zoom), int(H / zoom); x0, y0 = (W - w2) // 2, (H - h2) // 2; im = im.crop((x0, y0, x0 + w2, y0 + h2)).resize((W, H), Image.LANCZOS)
    im = Image.blend(live, im, suave((t - T_CLIP) / 0.4))
    b = suave((t - 8.3) / 0.4) * suave((12.9 - t) / 0.4)    # etiqueta de honestidad: la casa es ilustrativa
    if b > 0:
        capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa); etiqueta(d, W / 2, 250, 'ILUSTRACIÓN · CASA DE EJEMPLO', 34)
        capa.putalpha(capa.getchannel('A').point(lambda v: int(v * b))); im = Image.alpha_composite(im.convert('RGBA'), capa).convert('RGB')
    im = degradado(im)
    im = cap(im, ['ELEGIR DÓNDE CONSTRUIR', 'TU PATRIMONIO'], t, 3.6, 9.6)
    im = cap(im, ['TERRENO DE', '30,000 m²'], t, 9.9, 12.0)
    im = cap(im, ['LOTES DE', '400 A 600 m²'], t, 12.2, 13.5)
    return cap(im, ['A 20 MIN', 'DE LA PLAYA'], t, 13.6, TA - .1)


ESCB = [(0, TA, sA9b)] + v8.ESC8[1:]


def frameb(t):
    for i, (a, b, f) in enumerate(ESCB):
        if t < b or i == len(ESCB) - 1:
            im = f(t)
            if i < len(ESCB) - 1 and b - t < 0.18: im = Image.blend(im, ESCB[i + 1][2](t), 0.5 * (1 - (b - t) / 0.18))
            return im


if __name__ == '__main__':
    solo = [float(x) for x in sys.argv[1:]]
    if solo:
        for s in solo: frameb(s).save(TMP / f'pruebab_{s}.png'); print('ok', s)
        raise SystemExit
    sal = AQUI / 'final' / 'Lisbeth_terreno_v9b_construccion.mp4'; hd = TMP / 'hdb.mp4'
    p = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', str(VOZ),
                          '-map', '0:v', '-map', '1:a', '-t', f'{TOTAL:.2f}', '-c:v', 'libx264', '-profile:v', 'main', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p',
                          '-c:a', 'aac', '-ar', '44100', '-b:a', '160k', '-movflags', '+faststart', str(hd)], stdin=subprocess.PIPE)
    def f(n): return frameb(n / FPS).tobytes()
    with mp.get_context('fork').Pool(2) as pool:
        for n, b in enumerate(pool.imap(f, range(int(TOTAL * FPS)), chunksize=4)):
            p.stdin.write(b)
            if n % 90 == 0: print(f'{n / FPS:.1f}s', flush=True)
    p.stdin.close(); p.wait()
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(hd), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p',
                    '-crf', '21', '-c:a', 'copy', '-movflags', '+faststart', str(sal)], check=True)
    print(sal, sal.stat().st_size // 1024, 'KB')
