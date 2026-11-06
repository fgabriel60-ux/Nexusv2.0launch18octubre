"""Mariano · Vizcaíno v2: baja por la cuerda (T1, T1c), helicóptero en la azotea (T1d), habla (T2, T4 con voz Fish) y logo de Vizcaíno al cierre."""
import subprocess
from pathlib import Path
import imageio_ffmpeg

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
TMP = AQUI / 'tmp_v2'; TMP.mkdir(exist_ok=True)
TOMAS = [('T1', 5.0), ('T1c', 3.0), ('T1d', 3.0), ('T2', None), ('T4', None)]
VF = 'scale=720:1280:flags=lanczos,fps=30,format=yuv420p,setsar=1'
partes = []
for t, dur in TOMAS:
    out = TMP / f'{t}.mp4'
    src = str(AQUI / 'clips_v2' / f'{t}.mp4')
    if dur:
        cmd = ['-i', src, '-t', str(dur), '-vf', VF, '-af', 'aresample=44100', '-ac', '2']
    elif t == 'T4':   # cierre: logo de Vizcaíno en los últimos 2.5 s
        cmd = ['-i', src, '-i', str(AQUI / 'voz' / 'T4.wav'), '-i', str(AQUI / 'refs' / 'logo_vizcaino.png'),
               '-filter_complex', f'[0:v]{VF}[v];[2:v]scale=360:-1,format=rgba,fade=in:st=4.3:d=0.5:alpha=1[l];[v][l]overlay=(W-w)/2:110:enable=gte(t\\,4.3)[o]',
               '-map', '[o]', '-map', '1:a', '-af', 'aresample=44100', '-ac', '2', '-shortest']
    else:
        cmd = ['-i', src, '-i', str(AQUI / 'voz' / f'{t}.wav'), '-map', '0:v', '-map', '1:a', '-vf', VF, '-af', 'aresample=44100', '-ac', '2', '-shortest']
    subprocess.run([FF, '-v', 'error', '-y', *cmd, '-c:v', 'libx264', '-crf', '20', '-c:a', 'aac', str(out)], check=True)
    partes.append(out)
lista = TMP / 'lista.txt'
lista.write_text(''.join(f"file '{p}'\n" for p in partes))
salida = AQUI / 'final' / 'Mariano_helicoptero_Vizcaino_v2.mp4'
subprocess.run([FF, '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(lista), '-c:v', 'libx264', '-profile:v', 'main',
                '-level', '3.1', '-crf', '22', '-maxrate', '3M', '-bufsize', '6M', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart',
                str(salida)], check=True)
print(salida, round(salida.stat().st_size / 1e6, 1), 'MB')
