"""Lisbeth v3 · corrige la subida y la construcción, que salieron giradas 90° (Qwen rotó su foto aérea horizontal). Ahora la vista aérea es SU foto
real puesta en vertical aquí mismo (sin IA: la foto completa al centro y la misma foto desenfocada arriba y abajo) y desde ella se genera la versión
construida. Uso: python3 lisbeth_v3_aereo_fix.py"""
import io, sys
from pathlib import Path
from PIL import Image, ImageFilter, ImageOps
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/_productor')
from escenas_modal import app, escenas

AQUI = Path(__file__).resolve().parent
AEREO = AQUI.parent / 'whatsapp' / 'nuevas_1024' / '24_130408_image.jpg'


def vertical(foto, w=720, h=1280):
    im = ImageOps.exif_transpose(Image.open(foto)).convert('RGB')
    fondo = ImageOps.fit(im, (w, h), Image.LANCZOS).filter(ImageFilter.GaussianBlur(28))
    centro = ImageOps.fit(im, (w, int(w * 1.15)), Image.LANCZOS, centering=(0.5, 0.5))   # recorte un poco más alto que la foto para llenar más
    fondo.paste(centro, (0, (h - centro.height) // 2))
    b = io.BytesIO(); fondo.save(b, 'PNG'); return b.getvalue()


SIN = ' Vertical 9:16, realista, nítida, sin texto, sin letras.'
FIN = ' No text. Audio: soft wind, no speech.'
if __name__ == '__main__':
    aereo_v = vertical(AEREO)
    (AQUI / 'v3' / 'L3_aereo_v.png').write_bytes(aereo_v)
    listos = {'L3_calle': (AQUI / 'v3' / 'L3_calle.png').read_bytes(), 'L3_aereo_v': aereo_v}
    cuadros = {'L3_construido_v': (['aereo_v'], 'La MISMA vista aérea de dron, mismo encuadre vertical, misma orientación (el cielo arriba), misma loma y misma carretera curva, '
                                   'pero ahora sobre el terreno hay lotes trazados con calles de terracería y varias casas modernas de una y dos plantas ya construidas, '
                                   'con árboles y jardines.' + SIN)}
    tomas = [('LIS3_sube_v', 'L3_calle', 'Continuous single drone shot, no cut, the horizon always stays level and the sky stays at the top: the camera rises smoothly '
              'and fast from the roadside, flying up and forward over the land until it settles into the stable aerial view of the same hill, land and curving road. '
              'The woman stays on the ground and gets small below. No phone, no rotation, no spinning.' + FIN, 4.0, 'L3_aereo_v'),
             ('LIS3_construye_v', 'L3_aereo_v', 'Static aerial drone shot, time-lapse, no camera rotation: on the same land, dirt streets get traced and modern houses '
              'rise one by one with gardens, smooth and realistic; the hill and the curving road stay exactly the same.' + FIN, 4.0, 'L3_construido_v')]
    with app.run():
        res = escenas.remote('lisbeth_v3', {'aereo_v': aereo_v}, cuadros, tomas, 4, listos)
    for n, b in res.items():
        (AQUI / 'v3' / n).write_bytes(b); print('guardado', n)
