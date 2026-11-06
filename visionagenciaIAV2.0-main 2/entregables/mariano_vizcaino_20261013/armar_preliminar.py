"""Corte preliminar Vizcaíno (sin T3): T1 + T1b + T1c (sonido del modelo) + T2 + T4 (voz original de Fish en vez del audio del modelo)."""
import subprocess
from pathlib import Path
import imageio_ffmpeg

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
TMP = AQUI / 'tmp'; TMP.mkdir(exist_ok=True)
TOMAS = [('T1', 3.0), ('T1b', 2.5), ('T1c', 5.0), ('T2', None), ('T4', None)]
VF = 'scale=720:1280:flags=lanczos,fps=30,format=yuv420p,setsar=1'
partes = []
for t, dur in TOMAS:
    out = TMP / f'{t}.mp4'
    if dur:   # acción: recorta y conserva el sonido del modelo
        cmd = ['-i', str(AQUI / 'clips' / f'{t}.mp4'), '-t', str(dur), '-vf', VF, '-af', 'aresample=44100', '-ac', '2']
    else:     # habladas: voz original, el video dura lo que la voz
        cmd = ['-i', str(AQUI / 'clips' / f'{t}.mp4'), '-i', str(AQUI / 'voz' / f'{t}.wav'), '-map', '0:v', '-map', '1:a',
               '-vf', VF, '-af', 'aresample=44100', '-ac', '2', '-shortest']
    subprocess.run([FF, '-v', 'error', '-y', *cmd, '-c:v', 'libx264', '-crf', '20', '-c:a', 'aac', str(out)], check=True)
    partes.append(out)
lista = TMP / 'lista.txt'
lista.write_text(''.join(f"file '{p}'\n" for p in partes))
salida = AQUI / 'final'; salida.mkdir(exist_ok=True)
salida = salida / 'Mariano_helicoptero_Vizcaino_preliminar.mp4'
subprocess.run([FF, '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(lista), '-c:v', 'libx264', '-profile:v', 'main',
                '-level', '3.1', '-crf', '22', '-maxrate', '3M', '-bufsize', '6M', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart',
                str(salida)], check=True)
print(salida, round(salida.stat().st_size / 1e6, 1), 'MB')
