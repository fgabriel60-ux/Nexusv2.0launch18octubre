"""Lisbeth v18: la construcción avanza desde el terreno vacío y TERMINA rápido (P1 y P2 a 2x, P3 a 1.5x, ~8 s); el resto de los 15 s de voz queda sobre el desarrollo terminado con un acercamiento lento. Desde el s 15 sigue el v11."""
import subprocess
from pathlib import Path
import imageio_ffmpeg

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
TMP = AQUI / 'tmp_v18'; TMP.mkdir(exist_ok=True)
V11 = AQUI / 'final' / 'Lisbeth_terreno_v11_construccion.mp4'
CORTE = 15.0
BASE = 'scale=720:1260:flags=lanczos,crop=720:1260,pad=720:1280:0:10,fps=30,format=yuv420p,setsar=1'
VELOCIDADES = {'P1': 2.0, 'P2': 2.0, 'P3': 1.5}
partes, usado = [], 0.0
for n, vel in VELOCIDADES.items():
    dur = round(5.0 / vel, 3); usado += dur
    out = TMP / f'{n}.mp4'
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(AQUI / 'clips_v16' / f'{n}.mp4'), '-vf', f'{BASE},setpts=PTS/{vel}', '-an', '-t', str(dur),
                    '-c:v', 'libx264', '-crf', '18', str(out)], check=True)
    partes.append(out)
# desarrollo terminado: último cuadro de P3 con acercamiento lento hasta el s 15
resto = round(CORTE - usado, 3)
subprocess.run([FF, '-v', 'error', '-y', '-sseof', '-0.1', '-i', str(AQUI / 'clips_v16' / 'P3.mp4'), '-frames:v', '1', '-vf', BASE, str(TMP / 'final.png')], check=True)
subprocess.run([FF, '-v', 'error', '-y', '-loop', '1', '-i', str(TMP / 'final.png'), '-vf',
                f"scale=1440:2560,zoompan=z='min(1+0.0009*on,1.22)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(resto * 30)}:s=720x1280:fps=30,format=yuv420p,setsar=1",
                '-t', str(resto), '-c:v', 'libx264', '-crf', '18', str(TMP / 'terminado.mp4')], check=True)
partes.append(TMP / 'terminado.mp4')
subprocess.run([FF, '-v', 'error', '-y', '-ss', str(CORTE), '-i', str(V11), '-vf', 'fps=30,format=yuv420p,setsar=1', '-an', '-c:v', 'libx264', '-crf', '18', str(TMP / 'resto.mp4')], check=True)
partes.append(TMP / 'resto.mp4')
(TMP / 'lista.txt').write_text(''.join(f"file '{p}'\n" for p in partes))
salida = AQUI / 'final' / 'Lisbeth_terreno_v18_construccion_rapida.mp4'
subprocess.run([FF, '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(TMP / 'lista.txt'), '-i', str(V11), '-loop', '1', '-i', str(AQUI / 'tmp_v15' / 'texto.png'),
                '-filter_complex', "[2:v]format=rgba[t];[0:v][t]overlay=0:0:enable='between(t,0,3.2)':shortest=1,format=yuv420p[v]",
                '-map', '[v]', '-map', '1:a', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-crf', '21', '-maxrate', '3M', '-bufsize', '6M',
                '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', str(salida)], check=True)
print(salida, round(salida.stat().st_size / 1e6, 1), 'MB', 'construcción termina a', round(usado, 2), 's')
