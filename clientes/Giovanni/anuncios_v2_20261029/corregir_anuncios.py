"""Giovanni · anuncios corregidos según Glimmer (28-29 oct): sin promesa de plazo («15 días», «no pierdes días»), precio unificado «desde $20,000» (el que él mismo propuso).
Uso: python3 corregir_anuncios.py"""
import glob
from pathlib import Path
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
SRC = AQUI.parent / 'whatsapp' / 'hechos_por_mi'
FU = Path('/workspaces/Nexusv2.0launch18octubre/visionagenciaIAV2.0-main 2/entregables')
ANTON = str(next(FU.rglob('Anton-Regular.ttf')))
INTER = '/workspaces/Nexusv2.0launch18octubre/clientes/Carlos_Nexus/pixar/fonts/Inter-Bold.ttf'


def borrar(img, caja, claro=170, dil=9):
    """Quita el texto claro dentro de la caja (inpainting)."""
    x0, y0, x1, y1 = caja
    a = np.array(img.convert('RGB')); g = a[y0:y1, x0:x1].astype(int)
    m = ((g.min(axis=2) > claro) | (np.abs(g[..., 0] - g[..., 2]) < 0) ).astype(np.uint8) * 255
    m = cv2.dilate(m, np.ones((dil, dil), np.uint8))
    full = np.zeros(a.shape[:2], np.uint8); full[y0:y1, x0:x1] = m
    return Image.fromarray(cv2.inpaint(cv2.cvtColor(a, cv2.COLOR_RGB2BGR), full, 7, cv2.INPAINT_TELEA)[..., ::-1])


def texto(img, t, caja, fuente, color, sombra=(0, 0, 0), alinea='c'):
    d = ImageDraw.Draw(img); x0, y0, x1, y1 = caja; tam = y1 - y0
    f = ImageFont.truetype(fuente, tam)
    while d.textlength(t, font=f) > x1 - x0 and tam > 10: tam -= 2; f = ImageFont.truetype(fuente, tam)
    w = d.textlength(t, font=f); x = x0 + (x1 - x0 - w) / 2 if alinea == 'c' else x0
    bb = d.textbbox((0, 0), t, font=f); y = y0 + (y1 - y0 - (bb[3] - bb[1])) / 2 - bb[1]
    d.text((x + 3, y + 3), t, font=f, fill=sombra); d.text((x, y), t, font=f, fill=color)


def A():
    img = Image.open(SRC / '20261028_142956_image.jpg').convert('RGB')
    img = borrar(img, (540, 612, 1075, 672), claro=200)                       # «Tú no pierdes días.»
    texto(img, 'Todo claro y sin sorpresas.', (545, 618, 1075, 668), INTER, (255, 255, 255), alinea='c')
    oro = tuple(int(v) for v in np.array(img)[760, 70])                       # color liso de la caja dorada
    d = ImageDraw.Draw(img); d.rectangle((70, 712, 548, 1098), fill=oro)
    azul = (12, 22, 52)
    texto(img, 'PRECIO', (85, 745, 535, 905), ANTON, azul, sombra=oro)
    texto(img, 'ÚNICO', (85, 905, 535, 1065), ANTON, azul, sombra=oro)
    img.save(AQUI / 'A_menos_tramites_v2.jpg', quality=93)


def precio(origen, caja, salida, centro_extra=0):
    img = Image.open(SRC / origen).convert('RGB')
    img = borrar(img, caja, claro=185, dil=11)
    texto(img, '$20,000', (caja[0] + 4, caja[1] + 2, caja[2] - 4, caja[3] - 2), ANTON, (250, 250, 250), sombra=(60, 0, 0))
    img.save(AQUI / salida, quality=93)


if __name__ == '__main__':
    A()
    precio('20261028_142957_image.jpg', (92, 888, 420, 1018), 'B_proceso_claro_v2.jpg')
    precio('20261028_142958_image.jpg', (58, 702, 392, 850), 'C_cierre_en_paz_v2.jpg')
    print('listo')
