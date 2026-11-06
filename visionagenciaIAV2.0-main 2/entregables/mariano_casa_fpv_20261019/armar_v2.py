"""Mariano · Benjamina v2 al estilo del reel de recorrido FPV (Da1O7DIOwOC): cortes de ~2 s sobre planos continuos, color natural y brillante (sin filtro oscuro), casi sin texto, voz entusiasta «¡vamos a ver!» y sonido ambiente de las tomas debajo."""
import json, subprocess
from pathlib import Path
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
FUENTE = AQUI.parent / 'modelos_modal' / 'fuentes' / 'Anton-Regular.ttf'
TMP = AQUI / 'tmp_v2'; TMP.mkdir(exist_ok=True)
VOZ = AQUI / 'voz' / 'guion2.mp3'
PAL = json.loads((AQUI / 'voz' / 'palabras2.json').read_text())
FIN_VOZ = PAL[-1][2]
TOTAL = round(FIN_VOZ + 2.4, 2)
CORTE = 1.4
VF = 'scale=720:1280:flags=lanczos:force_original_aspect_ratio=increase,crop=720:1280,fps=30,setsar=1,eq=saturation=1.08:contrast=1.04,format=yuv420p'

def t_palabra(prefijo):
    return next(s for w, s, e in PAL if w.lower().strip('.,').startswith(prefijo))
ANCLAS = [(0.0, 'E0'), (t_palabra('entramos') - 0.15, 'E1'), (t_palabra('cocina') - 0.15, 'E2'), (t_palabra('comedor') - 0.15, 'E3'),
          (t_palabra('patio') - 0.15, 'E4'), (t_palabra('subimos') - 0.15, 'E5'), (t_palabra('terraza') - 0.25, 'E6'), (t_palabra('acepta') - 0.4, 'E7')]

def largo_de(p):
    e = subprocess.run([FF, '-i', str(p)], capture_output=True, text=True).stderr.split('Duration: ')[1].split(',')[0].split(':')
    return int(e[0]) * 3600 + int(e[1]) * 60 + float(e[2])

partes = []
for k, (ini, clip) in enumerate(ANCLAS):
    dur = (ANCLAS[k + 1][0] if k + 1 < len(ANCLAS) else TOTAL) - ini
    src = AQUI / 'clips' / f'{clip}.mp4'; largo = largo_de(src)
    if dur > largo:   # falta clip: un solo corte en cámara lenta
        n, sub, ajuste = 1, dur, f'setpts=PTS*{dur / largo:.4f}'
        offs = [0.0]
    else:
        n = max(1, round(dur / CORTE)); sub = dur / n; ajuste = 'setpts=PTS-STARTPTS'
        offs = [i * (largo - sub - 0.1) / (n - 1) if n > 1 else 0.0 for i in range(n)]
    for i, off in enumerate(offs):
        out = TMP / f's{k}_{i}.mp4'
        af = f'atrim=0:{sub / (dur / largo if dur > largo else 1):.3f},asetpts=PTS-STARTPTS,volume=0.3,aresample=44100,apad' if dur > largo else f'volume=0.3,aresample=44100,apad'
        subprocess.run([FF, '-v', 'error', '-y', '-ss', f'{off:.3f}', '-i', str(src), '-vf', f'{VF},{ajuste}', '-af', af, '-t', f'{sub:.3f}',
                        '-ac', '2', '-c:v', 'libx264', '-crf', '18', '-c:a', 'aac', str(out)], check=True)
        partes.append(out)
(TMP / 'lista.txt').write_text(''.join(f"file '{p}'\n" for p in partes))

# cierre: contacto en los últimos 2.4 s
im = Image.new('RGBA', (720, 1280), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
for txt, tam, y, color in (('ASESOR MARIANO H.', 64, 1280 * 0.57, (255, 255, 255, 255)), ('(664) 233-4848', 84, 1280 * 0.63, (255, 210, 60, 255))):
    f = ImageFont.truetype(str(FUENTE), tam); w = d.textlength(txt, font=f)
    d.text(((720 - w) / 2, y), txt, font=f, fill=color, stroke_width=6, stroke_fill=(0, 0, 0, 220))
im.save(TMP / 'cierre.png')
salida = AQUI / 'final' / 'Mariano_casa_recorrido_v2_estilo_fpv.mp4'
subprocess.run([FF, '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(TMP / 'lista.txt'), '-i', str(VOZ), '-loop', '1', '-i', str(TMP / 'cierre.png'),
                '-filter_complex', f"[2:v]format=rgba[t];[0:v][t]overlay=0:0:enable='gte(t,{FIN_VOZ + 0.4:.2f})':shortest=1,format=yuv420p[v];"
                f"[1:a]volume=1.3[vz];[0:a][vz]amix=inputs=2:duration=longest:normalize=0[a]",
                '-map', '[v]', '-map', '[a]', '-t', str(TOTAL), '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-crf', '21', '-maxrate', '3M', '-bufsize', '6M',
                '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', str(salida)], check=True)
print(salida, round(salida.stat().st_size / 1e6, 1), 'MB', TOTAL, 's', len(partes), 'cortes')
