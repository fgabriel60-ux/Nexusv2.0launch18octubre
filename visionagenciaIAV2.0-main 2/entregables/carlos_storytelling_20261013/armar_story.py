"""Storytelling de Carlos sobre Mariano: tú (S1, S3, S6) + b-roll de Mariano (S2, S4, S5), voz s2-pro, subtítulos por palabra."""
import subprocess
from pathlib import Path
import av, imageio_ffmpeg, numpy as np
from faster_whisper import WhisperModel
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = Path(__file__).resolve().parent
E = AQUI.parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
FUENTE = str(E / 'modelos_modal' / 'fuentes' / 'Montserrat.ttf')
W, H = 1080, 1920
TMP = AQUI / 'tmp'; TMP.mkdir(exist_ok=True); (AQUI / 'final').mkdir(exist_ok=True)
esc = 'scale=1080:1920:flags=lanczos,setsar=1,fps=30,format=yuv420p'


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1500:])


def dur(p):
    o = subprocess.run([FF, '-i', str(p)], capture_output=True, text=True).stderr
    h, m, s = o.split('Duration: ')[1].split(',')[0].split(':'); return int(h) * 3600 + int(m) * 60 + float(s)


def fuente(t, peso='Black'):
    f = ImageFont.truetype(FUENTE, t); f.set_variation_by_name(peso); return f


modelo = WhisperModel('small', device='cpu', compute_type='int8')


def palabras(p):
    c = av.open(str(p)); rs = av.AudioResampler(format='s16', layout='mono', rate=16000)
    a = np.concatenate([x.to_ndarray().ravel() for fr in c.decode(audio=0) for x in rs.resample(fr)]).astype(np.float32) / 32768
    s, _ = modelo.transcribe(a, language='es', word_timestamps=True, vad_filter=True)
    return [(w.word.strip(), w.start, w.end) for q in s for w in q.words]


def png(ruta, txt, y, tam=84, color=(255, 255, 255), peso='Black'):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    while d.textlength(txt, font=fuente(tam, peso)) > W - 100: tam -= 4
    f = fuente(tam, peso)
    d.text(((W - d.textlength(txt, font=f)) / 2, y), txt, font=f, fill=color, stroke_width=7, stroke_fill=(0, 0, 0)); img.save(ruta)


def tarjeta_cita(ruta):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle((80, 1180, W - 80, 1520), 36, fill=(255, 255, 255, 240))
    d.text((130, 1215), 'Mariano', font=fuente(40, 'ExtraBold'), fill=(7, 94, 84))
    for k, l in enumerate(['"Estoy realmente sorprendido', 'por todo el avance en', 'tan solo 3 meses."']):
        d.text((130, 1280 + k * 66), l, font=fuente(50, 'Bold'), fill=(20, 20, 20))
    img.save(ruta)


seg = []
def toma_carlos(n):
    w = AQUI / 'voz' / f'T{n}.wav'; fin = palabras(w)[-1][2] + 0.25; s = TMP / f'{n}.mp4'
    ff(['-i', str(AQUI / 'clips' / f'{n}.mp4'), '-i', str(w), '-filter_complex', f'[0:v]{esc},tpad=stop_mode=clone:stop_duration=2[v];[1:a]apad[a]',
        '-map', '[v]', '-map', '[a]', '-t', f'{fin:.2f}', '-c:v', 'libx264', '-preset', 'fast', '-crf', '17', '-c:a', 'aac', '-ar', '48000', '-ac', '2', str(s)])
    seg.append((n, s, w))


def broll(n, video=None, imagen=None, inicio=0.0, extra=None):
    w = AQUI / 'voz' / f'T{n}.wav'; fin = palabras(w)[-1][2] + 0.3; s = TMP / f'{n}.mp4'
    if video:
        entr = ['-ss', f'{inicio}', '-i', str(video)]
        v = f'[0:v]{esc},eq=brightness=-0.05,tpad=stop_mode=clone:stop_duration=20[b]'
    else:
        entr = ['-loop', '1', '-i', str(imagen)]
        v = (f"[0:v]scale=-2:1500,setsar=1,format=yuv420p,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=0x101418,"
             f"zoompan=z='min(zoom+0.0006,1.08)':d=1:s=1080x1920:fps=30[b]")
    entr += ['-i', str(w)]
    f = v + ';'
    if extra:
        entr += ['-i', str(extra)]; f += '[b][2:v]overlay=0:0[b2];'; lab = 'b2'
    else:
        lab = 'b'
    f += f'[{lab}]format=yuv420p[v];[1:a]apad[a]'
    ff([*entr, '-filter_complex', f, '-map', '[v]', '-map', '[a]', '-t', f'{fin:.2f}', '-c:v', 'libx264', '-preset', 'fast', '-crf', '17',
        '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', '48000', '-ac', '2', str(s)])
    seg.append((n, s, w))


tarjeta_cita(TMP / 'cita.png')
png(TMP / 'tres_meses.png', '3 MESES SIN RESULTADOS', 260, 80, (255, 90, 90))
toma_carlos('S1')
broll('S2', video=E / 'mariano_helicoptero_20261013' / 'referencia' / 'mariano_sanmarino.mp4', inicio=6, extra=TMP / 'tres_meses.png')
toma_carlos('S3')
broll('S4', imagen=E / 'carlos_vision_20261013' / 'referencia' / 'numeros_campana.jpg')
broll('S5', video=E / 'mariano_helicoptero_20261013' / 'final' / 'Mariano_helicoptero_v2_whatsapp.mp4', inicio=0.5, extra=TMP / 'cita.png')
toma_carlos('S6')

lista = TMP / 'lista.txt'; lista.write_text(''.join(f"file '{s}'\n" for _, s, _ in seg))
base = TMP / 'base.mp4'
ff(['-f', 'concat', '-safe', '0', '-i', str(lista), '-c:v', 'libx264', '-preset', 'fast', '-crf', '17', '-pix_fmt', 'yuv420p', '-c:a', 'aac', str(base)])
capas, t, k = [], 0.0, 0
for n, s, w in seg:
    for p, a, b in palabras(w):
        r = TMP / f'p{k}.png'; png(r, p, 1460 if n != 'S5' else 1580); capas.append((r, t + a, t + b + 0.12)); k += 1
    t += dur(s)
actual = base
for t0 in range(0, len(capas), 18):
    tanda = capas[t0:t0 + 18]
    entr = ['-i', str(actual)] + sum([['-i', str(r)] for r, _, _ in tanda], [])
    f, prev = '', '0:v'
    for j, (_, a, b) in enumerate(tanda):
        f += f"[{prev}][{j + 1}:v]overlay=0:0:enable='between(t,{a:.2f},{b:.2f})'[s{j}];"; prev = f's{j}'
    sig = TMP / f'paso_{t0}.mp4'
    ff([*entr, '-filter_complex', f.rstrip(';'), '-map', f'[{prev}]', '-map', '0:a', '-c:v', 'libx264', '-preset', 'fast', '-crf', '17',
        '-pix_fmt', 'yuv420p', '-c:a', 'copy', str(sig)]); actual = sig
sal = AQUI / 'final' / 'Carlos_Storytelling_Mariano.mp4'
ff(['-i', str(actual), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p',
    '-preset', 'slow', '-crf', '21', '-maxrate', '2800k', '-bufsize', '5600k', '-c:a', 'aac', '-af', 'loudnorm=I=-15:TP=-1.5', '-ar', '44100',
    '-ac', '2', '-b:a', '128k', '-movflags', '+faststart', str(sal)])
print(sal, f'{t:.1f} s')
