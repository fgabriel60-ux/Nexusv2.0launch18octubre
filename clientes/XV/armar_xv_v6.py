"""Reel XV v6 (Manuel): SOLO la parte de fiesta de la referencia «GIO XV» (pista → amigas → hora loca → clímax → giro final), nada estático.
Todo es video REAL (caras intactas): cámara virtual que recorre el 4K (paneo + zoom), rampas de velocidad sobre los 60 fps, golpes de zoom
y destello en cada corte, confeti en la hora loca y el clímax, color de cine. Audio: la música real de la fiesta (C6801).
Uso: python3 armar_xv_v6.py"""
import subprocess
from pathlib import Path
import av, imageio_ffmpeg, numpy as np
from PIL import Image, ImageDraw, ImageFilter
from armar_xv import tarjeta

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
ORI = AQUI / 'originales'
TMP = Path('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/30f81786-0fae-4f61-88f3-0421cbe18eec/scratchpad/xv6'); TMP.mkdir(parents=True, exist_ok=True)
W, H, FPS = 1080, 1920, 30
GLOW = "split[a][b];[b]gblur=sigma=20,eq=brightness=0.02[g];[a][g]blend=all_mode=screen:all_opacity=0.18,vignette=PI/5"
COLOR = "curves=all='0/0.03 0.35/0.40 1/1',eq=contrast=1.09:saturation=1.25:gamma=1.05,colorbalance=rs=0.05:bs=0.02:rh=0.03:bh=-0.02"
# (clip, inicio s, duración de salida, centro x inicio→fin, zoom inicio→fin, velocidad inicio→fin, confeti)
TOMAS = [
    ('C6755', 0.8, 1.8, (.42, .50), (1.00, 1.35), (1.0, 0.5), False),   # ella entra a la pista frente a las letras XV: empuje rápido que frena
    ('C6771', 2.0, 2.4, (.30, .55), (1.25, 1.10), (0.4, 0.4), False),   # giro del vestido en cámara lenta, la cámara la sigue
    ('C6755', 12.0, 1.2, (.65, .40), (1.15, 1.30), (1.0, 1.0), False),  # amigas bailando · paneo
    ('C6755', 24.0, 1.2, (.40, .55), (1.40, 1.15), (1.0, 1.0), False),
    ('C6755', 45.0, 1.2, (.55, .45), (1.10, 1.30), (1.0, 1.0), False),
    ('C6755', 60.0, 1.2, (.35, .55), (1.30, 1.10), (1.0, 1.0), False),
    ('C6801', 4.0, 1.6, (.30, .45), (1.30, 1.10), (1.0, 0.6), True),    # hora loca: robot LED
    ('C6801', 66.0, 1.2, (.55, .40), (1.10, 1.35), (1.0, 1.0), True),
    ('C6801', 84.0, 1.6, (.45, .55), (1.20, 1.40), (0.8, 0.5), True),   # ella con el robot
    ('C6801', 117.0, 1.4, (.35, .50), (1.35, 1.15), (1.0, 1.0), True),
    ('C6801', 126.0, 1.4, (.50, .40), (1.15, 1.35), (1.0, 0.7), True),  # clímax en la pista
    ('C6801', 141.0, 1.2, (.40, .55), (1.30, 1.10), (1.0, 1.0), True),
    ('C6801', 168.0, 1.8, (.45, .50), (1.10, 1.35), (0.6, 0.4), True),
    ('C6801', 177.0, 1.2, (.55, .40), (1.35, 1.15), (1.0, 1.0), True),
    ('C6771', 10.0, 5.6, (.40, .48), (1.10, 1.45), (0.5, 0.3), False),  # giro final en cámara muy lenta + tarjeta encima
]
TOTAL = sum(t[2] for t in TOMAS)
T_TARJ = TOTAL - 3.0


def suave(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)


