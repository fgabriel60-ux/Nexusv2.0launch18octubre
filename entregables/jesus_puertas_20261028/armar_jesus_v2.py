"""v2 (30 oct, cambios de Glimmer 5→7.5/10): precio de parota en J2 y cierre que pide medidas y colonia (mensajes calificados). Video de Jesús (carpintero, Mazatlán): fotos reales de sus trabajos con zoom suave, su voz clonada (Fish), subtítulos y tarjetas de precio con SUS precios reales.
720x1280, H.264 Main. Frases en voz_jesus.py."""
import subprocess
from pathlib import Path
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
FOTOS = Path('/workspaces/Nexusv2.0launch18octubre/clientes/Jesus_Puertas/whatsapp/del_cliente')
FUENTE = '/workspaces/Nexusv2.0launch18octubre/visionagenciaIAV2.0-main 2/entregables/modelos_modal/fuentes/Montserrat.ttf'
W, H = 720, 1280
MADERA, CREMA, VERDE = (122, 74, 40), (250, 243, 232), (37, 160, 90)
TMP = AQUI / 'tmp'; TMP.mkdir(exist_ok=True)
# (frase, foto, tarjeta)
ESCENAS = [('J1', '20261027_175649_image.jpg', None), ('J2b', '20261027_175651_image.jpg', ('PUERTA DE PAROTA · DESDE', '$7,000', 'con marco y vistas')),
           ('J3', '20261027_175649_image.jpg', ('OFERTA', '$3,500', 'Puerta económica · chapa, bisagras\ne instalación incluidas')),
           ('J4', '20261027_175920_image.jpg', ('COCINA EN MELAMINA', '$8,000', 'por metro lineal · gabinete alto y bajo')),
           ('J5b', '20261027_180532_image.jpg', ('WHATSAPP · TE COTIZO HOY', 'Medidas', 'y tu colonia'))]
TEXTO = {'J1': '¿Buscas puertas o cocinas\nen Mazatlán? Soy Jesús,\ncarpintero.', 'J2b': 'Puertas de parota desde\n$7,000 con marco y vistas.',
         'J3': 'Puerta económica\ncon chapa, bisagras\ne instalación.', 'J4': 'Cocina en melamina,\nel metro lineal.', 'J5b': 'Mándame tus medidas\ny tu colonia por WhatsApp.'}


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1500:])


def dur(p):
    o = subprocess.run([FF, '-i', str(p)], capture_output=True, text=True).stderr
    h, m, s = o.split('Duration: ')[1].split(',')[0].split(':'); return int(h) * 3600 + int(m) * 60 + float(s)


def fu(t, peso=800):
    f = ImageFont.truetype(FUENTE, t); ej = f.get_variation_axes()[0]
    f.set_variation_by_axes([max(ej['minimum'], min(ej['maximum'], peso))]); return f


def fondo(nombre):
    im = Image.open(FOTOS / nombre).convert('RGB')
    gris = im.convert('L').point(lambda v: 255 if v > 18 else 0); im = im.crop(gris.getbbox())   # quita franjas negras
    bg = im.resize((W * 2, H * 2)).filter(ImageFilter.GaussianBlur(30)).point(lambda v: int(v * 0.55))
    esc = min(W * 2 / im.width, H * 2 * 0.62 / im.height); fg = im.resize((int(im.width * esc), int(im.height * esc)), Image.LANCZOS)
    bg.paste(fg, ((W * 2 - fg.width) // 2, int(H * 2 * 0.17))); return bg


def capa(frase, tarjeta):
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    f = fu(40, 800); lineas = TEXTO[frase].split('\n'); y = 930 if tarjeta else 990
    if not tarjeta: y = 1010
    for l in lineas:
        w = d.textlength(l, font=f); d.rounded_rectangle((W / 2 - w / 2 - 14, y - 4, W / 2 + w / 2 + 14, y + 52), 10, fill=(0, 0, 0, 150))
        d.text((W / 2 - w / 2, y), l, font=f, fill=(255, 255, 255, 255)); y += 62
    if tarjeta:
        a, b, c = tarjeta; x0, y0, x1, y1 = 60, 120, W - 60, 330
        d.rounded_rectangle((x0, y0, x1, y1), 26, fill=CREMA + (240,), outline=MADERA + (255,), width=5)
        d.text((W / 2, y0 + 20), a, font=fu(30, 800), fill=MADERA, anchor='mt')
        d.text((W / 2, y0 + 58), b, font=fu(92, 900), fill=(40, 26, 14), anchor='mt')
        for k, l in enumerate(c.split('\n')): d.text((W / 2, y0 + 168 + k * 30), l, font=fu(25, 600), fill=(70, 55, 40), anchor='mt')
    top = fu(30, 800); d.text((W / 2, 40), 'JESÚS · CARPINTERÍA · MAZATLÁN', font=top, fill=(255, 255, 255, 235), anchor='mt')
    return L


clips = []
for i, (fr, foto, tj) in enumerate(ESCENAS):
    d = dur(AQUI / 'voz' / f'{fr}.wav') + (0.35 if fr != 'J5b' else 0.9)
    base = TMP / f'f{i}.jpg'; fondo(foto).save(base, quality=93); capa(fr, tj).save(TMP / f'c{i}.png')
    fps = 25; n = int(d * fps) + 1; z = 'zoom+0.0009' if i % 2 == 0 else 'if(eq(on,1),1.14,zoom-0.0009)'
    ff(['-i', str(base), '-i', str(TMP / f'c{i}.png'), '-filter_complex',
        f"[0:v]zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={fps}[v];[v][1:v]overlay=0:0:format=auto,format=yuv420p[o]",
        '-map', '[o]', '-frames:v', str(n), '-an', '-c:v', 'libx264', '-profile:v', 'main', '-crf', '20', str(TMP / f'v{i}.mp4')])
    clips.append((TMP / f'v{i}.mp4', AQUI / 'voz' / f'{fr}.wav', d))
lista = TMP / 'lista.txt'; lista.write_text(''.join(f"file '{c}'\n" for c, _, _ in clips))
ff(['-f', 'concat', '-safe', '0', '-i', str(lista), '-c', 'copy', str(TMP / 'mudo.mp4')])
# audio: cada frase en su escena
ent, flt, ini = [], [], 0.0
for k, (_, w, d) in enumerate(clips):
    ent += ['-i', str(w)]; flt.append(f'[{k}:a]adelay={int(ini * 1000)}|{int(ini * 1000)},apad[a{k}]'); ini += d
mezcla = ''.join(f'[a{k}]' for k in range(len(clips))) + f'amix=inputs={len(clips)}:normalize=0:duration=first[a]'
ff([*ent, '-filter_complex', ';'.join(flt) + ';' + mezcla, '-map', '[a]', '-t', f'{ini:.2f}', str(TMP / 'voz.wav')])
ff(['-i', str(TMP / 'mudo.mp4'), '-i', str(TMP / 'voz.wav'), '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', str(AQUI / 'Jesus_carpinteria_v2.mp4')])
print('listo', ini)
