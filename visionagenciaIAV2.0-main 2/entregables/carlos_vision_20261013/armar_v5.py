"""Reel de Carlos v4 (720x1280, todo compuesto cuadro a cuadro):
gancho con sticker (se ve más tiempo y se quema) → métricas visibles desde el inicio → testimonio de Mariano
(su video chico a la izquierda de Carlos + sticker de nota de voz de WhatsApp; ambos se despegan al terminar el audio)
→ IA correcta → CTA 5 clientes. Clips de cámara fija (sin zooms), cortes justo al terminar cada voz, subtítulos con el guion
(no con lo que 'oye' Whisper) y sin palabras encimadas."""
import subprocess
from pathlib import Path
import av, imageio_ffmpeg, numpy as np
from faster_whisper import WhisperModel
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
NEG = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
NOR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
W, H, FPS = 720, 1280, 30
TMP = AQUI / 'tmp_v5'; TMP.mkdir(exist_ok=True)
(AQUI / 'final').mkdir(exist_ok=True)
HELI = AQUI.parent / 'mariano_helicoptero_20261013' / 'final' / 'Mariano_helicoptero_v2_whatsapp.mp4'
NUMEROS = AQUI / 'fotos' / '02_sin_texto.jpg'
MARIANO_WAV = TMP / 'mariano.wav'
PAUSA_STICKER = 1.4

GUION = {
    'P1': 'Conseguir mensajes ya no es un problema, ni hacer videos de la máxima calidad.',
    'P2': 'Y Facebook nos confirma que la campaña será excepcional antes de sacarla.',
    'P4': 'Sí se logra con inteligencia artificial, pero casi nadie está usando la correcta.',
    'P5': 'Busco clientes que ya hayan corrido publicidad antes. Con la demanda que hay, no puedo detenerme a arreglar las '
          'fallas de Facebook. Mándame un mensaje y agendemos una llamada. Solo acepto cinco clientes por semana.',
}
# Mariano: transcripción revisada (Whisper medium) de su nota de voz recortada
MARIANO_TXT = ('Pues solo para avisarte que ya está dando el resultado la campaña que acabas de subir. '
               'Es lo que funciona y ya llegaron los primeros tres mensajitos. Muchas gracias y muchas felicidades.')


def ff(args):
    r = subprocess.run([FF, '-v', 'error', '-y', *args], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-2000:])


def dur(ruta):
    out = subprocess.run([FF, '-i', str(ruta)], capture_output=True, text=True).stderr
    h, m, s = out.split('Duration: ')[1].split(',')[0].split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)


def pcm(ruta):
    c = av.open(str(ruta)); rs = av.AudioResampler(format='s16', layout='mono', rate=16000)
    return np.concatenate([x.to_ndarray().ravel() for fr in c.decode(audio=0) for x in rs.resample(fr)]).astype(np.float32) / 32768


modelo = WhisperModel('small', device='cpu', compute_type='int8')


def span_voz(ruta):
    """(inicio, fin) del habla según Whisper; sólo se usa para los tiempos, no para el texto."""
    segs, _ = modelo.transcribe(pcm(ruta), language='es', word_timestamps=True, vad_filter=True)
    ws = [w for s in segs for w in s.words]
    return ws[0].start, ws[-1].end


def reparte(texto, t0, t1):
    """Reparte las palabras del guion entre t0 y t1 en proporción a su largo."""
    pal = texto.split()
    pesos = np.array([len(p.strip('.,¡!¿?')) + 2 for p in pal], float)
    cortes = t0 + (t1 - t0) * np.concatenate([[0], np.cumsum(pesos)]) / pesos.sum()
    return [(p, cortes[i], cortes[i + 1]) for i, p in enumerate(pal)]


# ---------- 1. segmentos: (nombre, video, audio, inicio_video_s, duración, palabras) ----------
seg = []
# P1: clip con su propia voz; el primer cuadro se sostiene PAUSA_STICKER s para que se vea el sticker antes de quemarse
a0, a1 = span_voz(AQUI / 'clips' / 'P1.mp4')
d1 = PAUSA_STICKER + a1 + 0.25
seg.append(dict(n='P1', vid=AQUI / 'clips' / 'P1.mp4', aud=AQUI / 'clips' / 'P1.mp4', pausa=PAUSA_STICKER, d=d1,
                pal=reparte(GUION['P1'], PAUSA_STICKER + a0, PAUSA_STICKER + a1)))
for n, v, w in [('P2', 'clips_v3/P2.mp4', 'voz/TC2.wav'), ('P4', 'clips_v3/P4.mp4', 'voz/TC3.wav')]:
    b0, b1 = span_voz(AQUI / w)
    seg.append(dict(n=n, vid=AQUI / v, aud=AQUI / w, pausa=0, d=b1 + 0.25, pal=reparte(GUION[n], b0, b1)))
lm = dur(MARIANO_WAV)
m0, m1 = span_voz(MARIANO_WAV)
seg.insert(2, dict(n='P3', vid=AQUI / 'clips_escucha' / 'PL.mp4', aud=MARIANO_WAV, pausa=0, d=lm,
                   pal=reparte(MARIANO_TXT, m0, m1)))
