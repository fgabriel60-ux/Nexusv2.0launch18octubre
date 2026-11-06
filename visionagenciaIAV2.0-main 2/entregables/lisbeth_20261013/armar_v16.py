"""Lisbeth v16: obra real sobre la foto satelital del terreno (P1→P2→P3, 15 s) en lugar de la escena dorada; desde el s 15 sigue el v11 (mapas, documentos, cierre). La voz es la del v11 completa."""
import subprocess
from pathlib import Path
import imageio_ffmpeg

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
TMP = AQUI / 'tmp_v16'; TMP.mkdir(exist_ok=True)
V11 = AQUI / 'final' / 'Lisbeth_terreno_v11_construccion.mp4'
CORTE = 15.0
partes = []
for n in ('P1', 'P2', 'P3'):
    out = TMP / f'{n}.mp4'
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(AQUI / 'clips_v16' / f'{n}.mp4'), '-vf', 'scale=720:1260:flags=lanczos,crop=720:1260,pad=720:1280:0:10,fps=30,format=yuv420p,setsar=1',
                    '-an', '-t', '5.0', '-c:v', 'libx264', '-crf', '18', str(out)], check=True)
    partes.append(out)
subprocess.run([FF, '-v', 'error', '-y', '-ss', str(CORTE), '-i', str(V11), '-vf', 'fps=30,format=yuv420p,setsar=1', '-an', '-c:v', 'libx264', '-crf', '18', str(TMP / 'resto.mp4')], check=True)
partes.append(TMP / 'resto.mp4')
(TMP / 'lista.txt').write_text(''.join(f"file '{p}'\n" for p in partes))
salida = AQUI / 'final' / 'Lisbeth_terreno_v16_obra_real.mp4'
subprocess.run([FF, '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(TMP / 'lista.txt'), '-i', str(V11), '-map', '0:v', '-map', '1:a',
                '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-crf', '21', '-maxrate', '3M', '-bufsize', '6M', '-c:a', 'aac', '-b:a', '160k',
                '-shortest', '-movflags', '+faststart', str(salida)], check=True)
print(salida, round(salida.stat().st_size / 1e6, 1), 'MB')
