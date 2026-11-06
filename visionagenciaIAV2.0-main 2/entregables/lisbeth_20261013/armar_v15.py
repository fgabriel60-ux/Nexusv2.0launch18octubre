"""Lisbeth v15: gancho de 3.5 s (obra activa en los lotes, clips_v15/K0) + el v11 completo detrás."""
import subprocess
from pathlib import Path
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
FUENTE = AQUI.parent / 'modelos_modal' / 'fuentes' / 'Anton-Regular.ttf'
TMP = AQUI / 'tmp_v15'; TMP.mkdir(exist_ok=True)
GANCHO = 3.5

# texto del gancho, centrado arriba con sombra suave
txt = Image.new('RGBA', (720, 1280), (0, 0, 0, 0))
d = ImageDraw.Draw(txt)
f1, f2 = ImageFont.truetype(str(FUENTE), 74), ImageFont.truetype(str(FUENTE), 92)
for y, linea, f, color in ((150, 'ASÍ EMPIEZA', f1, (255, 255, 255)), (235, 'TU PATRIMONIO', f2, (255, 205, 60))):
    w = d.textlength(linea, font=f)
    d.text(((720 - w) / 2, y), linea, font=f, fill=color + (255,))
sombra = Image.new('RGBA', txt.size, (0, 0, 0, 0)); sombra.putalpha(txt.getchannel('A').filter(ImageFilter.GaussianBlur(10)).point(lambda a: int(a * 0.8)))
Image.alpha_composite(sombra, txt).save(TMP / 'texto.png')

subprocess.run([FF, '-v', 'error', '-y', '-i', str(AQUI / 'clips_v15' / 'K0.mp4'), '-loop', '1', '-i', str(TMP / 'texto.png'),
                '-filter_complex', f'[0:v]scale=720:1280:flags=lanczos,fps=30,trim=0:{GANCHO},setpts=PTS-STARTPTS[v];'
                f'[1:v]format=rgba,fade=in:st=0.2:d=0.4:alpha=1[t];[v][t]overlay=0:0:shortest=1,format=yuv420p[o];'
                f'[0:a]atrim=0:{GANCHO},asetpts=PTS-STARTPTS,aresample=44100,afade=out:st={GANCHO - 0.4}:d=0.4[a]',
                '-map', '[o]', '-map', '[a]', '-t', str(GANCHO), '-c:v', 'libx264', '-profile:v', 'main', '-crf', '20', '-c:a', 'aac', '-ac', '2',
                str(TMP / 'gancho.mp4')], check=True)
salida = AQUI / 'final' / 'Lisbeth_terreno_v15_gancho_obra.mp4'
subprocess.run([FF, '-v', 'error', '-y', '-i', str(TMP / 'gancho.mp4'), '-i', str(AQUI / 'final' / 'Lisbeth_terreno_v11_construccion.mp4'),
                '-filter_complex', '[1:v]fps=30,format=yuv420p,setsar=1[b];[0:v]setsar=1[g];[g][0:a][b][1:a]concat=n=2:v=1:a=1[v][a]',
                '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-crf', '22', '-maxrate', '3M', '-bufsize', '6M',
                '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(salida)], check=True)
print(salida, round(salida.stat().st_size / 1e6, 1), 'MB')
