"""Rubén · v3 (30 oct, pedido de Carlos): Rubén HABLANDO (lipsync H3 de su voz clonada, video_v3/salida) al inicio y al cierre + escenas REALES de sus terapias de sus TikToks (sin el letrero de arriba) en medio. Frase R4 sin promesa de resultado (Glimmer: políticas de salud)."""
import json, os, subprocess, urllib.request, uuid
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
Q = AQUI.parent / 'video' / 'cuadros_qwen'
TMP = AQUI / 'tmp'; TMP.mkdir(exist_ok=True)
FUENTE = '/workspaces/Nexusv2.0launch18octubre/visionagenciaIAV2.0-main 2/entregables/modelos_modal/fuentes/Montserrat.ttf'
LLAVE = os.environ['FISH_API_KEY']
W, H = 720, 1280
ROJO = (40, 90, 200)
T = lambda n: AQUI.parent / 'tiktok' / f'{n}.mp4'
L = lambda n: AQUI / 'salida' / f'{n}.mp4'
ESCENAS = [
    ('R1', 'Hola, soy Rubén, en Zinacantepec y Metepec. Aquí no damos masaje ni tronamos huesos.', 'Aquí no damos masaje ni tronamos huesos', [(L('H_R1'), 0)]),
    ('R2', 'Hacemos Alineación Alphabiótica: tracción suave y puntos específicos para liberar la columna.', 'Alineación Alphabiótica', [(T('2026-01-26_39900vistas'), 27), (T('2026-03-19_113100vistas'), 29), (T('2026-03-06_26200vistas'), 39)]),
    ('R3', 'Mucha gente llega con dolor de cuello, espalda, ciática, adormecimiento o mucho estrés.', 'Cuello · espalda · ciática · estrés', [(T('2026-05-20_46300vistas'), 10), (T('2026-05-20_46300vistas'), 46)]),
    ('R4', 'En tu primera sesión revisamos tu caso y te explico tu plan.', 'Revisamos tu caso desde la primera sesión', [(T('2026-06-12_25600vistas'), 31), (T('2026-05-20_46300vistas'), 87)]),
    ('R5', 'Sesión trescientos pesos. Escríbeme por uatsap y te explico cómo te puedo ayudar.', 'Sesión $300 · escríbeme por WhatsApp', [(L('H_R5'), 0)]),
]


def ff(a):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1500:])


def dur(p):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)], capture_output=True, text=True).stdout)


def voz_id():
    return (AQUI.parent / 'voz' / 'voz_fish_id.txt').read_text().strip()


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
    d.text((W / 2, 46), 'ALINEACIÓN ALPHABIÓTICA', font=fu(28, 800), fill=(255, 255, 255, 235), anchor='mt', stroke_width=3, stroke_fill=(0, 0, 0, 200))
    f = fu(44, 900); lineas, l = [], ''
    for w in sub.upper().split():
        if d.textlength((l + ' ' + w).strip(), font=f) > 620: lineas.append(l); l = w
        else: l = (l + ' ' + w).strip()
    lineas.append(l); y = 1000 - 30 * (len(lineas) - 1)
    for ln in lineas:
        d.text((W / 2, y), ln, font=f, fill='white', anchor='mm', stroke_width=7, stroke_fill=ROJO); y += 58
    im.save(ruta)


def tarjeta(ruta):
    im = Image.new('RGB', (W, H), (12, 18, 40)); d = ImageDraw.Draw(im)
    c = lambda t, y, s, col, p=900: d.text((W / 2, y), t, font=fu(s, p), fill=col, anchor='mt')
    c('ALINEACIÓN', 300, 70, (255, 255, 255)); c('ALPHABIÓTICA', 385, 60, (120, 170, 255)); c('Aquí no damos masaje ni tronamos huesos', 480, 28, (210, 210, 210), 600)
    c('SESIÓN $300', 560, 64, (255, 214, 60)); c('Zinacantepec · Metepec', 650, 32, (200, 200, 200), 600)
    a = 520; d.rounded_rectangle(((W - a) / 2, 780, (W + a) / 2, 880), 50, fill=(37, 211, 102)); c('Agenda por WhatsApp', 810, 36, (255, 255, 255), 800)
    c('722 313 9882', 940, 64, (255, 255, 255))
    im.save(ruta)


def toma(src, ini, seg, ruta):
    base = f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps=30'
    if src.suffix == '.jpg':
        n = int(seg * 30) + 1
        ff(['-i', str(src), '-vf', f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},zoompan=z='min(zoom+0.0012,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps=30,setsar=1",
            '-frames:v', str(n), '-an', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', str(ruta)])
    else:
        if src.parent.name == 'tiktok':  # quita el letrero de arriba y difumina los subtítulos quemados del TikTok (Glimmer: se leían como promesa de resultado)
            base = 'crop=iw:ih*0.79:0:ih*0.20,' + base + f',split[a][b];[b]crop={W}:{int(H*0.30)}:0:{int(H*0.56)},boxblur=22:3,eq=brightness=-0.18:saturation=0.8[bb];[a][bb]overlay=0:{int(H*0.56)}'
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
sal = AQUI / 'Ruben_video_v3b.mp4'
ff(['-f', 'concat', '-safe', '0', '-i', str(TMP / 'lista.txt'), '-c:v', 'libx264', '-profile:v', 'main', '-crf', '23', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(sal)])
print(sal, round(dur(sal), 1), 's', sal.stat().st_size // 1024, 'KB')
