"""Pixar v5 de Carlos (caso Guillermo), 31 oct: estilo del reel de referencia @_k.elsie (DfHj27sRdQu): conversación cliente ↔ agencia
con palabra clave grande en serif itálica y brillo, y tarjetas tipo app que aparecen (calificación 8.2, $4.56 por mensaje, mensajes llegando).
Orden = método de Glimmer: dolor → qué hicimos → validación → prueba (celular + calificación) → oferta → cierre «muestra gratis». Sin GPU."""
import json, pathlib, subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = pathlib.Path(__file__).resolve().parent
G = AQUI.parent
RAIZ = G.parents[1]
TMP = AQUI / 'tmp'; TMP.mkdir(exist_ok=True)
MONT = str(RAIZ / 'visionagenciaIAV2.0-main 2/entregables/modelos_modal/fuentes/Montserrat.ttf')
SERIF = str(RAIZ / 'clientes/_productor/fuentes/PlayfairDisplay-Italic[wght].ttf')
W, H = 720, 1280
CV, CG = G / 'pixar_v4_20261030' / 'salida', G / 'pixar_v2_20261030' / 'salida'
VC, VG = G / 'pixar_v3_20261030' / 'voz', G / 'obrero_20261029' / 'voz'
# (clip, voz, palabra grande, subtítulo, tarjeta tipo app o None)
TOMAS = [(CG / 'T1_gui_urge.mp4', VG / 'g_urge.wav', '¿Qué crees?', 'Ya me urge volver a cotizar… ya quiero seguir agarrando', None),
         (CV / 'T2_car1.mp4', VC / 'c_1.wav', 'Guillermo', 'Hace zaguanes, cortinas, puertas y pérgolas', ('HERRERÍA · PUEBLA', 'Cliente desde octubre')),
         (CV / 'T3_car2.mp4', VC / 'c_2.wav', 'estrategia', 'Le hicimos su estrategia, sus volantes y su primer video', ('CALIFICACIÓN DE FACEBOOK', '8.2 / 10')),
         (CG / 'T4_gui_fregon.mp4', VG / 'g_fregon.wav', '¡Fregón!', '¡Se ve muy, muy fregón, eh!', None),
         (CV / 'T5_car3.mp4', VC / 'c_3.wav', 'fotos reales', 'Todo con sus fotos reales: esto se logra con inteligencia artificial', ('ANUNCIO 6/10', 'casi no llegan mensajes')),
         (CG / 'T6_gui_mensaje_chat.mp4', VG / 'g_mensaje.wav', 'mensajes', 'Quiero que me llegue el mensaje, cotizar y cerrar', ('ANUNCIO 8.2/10', '$4.56 por mensaje')),
         (CV / 'T7_car4.mp4', VC / 'c_4.wav', '4 videos', '4 videos al mes por $500', ('PLAN MENSUAL', 'estrategia + videos')),
         (AQUI / 'salida' / 'T9_cierre.mp4', AQUI / 'voz' / 'c_cierre.wav', 'muestra gratis', 'Te hago una muestra gratis para que veas el poder de mi método', ('NEXUS · VISIÓN AGENCIA', 'Escríbeme por WhatsApp'))]


def ff(a): subprocess.run(['ffmpeg', '-v', 'error', '-y', *a], check=True)


def dur(p): return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)], capture_output=True, text=True).stdout)


def fu(path, t, peso):
    f = ImageFont.truetype(path, t)
    try: f.set_variation_by_axes([peso])
    except Exception: pass
    return f


def envolver(d, txt, f, ancho):
    ls, l = [], ''
    for w in txt.split():
        if d.textlength((l + ' ' + w).strip(), font=f) > ancho: ls.append(l); l = w
        else: l = (l + ' ' + w).strip()
    return ls + [l]


def capa(grande, sub, tarjeta, ruta):
    im = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(im)
    # palabra clave grande en serif itálica con brillo (como la referencia)
    g = fu(SERIF, 84, 600); brillo = Image.new('RGBA', (W, H)); db = ImageDraw.Draw(brillo)
    db.text((W / 2, 150), grande, font=g, fill=(255, 120, 220, 255), anchor='mm'); brillo = brillo.filter(ImageFilter.GaussianBlur(18))
    im.alpha_composite(brillo); d.text((W / 2, 150), grande, font=g, fill='white', anchor='mm', stroke_width=2, stroke_fill=(40, 20, 40))
    # subtítulo limpio abajo
    f = fu(MONT, 34, 700); ls = envolver(d, sub, f, 600); y = 1060 - 22 * (len(ls) - 1)
    for ln in ls: d.text((W / 2, y), ln, font=f, fill='white', anchor='mm', stroke_width=5, stroke_fill=(0, 0, 0)); y += 46
    if tarjeta:   # tarjeta tipo app (vidrio esmerilado)
        x0, y0, y1 = 40, 800, 910
        x1 = x0 + 44 + max(d.textlength(tarjeta[0], font=fu(MONT, 20, 700)), d.textlength(tarjeta[1], font=fu(MONT, 34, 900)))
        caja = Image.new('RGBA', (W, H)); dc = ImageDraw.Draw(caja)
        dc.rounded_rectangle((x0, y0, x1, y1), 22, fill=(20, 20, 28, 185), outline=(255, 255, 255, 90), width=2)
        im.alpha_composite(caja)
        d.text((x0 + 22, y0 + 24), tarjeta[0], font=fu(MONT, 20, 700), fill=(200, 200, 210))
        d.text((x0 + 22, y0 + 56), tarjeta[1], font=fu(MONT, 34, 900), fill=(120, 255, 170) if '8.2' in tarjeta[1] or '$4.56' in tarjeta[1] else (255, 255, 255))
    im.save(ruta)


segs = []
for i, (clip, voz, grande, sub, tj) in enumerate(TOMAS):
    t = dur(voz) + 0.3
    capa(grande, sub, tj, TMP / f'c{i}.png')
    s = TMP / f's{i}.mp4'
    # la capa entra con un pequeño «pop» (escala) en 0.25 s
    ff(['-i', str(clip), '-i', str(voz), '-loop', '1', '-i', str(TMP / f'c{i}.png'), '-filter_complex',
        f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps=30,tpad=stop_mode=clone:stop_duration=3,setsar=1[b];"
        f"[2:v]format=rgba,fade=t=in:st=0:d=0.25:alpha=1[c];[b][c]overlay=0:0:shortest=1,format=yuv420p[v];[1:a]aresample=44100,aformat=channel_layouts=stereo,apad[a]",
        '-map', '[v]', '-map', '[a]', '-t', f'{t:.2f}', '-c:v', 'libx264', '-profile:v', 'main', '-crf', '20', '-c:a', 'aac', '-b:a', '128k', str(s)])
    segs.append(s)
(TMP / 'lista.txt').write_text(''.join(f"file '{s}'\n" for s in segs))
sal = G / 'Guillermo_Pixar_v5_metodo.mp4'
ff(['-f', 'concat', '-safe', '0', '-i', str(TMP / 'lista.txt'), '-c:v', 'libx264', '-profile:v', 'main', '-crf', '22', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(sal)])
print(sal, round(dur(sal), 1), 's')
