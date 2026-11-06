"""Manuel Fotografía · XV v13: reel v12 con la VOZ REAL de Manuel y las escenas reordenadas según lo que va diciendo.
Voz: nota de WhatsApp (completa para las frases 1-4, toma del cierre para la 5), limpiada (silencios largos fuera, highpass, afftdn, compresión, loudnorm).
Escenas: del v3 (reales y primera mitad), v12 (IA con color) y v8 (IA crudas). Música del v12 por debajo con ducking. Subtítulos palabra por palabra.
Uso: python3 armar_xv_v13.py   (tiempos por palabra de faster_whisper ya fijados abajo; --whisper los recalcula)"""
import subprocess, sys
from pathlib import Path
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
TMP = Path('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/632e0195-4202-422b-a741-74f9ff894c0c/scratchpad/v13'); TMP.mkdir(parents=True, exist_ok=True)
FINAL = AQUI / 'final'
V3, V12 = FINAL / 'XV_reel_v3.mp4', FINAL / 'XV_reel_v12_inicio_v3_fiesta_IA_sin_voz.mp4'
V8 = AQUI / 'v8' / 'clips'
VOZ_C, VOZ_X = AQUI / 'voz_manuel' / 'voz_manuel_completa.ogg', AQUI / 'voz_manuel' / 'voz_manuel_cierre.ogg'
FUENTE = '/workspaces/Nexusv2.0launch18octubre/visionagenciaIAV2.0-main 2/entregables/modelos_modal/fuentes/Montserrat.ttf'
W, H, FPS = 720, 1280, 30
LEAD, GAP, TAIL, XF = 0.5, 0.35, 1.8, 0.28

# Frases: (fuente de voz, inicio, fin del recorte, [(palabra, ini, fin) de whisper], chunks de subtítulo [n palabras])
FR = [
    ('C', 1.10, 4.40, [('Una', 1.24, 1.96), ('quinceañera,', 1.96, 2.68), ('un', 3.18, 3.32), ('recuerdo', 3.32, 3.64), ('que', 3.64, 3.86), ('dura.', 3.86, 4.22)], [2, 4]),
    ('C', 5.10, 9.40, [('Aquí', 5.20, 5.34), ('ves', 5.34, 5.66), ('la', 5.66, 5.90), ('luz,', 5.90, 6.34), ('la', 6.94, 7.08), ('sonrisa,', 7.08, 7.72), ('el', 8.34, 8.46), ('vestido', 8.46, 8.82), ('verde.', 8.82, 9.22)], [4, 2, 3]),
    ('C', 10.10, 15.86, [('Después,', 10.20, 10.92), ('la', 11.56, 11.80), ('entrada,', 11.80, 12.12), ('el', 12.98, 13.20), ('giro,', 13.20, 13.62), ('la', 14.06, 14.20), ('emoción', 14.20, 14.56), ('del', 14.56, 14.78), ('salón.', 14.78, 15.66)], [3, 2, 4]),
    ('C', 15.96, 20.45, [('Momentos', 16.06, 16.56), ('reales,', 16.56, 17.62), ('con', 17.72, 17.90), ('un', 17.90, 18.14), ('toque', 18.14, 18.54), ('cinematográfico.', 19.48, 20.20)], [2, 3, 1]),
    ('X', 0.52, 5.80, [('Si', 0.62, 1.18), ('quieres', 1.18, 1.46), ('algo', 1.46, 1.70), ('así', 1.70, 1.96), ('para', 1.96, 2.18), ('tu', 2.18, 2.32), ('hija,', 2.32, 3.32), ('escríbenos', 3.60, 3.88), ('por', 3.88, 4.06), ('WhatsApp', 4.06, 4.44), ('y', 4.44, 4.92), ('agenda', 4.92, 5.12), ('tu', 5.12, 5.30), ('fecha.', 5.30, 5.60)], [4, 3, 3, 4]),
]
# offsets de cada frase en la línea de tiempo de salida
OFF, t = [], LEAD
for _, a, b, _, _ in FR:
    OFF.append(t); t += (b - a) + GAP
T_VOZ = t - GAP
TOTAL = T_VOZ + TAIL


def V(k, src):
    """tiempo de salida de un instante (s de la fuente de voz) de la frase k"""
    return OFF[k] + src - FR[k][1]


