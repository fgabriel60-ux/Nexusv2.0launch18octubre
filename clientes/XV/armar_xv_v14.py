"""Manuel Fotografía · XV v14 (v13 + voz procesada tipo estudio, subtítulos virales y cierre con endcard de Hunab Ku): reel v12 con la VOZ REAL de Manuel y las escenas reordenadas según lo que va diciendo.
Voz: nota de WhatsApp (completa para las frases 1-4, toma del cierre para la 5), limpiada (silencios largos fuera, highpass, afftdn, compresión, loudnorm).
Escenas: del v3 (reales y primera mitad), v12 (IA con color) y v8 (IA crudas). Música del v12 por debajo con ducking. Subtítulos palabra por palabra.
Uso: python3 armar_xv_v14.py   (tiempos por palabra de faster_whisper ya fijados abajo; --whisper los recalcula)"""
import subprocess, sys
from pathlib import Path
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
TMP = Path('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/632e0195-4202-422b-a741-74f9ff894c0c/scratchpad/v14'); TMP.mkdir(parents=True, exist_ok=True)
FINAL = AQUI / 'final'
V3, V12 = FINAL / 'XV_reel_v3.mp4', FINAL / 'XV_reel_v12_inicio_v3_fiesta_IA_sin_voz.mp4'
V8 = AQUI / 'v8' / 'clips'
VOZ_C, VOZ_X = AQUI / 'voz_manuel' / 'voz_manuel_completa.ogg', AQUI / 'voz_manuel' / 'voz_manuel_cierre.ogg'
FUENTE = '/workspaces/Nexusv2.0launch18octubre/clientes/Carlos_Nexus/pixar/fonts/Inter-Black.ttf'
W, H, FPS = 720, 1280, 30
LEAD, GAP, XF = 0.5, 0.5, 0.28
END_HOLD, END_DUR = 0.9, 4.3   # la tarjeta se queda 0.9 s tras «fecha» y luego entra el endcard de Hunab Ku
ENDCARD = AQUI.parent / 'Manuel_fotografia' / 'logo' / 'HunabKu_endcard.mp4'

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
T_END = T_VOZ + END_HOLD
TOTAL = T_END + END_DUR


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
    ('endcard', ENDCARD, 0.0, T_END, 0, 0),             # logo Hunab Ku
]


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-2000:])


def voz():
    """Voz de estudio a partir de la nota de WhatsApp: recorte + pausas de GAP, reducción de ruido real (noisereduce con perfil del ruido de fondo),
    highpass 80 Hz, -3 dB en 320 Hz (cuarto/lodo), +2.5 dB en 4 kHz (presencia), de-esser, compresión 3:1, reverb de sala mínima y loudnorm -14."""
    import soundfile as sf, noisereduce as nr
    from scipy.signal import butter, sosfilt
    from pedalboard import Pedalboard, HighpassFilter, PeakFilter, Compressor, Reverb, Limiter
    ent, fl = [], ''
    for k, (src, a, b, _, _) in enumerate(FR):
        ent += ['-i', str(VOZ_C if src == 'C' else VOZ_X)]
        fl += f'[{k}:a]aresample=44100,atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={b - a - 0.04:.3f}:d=0.04,apad=pad_dur={GAP}[p{k}];'
    fl += ''.join(f'[p{k}]' for k in range(len(FR))) + f'concat=n={len(FR)}:v=0:a=1,atrim=0:{T_VOZ:.3f},adelay={int(LEAD * 1000)}[v]'
    crudo = TMP / 'voz_cruda.wav'
    ff(ent + ['-filter_complex', fl, '-map', '[v]', '-ac', '1', '-ar', '44100', str(crudo)])
    y, sr = sf.read(str(crudo), dtype='float32')
    ff(['-i', str(VOZ_C), '-t', '1.0', '-ac', '1', '-ar', '44100', str(TMP / 'raw_completa.wav')])
    ruido = sf.read(str(TMP / 'raw_completa.wav'), dtype='float32')[0][:int(1.0 * sr)]   # 1 s de «silencio» con solo ruido de fondo
    y = nr.reduce_noise(y=y, sr=sr, y_noise=ruido, stationary=True, prop_decrease=0.75, n_fft=1024, freq_mask_smooth_hz=400, time_mask_smooth_ms=60)
    # de-esser: banda 5.5-9 kHz con ganancia dinámica
    sos = butter(4, [5500, 9000], btype='band', fs=sr, output='sos'); banda = sosfilt(sos, y)
    env = np.convolve(np.abs(banda), np.ones(int(sr * 0.006)) / int(sr * 0.006), mode='same')
    umbral = np.percentile(env[env > 1e-4], 85) if (env > 1e-4).any() else 1
    g = np.minimum(1.0, (umbral / np.maximum(env, 1e-6)) ** 0.7)
    g = np.convolve(g, np.ones(int(sr * 0.01)) / int(sr * 0.01), mode='same')
    y = (y - banda * (1 - g)).astype(np.float32)
    tabla = Pedalboard([HighpassFilter(80), PeakFilter(320, -3.0, 1.0), PeakFilter(4000, 2.5, 0.8), Compressor(threshold_db=-21, ratio=3.0, attack_ms=10, release_ms=140),
                        Reverb(room_size=0.12, damping=0.6, wet_level=0.06, dry_level=0.94, width=0.5), Limiter(threshold_db=-1.5)])
    y = tabla(y.reshape(1, -1), sr).reshape(-1)
    pre = TMP / 'voz_pre.wav'; sf.write(str(pre), y, sr)
    out = TMP / 'voz_limpia.wav'
    ff(['-i', str(pre), '-af', 'loudnorm=I=-14:TP=-1.5:LRA=7', '-ac', '1', '-ar', '44100', str(out)])
    return out


