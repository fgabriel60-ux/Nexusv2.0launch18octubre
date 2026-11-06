"""Iván · Fumicam v5 (30 oct): sus 3 fotos nuevas de fumigación animadas (H3, salida/A0-A2) + sus tomas reales anteriores + SU voz clonada + guion del plan 10/10/10 de Glimmer (lluvias → plagas, al detalle, zona y plaga por WhatsApp)."""
import json, os, subprocess, urllib.request, uuid
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
T = AQUI.parent / 'video' / 'tomas'
TMP = AQUI / 'tmp'; TMP.mkdir(exist_ok=True)
FUENTE = '/workspaces/Nexusv2.0launch18octubre/visionagenciaIAV2.0-main 2/entregables/modelos_modal/fuentes/Montserrat.ttf'
LLAVE = os.environ['FISH_API_KEY']
W, H = 720, 1280
ROJO = (20, 120, 60)
A = lambda n: AQUI / 'salida' / f'{n}.mp4'
I = lambda n: T / f'{n}.mp4'
ESCENAS = [
    ('F1', 'Con las lluvias, las plagas buscan meterse a tu casa: cucarachas, alacranes y termitas.', '¿Plagas con las lluvias?', [(A('A0'), 0.3), (I('I3_sala'), 0.3)]),
    ('F2', 'Aquí en Fumi Cam vamos al detalle: grieta por grieta y rincón por rincón, nada de fumigar a medias.', 'Al detalle: grieta por grieta', [(A('A1'), 0.3), (A('A2'), 0.3)]),
    ('F3', 'Técnicos reales en casas, clínicas, oficinas y negocios de Cuernavaca y CDMX.', 'Casas · clínicas · oficinas · negocios', [(I('I4_oficina'), 0.3), (I('I2_patio'), 0.3), (I('I6_pasillo'), 0.3)]),
    ('F4', 'Escríbenos por uatsap con tu zona y la plaga que tienes, y te cotizamos sin compromiso.', 'Tu zona + tu plaga → cotización', [(I('I1_cuarto'), 0.3)]),
]


def ff(a):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1500:])


def dur(p):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)], capture_output=True, text=True).stdout)


def voz_id():
    return '2e7509fae4af43c0b4166202aeff3918'


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
    d.text((W / 2, 46), 'FUMICAM · CUERNAVACA Y CDMX', font=fu(28, 800), fill=(255, 255, 255, 235), anchor='mt', stroke_width=3, stroke_fill=(0, 0, 0, 200))
    f = fu(44, 900); lineas, l = [], ''
    for w in sub.upper().split():
        if d.textlength((l + ' ' + w).strip(), font=f) > 620: lineas.append(l); l = w
        else: l = (l + ' ' + w).strip()
    lineas.append(l); y = 1000 - 30 * (len(lineas) - 1)
    for ln in lineas:
        d.text((W / 2, y), ln, font=f, fill='white', anchor='mm', stroke_width=7, stroke_fill=ROJO); y += 58
    im.save(ruta)


def tarjeta(ruta):
    im = Image.new('RGB', (W, H), (8, 20, 36)); d = ImageDraw.Draw(im)
    c = lambda t, y, s, col, p=900: d.text((W / 2, y), t, font=fu(s, p), fill=col, anchor='mt')
    c('FUMICAM', 300, 88, (255, 255, 255)); c('CONTROL DE PLAGAS', 410, 40, (255, 196, 60), 800)
    c('Cucarachas · alacranes · chinches', 500, 30, (220, 220, 220), 600); c('pulgas · termitas', 545, 30, (220, 220, 220), 600)
    c('Cuernavaca y CDMX', 640, 36, (255, 255, 255), 700)
    a = 560; d.rounded_rectangle(((W - a) / 2, 780, (W + a) / 2, 880), 50, fill=(37, 211, 102)); c('Cotiza por WhatsApp', 810, 38, (255, 255, 255), 800)
    c('Dinos tu zona y tu plaga', 920, 32, (200, 200, 200), 600)
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
    w0 = TMP / f'{k}.wav'; tts(frase, w0, vid)
    w = TMP / f'{k}_rapida.wav'   # Iván (30 oct): «se oye medio con flojera» → 15% más rápida y con más presencia, mismo tono
    if not w.exists(): ff(['-i', str(w0), '-af', 'atempo=1.15,acompressor=threshold=-20dB:ratio=3:attack=5:release=60,loudnorm=I=-14:TP=-1.5', str(w)])
    d = dur(w) + 0.25
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
sal = AQUI / 'Fumicam_Ivan_v5c.mp4'
ff(['-f', 'concat', '-safe', '0', '-i', str(TMP / 'lista.txt'), '-c:v', 'libx264', '-profile:v', 'main', '-crf', '23', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(sal)])
print(sal, round(dur(sal), 1), 's', sal.stat().st_size // 1024, 'KB')
