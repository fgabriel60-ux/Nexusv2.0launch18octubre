"""Manuel Fotografía · XV v17 (v15 con UNA sola end card con el logo NUEVO de Hunab Ku (logo_nuevo_1027.jpg, negro sobre blanco -> alfa por oscuridad, pintado en blanco cálido con brillo dorado), sin endcard animado; subtítulos elegantes: serif Playfair, sin cajas ni mayúsculas, aparición suave; tarjeta final con la misma tipografía): reel v12 con la VOZ REAL de Manuel y las escenas reordenadas según lo que va diciendo.
Voz: nota de WhatsApp (completa para las frases 1-4, toma del cierre para la 5), limpiada (silencios largos fuera, highpass, afftdn, compresión, loudnorm).
Escenas: del v3 (reales y primera mitad), v12 (IA con color) y v8 (IA crudas). Música del v12 por debajo con ducking. Subtítulos palabra por palabra.
Uso: python3 armar_xv_v17.py   (tiempos por palabra de faster_whisper ya fijados abajo; --whisper los recalcula)"""
import subprocess, sys
from pathlib import Path
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
TMP = Path('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/632e0195-4202-422b-a741-74f9ff894c0c/scratchpad/v17'); TMP.mkdir(parents=True, exist_ok=True)
FINAL = AQUI / 'final'
V3, V12 = FINAL / 'XV_reel_v3.mp4', FINAL / 'XV_reel_v12_inicio_v3_fiesta_IA_sin_voz.mp4'
V8 = AQUI / 'v8' / 'clips'
VOZ_C, VOZ_X = AQUI / 'voz_manuel' / 'voz_manuel_completa.ogg', AQUI / 'voz_manuel' / 'voz_manuel_cierre.ogg'
FUENTE = '/workspaces/Nexusv2.0launch18octubre/clientes/_productor/fuentes/PlayfairDisplay[wght].ttf'
FUENTE_IT = '/workspaces/Nexusv2.0launch18octubre/clientes/_productor/fuentes/PlayfairDisplay-Italic[wght].ttf'
W, H, FPS = 720, 1280, 30
LEAD, GAP, XF = 0.5, 0.5, 0.28
END_HOLD, END_DUR = 2.5, 0.0   # la tarjeta se queda 0.9 s tras «fecha» y luego entra el endcard de Hunab Ku
ENDCARD = AQUI.parent / 'Manuel_fotografia' / 'logo' / 'HunabKu_endcard.mp4'

# Frases: (fuente de voz, inicio, fin del recorte, [(palabra, ini, fin) de whisper], chunks de subtítulo [n palabras])
FR = [
    ('C', 1.10, 4.40, [('Una', 1.24, 1.96), ('quinceañera,', 1.96, 2.68), ('un', 3.18, 3.32), ('recuerdo', 3.32, 3.64), ('que', 3.64, 3.86), ('dura.', 3.86, 4.22)], [6]),
    ('C', 5.10, 9.40, [('Aquí', 5.20, 5.34), ('ves', 5.34, 5.66), ('la', 5.66, 5.90), ('luz,', 5.90, 6.34), ('la', 6.94, 7.08), ('sonrisa,', 7.08, 7.72), ('el', 8.34, 8.46), ('vestido', 8.46, 8.82), ('verde.', 8.82, 9.22)], [4, 5]),
    ('C', 10.10, 15.86, [('Después,', 10.20, 10.92), ('la', 11.56, 11.80), ('entrada,', 11.80, 12.12), ('el', 12.98, 13.20), ('giro,', 13.20, 13.62), ('la', 14.06, 14.20), ('emoción', 14.20, 14.56), ('del', 14.56, 14.78), ('salón.', 14.78, 15.66)], [5, 4]),
    ('C', 15.96, 20.45, [('Momentos', 16.06, 16.56), ('reales,', 16.56, 17.62), ('con', 17.72, 17.90), ('un', 17.90, 18.14), ('toque', 18.14, 18.54), ('cinematográfico.', 19.48, 20.20)], [2, 4]),
    ('X', 0.52, 5.80, [('Si', 0.62, 1.18), ('quieres', 1.18, 1.46), ('algo', 1.46, 1.70), ('así', 1.70, 1.96), ('para', 1.96, 2.18), ('tu', 2.18, 2.32), ('hija,', 2.32, 3.32), ('escríbenos', 3.60, 3.88), ('por', 3.88, 4.06), ('WhatsApp', 4.06, 4.44), ('y', 4.44, 4.92), ('agenda', 4.92, 5.12), ('tu', 5.12, 5.30), ('fecha.', 5.30, 5.60)], [4, 3, 3, 4]),
]
# offsets de cada frase en la línea de tiempo de salida
OFF, t = [], LEAD
for _, a, b, _, _ in FR:
    OFF.append(t); t += (b - a) + GAP