b0, b1 = span_voz(AQUI / 'voz/TC4.wav')
seg.append(dict(n='P5', vid=AQUI / 'clips_v3/P5.mp4', aud=AQUI / 'voz/TC4.wav', pausa=0, d=b1 + 0.25, pal=reparte(GUION['P5'], b0, b1)))
t = 0.0
for s in seg:
    s['t0'] = t; t += s['d']
TOTAL = t
print({s['n']: round(s['d'], 2) for s in seg}, round(TOTAL, 1), 's')

# ---------- 2. audio ----------
partes = []
for i, s in enumerate(seg):
    p = TMP / f"aud_{s['n']}.wav"
    ret = int(s['pausa'] * 1000)
    voz = ("pan=mono|c0=0.5*c0+0.5*c1,highpass=f=85,afftdn=nr=12:nf=-38,equalizer=f=220:t=q:w=1.2:g=1.5,"
           "equalizer=f=3200:t=q:w=1.0:g=2.5,equalizer=f=7500:t=q:w=2:g=-2.5,acompressor=threshold=-22dB:ratio=3:attack=8:release=120:makeup=3,"
           "alimiter=limit=0.9,")
    ff(['-i', str(s['aud']), '-af', voz + (f"adelay={ret}|{ret},apad=whole_dur={s['d']:.3f}" if ret else f"apad=whole_dur={s['d']:.3f}"),
        '-t', f"{s['d']:.3f}", '-ar', '48000', '-ac', '2', str(p)])
    partes.append(p)
lista = TMP / 'aud_lista.txt'; lista.write_text(''.join(f"file '{p}'\n" for p in partes))
audio = TMP / 'audio_total.wav'
ff(['-f', 'concat', '-safe', '0', '-i', str(lista), '-c', 'copy', str(audio)])

# ---------- 3. cuadros ----------
def frames(ruta, inicio_clon=0.0):
    """Cuadros 720x1280 RGB; repite el primer cuadro inicio_clon s y el último si el clip se acaba."""
    c = av.open(str(ruta)); gen = (fr.to_image().convert('RGB').resize((W, H), Image.LANCZOS) for fr in c.decode(video=0))
    primero = next(gen)
    for _ in range(int(round(inicio_clon * FPS))):
        yield primero
    yield primero
    ultimo = primero
    for im in gen:
        ultimo = im; yield im
    while True:
        yield ultimo


def fuente(tam, neg=True):
    return ImageFont.truetype(NEG if neg else NOR, tam)


def png_texto(texto, tam=64, color=(255, 255, 255)):
    img = Image.new('RGBA', (W, 110), (0, 0, 0, 0)); d = ImageDraw.Draw(img); f = fuente(tam)
    while d.textlength(texto, font=f) > W - 70:
        tam -= 4; f = fuente(tam)
    d.text(((W - d.textlength(texto, font=f)) / 2, 20), texto, font=f, fill=color, stroke_width=6, stroke_fill=(0, 0, 0))
    return img


cache_txt = {}
def palabra_img(p):
    if p not in cache_txt:
        cache_txt[p] = png_texto(p)
    return cache_txt[p]


