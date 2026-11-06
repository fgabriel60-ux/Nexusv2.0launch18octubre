"""Lisbeth v5: voz REAL de Lisbeth (voz_real/LISBETH_2.ogg) + escenas de drone a pantalla completa (sin fondo borroso, sin fotos encimadas)."""
import subprocess
from pathlib import Path
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
FUENTE = str(AQUI.parent / 'modelos_modal' / 'fuentes' / 'Montserrat.ttf')
W, H = 1080, 1920
TMP = AQUI / 'tmp_v5'; TMP.mkdir(exist_ok=True)
VOZ = AQUI / 'voz_real' / 'LISBETH_2.ogg'
# (clip, segundos en pantalla, letrero)  — suman ~ voz (23.3 s) + 1 s de cola
TOMAS = [('clips_v5/P1.mp4', 5.3, ['TERRENOS DESDE', '300 m²']),
         ('anterior/lisbeth/toma2_00001_.mp4', 4.6, ['VISTA ESPECTACULAR', 'A LAS MONTAÑAS']),
         ('clips_v5/P2.mp4', 5.0, ['DOCUMENTOS', 'EN REGLA']),
         ('clips/L3.mp4', 4.8, ['A 20 MIN DE LA PLAYA', 'ZONA CON PLUSVALÍA']),
         ('clips_v5/P3.mp4', 5.17, ['TU FAMILIA', 'SE LO MERECE'])]
CTA = ['NO COMPRES PROMESA', 'INFORMACIÓN POR WHATSAPP']


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1500:])


def dur(p):
    o = subprocess.run([FF, '-i', str(p)], capture_output=True, text=True).stderr
    h, m, s = o.split('Duration: ')[1].split(',')[0].split(':'); return int(h) * 3600 + int(m) * 60 + float(s)


def png(ruta, lineas, y=1430, tam=58):
    """Letrero sobrio abajo a la izquierda: barra dorada + texto en 2 líneas (estilo del reel de referencia)."""
    f1 = ImageFont.truetype(FUENTE, tam); f1.set_variation_by_name('Bold')
    f2 = ImageFont.truetype(FUENTE, tam); f2.set_variation_by_name('Medium')
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    sombra = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sombra).rectangle((0, y - 120, W, y + 2 * tam + 140), fill=(0, 0, 0, 90))
    img = Image.alpha_composite(img, sombra); d = ImageDraw.Draw(img)
    d.rectangle((70, y, 76, y + 2 * tam + 14), fill=(232, 190, 110))
    for i, t in enumerate(lineas):
        d.text((105, y + i * (tam + 12)), t, font=f1 if i == 0 else f2, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
    img.save(ruta)


esc = 'scale=1080:1920:flags=lanczos,setsar=1,fps=30,format=yuv420p'
segs, capas, t0 = [], [], 0.0
for k, (src, d, letrero) in enumerate(TOMAS):
    s = TMP / f'{k}.mp4'; real = dur(AQUI / src); lento = min(1.0, real / d)
    ff(['-i', str(AQUI / src), '-vf', f'setpts=PTS/{lento:.4f},{esc},tpad=stop_mode=clone:stop_duration=3', '-t', f'{d:.2f}', '-an',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '17', str(s)])
    segs.append(s); r = TMP / f'l{k}.png'; png(r, letrero); capas.append((r, t0 + 0.2, t0 + d - (2.4 if k == len(TOMAS) - 1 else 0.2))); t0 += d
png(TMP / 'cta.png', CTA, 1430); capas.append((TMP / 'cta.png', t0 - 2.2, t0))
lista = TMP / 'lista.txt'; lista.write_text(''.join(f"file '{s}'\n" for s in segs))
entr = ['-f', 'concat', '-safe', '0', '-i', str(lista), '-i', str(VOZ)] + sum([['-i', str(r)] for r, _, _ in capas], [])
f, prev = '', '0:v'
for j, (_, a, b) in enumerate(capas):
    f += f"[{prev}][{j + 2}:v]overlay=0:0:enable='between(t,{a:.2f},{b:.2f})'[o{j}];"; prev = f'o{j}'
f += f'[{prev}]format=yuv420p[v];[1:a]adelay=300|300,loudnorm=I=-15:TP=-1.5,apad[a]'
sal = AQUI / 'final' / 'Lisbeth_terreno_v5.mp4'
ff([*entr, '-filter_complex', f, '-map', '[v]', '-map', '[a]', '-t', f'{t0:.2f}', '-c:v', 'libx264', '-profile:v', 'main', '-preset', 'slow',
    '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', '44100', '-b:a', '128k', '-movflags', '+faststart', str(TMP / 'hd.mp4')])
ff(['-i', str(TMP / 'hd.mp4'), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p',
    '-crf', '21', '-c:a', 'copy', '-movflags', '+faststart', str(sal)])
print(sal, f'{t0:.1f} s, voz {dur(VOZ):.1f} s', sal.stat().st_size // 1024, 'KB')
