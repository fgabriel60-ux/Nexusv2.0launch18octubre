"""Mariano · Benjamina «sync cut» con la CANCIÓN del reel DcIcueXPE33: usa su audio y su rejilla de cortes (3.2 s de gancho y un plano cada 0.932 s, medidos del propio reel), cierre con contacto."""
import subprocess, wave
from pathlib import Path
import imageio_ffmpeg, numpy as np
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
FUENTE = AQUI.parent / 'modelos_modal' / 'fuentes' / 'Anton-Regular.ttf'
TMP = AQUI / 'tmp_sync2'; TMP.mkdir(exist_ok=True)
CORTE = 0.932                                          # periodo medido de los cortes del reel
INTRO = 3.2
OUTRO = 23.7 - (INTRO + 18 * CORTE)                       # el reel sigue en rejilla hasta ~23.7 s
RUTA = ['E1', 'E2', 'E3', 'E4', 'E5', 'E6']; POR_TOMA = 3
TOTAL = INTRO + len(RUTA) * POR_TOMA * CORTE + OUTRO
VF = 'scale=720:1280:flags=lanczos:force_original_aspect_ratio=increase,crop=720:1280,fps=30,setsar=1,eq=saturation=1.08:contrast=1.04,format=yuv420p'

# --- música: audio original del reel (primeros 23.7 s) ---
REEL = Path('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/62e2c92e-a680-4cd6-b714-2b4bef6d89c6/scratchpad/ig/DcIcueXPE33.mp4')
subprocess.run([FF, '-v', 'error', '-y', '-i', str(REEL), '-t', f'{TOTAL:.3f}', '-vn', '-af', f'volume=4dB,alimiter=limit=0.95,afade=out:st={TOTAL - 1.2:.2f}:d=1.2',
                '-ar', '44100', '-ac', '2', str(TMP / 'musica.wav')], check=True)

# --- planos ---
partes = []
def plano(clip, off, dur, nombre, extra=''):
    out = TMP / f'{nombre}.mp4'
    subprocess.run([FF, '-v', 'error', '-y', '-ss', f'{off:.3f}', '-i', str(AQUI / 'clips' / f'{clip}.mp4'), '-vf', f'{VF}{extra}', '-an', '-t', f'{dur:.4f}',
                    '-c:v', 'libx264', '-crf', '18', str(out)], check=True)
    partes.append(out)
plano('E0', 0.0, INTRO, 'intro')
for k, clip in enumerate(RUTA):
    for i in range(POR_TOMA):
        plano(clip, i * 1.55, CORTE, f'{clip}_{i}')
plano('E7', 0.0, OUTRO, 'outro')
(TMP / 'lista.txt').write_text(''.join(f"file '{p}'\n" for p in partes))

# --- textos ---
def png(nombre, lineas):
    im = Image.new('RGBA', (720, 1280), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for txt, tam, y, color in lineas:
        f = ImageFont.truetype(str(FUENTE), tam); w = d.textlength(txt, font=f)
        d.text(((720 - w) / 2, y), txt, font=f, fill=color, stroke_width=6, stroke_fill=(0, 0, 0, 215))
    im.save(TMP / f'{nombre}.png')
B, Y = (255, 255, 255, 255), (255, 210, 60, 255)
png('gancho', [('BENJAMINA', 110, 1280 * 0.60, B), ('DESDE $2.8M', 84, 1280 * 0.68, Y)])
png('pago', [('INFONAVIT', 64, 1280 * 0.72, B), ('HIPOTECARIO · CONTADO', 50, 1280 * 0.78, Y)])
png('cierre', [('ASESOR MARIANO H.', 64, 1280 * 0.58, B), ('(664) 233-4848', 84, 1280 * 0.64, Y)])
t_pago = INTRO + 9 * CORTE; t_cierre = TOTAL - OUTRO + 0.5
salida = AQUI / 'final' / 'Mariano_casa_sync_cut_cancion.mp4'
subprocess.run([FF, '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(TMP / 'lista.txt'), '-i', str(TMP / 'musica.wav'),
                '-loop', '1', '-i', str(TMP / 'gancho.png'), '-loop', '1', '-i', str(TMP / 'pago.png'), '-loop', '1', '-i', str(TMP / 'cierre.png'),
                '-filter_complex', f"[2:v]format=rgba[g];[3:v]format=rgba[p];[4:v]format=rgba[c];"
                f"[0:v][g]overlay=0:0:enable='between(t,0.1,{INTRO - 0.2:.2f})':shortest=1[v1];[v1][p]overlay=0:0:enable='between(t,{t_pago:.2f},{t_pago + 3 * CORTE:.2f})'[v2];"
                f"[v2][c]overlay=0:0:enable='gte(t,{t_cierre:.2f})',format=yuv420p[v]",
                '-map', '[v]', '-map', '1:a', '-t', f'{TOTAL:.3f}', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-crf', '21', '-maxrate', '3M', '-bufsize', '6M',
                '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', str(salida)], check=True)
print(salida, round(salida.stat().st_size / 1e6, 1), 'MB', round(TOTAL, 2), 's', len(partes), 'planos')