T_VOZ = t - GAP
T_END = T_VOZ + END_HOLD
TOTAL = T_END


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
    ('tarjeta', V8 / 'M8.mp4', 0.0, OFF[4] - 0.1, 1, 0),         # frase 5: cierre
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
        ent += ['-ss', f'{ss}', '-t', f'{L + 0.1:.2f}', '-i', str(f)]
        ef = ''
        if str(f).startswith(str(V8)): ef = ',eq=contrast=1.05:saturation=1.1,vignette=PI/5'
        if nom == 'tarjeta': ef = ',eq=brightness=-0.36:contrast=1.05:saturation=0.85,gblur=sigma=4,vignette=PI/4,setpts=1.4*PTS'
        bl = ''
        if bi: bl += f",gblur=sigma=14:enable='lt(t,{XF * 1.4:.2f})'"
        if bo: bl += f",gblur=sigma=14:enable='gt(t,{L - XF * 1.4:.2f})'"
        tp = f',tpad=stop_mode=clone:stop_duration=4' if nom == 'tarjeta' else ''
        fl += f'[{i}:v]{norm}{ef}{tp},trim=duration={L:.3f},setpts=PTS-STARTPTS{bl},fps={FPS},settb=AVTB[c{i}];'
    prev = 'c0'
    for i in range(1, n):
        fl += f'[{prev}][c{i}]xfade=transition=fade:duration={XF}:offset={SC[i][3] - XF / 2:.3f}[x{i}];'; prev = f'x{i}'
    fl += f'[{prev}]tpad=stop_mode=clone:stop_duration=3[vf];'; prev = 'vf'
    out = TMP / 'mudo.mp4'
    ff(ent + ['-filter_complex', fl.rstrip(';'), '-map', f'[{prev}]', '-t', f'{TOTAL:.2f}', '-an', '-c:v', 'libx264', '-crf', '15', '-preset', 'fast', '-pix_fmt', 'yuv420p', str(out)])
    return out


# ---------- subtítulos ----------
CLAVE = {'quinceañera', 'recuerdo', 'luz', 'sonrisa', 'vestido', 'verde', 'giro', 'emoción', 'cinematográfico'}
CALIDO, DORADO = (255, 248, 238), (232, 201, 138)
TAM, ANCHO_MAX, SUBE, FADE = 54, 640, 7, 0.28


def fnt(it, t):
    f = ImageFont.truetype(FUENTE_IT if it else FUENTE, t); f.set_variation_by_name('Italic' if it else 'Regular'); return f


