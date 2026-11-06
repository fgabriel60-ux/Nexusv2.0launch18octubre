"""Flyer animado (versión B de Glimmer: 15 s, sin voz, música + texto cinético) del Modelo Benjamina · Vizcaíno Residencial, Rosarito.
0-3 s   fachada (clip H3 de la foto real) con golpe de zoom · VIZCAÍNO RESIDENCIAL / ROSARITO, B.C. + sello DESDE $2.85 MDP*
3-6 s   recámara (barrido) · MODELO BENJAMINA
6-9 s   comedor y cocina · DESDE $2.85 MDP*
9-12 s  terraza · amenidades que aparecen una por una
12-15 s las 4 fotos reales entran como paneles (SIN el texto del flyer original) + precio, amenidades, botón ESCRÍBENOS POR WHATSAPP + *Aplican restricciones
Sin «No esperes a que suban los precios» en los textos animados (Glimmer: promesa sin respaldo; solo queda en el flyer original del cliente).
Uso: python3 armar_flyer.py"""
import subprocess, sys
from pathlib import Path
import av, numpy as np
from PIL import Image, ImageDraw, ImageFilter
import imageio_ffmpeg
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/XV')
from armar_xv import fu

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 30
AZUL, MARINO, BLANCO = (32, 170, 225), (22, 36, 66), (255, 255, 255)
MUSICA = Path('/workspaces/Nexusv2.0launch18octubre/clientes/XV/musica_suave_s7.wav')   # generada en Modal (sin derechos de terceros)
MODELO, PRECIO = 'BENJAMINA', '$2.85 MDP*'
ESCENAS = [('A1', 3.0), ('A2', 3.0), ('A3', 3.0), ('A4', 3.0), ('FLYER', 3.0)]
TOTAL = sum(d for _, d in ESCENAS)
AMENIDADES = ['Cancha de pádel', 'Acceso controlado', 'Plaza comercial', 'Área de juegos']


def suave(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)
def sale(x): x = min(1, max(0, x)); return 1 - (1 - x) ** 3


def clip(n):
    c = av.open(str(AQUI / 'clips' / f'{n}.mp4'))
    fr = [f.to_image().convert('RGB').resize((W, H), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.4, 60, 2)) for f in c.decode(video=0)]
    c.close(); return fr


def texto(d, t, y, tam, col, peso='Black', borde=0, x=None, a=1.0, ancho=W):
    f = fu(tam, peso)
    while d.textlength(t, font=f) > ancho - 80: tam -= 3; f = fu(tam, peso)
    x = (ancho - d.textlength(t, font=f)) / 2 if x is None else x
    d.text((x, y), t, font=f, fill=col + (int(255 * a),), stroke_width=borde, stroke_fill=(0, 0, 0, int(150 * a)))