# Escenas: (nombre, archivo, ss, inicio en la salida, desenfoque_in, desenfoque_out, zoom)
SC = [
    ('salon', V3, 0.0, 0.0, 0, 0),                      # frase 1: apertura (salón XV)
    ('aerea', V8 / 'M1.mp4', 0.3, V(0, 1.80), 0, 0),    # «quinceañera»
    ('tiara', V8 / 'M3.mp4', 0.6, V(0, 3.05), 0, 0),    # «un recuerdo que dura»
    ('luz', V8 / 'M2.mp4', 0.3, V(1, 5.12), 0, 1),      # «Aquí ves la luz»
    ('sonrisa', V3, 3.6, V(1, 6.80), 1, 0),             # «la sonrisa»
    ('verde', V3, 9.0, V(1, 8.25), 0, 0),               # «el vestido verde»
    ('caballo', V3, 11.2, V(2, 10.12), 0, 1),           # «Después,»
    ('entrada', V12, 14.0, V(2, 11.40), 1, 0),          # «la entrada»
    ('giro', V12, 17.0, V(2, 12.85), 0, 1),             # «el giro»
    ('pista', V3, 17.0, V(2, 14.00), 1, 0),             # «la emoción del salón»
    ('real1', V3, 20.1, V(3, 15.96), 0, 0),             # «Momentos reales»
    ('real2', V3, 23.2, V(3, 16.90), 0, 1),
    ('robot', V12, 22.4, V(3, 17.75), 1, 0),            # «con un toque cinematográfico»
    ('arco', V12, 25.6, V(3, 19.35), 0, 1),
    ('tarjeta', V12, 32.0, OFF[4] - 0.1, 1, 0),         # frase 5: cierre
]


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-2000:])


def voz():
    """Voz limpia y recortada, con huecos de GAP entre frases. Devuelve wav mono 44.1 k."""
    ent, fl = [], ''
    for k, (src, a, b, _, _) in enumerate(FR):
        ent += ['-i', str(VOZ_C if src == 'C' else VOZ_X)]
        fl += f'[{k}:a]aresample=44100,atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={b - a - 0.04:.3f}:d=0.04,apad=pad_dur={GAP}[p{k}];'
    fl += ''.join(f'[p{k}]' for k in range(len(FR))) + f'concat=n={len(FR)}:v=0:a=1,atrim=0:{T_VOZ:.3f},adelay={int(LEAD * 1000)},'
    fl += 'highpass=f=75,afftdn=nr=10:nf=-32:tn=1,acompressor=threshold=-21dB:ratio=2.5:attack=8:release=140:makeup=2,alimiter=limit=0.9,loudnorm=I=-15:TP=-1.5:LRA=7[v]'
    out = TMP / 'voz_limpia.wav'
    ff(ent + ['-filter_complex', fl, '-map', '[v]', '-ac', '1', '-ar', '44100', str(out)])
    return out


def video_mudo():
    ent, fl = [], ''
    n = len(SC)
    norm = f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},setsar=1,format=yuv420p'
    for i, (nom, f, ss, s0, bi, bo) in enumerate(SC):
        s1 = SC[i + 1][3] if i + 1 < n else TOTAL
        L = (s1 - s0) + (XF if i + 1 < n else 0) + (XF / 2 if i == 0 else 0)
        if i == n - 1: L = TOTAL - s0 + 0.2
        ent += ['-ss', f'{ss}', '-t', f'{L + 0.1:.2f}', '-i', str(f)]
        ef = ''
        if str(f).startswith(str(V8)): ef = ',eq=contrast=1.05:saturation=1.1,vignette=PI/5'
        bl = ''
        if bi: bl += f",gblur=sigma=14:enable='lt(t,{XF * 1.4:.2f})'"
        if bo: bl += f",gblur=sigma=14:enable='gt(t,{L - XF * 1.4:.2f})'"
        tp = f',tpad=stop_mode=clone:stop_duration=4' if nom == 'tarjeta' else ''
        fl += f'[{i}:v]{norm}{ef}{tp},trim=duration={L:.3f},setpts=PTS-STARTPTS{bl},fps={FPS},settb=AVTB[c{i}];'
    prev = 'c0'
    for i in range(1, n):
        fl += f'[{prev}][c{i}]xfade=transition=fade:duration={XF}:offset={SC[i][3] - XF / 2:.3f}[x{i}];'; prev = f'x{i}'
    out = TMP / 'mudo.mp4'
    ff(ent + ['-filter_complex', fl.rstrip(';'), '-map', f'[{prev}]', '-t', f'{TOTAL:.2f}', '-an', '-c:v', 'libx264', '-crf', '15', '-preset', 'fast', '-pix_fmt', 'yuv420p', str(out)])
    return out


# ---------- subtítulos ----------
def fuente(t):
    f = ImageFont.truetype(FUENTE, t); f.set_variation_by_name('ExtraBold'); return f


