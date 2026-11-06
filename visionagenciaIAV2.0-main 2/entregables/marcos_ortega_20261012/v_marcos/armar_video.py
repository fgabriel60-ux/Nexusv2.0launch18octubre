"""Arma el video de Ortega estilo la chica de la Afore: asesor con la voz de Marcos (T1..T3), subtítulos y cierre."""
import subprocess
from pathlib import Path
import av
import imageio_ffmpeg
import numpy as np
from faster_whisper import WhisperModel
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
FUENTE = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
W, H = 1080, 1920
TMP = AQUI / 'tmp_armado'
TMP.mkdir(exist_ok=True)
CRUCE = 0.25
CIERRE = 2.5
TOMAS = ['T1', 'T2', 'T3']


def dur(ruta):
    out = subprocess.run([FF, '-i', str(ruta)], capture_output=True, text=True).stderr
    h, m, s = out.split('Duration: ')[1].split(',')[0].split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)


def palabras(ruta, desfase, modelo):
    c = av.open(str(ruta))
    rs = av.AudioResampler(format='s16', layout='mono', rate=16000)
    a = np.concatenate([x.to_ndarray().ravel() for fr in c.decode(audio=0) for x in rs.resample(fr)]).astype(np.float32) / 32768
    segs, _ = modelo.transcribe(a, language='es', word_timestamps=True, vad_filter=True)
    return [(w.word.strip(), w.start + desfase, w.end + desfase) for s in segs for w in s.words]


def subtitulo(texto, ruta):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FUENTE, 80)
    tw = d.textlength(texto, font=f)
    d.text(((W - tw) / 2, 1300), texto, font=f, fill=(255, 255, 255), stroke_width=7, stroke_fill=(0, 0, 0))
    img.save(ruta)


def cierre(ruta):
    base = Image.new('RGB', (W, H), (12, 24, 52))
    d = ImageDraw.Draw(base)
    def centro(txt, y, tam, color):
        f = ImageFont.truetype(FUENTE, tam)
        d.text(((W - d.textlength(txt, font=f)) / 2, y), txt, font=f, fill=color)
    centro('Soluciones Previsionales', 470, 64, (235, 190, 90))
    centro('ORTEGA', 560, 150, (235, 190, 90))
    centro('SIN ANTICIPOS', 900, 80, (255, 255, 255))
    centro('Pagas cuando recibes tu dinero', 1010, 50, (255, 255, 255))
    fw = ImageFont.truetype(FUENTE, 56)
    txt = 'Escríbenos por WhatsApp'
    a = d.textlength(txt, font=fw) + 120
    d.rounded_rectangle(((W - a) / 2, 1300, (W + a) / 2, 1440), 70, fill=(37, 211, 102))
    d.text(((W - a) / 2 + 60, 1340), txt, font=fw, fill=(255, 255, 255))
    base.save(ruta)


clips = [AQUI / 'clips' / f'{t}.mp4' for t in TOMAS]
dur_c = [dur(c) for c in clips]
inicios = [sum(dur_c[:i]) - i * CRUCE for i in range(len(clips))]
total = sum(dur_c) - (len(clips) - 1) * CRUCE
modelo = WhisperModel('small', device='cpu', compute_type='int8')
lista = []
for i in range(len(clips)):
    lista += palabras(clips[i], inicios[i], modelo)
cierre(TMP / 'cierre.png')

def ffmpeg(args):
    r = subprocess.run([FF, '-v', 'error', '-y', *args], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-1500:])


esc = 'scale=1080:1920:flags=lanczos,setsar=1,fps=30'
n = len(clips)
# 1) base: tomas con cruces + cierre + audio
entradas = sum([['-i', str(c)] for c in clips], []) + ['-loop', '1', '-t', str(CIERRE), '-i', str(TMP / 'cierre.png')]
filtro = ''.join(f'[{i}:v]{esc},format=yuv420p[v{i}];' for i in range(n)) + f'[{n}:v]scale=1080:1920,setsar=1,fps=30,format=yuv420p[vc];'
prev = 'v0'
for i in range(1, n):
    filtro += f'[{prev}][v{i}]xfade=transition=fade:duration={CRUCE}:offset={inicios[i]:.2f}[x{i}];'
    prev = f'x{i}'
filtro += f'[{prev}][vc]xfade=transition=fade:duration=0.4:offset={total - 0.4:.2f}[v];'
audio = '[0:a]'
for i in range(1, n):
    filtro += f'{audio}[{i}:a]acrossfade=d={CRUCE}[a{i}];'
    audio = f'[a{i}]'
filtro += f'{audio}loudnorm=I=-15:TP=-1.5,apad[a]'
largo = total + CIERRE - 0.4
base = TMP / 'base.mp4'
ffmpeg([*entradas, '-filter_complex', filtro, '-map', '[v]', '-map', '[a]', '-t', f'{largo:.2f}',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '16', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', '44100', '-b:a', '192k', str(base)])
# 2) subtítulos en tandas de 20 palabras
for k, (p, a, b) in enumerate(lista):
    subtitulo(p, TMP / f'p{k}.png')
actual = base
for t0 in range(0, len(lista), 20):
    tanda = list(range(t0, min(t0 + 20, len(lista))))
    entradas = ['-i', str(actual)] + sum([['-i', str(TMP / f'p{k}.png')] for k in tanda], [])
    filtro, prev = '', '0:v'
    for j, k in enumerate(tanda):
        p, a, b = lista[k]
        fin = lista[k + 1][1] if k + 1 < len(lista) and lista[k + 1][1] - b < 0.6 else b + 0.25
        filtro += f"[{prev}][{j + 1}:v]overlay=0:0:enable='between(t,{a:.2f},{fin:.2f})'[s{j}];"
        prev = f's{j}'
    filtro = filtro.rstrip(';')
    sig = TMP / f'paso_{t0}.mp4'
    ffmpeg([*entradas, '-filter_complex', filtro, '-map', f'[{prev}]', '-map', '0:a', '-c:v', 'libx264', '-preset', 'fast',
            '-crf', '16', '-pix_fmt', 'yuv420p', '-c:a', 'copy', str(sig)])
    actual = sig
salida = AQUI / 'final' / 'Ortega_Marcos_su_cara_voz.mp4'
salida.parent.mkdir(exist_ok=True)
ffmpeg(['-i', str(actual), '-c:v', 'libx264', '-profile:v', 'main', '-preset', 'slow', '-crf', '21', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', str(salida)])
print(salida, f'{largo:.1f} s', len(lista), 'palabras')