class Confeti:
    def __init__(self, n=140, semilla=7):
        r = np.random.default_rng(semilla)
        self.x = r.uniform(0, W, n); self.y = r.uniform(-H, H, n); self.v = r.uniform(5, 13, n); self.f = r.uniform(0, 6.3, n)
        self.c = r.choice([(255, 215, 90), (255, 255, 255), (255, 120, 190), (120, 220, 255)], n)
        self.s = r.uniform(7, 15, n)

    def dibuja(self, img, k):
        d = ImageDraw.Draw(img)
        for i in range(len(self.x)):
            y = (self.y[i] + self.v[i] * k) % (H + 200) - 100; x = self.x[i] + 30 * np.sin(self.f[i] + k * 0.08)
            a = abs(np.cos(self.f[i] + k * 0.15)); s = self.s[i]
            d.rectangle((x, y, x + s, y + s * (0.3 + 0.7 * a)), fill=tuple(int(v) for v in self.c[i]) + (230,))


def toma(enc, n, clip, ini, dur, cx, zz, vel, confeti, conf):
    c = av.open(str(ORI / f'{clip}.MP4')); st = c.streams.video[0]; st.thread_type = 'AUTO'
    c.seek(int(ini / st.time_base), stream=st, backward=True)
    gen = (f for f in c.decode(st))
    fr = next(gen); tf = float(fr.pts * st.time_base)
    nf = int(round(dur * FPS)); t_src = ini
    for k in range(nf):
        u = k / max(1, nf - 1)
        t_src += (vel[0] + (vel[1] - vel[0]) * suave(u)) / FPS                      # rampa de velocidad
        while tf < t_src:
            try: fr = next(gen); tf = float(fr.pts * st.time_base)
            except StopIteration: break
        im = fr.to_image(width=2560, height=1440)
        z = zz[0] + (zz[1] - zz[0]) * suave(u) + 0.10 * max(0, 1 - k / 8)         # golpe de zoom al entrar
        ch = 1440 / z; cw = ch * 9 / 16
        x = cx[0] + (cx[1] - cx[0]) * suave(u)
        x0 = min(2560 - cw, max(0, x * 2560 - cw / 2)); y0 = (1440 - ch) / 2
        im = im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.BICUBIC).convert('RGBA')
        if k < 3: im = Image.blend(im, Image.new('RGBA', (W, H), (255, 255, 255, 255)), 0.4 * (1 - k / 3))   # destello en el corte
        if confeti: conf.dibuja(im, enc.k)
        enc.k += 1
        enc.p.stdin.write(np.asarray(im.convert('RGB')).tobytes())
    c.close()
    print('toma', n, clip, ini, flush=True)


class Enc:
    def __init__(self, ruta):
        self.k = 0
        self.p = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                                   '-vf', f"{COLOR},{GLOW},noise=alls=4:allf=t,format=yuv420p", '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', str(ruta)],
                                  stdin=subprocess.PIPE)


def main():
    tarjeta(TMP / 'tarjeta.png')
    mudo = TMP / 'mudo.mp4'; e = Enc(mudo); conf = Confeti()
    for n, t in enumerate(TOMAS): toma(e, n, *t, conf)
    e.p.stdin.close(); e.p.wait()
    fiesta = TMP / 'fiesta.wav'
    subprocess.run([FF, '-v', 'error', '-y', '-ss', '72', '-t', f'{TOTAL + 1:.1f}', '-i', str(ORI / 'C6801.MP4'), '-vn', '-ac', '2', '-ar', '44100', str(fiesta)], check=True)
    fl = (f"[1:v]format=rgba,fade=t=in:st=0:d=0.4:alpha=1,setpts=PTS+{T_TARJ:.2f}/TB[tj];[0:v][tj]overlay=0:0:eof_action=pass,scale=720:1280:flags=lanczos[v];"
          f"[2:a]loudnorm=I=-14:TP=-1.5,afade=t=in:st=0:d=0.3,afade=t=out:st={TOTAL - 1.2:.2f}:d=1.2[a]")
    sal = AQUI / 'final' / 'XV_reel_v6_fiesta.mp4'
    r = subprocess.run([FF, '-v', 'error', '-y', '-i', str(mudo), '-loop', '1', '-t', '3.0', '-i', str(TMP / 'tarjeta.png'), '-i', str(fiesta), '-filter_complex', fl,
                        '-map', '[v]', '-map', '[a]', '-t', f'{TOTAL:.2f}', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p', '-crf', '22',
                        '-preset', 'slow', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', str(sal)], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1500:])
    print(sal, sal.stat().st_size // 1024, 'KB', f'{TOTAL:.1f}s')


if __name__ == '__main__':
    main()
