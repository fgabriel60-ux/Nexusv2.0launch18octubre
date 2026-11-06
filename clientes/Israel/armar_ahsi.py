"""Israel · SIRLed · reel estilo referencia DduYDrtJQJa («¿Ah sí?» antes → después) con SUS videos reales (31 oct).
Duda del cliente → instalación en timelapse («¿Ah sí?») → pantallas encendidas en bares («¿No cabía?») → tarjeta con WhatsApp.
  python3 armar_ahsi.py [version] [musica.wav]"""
import glob, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
A = Path(__file__).parent; WA = sorted(glob.glob(str(A / 'whatsapp/*.mp4')))
V = sys.argv[1] if len(sys.argv) > 1 else 'v1'
MUS = sys.argv[2] if len(sys.argv) > 2 else '/workspaces/Nexusv2.0launch18octubre/entregables/prospectos_sancarlos_20261031/musica/villa_s11.wav'
F = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
# (índice de video, inicio, duración final, velocidad, texto)
P = [(31, 0.3, 1.5, 3.5, '“Una pantalla gigante\nno cabe en mi negocio”'),
     (28, 1.0, 1.3, 3.0, '¿Ah sí?'), (5, 3.0, 1.3, 3.0, '¿Ah sí?'), (12, 0.5, 1.2, 3.0, '¿Ah sí?'), (0, 3.0, 1.4, 3.0, '¿Ah sí?'),
     (2, 0.3, 2.0, 1.0, '¿No cabía?'), (8, 0.5, 2.0, 1.0, '¿No cabía?'), (26, 2.0, 2.2, 1.0, '¿No cabía?\nInstalación en bar real, CDMX'), (24, 1.0, 1.8, 1.0, 'Bares, restaurantes y tiendas\n¿Tienes local en CDMX?'),
     (21, 2.0, 2.2, 1.0, 'Escríbenos con los metros\nque tienes disponibles')]
T = A / f'tmp_{V}'; T.mkdir(exist_ok=True)
segs = []
for k, (i, a, d, vel, txt) in enumerate(P):
    lines = txt.split('\n'); y0 = 'h*0.40' if '?' in txt and len(lines) == 1 else 'h*0.36'
    dt = ','.join(f"drawtext=fontfile={F}:text='{l}':fontsize={min(56, int(1150 / max(len(l), 1)))}:fontcolor=white:borderw=6:bordercolor=black:x=(w-text_w)/2:y={y0}+{j * 70}" for j, l in enumerate(lines))
    o = T / f's{k:02d}.mp4'; segs.append(o)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a}', '-t', f'{d * vel + .2}', '-i', WA[i], '-vf',
                    f'setpts=PTS/{vel},scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1,fps=30,trim=0:{d},setpts=PTS-STARTPTS,{dt}',
                    '-an', '-c:v', 'libx264', '-crf', '19', '-pix_fmt', 'yuv420p', str(o)], check=True)
# tarjeta final
im = Image.new('RGB', (720, 1280), (6, 12, 40)); d = ImageDraw.Draw(im)
for y, t, s, c in [(440, 'SIRLed', 96, (80, 170, 255)), (560, 'Pantallas LED para tu negocio', 38, 'white'), (640, 'Venta · Instalación · Reparación', 34, (200, 200, 200)),
                   (800, 'WhatsApp', 44, (90, 220, 120)), (870, '55 7503 1182', 72, 'white')]:
    d.text((360, y), t, font=ImageFont.truetype(F, s), fill=c, anchor='mm')
im.save(T / 'tarjeta.png'); o = T / 'tarjeta.mp4'; segs.append(o)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-t', '2.0', '-i', str(T / 'tarjeta.png'), '-vf', "zoompan=z='1+0.0025*on':d=1:s=720x1280:fps=30,format=yuv420p", '-c:v', 'libx264', str(o)], check=True)
(T / 'lista.txt').write_text(''.join(f"file '{s}'\n" for s in segs))
tot = sum(p[2] for p in P) + 2.0
out = A / f'Israel_SIRLed_ahsi_{V}.mp4'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(T / 'lista.txt'), '-stream_loop', '-1', '-i', MUS,
                '-filter_complex', f'[1:a]atrim=0:{tot},afade=t=out:st={tot - 1}:d=1[a]', '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-shortest', str(out)], check=True)
print('listo', out, round(tot, 1))
