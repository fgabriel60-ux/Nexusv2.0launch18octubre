"""Rar~Amore rayos X (cartílago): 4 clips MiniMax H3 + voz de Jesús (Fish s2-pro) + etiquetas finas + cierre WhatsApp."""
import json, os, subprocess, urllib.request
from pathlib import Path
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
FUENTE = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
LIGERA = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
W, H = 1080, 1920
TMP = AQUI / 'tmp_armado'; TMP.mkdir(exist_ok=True)
(AQUI / 'final').mkdir(exist_ok=True)
CRUCE = 0.3
VOZ = 'd05ec13b5ba84b848060b6f2cfa8464b'  # Jesus Rar Amore natural
TEXTO = ('Tus articulaciones trabajan todos los días. Entre tus huesos, el cartílago necesita nutrientes para mantener '
         'tu movimiento. Rar Amore aporta colágeno, magnesio, calcio y vitamina D para apoyar su nutrición. '
         'Pide el tuyo por WhatsApp, con envío a todo México.')
ORO = (235, 200, 110)


def dur(ruta):
    out = subprocess.run([FF, '-i', str(ruta)], capture_output=True, text=True).stderr
    h, m, s = out.split('Duration: ')[1].split(',')[0].split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)


def ff(args):
    r = subprocess.run([FF, '-v', 'error', '-y', *args], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-1500:])


def etiqueta(ruta, texto, x, y, lado=1):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    f = ImageFont.truetype(LIGERA, 40)
    d.ellipse((x - 70, y - 70, x + 70, y + 70), outline=(255, 255, 255, 220), width=3)
    x2 = x + lado * 230; y2 = y - 120
    d.line([(x + lado * 50, y - 50), (x2, y2), (x2 + lado * 60, y2)], fill=(255, 255, 255, 220), width=3)
    tw = d.textlength(texto, font=f)
    d.text((x2 + lado * 75 if lado > 0 else x2 - 75 - tw, y2 - 24), texto, font=f, fill=(255, 255, 255, 235))
    img.save(ruta)


def banda(ruta, texto, y=230):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    f = ImageFont.truetype(LIGERA, 38)
    t = '>> ' + texto + ' <<'
    d.text(((W - d.textlength(t, font=f)) / 2, y), t, font=f, fill=(255, 255, 255, 220))
    img.save(ruta)


def cierre(ruta):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    def centro(txt, y, tam, color, fuente=FUENTE):
        f = ImageFont.truetype(fuente, tam)
        d.text(((W - d.textlength(txt, font=f)) / 2, y), txt, font=f, fill=color, stroke_width=3, stroke_fill=(0, 0, 0))
    centro('Rar~Amore', 220, 110, ORO)
    centro('Apoya la nutrición de tus articulaciones', 360, 44, (255, 255, 255), LIGERA)
    fw = ImageFont.truetype(FUENTE, 54)
    txt = 'WhatsApp 81 8466 8456'
    a = d.textlength(txt, font=fw) + 110
    d.rounded_rectangle(((W - a) / 2, 1500, (W + a) / 2, 1630), 65, fill=(37, 211, 102, 255))
    d.text(((W - a) / 2 + 55, 1535), txt, font=fw, fill=(255, 255, 255))
    centro('Envíos a todo México · Suplemento alimenticio', 1680, 36, (220, 220, 220), LIGERA)
    img.save(ruta)


# voz
mp3 = TMP / 'voz.mp3'
req = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST',
                             data=json.dumps({'text': TEXTO, 'format': 'mp3', 'reference_id': VOZ}).encode(),
                             headers={'Authorization': 'Bearer ' + os.environ['FISH_API_KEY'],
                                      'Content-Type': 'application/json', 'model': 's2-pro'})
mp3.write_bytes(urllib.request.urlopen(req, timeout=300).read())
clips = [AQUI / 'clips' / f'C{i}.mp4' for i in (1, 2, 3, 4)]
d = [dur(c) for c in clips]
ini = [sum(d[:i]) - i * CRUCE for i in range(4)]
total = sum(d) - 3 * CRUCE
voz = dur(mp3)
cola = max(0.0, voz + 0.8 - total)
etiqueta(TMP / 'e1.png', 'Mapa articular', 330, 900)
banda(TMP / 'b1.png', 'Nutrición para tu cartílago')
etiqueta(TMP / 'e2.png', 'Colágeno · Magnesio', 760, 1000, -1)
etiqueta(TMP / 'e3.png', 'Calcio · Vitamina D', 300, 1150)
cierre(TMP / 'cierre.png')
capas = [('e1.png', 2.0, ini[1] - 0.2), ('b1.png', ini[1], ini[2]), ('e2.png', ini[1] + 1.2, ini[2] - 0.2),
         ('e3.png', ini[2] - 0.2, ini[2] + 2.6), ('cierre.png', ini[3] + 1.0, 999)]
entradas = sum([['-i', str(c)] for c in clips], []) + ['-i', str(mp3)] + sum([['-i', str(TMP / c)] for c, _, _ in capas], [])
esc = 'scale=1080:1920:flags=lanczos,setsar=1,fps=30,format=yuv420p'
f = ''.join(f'[{i}:v]{esc}[v{i}];' for i in range(4))
f += f'[v3]tpad=stop_mode=clone:stop_duration={cola:.2f}[v3p];'
f += f'[v0][v1]xfade=transition=fade:duration={CRUCE}:offset={ini[1]:.2f}[x1];[x1][v2]xfade=transition=fade:duration={CRUCE}:offset={ini[2]:.2f}[x2];'
f += f'[x2][v3p]xfade=transition=fade:duration={CRUCE}:offset={ini[3]:.2f}[x3];'
prev = 'x3'
for k, (_, a, b) in enumerate(capas):
    f += f"[{prev}][{5 + k}:v]overlay=0:0:enable='between(t,{a:.2f},{b:.2f})'[o{k}];"; prev = f'o{k}'
f += f'[{prev}]format=yuv420p[v];'
f += f'[0:a][1:a]acrossfade=d={CRUCE}[a1];[a1][2:a]acrossfade=d={CRUCE}[a2];[a2][3:a]acrossfade=d={CRUCE},apad,volume=0.3[amb];'
f += '[4:a]adelay=400|400,loudnorm=I=-16:TP=-1.5[vz];[amb][vz]amix=inputs=2:duration=longest:normalize=0[a]'
largo = total + cola
salida = AQUI / 'final' / 'RarAmore_cartilago_rayosX.mp4'
ff([*entradas, '-filter_complex', f, '-map', '[v]', '-map', '[a]', '-t', f'{largo:.2f}', '-c:v', 'libx264', '-preset', 'slow',
    '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', str(TMP / 'hd.mp4')])
ff(['-i', str(TMP / 'hd.mp4'), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1',
    '-pix_fmt', 'yuv420p', '-preset', 'slow', '-crf', '22', '-maxrate', '2600k', '-bufsize', '5200k', '-c:a', 'aac', '-ar', '44100',
    '-ac', '2', '-b:a', '128k', '-movflags', '+faststart', str(salida)])
print(salida, f'{largo:.1f} s, voz {voz:.1f} s')
