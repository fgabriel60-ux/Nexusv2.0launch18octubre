"""Arma las 2 versiones (fondo negro / Pixar): sticker de métricas que se pega, se lee y se despega + subtítulos + voz limpia."""
import subprocess, sys
from pathlib import Path
import av, imageio_ffmpeg, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
NEG = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; NOR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
W, H, FPS = 720, 1280, 30
TMP = AQUI / 'tmp'; TMP.mkdir(exist_ok=True); (AQUI / 'final').mkdir(exist_ok=True)
TEXTO = ('Mira esto. Campaña de Nexus: seiscientos ochenta y ocho pesos, cincuenta conversaciones, a trece setenta y seis cada una. '
         'Es la de Mariano, de San Marino. Lanzamos ayer y ya le cayeron tres.')
SUB = ['Mira esto.', 'Campaña de Nexus:', '$688 pesos,', '50 conversaciones,', 'a $13.76 cada una.', 'Es la de Mariano,', 'de San Marino.', 'Lanzamos ayer', 'y ya le cayeron tres.']
T_ENTRA, T_SALE = 0.6, 4.6        # el sticker se pega a 0.6 s, se lee hasta 4.6 s y se despega
F = lambda t, n=True: ImageFont.truetype(NEG if n else NOR, t)


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1500:])


def tarjeta():
    w, h = 600, 250
    g = Image.new('RGBA', (w + 30, h + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    sh = Image.new('RGBA', g.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((12, 20, w + 12, h + 20), 28, fill=(0, 0, 0, 150))
    g.alpha_composite(sh.filter(ImageFilter.GaussianBlur(9)))
    d.rounded_rectangle((8, 8, w + 8, h + 8), 28, fill=(24, 28, 38, 255), outline=(37, 211, 102, 255), width=5)
    d.text((34, 26), 'NEXUS · WhatsApp · sep 2026', font=F(25), fill=(235, 238, 245))
    d.text((34, 62), '● Activa  Interacción', font=F(19, False), fill=(60, 215, 120))
    for i, (v, l) in enumerate([('50', 'Conversaciones'), ('$13.76', 'Costo por resultado'), ('$688.09', 'Gasto')]):
        x = 30 + i * 195
        d.text((x, 118), v, font=F(40), fill=(255, 255, 255)); d.text((x, 182), l, font=F(17, False), fill=(190, 198, 210))
    return g


def ease(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)


def pegar(base, spr, xy, t):
    if t < T_ENTRA: return
    pe = ease((t - T_ENTRA) / 0.3); ps = ease((t - T_SALE) / 0.7) if t >= T_SALE else 0
    if ps >= 1: return
    esc = (0.6 + 0.4 * pe + 0.05 * np.sin(pe * np.pi)) * (1 - 0.25 * ps)
    im = spr.resize((int(spr.width * esc), int(spr.height * esc)), Image.LANCZOS)
    if ps > 0:       # se despega: gira desde la esquina, sube y se desvanece
        im = im.rotate(-28 * ps, resample=Image.BICUBIC, expand=True)
        im.putalpha(im.getchannel('A').point(lambda v: int(v * (1 - ps))))
    cx = xy[0] + spr.width / 2 + 60 * ps; cy = xy[1] + spr.height / 2 - 260 * ps
    base.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def sub_img(txt):
    img = Image.new('RGBA', (W, 120), (0, 0, 0, 0)); d = ImageDraw.Draw(img); t = 56; f = F(t)
    while d.textlength(txt, font=f) > W - 60: t -= 3; f = F(t)
    d.text(((W - d.textlength(txt, font=f)) / 2, 25), txt, font=f, fill=(255, 255, 255), stroke_width=6, stroke_fill=(0, 0, 0))
    return img


def main(nombre, clip):
    clip = Path(clip)
    # audio: limpieza de voz y volumen parejo
    aud = TMP / f'{nombre}.wav'
    ff(['-i', str(clip), '-vn', '-af', 'pan=mono|c0=0.5*c0+0.5*c1,highpass=f=85,afftdn=nr=10:nf=-38,equalizer=f=3200:t=q:w=1:g=2.5,'
        'equalizer=f=7500:t=q:w=2:g=-2.5,acompressor=threshold=-22dB:ratio=3:attack=8:release=120:makeup=3,alimiter=limit=0.9', '-ar', '48000', '-ac', '2', str(aud)])
    c = av.open(str(clip)); n_fr = c.streams.video[0].frames or 0
    dur = float(c.duration) / 1e6
    # palabras repartidas en el tramo hablado (0.3 s .. dur-0.4 s)
    pesos = np.array([len(s) + 3 for s in SUB], float); t0, t1 = 0.35, dur - 0.5
    cortes = t0 + (t1 - t0) * np.concatenate([[0], np.cumsum(pesos)]) / pesos.sum()
    card = tarjeta(); subs = [sub_img(s) for s in SUB]
    mudo = TMP / f'{nombre}_mudo.mp4'
    p = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', str(mudo)], stdin=subprocess.PIPE)
    ult = None
    gen = (fr.to_image().convert('RGB').resize((W, H), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.4, 60, 2)) for fr in c.decode(video=0))
    # el clip va a 24 fps: se remuestrea a 30
    frames = list(gen); N = int(dur * FPS)
    for k in range(N):
        t = k / FPS; base = frames[min(len(frames) - 1, int(t * len(frames) / dur))].convert('RGBA')
        pegar(base, card, (40, 720), t)
        for i, s in enumerate(subs):
            if cortes[i] <= t < (cortes[i + 1] if i + 1 < len(SUB) else dur):
                base.alpha_composite(s, (0, 1040)); break
        p.stdin.write(np.asarray(base.convert('RGB')).tobytes())
    p.stdin.close(); p.wait()
    sal = AQUI / 'final' / f'Carlos_{nombre}.mp4'
    ff(['-i', str(mudo), '-i', str(aud), '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p', '-crf', '21',
        '-preset', 'slow', '-c:a', 'aac', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=7', '-ar', '44100', '-b:a', '192k', '-shortest', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB', f'{dur:.1f}s')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
