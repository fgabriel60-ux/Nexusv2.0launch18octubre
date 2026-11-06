"""Arma el reel de Omar: 2 clips hablando (MiniMax H3) + subtítulos palabra por palabra + tarjeta final con WhatsApp."""
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
NARANJA = (255, 140, 0)
TMP = AQUI / 'tmp_armado'
TMP.mkdir(exist_ok=True)
CRUCE = 0.3
TARJETA = 3.0


def dur(ruta):
    out = subprocess.run([FF, '-i', str(ruta)], capture_output=True, text=True).stderr
    h, m, s = out.split('Duration: ')[1].split(',')[0].split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)


def palabras(ruta, desfase, modelo):
    c = av.open(str(ruta))
    rs = av.AudioResampler(format='s16', layout='mono', rate=16000)
    a = np.concatenate([x.to_ndarray().ravel() for fr in c.decode(audio=0) for x in rs.resample(fr)]).astype(np.float32) / 32768
    segs, _ = modelo.transcribe(a, language='es', word_timestamps=True)
    return [(w.word.strip(), w.start + desfase, w.end + desfase) for s in segs for w in s.words]


def subtitulo(texto, ruta):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FUENTE, 84)
    tw = d.textlength(texto, font=f)
    d.text(((W - tw) / 2, 1250), texto, font=f, fill=NARANJA, stroke_width=6, stroke_fill=(20, 20, 20))
    img.save(ruta)


def tarjeta(ruta):
    img = Image.new('RGB', (W, H), (24, 70, 136))
    logo = Image.open(AQUI / 'refs' / 'logo_rednatura.jpg').convert('RGB')
    logo = logo.crop((60, 300, 1004, 660)).resize((900, int(360 * 900 / 944)), Image.LANCZOS)
    img.paste(logo, ((W - logo.width) // 2, 330))
    d = ImageDraw.Draw(img)
    def centro(txt, y, tam, color):
        f = ImageFont.truetype(FUENTE, tam)
        d.text(((W - d.textlength(txt, font=f)) / 2, y), txt, font=f, fill=color)
    centro('Omar', 780, 140, (255, 255, 255))
    centro('Distribuidor independiente', 970, 54, (210, 225, 255))
    centro('RIR 225430', 1050, 60, (255, 255, 255))
    fw = ImageFont.truetype(FUENTE, 60)
    ancho = d.textlength('WhatsApp 56 5587 4031', font=fw) + 120
    d.rounded_rectangle(((W - ancho) / 2, 1260, (W + ancho) / 2, 1400), 70, fill=(37, 211, 102))
    centro('WhatsApp 56 5587 4031', 1300, 60, (255, 255, 255))
    img.save(ruta)


clips = [AQUI / 'clips_v3_voz' / 'O1.mp4', AQUI / 'clips_v3_voz' / 'O2.mp4']
d1, d2 = dur(clips[0]), dur(clips[1])
total_habla = d1 + d2 - CRUCE
modelo = WhisperModel('small', device='cpu', compute_type='int8')
lista = palabras(clips[0], 0, modelo) + palabras(clips[1], d1 - CRUCE, modelo)
tarjeta(TMP / 'tarjeta.png')

entradas = ['-i', str(clips[0]), '-i', str(clips[1]), '-loop', '1', '-t', str(TARJETA), '-i', str(TMP / 'tarjeta.png')]
esc = 'scale=1080:1920:flags=lanczos,setsar=1,fps=30'
filtro = (f'[0:v]{esc}[v0];[1:v]{esc}[v1];[2:v]scale=1080:1920,setsar=1,fps=30,format=yuv420p[vt];'
          f'[v0][v1]xfade=transition=fade:duration={CRUCE}:offset={d1 - CRUCE:.2f}[x];')
prev = 'x'
for i, (p, a, b) in enumerate(lista):
    subtitulo(p, TMP / f'p{i}.png')
    entradas += ['-i', str(TMP / f'p{i}.png')]
    fin = lista[i + 1][1] if i + 1 < len(lista) else b + 0.3
    filtro += f"[{prev}][{3 + i}:v]overlay=0:0:enable='between(t,{a:.2f},{fin:.2f})'[s{i}];"
    prev = f's{i}'
filtro += (f'[{prev}]format=yuv420p[vh];[vh][vt]xfade=transition=fade:duration=0.4:offset={total_habla - 0.4:.2f}[v];'
           f'[0:a][1:a]acrossfade=d={CRUCE},apad[a]')
salida = AQUI / 'final' / 'Omar_RedNatura_v3.mp4'
salida.parent.mkdir(exist_ok=True)
subprocess.run([FF, '-v', 'error', '-y', *entradas, '-filter_complex', filtro, '-map', '[v]', '-map', '[a]',
                '-t', f'{total_habla + TARJETA - 0.4:.2f}', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p', '-preset', 'slow', '-crf', '23', '-maxrate', '2500k', '-bufsize', '5000k',
                '-c:a', 'aac', '-ar', '44100', '-ac', '2', '-b:a', '128k', '-movflags', '+faststart', str(salida)], check=True)
print(salida, len(lista), 'palabras')