class Subs:
    def __init__(self, y=0.80, tam=56):
        self.items = []   # (ini, fin, [(sprite_x, sprite, idx)])
        f = fuente(tam)
        for k, (_, a, b, ws, chunks) in enumerate(FR):
            pos = 0; grupos = []
            for c in chunks:
                grupos.append(ws[pos:pos + c]); pos += c
            for gi, g in enumerate(grupos):
                ini = V(k, g[0][1]) - 0.05
                fin = V(k, grupos[gi + 1][0][1]) - 0.05 if gi + 1 < len(grupos) else V(k, g[-1][2]) + 0.45
                espacio = 16; anchos = [f.getlength(w[0]) for w in g]
                tot = sum(anchos) + espacio * (len(g) - 1); x = (W - tot) / 2
                spr = []
                for w, an in zip(g, anchos):
                    spr.append((x, w[0], V(k, w[1]) - 0.02, V(k, w[2]) + (0.0 if w is not g[-1] else 0.0))); x += an + espacio
                self.items.append((ini, fin, spr))
        self.f = f; self.y = int(H * y); self.cache = {}

    def sprite(self, txt, activa):
        key = (txt, activa)
        if key in self.cache: return self.cache[key]
        w = int(self.f.getlength(txt)) + 40; h = 110
        img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        sh = Image.new('L', (w, h), 0); ImageDraw.Draw(sh).text((20, 22), txt, font=self.f, fill=230); sh = sh.filter(ImageFilter.GaussianBlur(6))
        s = Image.new('RGBA', (w, h), (0, 0, 0, 0)); s.putalpha(sh); img = Image.alpha_composite(img, s)
        col = (255, 214, 10, 255) if activa else (255, 255, 255, 255)
        if activa:
            gl = Image.new('L', (w, h), 0); ImageDraw.Draw(gl).text((20, 18), txt, font=self.f, fill=255); gl = gl.filter(ImageFilter.GaussianBlur(8))
            capa = Image.new('RGBA', (w, h), (255, 190, 0, 0)); capa.putalpha(gl.point(lambda v: int(v * 0.8))); img = Image.alpha_composite(img, capa)
        ImageDraw.Draw(img).text((20, 18 if activa else 22), txt, font=self.f, fill=col, stroke_width=3, stroke_fill=(25, 15, 10, 255))
        self.cache[key] = img; return img

    def pintar(self, img, t):
        for ini, fin, spr in self.items:
            if ini <= t < fin:
                ult = max((i for i, s in enumerate(spr) if s[2] <= t), default=None)
                for i, (x, txt, a, b) in enumerate(spr):   # dichas: la última resaltada; las que faltan, en blanco
                    img.alpha_composite(self.sprite(txt, i == ult), (int(x) - 20, self.y))
                return


def montar(mudo, vozwav):
    subs = Subs()
    dec = subprocess.Popen([FF, '-v', 'error', '-i', str(mudo), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    sin_audio = TMP / 'con_subs.mp4'
    enc = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-profile:v', 'main', '-pix_fmt', 'yuv420p',
                            '-crf', '22', '-preset', 'slow', str(sin_audio)], stdin=subprocess.PIPE)
    n = 0; sz = W * H * 3
    while True:
        b = dec.stdout.read(sz)
        if len(b) < sz: break
        img = Image.frombuffer('RGB', (W, H), b).convert('RGBA')
        subs.pintar(img, n / FPS)
        enc.stdin.write(img.convert('RGB').tobytes()); n += 1
    enc.stdin.close(); enc.wait(); dec.wait()
    return sin_audio


def audio_final(vozwav):
    """música del v12: calma (0-9.6) → fiesta (desde 13.0), con ducking por la voz"""
    t_cambio = V(2, 10.0) - 0.6
    mus = (f'[1:a]aresample=44100,atrim=0:{t_cambio + 1.4:.2f},afade=t=out:st={t_cambio - 0.2:.2f}:d=1.6,volume=0.8[m1];'
           f'[2:a]aresample=44100,atrim=13.0:{13.0 + TOTAL - t_cambio + 1:.2f},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.8,volume=1.0,adelay={int(t_cambio * 1000)}|{int(t_cambio * 1000)}[m2];'
           f'[m1][m2]amix=inputs=2:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},loudnorm=I=-19:TP=-2,afade=t=in:st=0:d=0.8[m];')
    duck = ('[0:a]asplit=2[vk][vv];[m][vk]sidechaincompress=threshold=0.02:ratio=9:attack=15:release=450:makeup=1[md];'
            f'[md][vv]amix=inputs=2:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},afade=t=out:st={TOTAL - 1.4:.2f}:d=1.4,alimiter=limit=0.95,loudnorm=I=-14:TP=-1.5[a]')
    out = TMP / 'audio_final.m4a'
    ff(['-i', str(vozwav), '-i', str(V12), '-i', str(V12), '-filter_complex', mus + duck, '-map', '[a]', '-ac', '2', '-ar', '44100', '-c:a', 'aac', '-b:a', '160k', str(out)])
    return out


def main():
    v = voz(); m = video_mudo(); s = montar(m, v); a = audio_final(v)
    sal = FINAL / 'XV_reel_v13_voz_manuel.mp4'
    ff(['-i', str(s), '-i', str(a), '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'copy', '-t', f'{TOTAL:.2f}', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB', f'{TOTAL:.1f}s')
    for nom, f, ss, s0, *_ in SC: print(f'{s0:5.2f}  {nom}')


if __name__ == '__main__':
    main()
