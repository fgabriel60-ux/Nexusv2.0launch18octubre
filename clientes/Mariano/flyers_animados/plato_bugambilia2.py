"""Cuadro limpio del flyer Bugambilia «La mejor opción» SIN Qwen (Qwen borraba el cielo azul): la escena (casa, árboles, cielo) es la del
flyer original intacta; arriba fondo blanco liso, franja gris lisa abajo, y la franja de BUGAMBILIA (letras-ventana) se completa con inpaint.
Salida: nuevos/bugambilia2/limpio_ok.png (720×1280 para H3) y plato_900.png (900×1600). Uso: python3 plato_bugambilia2.py"""
from pathlib import Path
import numpy as np, cv2
from PIL import Image

AQUI = Path(__file__).resolve().parent
ORIG = AQUI.parent / 'flyers_recibidos' / '1020_210408_4AF9D8.jpg'
BANDA = (722, 832)      # filas de la palabra BUGAMBILIA (letras = ventana a la foto)
ESCENA_FIN = 1358       # empieza la franja gris
GRIS = (94, 92, 95)


def mascara_letras(a):
    """Letras-ventana de BUGAMBILIA: dentro de la banda, todo lo que no es blanco de página."""
    y0, y1 = BANDA
    m = np.zeros(a.shape[:2], bool)
    m[y0:y1] = a[y0:y1].min(2) < 236
    return m


def main():
    a = np.asarray(Image.open(ORIG).convert('RGB')).copy()
    letras = mascara_letras(a)
    y0, y1 = BANDA
    plato = a.copy()
    # banda: la foto ORIGINAL dentro de las letras (erosionada 3 px para no arrastrar el borde claro antialias) y el resto (blanco entre letras)
    # se reconstruye por inpaint desde esas letras y desde la escena de abajo. Así el push-in digital no mete bordes fantasma en las letras-ventana.
    nucleo = cv2.erode(letras.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
    hueco = np.zeros(a.shape[:2], np.uint8)
    hueco[y0 - 30:y1 + 2] = 255
    hueco[nucleo] = 0
    tmp = a.copy()
    roi = slice(y0 - 60, y1 + 100)
    plato[roi] = cv2.inpaint(np.ascontiguousarray(tmp[roi][..., ::-1]), np.ascontiguousarray(hueco[roi]), 21, cv2.INPAINT_TELEA)[..., ::-1]
    plato[:y0 - 30] = 254
    for i, y in enumerate(range(y0 - 30, y0)):          # degradado suave hacia el blanco de arriba (lo tapa el panel blanco final)
        k = i / 30; plato[y] = (k * plato[y] + (1 - k) * 254).astype(np.uint8)
    plato[ESCENA_FIN:] = GRIS
    d = AQUI / 'nuevos' / 'bugambilia2'; d.mkdir(parents=True, exist_ok=True)
    Image.fromarray(plato).save(d / 'plato_900.png')
    Image.fromarray(plato).resize((720, 1280), Image.LANCZOS).save(d / 'limpio_ok.png')
    Image.fromarray((letras * 255).astype('uint8')).save(d / 'letras_mask.png')
    print('ok', letras.sum())


if __name__ == '__main__':
    main()