def video_mudo():
    ent, fl = [], ''
    n = len(SC)
    norm = f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},setsar=1,format=yuv420p'
    for i, (nom, f, ss, s0, bi, bo) in enumerate(SC):
        s1 = SC[i + 1][3] if i + 1 < n else TOTAL
        L = (s1 - s0) + (XF if i + 1 < n else 0) + (XF / 2 if i == 0 else 0)
        if i == n - 1: L = TOTAL - s0 + 0.2
        if nom == 'endcard': L = END_DUR + XF
        ent += ['-ss', f'{ss}', '-t', f'{L + 0.1:.2f}', '-i', str(f)]
        ef = ''
        if str(f).startswith(str(V8)): ef = ',eq=contrast=1.05:saturation=1.1,vignette=PI/5'
        bl = ''
        if bi: bl += f",gblur=sigma=14:enable='lt(t,{XF * 1.4:.2f})'"
        if bo: bl += f",gblur=sigma=14:enable='gt(t,{L - XF * 1.4:.2f})'"
        tp = f',tpad=stop_mode=clone:stop_duration=4' if nom in ('tarjeta', 'endcard') else ''
        fl += f'[{i}:v]{norm}{ef}{tp},trim=duration={L:.3f},setpts=PTS-STARTPTS{bl},fps={FPS},settb=AVTB[c{i}];'
    prev = 'c0'
    for i in range(1, n):
        fl += f'[{prev}][c{i}]xfade=transition=fade:duration={XF}:offset={SC[i][3] - XF / 2:.3f}[x{i}];'; prev = f'x{i}'
    out = TMP / 'mudo.mp4'
    ff(ent + ['-filter_complex', fl.rstrip(';'), '-map', f'[{prev}]', '-t', f'{TOTAL:.2f}', '-an', '-c:v', 'libx264', '-crf', '15', '-preset', 'fast', '-pix_fmt', 'yuv420p', str(out)])
    return out


# ---------- subtítulos ----------
CLAVE = {'quinceañera', 'recuerdo', 'luz', 'sonrisa', 'vestido', 'verde', 'entrada', 'giro', 'emoción', 'cinematográfico', 'whatsapp', 'fecha'}
AMARILLO, VERDE, OSCURO = (255, 214, 10), (40, 205, 115), (22, 14, 10)


def fuente(t):
    return ImageFont.truetype(FUENTE, t)


