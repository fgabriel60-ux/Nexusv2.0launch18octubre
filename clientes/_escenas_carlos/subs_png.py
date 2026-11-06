"""Subtítulos como PNG (el ffmpeg de imageio no trae drawtext). trozos(wav, guion) → [(ini, fin, texto)] con tiempos de Whisper
y TEXTO del guion real; png_sub(texto, ruta) dibuja blanco con borde negro, centrado, para overlay a y=H*0.78."""
import re
from PIL import Image, ImageDraw, ImageFont
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


def trozos(wav, guion, maxp=4, desfase=0.0):
    from faster_whisper import WhisperModel
    seg, _ = WhisperModel('medium', compute_type='int8').transcribe(str(wav), language='es', word_timestamps=True)
    pal = [(w.start, w.end) for s in seg for w in s.words]; g = guion.split()
    if len(pal) != len(g):   # reparte el guion proporcional si Whisper partió distinto
        a, b = pal[0][0], pal[-1][1]; n = len(g); pal = [(a + (b - a) * i / n, a + (b - a) * (i + 1) / n) for i in range(n)]
    out, cur = [], []
    for (a, b), w in zip(pal, g):
        cur.append((a, b, w))
        if len(cur) >= maxp or w[-1:] in '.,?!':
            out.append(cur); cur = []
    if cur: out.append(cur)
    return [(tr[0][0] + desfase, (out[i + 1][0][0] if i + 1 < len(out) else tr[-1][1] + .4) + desfase, ' '.join(w for _, _, w in tr)) for i, tr in enumerate(out)]


def png_sub(texto, ruta, ancho=720, tam=44):
    f = ImageFont.truetype(FB, tam); im = Image.new('RGBA', (ancho, tam + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    while d.textlength(texto, font=f) > ancho - 40: tam -= 2; f = ImageFont.truetype(FB, tam)
    d.text(((ancho - d.textlength(texto, font=f)) / 2, 10), texto, font=f, fill='white', stroke_width=4, stroke_fill='black'); im.save(ruta)


def overlays(lista, base_idx, etiqueta='v', y='H*0.78'):
    """lista [(ini, fin, png_input_idx)] → cadena filter_complex que encadena overlays sobre [base] y deja [etiqueta]."""
    fc, cur = '', base_idx
    for k, (a, b, i) in enumerate(lista):
        nxt = f'o{k}' if k < len(lista) - 1 else etiqueta
        fc += f"[{cur}][{i}:v]overlay=x=(W-w)/2:y={y}:enable='between(t,{a:.2f},{b:.2f})'[{nxt}];"; cur = nxt
    return fc