# tarjeta de métricas (mitad de arriba de la captura)
num = Image.open(NUMEROS).convert('RGB'); nw, nh = num.size
tarjeta = num.crop((0, 0, nw, int(nh * 0.52))); tw = 620; tarjeta = tarjeta.resize((tw, int(tw * tarjeta.height / tarjeta.width)), Image.LANCZOS)
card = Image.new('RGBA', (tw + 12, tarjeta.height + 12), (0, 0, 0, 0))
ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 22, fill=(37, 211, 102, 255))
mask = Image.new('L', tarjeta.size, 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, tarjeta.width - 1, tarjeta.height - 1), 18, fill=255)
card.paste(tarjeta, (6, 6), mask)
CARD_XY = ((W - card.width) // 2, 770)

# sticker del video de Mariano
MW = 206
heli_gen = frames(HELI)
def sticker_video(frame):
    v = frame.resize((MW, int(MW * 16 / 9)), Image.LANCZOS)
    g = Image.new('RGBA', (MW + 14, v.height + 74), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    d.rounded_rectangle((0, 0, g.width - 1, v.height + 13), 20, fill=(15, 15, 15, 235))
    m = Image.new('L', v.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, v.width - 1, v.height - 1), 16, fill=255)
    g.paste(v.convert('RGBA'), (7, 7), m)
    d.text((8, v.height + 20), 'Mariano Herrera', font=fuente(21), fill=(255, 255, 255))
    d.text((8, v.height + 46), 'cliente · San Marino', font=fuente(17, False), fill=(225, 225, 225))
    return g

rng = np.random.default_rng(7); BARRAS = (0.25 + 0.75 * rng.random(24)).tolist()
def sticker_nota(avance, seg_txt):
    g = Image.new('RGBA', (360, 96), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    d.rounded_rectangle((3, 8, 357, 94), 24, fill=(0, 0, 0, 90))
    d.rounded_rectangle((0, 2, 354, 88), 24, fill=(0, 92, 75, 255))
    d.ellipse((10, 12, 76, 78), fill=(120, 130, 140)); d.text((24, 31), 'MH', font=fuente(24), fill=(255, 255, 255))
    d.polygon([(92, 32), (92, 64), (116, 48)], fill=(230, 240, 235))
    for b, alto in enumerate(BARRAS):
        h = int(alto * 40); xx = 130 + b * 9
        d.rounded_rectangle((xx, 45 - h // 2, xx + 4, 45 + h // 2), 2, fill=(83, 189, 235) if b / len(BARRAS) <= avance else (180, 200, 195))
    d.text((130, 66), f'0:{seg_txt:02d}', font=fuente(17, False), fill=(220, 235, 230))
    return g


def ease(x):
    x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)


def pegar_animado(base, spr, xy, entra, sale, t, pivote):
    """Sticker que 'pop' al entrar y se despega (gira desde una esquina, sube y se desvanece) al salir."""
    x, y = xy
    if t < entra:
        return base
    pe = ease((t - entra) / 0.30)
    ps = ease((t - sale) / 0.55) if t >= sale else 0.0
    if ps >= 1:
        return base
    esc = (0.55 + 0.45 * pe + 0.06 * np.sin(pe * np.pi)) * (1 - 0.22 * ps)
    w, h = spr.size
    img = spr.resize((max(2, int(w * esc)), max(2, int(h * esc))), Image.LANCZOS)
    if ps > 0:
        img = img.rotate(24 * ps, resample=Image.BICUBIC, expand=True)
        a = img.getchannel('A').point(lambda v: int(v * (1 - ps))); img.putalpha(a)
    cx = x + w / 2 - 70 * ps; cy = y + h / 2 - 110 * ps
    base.alpha_composite(img, (int(cx - img.width / 2), int(cy - img.height / 2)))
    return base


# ---------- 4. render ----------
salida_mudo = TMP / 'video_mudo.mp4'
proc = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                         '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', str(salida_mudo)], stdin=subprocess.PIPE)
n_total = int(round(TOTAL * FPS))
fuentes = {s['n']: frames(s['vid'], s['pausa']) for s in seg}
P3 = next(s for s in seg if s['n'] == 'P3'); T3A = P3['t0']; T3B = P3['t0'] + P3['d']
SAL_NOTA = T3B - 0.7          # el sticker se despega cuando el audio termina
SAL_VID = T3B - 0.7
P5 = next(s for s in seg if s['n'] == 'P5')
P2 = next(s for s in seg if s['n'] == 'P2')
CARD_A, CARD_B = 0.5, P2['t0'] + P2['d']       # métricas visibles desde el inicio y hasta que cierra la frase de Facebook
heli_prev = None
for k in range(n_total):
    tt = k / FPS
    s = next(x for x in seg if x['t0'] <= tt < x['t0'] + x['d'] or x is seg[-1])
    base = next(fuentes[s['n']]).convert('RGBA')
    if False:  # v5: sin tarjeta de métricas
        pc = ease((tt - CARD_A) / 0.35); pf = 1 - ease((tt - (CARD_B - 0.3)) / 0.3)
        c = card.copy(); c.putalpha(c.getchannel('A').point(lambda v: int(v * pc * pf)))
        base.alpha_composite(c, CARD_XY)
    if s['n'] == 'P3':
        frame_h = next(heli_gen)
        rel = tt - T3A
        pegar_animado(base, sticker_video(frame_h), (12, 300), T3A + 0.15, SAL_VID, tt, 'tl')
        pegar_animado(base, sticker_nota(min(1, rel / P3['d']), int(rel)), (14, 740), T3A + 0.35, SAL_NOTA, tt, 'bl')
    # subtítulos: una palabra a la vez, sin encimarse
    pal = s['pal']
    for i, (p, a, b) in enumerate(pal):
        fin = pal[i + 1][1] if i + 1 < len(pal) else b + 0.3
        if s['t0'] + a <= tt < s['t0'] + fin:
            base.alpha_composite(palabra_img(p), (0, 1090 if s['n'] != 'P3' else 1090))
            break
    if s is P5 and tt >= TOTAL - 3.2:
        base.alpha_composite(png_texto('SOLO 5 CLIENTES POR SEMANA', 56, (255, 214, 64)), (0, 120))
    proc.stdin.write(np.asarray(base.convert('RGB')).tobytes())
proc.stdin.close(); proc.wait()

salida = AQUI / 'final' / 'Carlos_VisionAgencia_v5.mp4'
ff(['-i', str(salida_mudo), '-i', str(audio), '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1',
    '-pix_fmt', 'yuv420p', '-preset', 'slow', '-crf', '21', '-maxrate', '2800k', '-bufsize', '5600k', '-c:a', 'aac',
    '-af', 'loudnorm=I=-14:TP=-1.5:LRA=7', '-ar', '44100', '-ac', '2', '-b:a', '192k', '-shortest', '-movflags', '+faststart', str(salida)])
print(salida, f'{TOTAL:.1f} s', salida.stat().st_size // 1024, 'KB')
