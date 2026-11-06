"""Andrés · contratista (656 130 0006) · muestra v1 (30 oct): SUS 25 fotos reales con zoom, voz de locutor (él pidió «mejor otra voz»), guion de Glimmer
adaptado al brief (datos.txt): sin ciudad ni nombre comercial porque no están confirmados; antes/después real del baño. Sin GPU."""
import json, os, subprocess, urllib.request, uuid
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
WA = AQUI.parent / 'whatsapp'
TMP = AQUI / 'tmp'; TMP.mkdir(exist_ok=True)
FUENTE = '/workspaces/Nexusv2.0launch18octubre/visionagenciaIAV2.0-main 2/entregables/modelos_modal/fuentes/Montserrat.ttf'
LLAVE = os.environ['FISH_API_KEY']
W, H = 720, 1280
ROJO = (230, 126, 20)
# (frase, voz, subtítulo, [(archivo, inicio_s)…])  · varias tomas = cortes rápidos dentro de la frase
F = lambda n: WA / f'{n}.jpg'
ESCENAS = [
    ('A1', '¿Quieres una obra real, con factura y sin sorpresas?', '¿Obra real, con factura y sin sorpresas?', [(F('122C026DFA98'), 0)]),
    ('A2', 'Construcción desde cero, ampliaciones y remodelaciones.', 'Construcción desde cero · ampliaciones · remodelación', [(F('030E5F2B2A54'), 0), (F('3A7A401D8622'), 0)]),
    ('A3', 'Herrería general y estructural, albercas, cisternas e impermeabilizado.', 'Herrería · albercas · cisternas · impermeabilizado', [(F('57863B9B440E'), 0), (F('3DAD6DC4F2D6'), 0)]),
    ('A4', 'Mira el antes y el después.', 'Antes y después real', [(F('7F01FAA98CDF'), 0), (F('47A897391FF7'), 0)]),
    ('A5', 'Residencial y comercial. Estamos dados de alta en Hacienda y facturamos.', 'Residencial y comercial · facturamos', [(F('20B424BCDCE3'), 0), (F('5C40E4DA49F6'), 0)]),
    ('A6', 'Escríbenos por uatsap y cotiza tu proyecto.', 'Escríbenos por WhatsApp y cotiza tu proyecto', [(F('3C6D8459198C'), 0)]),
]


def ff(a):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1500:])


def dur(p):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)], capture_output=True, text=True).stdout)


def voz_id():
    return '5e8ee00af4dd4f438d66fea8efa4baf4'  # voz Fish masculina de locutor (él no quiere su voz)


def tts(texto, ruta, vid):
    if ruta.exists(): return
    r = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST', data=json.dumps({'text': texto, 'format': 'wav', 'reference_id': vid}).encode(),
                               headers={'Authorization': 'Bearer ' + LLAVE, 'Content-Type': 'application/json', 'model': 's2-pro'})
    ruta.write_bytes(urllib.request.urlopen(r, timeout=300).read())


def fu(t, peso=800):
    f = ImageFont.truetype(FUENTE, t)
    try: f.set_variation_by_axes([peso])
    except Exception: pass
    return f


def capa(sub, ruta):
    im = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(im)
    d.text((W / 2, 46), 'CONSTRUCCIÓN Y REMODELACIÓN', font=fu(28, 800), fill=(255, 255, 255, 235), anchor='mt', stroke_width=3, stroke_fill=(0, 0, 0, 200))
    f = fu(44, 900); lineas, l = [], ''
    for w in sub.upper().split():
        if d.textlength((l + ' ' + w).strip(), font=f) > 620: lineas.append(l); l = w
        else: l = (l + ' ' + w).strip()
    lineas.append(l); y = 1000 - 30 * (len(lineas) - 1)
    for ln in lineas:
        d.text((W / 2, y), ln, font=f, fill='white', anchor='mm', stroke_width=7, stroke_fill=ROJO); y += 58
    im.save(ruta)


def tarjeta(ruta):
    im = Image.new('RGB', (W, H), (18, 20, 24)); d = ImageDraw.Draw(im)
    c = lambda t, y, s, col, p=900: d.text((W / 2, y), t, font=fu(s, p), fill=col, anchor='mt')
    c('CONSTRUCCIÓN', 300, 70, (255, 255, 255)); c('Y REMODELACIÓN', 385, 54, ROJO); c('RESIDENCIAL Y COMERCIAL', 480, 34, (210, 210, 210), 700)
    c('Facturamos · obra civil · herrería · albercas', 560, 28, (170, 170, 170), 500)
    a = 520; d.rounded_rectangle(((W - a) / 2, 760, (W + a) / 2, 860), 50, fill=(37, 211, 102)); c('Cotiza por WhatsApp', 790, 36, (255, 255, 255), 800)
    c('656 130 0006', 920, 64, (255, 255, 255))
    im.save(ruta)


def toma(src, ini, seg, ruta):
    base = f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps=30'
    if src.suffix == '.jpg':
        n = int(seg * 30) + 1
        ff(['-i', str(src), '-vf', f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},zoompan=z='min(zoom+0.0012,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps=30,setsar=1",
            '-frames:v', str(n), '-an', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', str(ruta)])
    else:
        ff(['-ss', str(ini), '-i', str(src), '-t', f'{seg:.2f}', '-vf', base, '-an', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', str(ruta)])


vid = voz_id(); print('voz', vid)
segs, voces = [], []
for i, (k, frase, sub, tomas) in enumerate(ESCENAS):
    w = TMP / f'{k}.wav'; tts(frase, w, vid); d = dur(w) + 0.25
    partes = []
    for j, (src, ini) in enumerate(tomas):
        p = TMP / f'{k}_{j}.mp4'; toma(src, ini, d / len(tomas) + 0.05, p); partes.append(p)
    (TMP / f'{k}.txt').write_text(''.join(f"file '{p}'\n" for p in partes))
    ff(['-f', 'concat', '-safe', '0', '-i', str(TMP / f'{k}.txt'), '-c', 'copy', str(TMP / f'{k}_base.mp4')])
    capa(sub, TMP / f'{k}.png')
    s = TMP / f'seg{i}.mp4'
    ff(['-i', str(TMP / f'{k}_base.mp4'), '-i', str(TMP / f'{k}.png'), '-i', str(w), '-filter_complex', '[0:v][1:v]overlay=0:0[v];[2:a]aresample=44100,aformat=channel_layouts=stereo,apad[a]',
        '-map', '[v]', '-map', '[a]', '-t', f'{d:.2f}', '-c:v', 'libx264', '-profile:v', 'main', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', str(s)])
    segs.append(s)
tarjeta(TMP / 'tarjeta.png')
ff(['-loop', '1', '-t', '3', '-i', str(TMP / 'tarjeta.png'), '-f', 'lavfi', '-t', '3', '-i', 'anullsrc=r=44100:cl=stereo', '-vf', 'fps=30,format=yuv420p', '-c:v', 'libx264', '-profile:v', 'main', '-c:a', 'aac', '-shortest', str(TMP / 'segT.mp4')])
segs.append(TMP / 'segT.mp4')
(TMP / 'lista.txt').write_text(''.join(f"file '{s}'\n" for s in segs))
sal = AQUI / 'Contratista_muestra_v1.mp4'
ff(['-f', 'concat', '-safe', '0', '-i', str(TMP / 'lista.txt'), '-c:v', 'libx264', '-profile:v', 'main', '-crf', '23', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(sal)])
print(sal, round(dur(sal), 1), 's', sal.stat().st_size // 1024, 'KB')
