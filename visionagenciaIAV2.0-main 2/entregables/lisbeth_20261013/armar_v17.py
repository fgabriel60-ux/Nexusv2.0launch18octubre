"""Lisbeth v17: gancho más rápido. Abre (1.67 s) con el desarrollo terminado y «ASÍ EMPIEZA TU PATRIMONIO» desde el primer cuadro, luego P1 y P2 a 1.2x y P3 completo; 15 s totales para no perder la sincronía con la voz del v11. Desde el s 15 sigue el v11."""
import subprocess
from pathlib import Path
import imageio_ffmpeg

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
TMP = AQUI / 'tmp_v17'; TMP.mkdir(exist_ok=True)
V11 = AQUI / 'final' / 'Lisbeth_terreno_v11_construccion.mp4'
CORTE = 15.0
BASE = 'scale=720:1260:flags=lanczos,crop=720:1260,pad=720:1280:0:10,fps=30,format=yuv420p,setsar=1'
AJUSTES = {  # nombre: (inicio, duración fuente, velocidad, filtros extra)
    'A': ('P3', 3.33, 1.0, 1.0, 'setpts=PTS-STARTPTS'),
    'B': ('P1', 0.0, 5.0, 1.2, 'setpts=PTS/1.2'),
    'C': ('P2', 0.0, 5.0, 1.2, 'setpts=PTS/1.2'),
    'D': ('P3', 0.0, 5.0, 1.0, 'setpts=PTS-STARTPTS'),
}
partes = []
for n, (clip, ss, dur, vel, ajuste) in AJUSTES.items():
    out = TMP / f'{n}.mp4'
    total = round(dur / vel, 3) if n != 'A' else 1.67
    subprocess.run([FF, '-v', 'error', '-y', '-ss', str(ss), '-t', str(dur), '-i', str(AQUI / 'clips_v16' / f'{clip}.mp4'), '-vf', f'{BASE},{ajuste}',
                    '-an', '-t', str(total), '-c:v', 'libx264', '-crf', '18', str(out)], check=True)
    partes.append(out)
subprocess.run([FF, '-v', 'error', '-y', '-ss', str(CORTE), '-i', str(V11), '-vf', 'fps=30,format=yuv420p,setsar=1', '-an', '-c:v', 'libx264', '-crf', '18', str(TMP / 'resto.mp4')], check=True)
partes.append(TMP / 'resto.mp4')
(TMP / 'lista.txt').write_text(''.join(f"file '{p}'\n" for p in partes))
salida = AQUI / 'final' / 'Lisbeth_terreno_v17_gancho_rapido.mp4'
texto = AQUI / 'tmp_v15' / 'texto.png'
subprocess.run([FF, '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(TMP / 'lista.txt'), '-i', str(V11), '-loop', '1', '-i', str(texto),
                '-filter_complex', '[2:v]format=rgba[t];[0:v][t]overlay=0:0:enable=\'between(t,0,3.2)\':shortest=1,format=yuv420p[v]',
                '-map', '[v]', '-map', '1:a', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-crf', '21', '-maxrate', '3M', '-bufsize', '6M',
                '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', str(salida)], check=True)
print(salida, round(salida.stat().st_size / 1e6, 1), 'MB')
