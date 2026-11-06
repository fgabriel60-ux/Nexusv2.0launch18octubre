"""Flyer Anegocios 1080x1350: azul/amarillo de la marca, foto real del kit, todo el texto por código."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
A = Path(__file__).resolve().parent
W, H = 1080, 1350
FD = '/usr/share/fonts/truetype/dejavu/'
f = lambda s, b=True: ImageFont.truetype(FD + ('DejaVuSans-Bold.ttf' if b else 'DejaVuSans.ttf'), s)
AMAR, BLANCO, VERDE = (255, 232, 0), (255, 255, 255), (37, 211, 102)
img = Image.new('RGB', (W, H)); d = ImageDraw.Draw(img)
for y in range(H):  # degradado azul como el flyer de Fernando
    k = y / H; d.line((0, y, W, y), fill=(int(8 + 10 * k), int(70 + 20 * (1 - abs(k - .4))), int(185 - 55 * k)))
# resplandor
glow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(glow).ellipse((140, 380, 940, 920), fill=(70, 150, 255, 120))
img = Image.alpha_composite(img.convert('RGBA'), glow.filter(ImageFilter.GaussianBlur(120))).convert('RGB'); d = ImageDraw.Draw(img)
def borde(xy, s, fo, fill, anchor, grosor=0, col=(0, 40, 120)):
    d.text(xy, s, font=fo, fill=fill, anchor=anchor, stroke_width=grosor, stroke_fill=col)
# gancho
borde((W // 2, 82), '¿Todavía llevas tu tienda', f(66), BLANCO, 'mm')
borde((W // 2, 160), 'en libreta o Excel?', f(78), AMAR, 'mm')
# precio
borde((W // 2, 262), 'TODO POR', f(50), BLANCO, 'mm')
borde((W // 2 - 55, 392), '$3,500', f(200), AMAR, 'mm', 6)
borde((W // 2 + 405, 455), 'MXN', f(44), BLANCO, 'mm')
# foto real del kit
import numpy as np
orig = Image.open(A / 'refs' / 'fernando_image.jpg').convert('RGB')
arr = np.array(orig).astype(int)
# quitar los restos del '$3,500' original (amarillo) que entran en el recorte: se rellenan con el azul del fondo
amarillo = (arr[:, :, 0] > 170) & (arr[:, :, 1] > 140) & (arr[:, :, 2] < 150)
amarillo[420:, :] = False; amarillo[:, :360] = False
from PIL import ImageFilter as IF
m = Image.fromarray((amarillo * 255).astype('uint8')).filter(IF.MaxFilter(9))
m = np.array(m) > 0; m[420:, :] = False; m[:, :360] = False
fondo = np.array(orig.filter(IF.GaussianBlur(40))).astype(int)
arr[m] = np.array([14, 88, 205]) * 0.0 + fondo[m] * 0.0 + np.array([12, 82, 200])
orig = Image.fromarray(arr.astype('uint8'))
src = orig.crop((50, 374, 1210, 790))
src = src.resize((1000, round(416 * 1000 / 1160)), Image.LANCZOS)
mask = Image.new('L', src.size, 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, src.width, src.height), 40, fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(14)); img.paste(src, ((W - src.width) // 2, 530), mask); d = ImageDraw.Draw(img)
# lista de incluye
items = ['1 año de software', 'Impresora de tickets', 'Lector de códigos', 'Instalación', 'Capacitación', 'Soporte por 1 año']
for i, t in enumerate(items):
    col, row = i % 2, i // 2
    x = 90 + col * 480; y = 925 + row * 58
    d.ellipse((x, y - 20, x + 40, y + 20), fill=AMAR); d.text((x + 20, y), '✓', font=f(26), fill=(10, 50, 130), anchor='mm')
    d.text((x + 56, y), t, font=f(30), fill=BLANCO, anchor='lm')
# franja amarilla
d.rounded_rectangle((50, 1110, W - 50, 1190), 40, fill=AMAR); d.text((W // 2, 1150), 'PAGAS HASTA QUE ESTÉ FUNCIONANDO.', font=f(41), fill=(10, 40, 100), anchor='mm')
d.text((W // 2, 1222), 'App Android para tus rutas de venta · Software + tienda en línea', font=f(25, False), fill=(215, 230, 255), anchor='mm')
# CTA
d.rounded_rectangle((250, 1252, W - 250, 1322), 35, fill=VERDE); d.text((W // 2, 1287), 'Escríbenos por WhatsApp', font=f(34), fill=BLANCO, anchor='mm')
d.text((W // 2, 1334), 'anegocios.com', font=f(20), fill=(215, 230, 255), anchor='mm')
(A / 'final').mkdir(exist_ok=True); img.save(A / 'final' / 'Flyer_Anegocios_v1.png'); print('ok', img.size)
