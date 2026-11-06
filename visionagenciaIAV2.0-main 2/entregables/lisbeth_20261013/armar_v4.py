"""Lisbeth v4: sin 'vista al mar' (el terreno está a 20 min del mar) y lugares de plusvalía con las imágenes reales, completas, sin retocar."""
import json, os, subprocess, urllib.request
from pathlib import Path
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
FUENTE = str(AQUI.parent / 'modelos_modal' / 'fuentes' / 'Montserrat.ttf')
W, H = 1080, 1920
TMP = AQUI / 'tmp_v4'; TMP.mkdir(exist_ok=True)
A = AQUI / 'anterior' / 'lisbeth'
P = AQUI / 'refs' / 'plusvalia'
VOZ = os.environ.get('VOZ_LISBETH', '561fe660218349598b7570bab1c8148b')  # "Mexicana" (provisional)
TEXTO = ('Hay una gran diferencia entre comprar un terreno... y comprar el terreno correcto. Este terreno tiene medidas '
         'equilibradas, buen acceso, y espacio para construir la casa que imaginas, a solo veinte minutos del mar. Y está en una zona con '
         'proyección: cerca del nuevo aeropuerto, de hoteles y de nuevos desarrollos. Escríbeme y te comparto toda la información.')
# (tipo, fuente, segundos base, letrero)  — clip = toma del video anterior; foto = imagen real completa; lote = foto del terreno a pantalla completa
TOMAS = [('clip', 'toma2', 4.8, 'MEDIDAS EQUILIBRADAS'), ('clip', 'toma4', 4.8, 'ESPACIO PARA TU CASA'),
         ('lote', AQUI / 'refs' / 'lote.png', 3.6, 'A 20 MINUTOS DEL MAR'),
         ('foto', P / 'aeropuerto.jpg', 3.0, 'NUEVO AEROPUERTO'), ('foto', P / 'aeropista.jpg', 3.0, 'AEROPISTA CHALACATEPEC'),
         ('foto', P / 'hotel.jpg', 3.0, 'HOTELES'), ('foto', P / 'entorno.jpg', 3.4, 'ENTORNO NATURAL')]


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1500:])


def dur(p):
    o = subprocess.run([FF, '-i', str(p)], capture_output=True, text=True).stderr
    h, m, s = o.split('Duration: ')[1].split(',')[0].split(':'); return int(h) * 3600 + int(m) * 60 + float(s)


def fuente(t, peso='Black'):
    f = ImageFont.truetype(FUENTE, t); f.set_variation_by_name(peso); return f


def png(ruta, txt, y, tam=78, color=(255, 255, 255), peso='Black'):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    while d.textlength(txt, font=fuente(tam, peso)) > W - 100: tam -= 4
    f = fuente(tam, peso); d.text(((W - d.textlength(txt, font=f)) / 2, y), txt, font=f, fill=color, stroke_width=6, stroke_fill=(0, 0, 0))
    img.save(ruta)


def lienzo(src, ruta, completa):
    """completa=True: la imagen entera (sin recortar) sobre su propio fondo desenfocado. False: relleno vertical."""
    im = Image.open(src).convert('RGB')
    fondo = im.resize((W, H), Image.LANCZOS) if not completa else im
    if completa:
        e = max(W / im.width, H / im.height); fondo = im.resize((round(im.width * e), round(im.height * e)), Image.LANCZOS)
        x, y = (fondo.width - W) // 2, (fondo.height - H) // 2
        fondo = fondo.crop((x, y, x + W, y + H)).filter(ImageFilter.GaussianBlur(40))
        e = min(1000 / im.width, 1200 / im.height); fg = im.resize((round(im.width * e), round(im.height * e)), Image.LANCZOS)
        fondo.paste(fg, ((W - fg.width) // 2, (H - fg.height) // 2 + 40))
    else:
        e = max(W / im.width, H / im.height); fondo = im.resize((round(im.width * e), round(im.height * e)), Image.LANCZOS)
        x, y = (fondo.width - W) // 2, (fondo.height - H) // 2; fondo = fondo.crop((x, y, x + W, y + H))
    fondo.save(ruta)


mp3 = TMP / 'voz.mp3'
req = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST',
                             data=json.dumps({'text': TEXTO, 'format': 'mp3', 'reference_id': VOZ}).encode(),
                             headers={'Authorization': 'Bearer ' + os.environ['FISH_API_KEY'], 'Content-Type': 'application/json', 'model': 's2-pro'})
mp3.write_bytes(urllib.request.urlopen(req, timeout=300).read())
voz = dur(mp3)
factor = (voz + 1.2) / sum(t for _, _, t, _ in TOMAS)
esc = 'scale=1080:1920:flags=lanczos,setsar=1,fps=30,format=yuv420p'
segs, t0, capas = [], 0.0, []
for k, (tipo, fuente_, t, letrero) in enumerate(TOMAS):
    d = t * factor; s = TMP / f'{k}.mp4'
    if tipo == 'clip':
        src = A / f'{fuente_}_00001_.mp4'; lento = min(1.0, dur(src) / d)
        ff(['-i', str(src), '-filter_complex', f'[0:v]setpts=PTS/{lento:.4f},{esc},tpad=stop_mode=clone:stop_duration=3[v]', '-map', '[v]',
            '-t', f'{d:.2f}', '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '17', str(s)])
    else:
        im = TMP / f'{k}.png'; lienzo(fuente_, im, tipo == 'foto'); n = int(d * 30) + 1
        ff(['-loop', '1', '-i', str(im), '-vf', f"zoompan=z='1+0.06*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s=1080x1920:fps=30,format=yuv420p",
            '-t', f'{d:.2f}', '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '17', str(s)])
    ini_ultima = t0
    segs.append(s); r = TMP / f'l{k}.png'; png(r, letrero, 200 if tipo == 'foto' else 260); capas.append((r, t0 + 0.2, t0 + d - 0.2)); t0 += d
lista = TMP / 'lista.txt'; lista.write_text(''.join(f"file '{s}'\n" for s in segs))
png(TMP / 'cta.png', 'ESCRÍBEME Y TE COMPARTO TODA LA INFORMACIÓN', 1560, 52, (255, 214, 120), 'ExtraBold')
capas.append((TMP / 'cta.png', ini_ultima + 0.3, t0))
entr = ['-f', 'concat', '-safe', '0', '-i', str(lista), '-i', str(mp3)] + sum([['-i', str(r)] for r, _, _ in capas], [])
f, prev = '', '0:v'
for j, (_, a, b) in enumerate(capas):
    f += f"[{prev}][{j + 2}:v]overlay=0:0:enable='between(t,{a:.2f},{b:.2f})'[o{j}];"; prev = f'o{j}'
f += f'[{prev}]format=yuv420p[v];[1:a]adelay=500|500,loudnorm=I=-15:TP=-1.5,apad[a]'
sal = AQUI / 'final' / 'Lisbeth_terreno_v4.mp4'
ff([*entr, '-filter_complex', f, '-map', '[v]', '-map', '[a]', '-t', f'{t0:.2f}', '-c:v', 'libx264', '-profile:v', 'main',
    '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', '44100', '-b:a', '128k', '-movflags', '+faststart', str(TMP / 'hd.mp4')])
ff(['-i', str(TMP / 'hd.mp4'), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p',
    '-crf', '21', '-c:a', 'copy', '-movflags', '+faststart', str(sal)])
print(sal, f'{t0:.1f} s, voz {voz:.1f} s')