class Subs:
    """Frase (o media frase) centrada en 1-2 líneas, mismo tamaño siempre. Cada palabra entra con fundido y leve subida; las pendientes al 35 %.
    Claves en Playfair Italic dorado suave; sombra difusa suave y un degradado muy sutil abajo."""
    def __init__(self, y=0.80):
        self.items = []; self.cache = {}; self.fonts = {}; self.y = y; self.g = 0.0
        self.grad = self._degradado()
        for k, (_, a, b, ws, chunks) in enumerate(FR):
            pos = 0; grupos = []
            for c in chunks:
                grupos.append(ws[pos:pos + c]); pos += c
            for gi, g in enumerate(grupos):
                ini = V(k, g[0][1]) - 0.2
                fin = V(k, grupos[gi + 1][0][1]) - 0.2 if gi + 1 < len(grupos) else V(k, g[-1][2]) + 0.6
                ps = [(w[0], w[0].rstrip('.,').lower() in CLAVE, V(k, w[1])) for w in g]
                self.items.append((ini, fin, self.layout(ps)))

    def f(self, it):
        if it not in self.fonts: self.fonts[it] = fnt(it, TAM)
        return self.fonts[it]

    def ancho(self, p): return self.f(p[1]).getlength(p[0])

    def layout(self, ps):
        esp = TAM * 0.27
        def w_de(l): return sum(self.ancho(p) for p in l) + esp * (len(l) - 1)
        # corte natural en coma/punto si da 2 líneas que caben; si no, reparto voraz
        lineas = None
        for i, p in enumerate(ps[:-1]):
            if p[0][-1] in ',.' :
                a, b = ps[:i + 1], ps[i + 1:]
                if w_de(a) <= ANCHO_MAX and w_de(b) <= ANCHO_MAX and (lineas is None or abs(w_de(a) - w_de(b)) < abs(w_de(lineas[0]) - w_de(lineas[1]))): lineas = [a, b]
        if lineas is None:
            if w_de(ps) <= ANCHO_MAX: lineas = [ps]
            else:
                mejor = None
                for i in range(1, len(ps)):
                    a, b = ps[:i], ps[i:]; d = max(w_de(a), w_de(b))
                    if mejor is None or d < mejor[0]: mejor = (d, [a, b])
                lineas = mejor[1]
        lh = TAM * 1.38; top = H * self.y - lh * len(lineas) / 2; out = []
        for li, l in enumerate(lineas):
            x = (W - w_de(l)) / 2
            for p in l:
                out.append((x, top + li * lh, p)); x += self.ancho(p) + esp
        return out

    def sprite(self, txt, it, alfa):
        key = (txt, it, round(alfa * 20))
        if key in self.cache: return self.cache[key]
        f = self.f(it); w = int(f.getlength(txt)) + 60; h = int(TAM * 1.7)
        sh = Image.new('L', (w, h), 0); ImageDraw.Draw(sh).text((30, 22 + 3), txt, font=f, fill=int(255 * 0.55 * alfa)); sh = sh.filter(ImageFilter.GaussianBlur(7))
        img = Image.new('RGBA', (w, h), (0, 0, 0, 0)); sp = Image.new('RGBA', (w, h), (0, 0, 0, 0)); sp.putalpha(sh); img = Image.alpha_composite(img, sp)
        tx = Image.new('RGBA', (w, h), (0, 0, 0, 0)); col = DORADO if it else CALIDO
        ImageDraw.Draw(tx).text((30, 22), txt, font=f, fill=col + (int(255 * alfa),)); img = Image.alpha_composite(img, tx)
        self.cache[key] = img; return img

    def _degradado(self):
        a = np.zeros((H, W), np.float32); y0 = int(H * 0.60)
        a[y0:] = np.linspace(0, 1, H - y0)[:, None] ** 1.6 * 0.38
        return a

    def pintar(self, img, t):
        act = next(((ini, fin, spr) for ini, fin, spr in self.items if ini <= t < fin), None)
        self.g += ((1.0 if act else 0.0) - self.g) * 0.12
        if self.g > 0.01:
            arr = np.asarray(img.convert('RGB'), np.float32) * (1 - self.grad[..., None] * self.g)
            img.paste(Image.fromarray(arr.astype(np.uint8)).convert('RGBA'))
        if not act: return
        ini, fin, spr = act
        sal = min(1.0, max(0.0, (fin - t) / 0.25))     # salida suave del bloque
        for x, y, (txt, it, ts) in spr:
            u = min(1.0, max(0.0, (t - ts) / FADE)); u = u * u * (3 - 2 * u)
            alfa = (0.35 + 0.65 * u) * (min(1.0, (t - ini) / 0.2) if t - ini < 0.2 else 1.0) * sal
            if alfa <= 0.01: continue
            s = self.sprite(txt, it, alfa)
            img.alpha_composite(s, (int(x - 30), int(y - 22 + SUBE * (1 - u))))