class Subs:
    """Bloques de 2-4 palabras en Inter Black; la palabra activa va en caja de color con «pop» de escala; claves en color; borde y sombra suaves."""
    def __init__(self, y=0.80, tam=64, ancho_max=640):
        self.items = []; self.y = int(H * y); self.cache = {}; self.fonts = {}
        for k, (_, a, b, ws, chunks) in enumerate(FR):
            pos = 0; grupos = []
            for c in chunks:
                grupos.append(ws[pos:pos + c]); pos += c
            for gi, g in enumerate(grupos):
                ini = V(k, g[0][1]) - 0.05
                fin = V(k, grupos[gi + 1][0][1]) - 0.05 if gi + 1 < len(grupos) else V(k, g[-1][2]) + 0.5
                txts = [w[0].rstrip('.,').upper() for w in g]
                tm = tam
                while tm > 40 and sum(self.f(tm).getlength(t) + 34 for t in txts) + 14 * (len(txts) - 1) > ancho_max: tm -= 2
                f = self.f(tm); anchos = [f.getlength(t) + 34 for t in txts]
                x = (W - sum(anchos) - 14 * (len(txts) - 1)) / 2; spr = []
                for w, t, an in zip(g, txts, anchos):
                    spr.append((x, an, t, w[0].rstrip('.,').lower() in CLAVE, tm, V(k, w[1]) - 0.02)); x += an + 14
                self.items.append((ini, fin, spr))

    def f(self, t):
        if t not in self.fonts: self.fonts[t] = fuente(t)
        return self.fonts[t]

    def sprite(self, txt, clave, activa, tm, escala):
        key = (txt, clave, activa, tm, round(escala, 2))
        if key in self.cache: return self.cache[key]
        f = self.f(int(tm * escala)); w = int(f.getlength(txt)) + 34; asc, desc = f.getmetrics(); h = asc + desc + 40
        img = Image.new('RGBA', (w + 40, h + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
        sh = Image.new('L', img.size, 0); ImageDraw.Draw(sh).text((37, 24 + 6), txt, font=f, fill=200); sh = sh.filter(ImageFilter.GaussianBlur(8))
        sp = Image.new('RGBA', img.size, (0, 0, 0, 0)); sp.putalpha(sh); img = Image.alpha_composite(img, sp); d = ImageDraw.Draw(img)
        if activa:
            col = VERDE if clave else AMARILLO
            d.rounded_rectangle((20, 14, 20 + w, 14 + h - 10), 16, fill=col + (255,))
            d.text((20 + 17, 14 + 10), txt, font=f, fill=(255, 255, 255, 255) if clave else OSCURO + (255,))
        else:
            col = AMARILLO if clave else (255, 255, 255)
            d.text((37, 24), txt, font=f, fill=col + (255,), stroke_width=5, stroke_fill=OSCURO + (255,))
        self.cache[key] = img; return img

    def pintar(self, img, t):
        for ini, fin, spr in self.items:
            if ini <= t < fin:
                ult = max((i for i, s in enumerate(spr) if s[5] <= t), default=None)
                for i, (x, an, txt, clave, tm, a) in enumerate(spr):
                    activa = i == ult
                    esc = 1.0
                    if activa:
                        u = (t - a) / 0.14; esc = 1.0 + 0.14 * (1 - abs(1 - 2 * min(u, 1)) ** 2) if u < 1 else 1.06
                        esc = max(1.0, min(1.14, esc)) if u < 1 else 1.04
                    spr_img = self.sprite(txt, clave, activa, tm, esc if activa else 1.0)
                    cx = x + an / 2; cy = self.y + 40
                    img.alpha_composite(spr_img, (int(cx - spr_img.width / 2), int(cy - spr_img.height / 2)))
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
    sal = FINAL / 'XV_reel_v14_voz_manuel.mp4'
    ff(['-i', str(s), '-i', str(a), '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'copy', '-t', f'{TOTAL:.2f}', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB', f'{TOTAL:.1f}s')
    for nom, f, ss, s0, *_ in SC: print(f'{s0:5.2f}  {nom}')


if __name__ == '__main__':
    main()
