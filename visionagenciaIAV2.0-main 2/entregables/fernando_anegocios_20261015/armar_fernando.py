"""Arma el video final 720x1280: clip H3 (libreta) + metraje real de Fernando + imagen del kit + CTA, voz Fish y subtítulos."""
import subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
A = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
T = A / 'tmp'; T.mkdir(exist_ok=True)
W, H = 720, 1280
NEG = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
AZUL, AMAR = (10, 60, 160), (255, 232, 0)


def dur(p):
    e = subprocess.run([FF, '-i', str(p)], capture_output=True, text=True).stderr
    h, m, s = e.split('Duration: ')[1].split(',')[0].split(':'); return int(h) * 3600 + int(m) * 60 + float(s)


def run(*a):
    subprocess.run([FF, '-v', 'error', '-y', *map(str, a)], check=True)


def subt(texto, nombre, amarillo=None):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    f = ImageFont.truetype(NEG, 46)
    palabras, lineas, cur = texto.split(), [], ''
    for p in palabras:
        if d.textlength((cur + ' ' + p).strip(), font=f) > W - 90: lineas.append(cur); cur = p
        else: cur = (cur + ' ' + p).strip()
    lineas.append(cur)
    alto = len(lineas) * 58 + 30; y0 = 960
    d.rounded_rectangle((30, y0, W - 30, y0 + alto), 22, fill=(0, 0, 0, 170))
    for i, l in enumerate(lineas):
        d.text((W // 2, y0 + 15 + i * 58 + 29), l, font=f, fill=AMAR if amarillo else (255, 255, 255), anchor='mm', stroke_width=2, stroke_fill=(0, 0, 0))
    img.save(T / f'{nombre}.png')


def cta():
    img = Image.new('RGB', (W, H), AZUL); d = ImageDraw.Draw(img)
    for y in range(H): d.line((0, y, W, y), fill=(10, 60 + y // 14, 160 + y // 25))
    g = lambda s: ImageFont.truetype(NEG, s)
    d.text((W // 2, 330), 'TODO POR', font=g(70), fill=(255, 255, 255), anchor='mm')
    d.text((W // 2, 460), '$3,500', font=g(165), fill=AMAR, anchor='mm')
    d.text((W // 2, 590), 'MXN', font=g(52), fill=(255, 255, 255), anchor='mm')
    d.rounded_rectangle((60, 700, W - 60, 800), 30, fill=AMAR); d.text((W // 2, 750), 'PAGAS HASTA QUE FUNCIONE', font=g(32), fill=(10, 30, 90), anchor='mm')
    d.rounded_rectangle((60, 860, W - 60, 990), 30, fill=(37, 211, 102)); d.text((W // 2, 925), 'Escríbenos por WhatsApp', font=g(40), fill=(255, 255, 255), anchor='mm')
    d.text((W // 2, 1100), 'Anegocios.com', font=g(54), fill=(255, 255, 255), anchor='mm')
    d.text((W // 2, 1170), 'Punto de venta + tienda en línea', font=g(32), fill=(200, 220, 255), anchor='mm')
    img.save(T / 'cta.png')


def kit():
    img = Image.new('RGB', (W, H), AZUL); d = ImageDraw.Draw(img)
    for y in range(H): d.line((0, y, W, y), fill=(10, 50 + y // 14, 150 + y // 25))
    k = Image.open(A / 'refs' / 'fernando_image.jpg').convert('RGB').resize((W, W), Image.LANCZOS)
    img.paste(k, (0, 140)); img.save(T / 'kit.png')


v = {k: dur(A / 'voz' / f'{k}.wav') for k in ('V1', 'V2', 'V3', 'V4')}
G = 0.25
t1 = 0; t2 = t1 + v['V1'] + G; t3 = t2 + v['V2'] + G; t4 = t3 + v['V3'] + G; fin = t4 + v['V4'] + 0.6
seg = [(t1, t2 - t1), (t2, t3 - t2), (t3, t4 - t3), (t4, fin - t4)]
print('tiempos', [round(x, 2) for x in (t2, t3, t4, fin)])
cta(); kit()
subt('¿Sigues llevando tu tienda en libreta?', 's1')
subt('Punto de venta completo + impresora + lector', 's2')
subt('1 año de software · instalación · capacitación · soporte', 's3')
fps = 30
# escena 1: clip H3
run('-i', A / 'clips' / 'L1.mp4', '-t', seg[0][1], '-vf', f'scale={W}:{H}:flags=lanczos,fps={fps},setsar=1', '-an', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', T / 'e1.mp4')
# escena 2: metraje real (mitad pantalla de venta, mitad impresora), recorte vertical
m = seg[1][1] / 2
for n, (ss, cx) in enumerate([(17, 0), (40.6, 0)]):
    run('-ss', ss, '-t', m, '-i', A / 'refs' / 'fernando_video.mp4', '-vf', f'scale={W}:{H}:flags=lanczos,fps={fps},setsar=1', '-an', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', T / f'e2{n}.mp4')
(T / 'l2.txt').write_text(f"file 'e20.mp4'\nfile 'e21.mp4'\n")
run('-f', 'concat', '-safe', 0, '-i', T / 'l2.txt', '-c', 'copy', T / 'e2.mp4')
# escena 3: kit con zoom lento
nf = round(seg[2][1] * fps)
run('-i', T / 'kit.png', '-vf', f"zoompan=z='1+0.0004*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={nf}:s={W}x{H}:fps={fps},setsar=1", '-frames:v', nf, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', T / 'e3.mp4')
# escena 4: CTA
run('-loop', 1, '-t', seg[3][1], '-i', T / 'cta.png', '-vf', f'scale={W}:{H},fps={fps},setsar=1', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', T / 'e4.mp4')
(T / 'l.txt').write_text(''.join(f"file 'e{i}.mp4'\n" for i in (1, 2, 3, 4)))
run('-f', 'concat', '-safe', 0, '-i', T / 'l.txt', '-c', 'copy', T / 'mudo.mp4')
# audio con retardos
fa = ''.join(f'[{i+1}:a]adelay={int(t*1000)}|{int(t*1000)}[a{i}];' for i, t in enumerate((t1, t2, t3, t4)))
run('-i', T / 'mudo.mp4', *sum([['-i', A / 'voz' / f'{k}.wav'] for k in ('V1', 'V2', 'V3', 'V4')], []),
    '-i', T / 's1.png', '-i', T / 's2.png', '-i', T / 's3.png',
    '-filter_complex', fa + '[a0][a1][a2][a3]amix=inputs=4:normalize=0,volume=1.6[aud];'
    f"[0:v][5:v]overlay=enable='between(t,{t1},{t2-0.1})'[x1];[x1][6:v]overlay=enable='between(t,{t2},{t3-0.1})'[x2];[x2][7:v]overlay=enable='between(t,{t3},{t4-0.1})'[vid]",
    '-map', '[vid]', '-map', '[aud]', '-t', fin, '-c:v', 'libx264', '-profile:v', 'main', '-level', '4.0', '-pix_fmt', 'yuv420p', '-crf', '23', '-preset', 'medium',
    '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', A / 'final' / 'Anegocios_kit_v2.mp4')
print('listo', A / 'final' / 'Anegocios_kit_v2.mp4')