class Tarjeta:
    """UNA sola end card: logo real de Manuel (perfil.jpg, mismo recorte que usa endcard.py) + texto Playfair, sobre la aérea del salón oscurecida."""
    @staticmethod
    def prepara_logo(ancho_panel):
        """Logo ORIGINAL (logo_nuevo_1027.jpg, negro con su bisel, sin invertir) multiplicado sobre un panel marfil #FAF5EC de esquinas redondeadas, ~95 % opaco, con sombra suave."""
        im = Image.open(AQUI.parent / 'Manuel_fotografia' / 'logo' / 'logo_nuevo_1027.jpg').convert('L')
        a = np.asarray(im, np.float32); ys, xs = np.where(a < 200); pad = 10
        x0, x1, y0, y1 = max(0, xs.min() - pad), xs.max() + pad, max(0, ys.min() - pad), ys.max() + pad
        rec = a[y0:y1, x0:x1] / 255.0; Hh, Ww = rec.shape
        marg = 46; anch_logo = ancho_panel - 2 * marg; k = anch_logo / Ww
        rec = np.asarray(Image.fromarray((rec * 255).astype(np.uint8)).resize((anch_logo, int(Hh * k)), Image.LANCZOS), np.float32) / 255
        hp = rec.shape[0] + 2 * marg
        marfil = np.array((250, 245, 236), np.float32)
        panel = np.ones((hp, ancho_panel, 3), np.float32) * marfil
        panel[marg:marg + rec.shape[0], marg:marg + anch_logo] *= rec[..., None]      # blanco -> marfil, negro y bisel intactos
        mask = Image.new('L', (ancho_panel, hp), 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, ancho_panel - 1, hp - 1), 28, fill=int(255 * 0.95))
        pan = Image.fromarray(panel.astype(np.uint8)).convert('RGBA'); pan.putalpha(mask)
        pad2 = 50; out = Image.new('RGBA', (ancho_panel + 2 * pad2, hp + 2 * pad2), (0, 0, 0, 0))
        sh = Image.new('L', out.size, 0); ImageDraw.Draw(sh).rounded_rectangle((pad2, pad2 + 10, pad2 + ancho_panel, pad2 + 10 + hp), 28, fill=130); sh = sh.filter(ImageFilter.GaussianBlur(16))
        sp = Image.new('RGBA', out.size, (0, 0, 0, 0)); sp.putalpha(sh); out.alpha_composite(sp); out.alpha_composite(pan, (pad2, pad2))
        return out

    def __init__(self):
        self.logo = self.prepara_logo(int(W * 0.88))
        self.t0 = OFF[4] + 0.0; self.t1 = TOTAL
        def tx(txt, it, t, col, y, sp=0):
            f = ImageFont.truetype(FUENTE_IT if it else FUENTE, t); f.set_variation_by_name('Italic' if it else 'Regular')
            w = int(sum(f.getlength(c) + sp for c in txt)); img = Image.new('RGBA', (W, int(t * 1.9)), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
            sh = Image.new('L', img.size, 0); x = (W - w) / 2; xs = x
            for c in txt: ImageDraw.Draw(sh).text((x, t * 0.4 + 3), c, font=f, fill=140); x += f.getlength(c) + sp
            sh = sh.filter(ImageFilter.GaussianBlur(7)); sp_ = Image.new('RGBA', img.size, (0, 0, 0, 0)); sp_.putalpha(sh); img = Image.alpha_composite(img, sp_); d = ImageDraw.Draw(img)
            x = xs
            for c in txt: d.text((x, t * 0.4), c, font=f, fill=col + (255,)); x += f.getlength(c) + sp
            return img, y
        self.capas = [tx('Agenda tu fecha', True, 64, CALIDO, 0.60)]
        b = Image.new('RGBA', (W, 140), (0, 0, 0, 0)); d = ImageDraw.Draw(b)
        d.rounded_rectangle((120, 36, W - 120, 100), 32, outline=DORADO + (230,), width=2)
        f = ImageFont.truetype(FUENTE, 30); f.set_variation_by_name('Regular'); tt = 'Escríbenos por WhatsApp'; w = f.getlength(tt) + 1.2 * len(tt)
        x = (W - w) / 2
        for c in tt: d.text((x, 50), c, font=f, fill=CALIDO + (255,)); x += f.getlength(c) + 1.2
        self.boton = (b, 0.68)

    def pintar(self, img, t):
        if t < self.t0: return
        u = lambda a, d: min(1.0, max(0.0, (t - self.t0 - a) / d))
        # logo: fundido y escala 0.96 -> 1
        ul = u(0.15, 1.0); ul = ul * ul * (3 - 2 * ul)
        if ul > 0:
            e = 0.96 + 0.04 * ul; lg = self.logo.resize((int(self.logo.width * e), int(self.logo.height * e)), Image.LANCZOS)
            lg.putalpha(lg.getchannel('A').point(lambda v: int(v * ul)))
            img.alpha_composite(lg, (int(W / 2 - lg.width / 2), int(H * 0.34 - lg.height / 2)))
        for k, (cap, y) in enumerate(self.capas + [self.boton]):
            ak = u(0.9 + 0.2 * k, 0.6)
            if ak <= 0: continue
            c = cap.copy(); c.putalpha(c.getchannel('A').point(lambda v: int(v * ak)))
            img.alpha_composite(c, (0, int(H * y - cap.height / 2 + 8 * (1 - ak))))


def montar(mudo, vozwav):
    subs = Subs(); tarj = Tarjeta()
    dec = subprocess.Popen([FF, '-v', 'error', '-i', str(mudo), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    sin_audio = TMP / 'con_subs.mp4'
    enc = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-profile:v', 'main', '-pix_fmt', 'yuv420p',
                            '-crf', '22', '-preset', 'slow', str(sin_audio)], stdin=subprocess.PIPE)
    n = 0; sz = W * H * 3
    while True:
        b = dec.stdout.read(sz)
        if len(b) < sz: break
        img = Image.frombuffer('RGB', (W, H), b).convert('RGBA')
        tarj.pintar(img, n / FPS); subs.pintar(img, n / FPS)
        enc.stdin.write(img.convert('RGB').tobytes()); n += 1
    enc.stdin.close(); enc.wait(); dec.wait()
    return sin_audio


def audio_final(vozwav):
    """música del v12: calma (0-9.6) → fiesta (desde 13.0), con ducking por la voz"""
    t_cambio = V(2, 10.0) - 0.6
    mus = (f'[1:a]aresample=44100,atrim=0:{t_cambio + 1.4:.2f},afade=t=out:st={t_cambio - 0.2:.2f}:d=1.6,volume=0.8[m1];'
           f'[2:a]aresample=44100,atrim=13.0:{13.0 + TOTAL - t_cambio + 1:.2f},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.8,volume=1.0,adelay={int(t_cambio * 1000)}|{int(t_cambio * 1000)}[m2];'
           f'[m1][m2]amix=inputs=2:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},loudnorm=I=-19:TP=-2,afade=t=in:st=0:d=0.8[m];')
    duck = (f'[0:a]apad=whole_dur={TOTAL:.2f},asplit=2[vk][vv];[m][vk]sidechaincompress=threshold=0.02:ratio=9:attack=15:release=450:makeup=1[md];'
            f'[md][vv]amix=inputs=2:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},afade=t=out:st={TOTAL - 2.2:.2f}:d=2.2,alimiter=limit=0.95,loudnorm=I=-14:TP=-1.5[a]')
    out = TMP / 'audio_final.m4a'
    ff(['-i', str(vozwav), '-i', str(V12), '-i', str(V12), '-filter_complex', mus + duck, '-map', '[a]', '-ac', '2', '-ar', '44100', '-c:a', 'aac', '-b:a', '160k', str(out)])
    return out


def main():
    v = voz(); m = video_mudo(); s = montar(m, v); a = audio_final(v)
    sal = FINAL / 'XV_reel_v17_FINAL_manuel.mp4'
    ff(['-i', str(s), '-i', str(a), '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'copy', '-t', f'{TOTAL:.2f}', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB', f'{TOTAL:.1f}s')
    for nom, f, ss, s0, *_ in SC: print(f'{s0:5.2f}  {nom}')


if __name__ == '__main__':
    main()
