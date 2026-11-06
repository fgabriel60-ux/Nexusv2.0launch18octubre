"""José v9h (1 nov 2026): v9g + cambio de Glimmer «precio antes»: banner de precio desde 17.7 s
(«Tu losa queda lista…») hasta 20.4 s, encima del video y sin tapar los subtítulos. La tarjeta final queda igual
(segunda y última mención del precio). Parte del mp4 de v9g porque los clips de tmp_v9d ya no están en el workspace."""
from pathlib import Path
import subprocess
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

R = Path('/workspaces/Nexusv2.0launch18octubre'); A = R / 'clientes/Jose/armado_20261029'; T = A / 'tmp_v9h'; T.mkdir(exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe()
F = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
BASE = R / 'clientes/Jose/Jose_GrupoJR_Pixar_obrero_v9g.mp4'
OUT = R / 'clientes/Jose/Jose_GrupoJR_Pixar_obrero_v9h.mp4'
INI, FIN = 17.7, 20.4
AZUL, AMARILLO, BLANCO = (8, 29, 78, 235), (255, 204, 0, 255), (255, 255, 255, 255)

W, H = 540, 165
im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
d.rounded_rectangle([0, 0, W - 1, H - 1], radius=28, fill=AZUL, outline=AMARILLO, width=5)
def centro(y, txt, tam, color):
    f = ImageFont.truetype(F, tam); w = d.textlength(txt, font=f); d.text(((W - w) / 2, y), txt, font=f, fill=color)
centro(14, 'Desde $150 por m²', 46, AMARILLO)
centro(76, 'Sellador + 2 capas', 32, BLANCO)
centro(119, '10% desc. en más de 100 m²', 26, BLANCO)
im.save(T / 'banner.png')

# zona segura de Reels/Historias: encima de los subtítulos (y=1024); entra con un fundido corto
y = 830
subprocess.run([FF, '-v', 'error', '-y', '-i', str(BASE), '-loop', '1', '-i', str(T / 'banner.png'),
                '-filter_complex', f"[1:v]format=rgba,fade=in:st={INI}:d=0.25:alpha=1[b];[0:v][b]overlay=x=(W-w)/2:y={y}:enable='between(t,{INI},{FIN})':shortest=1[v]",
                '-map', '[v]', '-map', '0:a', '-c:v', 'libx264', '-profile:v', 'main', '-pix_fmt', 'yuv420p', '-preset', 'fast',
                '-crf', '22', '-c:a', 'copy', '-movflags', '+faststart', str(OUT)], check=True)
print(OUT)
