"""José v9j (1 nov 2026): igual que v9i pero sobre tmp_v9j/base_v9j.mp4 (precio a 6.8 s) y con «WhatsApp 221 573 3127» fijo de 21.6 a 24.1 s (pedidos de Glimmer en v9i).
Original v9i: v9h + las 10 fotos REALES que José mandó el 1 nov (clientes/Jose/whatsapp/del_cliente/20261101_*)
en hard cut de 20.4 a 24.1 s (donde estaba la azotea animada), 0.37 s por foto, clic de cámara en cada corte (como Guillermo),
etiqueta «TRABAJOS REALES · GRUPO JR» y los mismos subtítulos de la voz. Voz y resto del video igual que v9h."""
from pathlib import Path
import subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
import imageio_ffmpeg

R = Path('/workspaces/Nexusv2.0launch18octubre'); A = R / 'clientes/Jose/armado_20261029'; T = A / 'tmp_v9j'; T.mkdir(exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe(); FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
BASE = A / 'tmp_v9j/base_v9j.mp4'; OUT = R / 'clientes/Jose/Jose_GrupoJR_Pixar_obrero_v9j.mp4'
CLIC = R / 'clientes/Guillermo/video/sfx/clic.wav'
FOTOS = sorted((R / 'clientes/Jose/whatsapp/del_cliente').glob('20261101_*.jpg'))
ORDEN = [2, 7, 6, 4, 0, 8, 9, 5, 1, 3]          # primero el trabajador aplicando, luego terminados
INI, FIN = 20.4, 24.1; D = (FIN - INI) / len(ORDEN)
SUBS = [(20.4, 'Mándanos fotos de tu'), (22.3, 'azotea por WhatsApp y'), (23.2, 'te cotizamos hoy.')]   # tiempos de v9g (Whisper)
W, H = 720, 1280

def texto(d, xy_c, t, tam, relleno, borde=4):
    f = ImageFont.truetype(FB, tam); w = d.textlength(t, font=f)
    d.text((xy_c[0] - w / 2, xy_c[1]), t, font=f, fill=relleno, stroke_width=borde, stroke_fill='black')

for j, k in enumerate(ORDEN):
    im = ImageOps.exif_transpose(Image.open(FOTOS[k])).convert('RGB')
    fondo = ImageOps.fit(im, (W, H)).filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v * 0.55))
    fr = im.copy(); fr.thumbnail((W, int(H * 0.62)), Image.LANCZOS)
    if fr.width < W: fr = fr.resize((W, int(fr.height * W / fr.width)), Image.LANCZOS) if fr.height * W / fr.width <= H * 0.62 else fr
    fondo.paste(fr, ((W - fr.width) // 2, (H - fr.height) // 2 - 40))
    d = ImageDraw.Draw(fondo)
    d.rounded_rectangle([110, 120, 610, 190], radius=20, fill=(8, 29, 78), outline=(255, 204, 0), width=4)
    texto(d, (W / 2, 135), 'TRABAJOS REALES · GRUPO JR', 30, (255, 204, 0), 0)
    t = INI + (j + 0.5) * D; sub = [s for a, s in SUBS if a <= t][-1]
    texto(d, (W / 2, H * 0.80), sub, 40, 'white')
    if t >= 21.6:
        d.rounded_rectangle([140, 1110, 580, 1190], radius=40, fill=(37, 211, 102))
        texto(d, (W / 2, 1127), 'WhatsApp 221 573 3127', 36, 'white', 0)
    fondo.save(T / f'f{j:02d}.png')
(T / 'lista.txt').write_text(''.join(f"file 'f{j:02d}.png'\nduration {D:.4f}\n" for j in range(len(ORDEN))) + f"file 'f{len(ORDEN) - 1:02d}.png'\n")
subprocess.run([FF, '-v', 'error', '-y', '-f', 'concat', '-i', str(T / 'lista.txt'), '-vf', f'fps=30,format=yuv420p,trim=duration={FIN - INI:.3f}',
                '-c:v', 'libx264', '-crf', '18', str(T / 'montaje.mp4')], check=True)

clics = ''.join(f"[2:a]aresample=48000,volume=0.5,adelay={int((INI + j * D) * 1000)}|{int((INI + j * D) * 1000)}[c{j}];" for j in range(len(ORDEN)))
fc = (f"[0:v]trim=0:{INI},setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS,scale={W}:{H},setsar=1[m];[0:v]trim={FIN},setpts=PTS-STARTPTS[b];"
      f"[a][m][b]concat=n=3:v=1:a=0[v];[0:a]aresample=48000[voz];" + clics +
      "[voz]" + ''.join(f'[c{j}]' for j in range(len(ORDEN))) + f"amix=inputs={len(ORDEN) + 1}:duration=first:normalize=0[au]")
subprocess.run([FF, '-v', 'error', '-y', '-i', str(BASE), '-i', str(T / 'montaje.mp4'), '-i', str(CLIC), '-filter_complex', fc, '-map', '[v]', '-map', '[au]',
                '-c:v', 'libx264', '-profile:v', 'main', '-pix_fmt', 'yuv420p', '-preset', 'fast', '-crf', '22', '-c:a', 'aac', '-b:a', '128k',
                '-movflags', '+faststart', str(OUT)], check=True)
print(OUT)