def sello(capa, t, t0, y):
    """Sello de precio que entra con rebote."""
    k = sale((t - t0) / 0.35)
    if k <= 0: return
    s = Image.new('RGBA', (760, 230), (0, 0, 0, 0)); d = ImageDraw.Draw(s)
    d.rounded_rectangle((0, 0, 760, 230), 40, fill=AZUL + (240,))
    texto(d, 'DESDE', 22, 46, BLANCO, 'ExtraBold', ancho=760); texto(d, PRECIO, 72, 120, BLANCO, 'Black', ancho=760)
    esc = 0.6 + 0.4 * k + 0.08 * np.sin(k * np.pi)
    s = s.resize((int(760 * esc), int(230 * esc)), Image.LANCZOS)
    capa.alpha_composite(s, ((W - s.width) // 2, int(y - s.height / 2)))


def franja(capa, lineas, t, t0, y):
    """Titular sobre franja oscura que entra desde la izquierda."""
    k = sale((t - t0) / 0.35)
    if k <= 0: return
    d = ImageDraw.Draw(capa); dx = int(-W * (1 - k))
    alto = 30 + sum(l[1] + 14 for l in lineas)
    d.rectangle((dx, y, dx + W, y + alto), fill=MARINO + (215,))
    yy = y + 18
    for txt, tam, col in lineas:
        f = fu(tam, 'Black'); d.text((dx + (W - d.textlength(txt, font=f)) / 2, yy), txt, font=f, fill=col + (255,)); yy += tam + 14


def pastillas(capa, t, t0):
    d = ImageDraw.Draw(capa); f = fu(50, 'Bold')
    for i, a in enumerate(AMENIDADES):
        k = sale((t - t0 - 0.35 * i) / 0.3)
        if k <= 0: continue
        an = d.textlength(a, font=f) + 150; x = (W - an) / 2 + (1 - k) * 300; y = 1080 + i * 125
        d.rounded_rectangle((x, y, x + an, y + 100), 50, fill=(255, 255, 255, int(235 * k)))
        d.ellipse((x + 30, y + 26, x + 78, y + 74), fill=AZUL + (int(255 * k),))                       # palomita dibujada (la fuente no trae ✓)
        d.line([(x + 42, y + 51), (x + 51, y + 61), (x + 67, y + 39)], fill=(255, 255, 255, int(255 * k)), width=7)
        d.text((x + 100, y + 22), a, font=f, fill=MARINO + (int(255 * k),))


def portada(png, w, h, t):
    """Foto del cuadro recortada a w×h con un acercamiento lento (Ken Burns) para que el panel no se vea fijo."""
    im = Image.open(AQUI / 'cuadros' / png).convert('RGB'); z = 1.0 + 0.05 * min(1, t / 3)
    esc = max(w / im.width, h / im.height) * z; im = im.resize((int(im.width * esc), int(im.height * esc)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def cierre(t):
    """Cierre SIN el texto del flyer original: las 4 fotos reales entran como paneles y el texto nuevo se anima encima
    (precio con asterisco, amenidades, CTA a WhatsApp). Sin «No esperes a que suban los precios» (promesa sin respaldo)."""
    lienzo = Image.new('RGBA', (W, H), MARINO + (255,)); d = ImageDraw.Draw(lienzo)
    pw, ph, x0, y0, gap = 480, 500, 50, 300, 20
    pos = [(x0, y0, -1, 'F2'), (x0 + pw + gap, y0, 1, 'F1'), (x0, y0 + ph + gap, -1, 'F4'), (x0 + pw + gap, y0 + ph + gap, 1, 'F3')]
    k = sale(t / 0.4)
    texto(d, 'VIZCAÍNO RESIDENCIAL', 120, 70, BLANCO, 'Black', a=k); texto(d, 'ROSARITO, B.C.', 215, 50, AZUL, 'ExtraBold', a=k)
    for i, (x, y, lado, n) in enumerate(pos):
        kp = sale((t - 0.15 - 0.2 * i) / 0.45)
        if kp <= 0: continue
        panel = portada(n + '.png', pw, ph, t).convert('RGBA')
        m = Image.new('L', (pw, ph), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, pw, ph), 28, fill=int(255 * kp)); panel.putalpha(m)
        lienzo.alpha_composite(panel, (int(x + lado * 260 * (1 - kp)), y))
    kc = sale((t - 1.0) / 0.4)
    if kc > 0:
        yy = 1350 + int((1 - kc) * 60); d.rounded_rectangle((50, yy, W - 50, yy + 175), 36, fill=AZUL + (int(255 * kc),))
        texto(d, 'MODELO BENJAMINA · DESDE', yy + 14, 40, BLANCO, 'ExtraBold', a=kc, ancho=W - 100); texto(d, PRECIO, yy + 58, 92, BLANCO, 'Black', a=kc, ancho=W - 100)
    for i, a in enumerate(['Cancha de pádel', 'Acceso controlado', 'Plaza comercial', 'Área de juegos']):
        ka = sale((t - 1.4 - 0.12 * i) / 0.25)
        if ka > 0:
            f = fu(34, 'Bold'); cx = 50 + (i % 2) * 495; cy = 1560 + (i // 2) * 58
            d.text((cx, cy), '• ' + a, font=f, fill=BLANCO + (int(255 * ka),))
    kb = sale((t - 1.9) / 0.35)
    if kb > 0:
        txt = 'ESCRÍBENOS POR WHATSAPP'; f = fu(50, 'ExtraBold'); an = d.textlength(txt, font=f) + 110
        pul = 1 + 0.03 * np.sin(t * 7) if t > 2.3 else 1; bw, bh = an * pul, 110 * pul; yb = H - 150 + (1 - kb) * 60
        d.rounded_rectangle(((W - bw) / 2, yb - 40, (W + bw) / 2, yb - 40 + bh), 55, fill=(37, 211, 102, int(255 * kb)))
        d.text(((W - d.textlength(txt, font=f)) / 2, yb - 40 + (bh - 58) / 2), txt, font=f, fill=BLANCO + (int(255 * kb),))
        f3 = fu(26, 'Medium'); n = '*Aplican restricciones'; d.text(((W - d.textlength(n, font=f3)) / 2, H - 52), n, font=f3, fill=BLANCO + (int(220 * kb),))
    return lienzo


def main():
    mudo = AQUI / 'mudo.mp4'
    p = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', str(mudo)], stdin=subprocess.PIPE)
    t0 = 0.0; previo = None
    for n, dur in ESCENAS:
        fr = clip(n) if n != 'FLYER' else None
        for k in range(int(dur * FPS)):
            t = k / FPS
            if fr:
                im = fr[min(len(fr) - 1, int(t * 24))]
                z = 1 + 0.12 * max(0, 1 - t / 0.4)                                      # golpe de zoom al entrar
                cw, ch = int(W / z), int(H / z); im = im.crop(((W - cw) // 2, (H - ch) // 2, (W + cw) // 2, (H + ch) // 2)).resize((W, H), Image.BICUBIC)
                im = im.convert('RGBA')
                g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
                for i in range(40): gd.rectangle((0, H - 700 + i * 17, W, H), fill=(0, 0, 0, 5))   # degradado inferior para leer textos
                im.alpha_composite(g)
                capa = Image.new('RGBA', (W, H), (0, 0, 0, 0))
                if n == 'A1':
                    franja(capa, [('VIZCAÍNO RESIDENCIAL', 78, BLANCO), ('ROSARITO, B.C.', 54, AZUL)], t, 0.1, 230); sello(capa, t, 0.9, 1500)
                elif n == 'A2': franja(capa, [('MODELO', 56, AZUL), (MODELO, 104, BLANCO)], t, 0.15, 240)
                elif n == 'A3': sello(capa, t, 0.3, 1450)
                elif n == 'A4': franja(capa, [('DENTRO DEL DESARROLLO', 58, BLANCO)], t, 0.1, 240); pastillas(capa, t, 0.4)
                im.alpha_composite(capa)
            else:
                im = cierre(t)
            if previo is not None and k < 7:                                            # barrido: la escena anterior sale a la izquierda
                u = sale((k + 1) / 7); prev = previo.convert('RGBA')
                lienzo = Image.new('RGBA', (W, H)); lienzo.paste(prev, (int(-W * u), 0)); lienzo.paste(im, (int(W * (1 - u)), 0)); im = lienzo
            if k == int(dur * FPS) - 1: previo = im
            p.stdin.write(np.asarray(im.convert('RGB')).tobytes())
        t0 += dur
    p.stdin.close(); p.wait()
    sal = AQUI / f'Mariano_flyer_animado_{MODELO.lower()}.mp4'
    r = subprocess.run([FF, '-v', 'error', '-y', '-i', str(mudo), '-i', str(MUSICA), '-map', '0:v', '-map', '1:a', '-vf', 'scale=720:1280:flags=lanczos',
                        '-af', f'afade=in:d=0.3,afade=out:st={TOTAL - 1.2}:d=1.2,loudnorm=I=-14:TP=-1.5', '-t', str(TOTAL), '-c:v', 'libx264', '-profile:v', 'main',
                        '-level', '3.1', '-pix_fmt', 'yuv420p', '-crf', '21', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', str(sal)], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1500:])
    mudo.unlink(); print(sal, sal.stat().st_size // 1024, 'KB')


if __name__ == '__main__':
    main()
