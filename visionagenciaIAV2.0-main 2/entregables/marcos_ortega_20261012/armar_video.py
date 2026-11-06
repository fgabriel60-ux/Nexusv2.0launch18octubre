"""Arma el video final de Ortega: 3 clips MiniMax H3 + cierre congelado, textos en pantalla y voz en off."""
import subprocess
from pathlib import Path
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
FUENTE = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
W, H = 1080, 1920
VOZ = AQUI / 'Ortega_voz.mp3'
# (texto, inicio, fin, color de acento)
TEXTOS = [
    ('¿TE QUEDASTE\nSIN TRABAJO?', 0.0, 4.6, (255, 255, 255)),
    ('TU AFORE TE PUEDE DAR\nHASTA $35,192', 4.6, 9.4, (255, 214, 64)),
    ('SIN ANTICIPOS\nPAGAS AL RECIBIR', 9.4, 15.0, (120, 230, 140)),
    ('ASESORÍA SIN COSTO\nESCRÍBENOS POR WHATSAPP', 15.0, 99.0, (120, 230, 140)),
]


def cartel(texto, color, ruta):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    lineas = texto.split('\n')
    tam = 78
    while max(d.textlength(l, font=ImageFont.truetype(FUENTE, tam)) for l in lineas) > W - 200:
        tam -= 2
    f = ImageFont.truetype(FUENTE, tam)
    alto = 100 * len(lineas)
    y0 = 300
    d.rounded_rectangle((60, y0 - 40, W - 60, y0 + alto + 20), 36, fill=(10, 20, 40, 190))
    for i, l in enumerate(lineas):
        tw = d.textlength(l, font=f)
        d.text(((W - tw) / 2, y0 + i * 100), l, font=f, fill=color if i == len(lineas) - 1 else (255, 255, 255),
               stroke_width=3, stroke_fill=(0, 0, 0))
    img.save(ruta)


def dur(ruta):
    out = subprocess.run([FF, '-i', str(ruta)], capture_output=True, text=True).stderr
    h, m, s = out.split('Duration: ')[1].split(',')[0].split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)


tmp = AQUI / 'tmp_armado'
tmp.mkdir(exist_ok=True)
for i, (t, a, b, c) in enumerate(TEXTOS):
    cartel(t, c, tmp / f'texto{i}.png')

voz = dur(VOZ)
clips = [AQUI / 'clips' / f'toma{i}.mp4' for i in (1, 2, 3)]
base = sum(dur(c) for c in clips) - 2 * 0.4
cola = max(0.0, voz + 1.0 - base)

entradas = sum([['-i', str(c)] for c in clips], [])
entradas += ['-i', str(VOZ)] + sum([['-i', str(tmp / f'texto{i}.png')] for i in range(len(TEXTOS))], [])
esc = 'scale=1080:1920:flags=lanczos,setsar=1,fps=30'
d1 = dur(clips[0]); d2 = dur(clips[1])
filtro = (f'[0:v]{esc}[v0];[1:v]{esc}[v1];[2:v]{esc},tpad=stop_mode=clone:stop_duration={cola:.2f}[v2];'
          f'[v0][v1]xfade=transition=fade:duration=0.4:offset={d1 - 0.4:.2f}[x1];'
          f'[x1][v2]xfade=transition=fade:duration=0.4:offset={d1 + d2 - 0.8:.2f}[x2];')
prev = 'x2'
for i, (_, a, b, _) in enumerate(TEXTOS):
    filtro += f"[{prev}][{4 + i}:v]overlay=0:0:enable='between(t,{a},{b})'[o{i}];"
    prev = f'o{i}'
filtro += (f'[{prev}]format=yuv420p[v];'
           f'[0:a][1:a]acrossfade=d=0.4[a1];[a1][2:a]acrossfade=d=0.4,apad,volume=0[amb];'
           f'[3:a]adelay=300|300,highpass=f=80,lowpass=f=12000,afftdn=nf=-25,loudnorm=I=-16:TP=-1.5[vz];[amb][vz]amix=inputs=2:duration=longest:normalize=0,atrim=0:{base + cola:.2f}[a]')
salida = AQUI / 'final' / 'Ortega_desempleo_v1.mp4'
salida.parent.mkdir(exist_ok=True)
subprocess.run([FF, '-v', 'error', '-y', *entradas, '-filter_complex', filtro, '-map', '[v]', '-map', '[a]',
                '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-c:a', 'aac', '-b:a', '160k',
                '-movflags', '+faststart', '-t', f'{base + cola:.2f}', str(salida)], check=True)
print(salida, f'{base + cola:.1f} s')
