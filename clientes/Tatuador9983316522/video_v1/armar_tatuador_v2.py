"""Tatuador (Cancún centro, 998 331 6522) · v1 con el guion 10/10/10 de Glimmer (30 oct): SUS videos y fotos reales + su voz clonada en Fish
(de su audio «¿Llevas tiempo queriéndote tatuar…»), subtítulo por frase y tarjeta final con WhatsApp. Sin GPU. Uso: python3 armar_tatuador.py"""
import json, os, subprocess, urllib.request, uuid
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
WA = AQUI.parent / 'whatsapp'
TMP = AQUI / 'tmp'; TMP.mkdir(exist_ok=True)
FUENTE = '/workspaces/Nexusv2.0launch18octubre/visionagenciaIAV2.0-main 2/entregables/modelos_modal/fuentes/Montserrat.ttf'
LLAVE = os.environ['FISH_API_KEY']
W, H = 720, 1280
ROJO = (196, 30, 46)
V = lambda n: WA / f'1029_{n}_el_video.mp4'
F = lambda n: WA / f'1029_{n}_el_image.jpg'
# (frase, voz, subtítulo, [(archivo, inicio_s)…])  · varias tomas = cortes rápidos dentro de la frase
L = lambda n: AQUI.parent / 'video_v2' / 'salida' / f'{n}.mp4'
ESCENAS = [
    ('H1', None, '¿Llevas tiempo queriéndote tatuar?', [(L('H1'), 0)]),
    ('T3', 'Ya no es excusa.', 'Ya no es excusa', [(F('180626'), 0)]),
    ('H2', None, 'Tu idea → diseño único y personalizado', [(L('H2'), 0)]),
    ('T5', 'Japonés, anime, realismo, black and gray y fineline.', 'Japonés · anime · realismo · black and gray · fineline', [(V('180320'), 2), (F('180322'), 0), (F('180319'), 0), (V('181226'), 3)]),
    ('H3', None, 'Estudio profesional · centro de Cancún · escríbeme por WhatsApp', [(L('H3'), 0)]),
]


def ff(a):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1500:])


def dur(p):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)], capture_output=True, text=True).stdout)


def voz_id():
    f = AQUI / 'voz_id.txt'
    if f.exists(): return f.read_text().strip()
    mp3 = TMP / 'muestra.mp3'
    ff(['-i', str(WA / '1029_182848_el_audio.ogg'), '-ac', '1', '-ar', '44100', str(mp3)])
    lim = '----fish' + uuid.uuid4().hex; p = []
    for n, v in [('title', 'Tatuador Cancún 998 331 6522 (voz real)'), ('type', 'tts'), ('train_mode', 'fast'), ('visibility', 'private')]:
        p.append(f'--{lim}\r\nContent-Disposition: form-data; name="{n}"\r\n\r\n{v}\r\n'.encode())
    p.append(f'--{lim}\r\nContent-Disposition: form-data; name="voices"; filename="muestra.mp3"\r\nContent-Type: audio/mpeg\r\n\r\n'.encode() + mp3.read_bytes() + b'\r\n')
    p.append(f'--{lim}--\r\n'.encode())
    r = urllib.request.Request('https://api.fish.audio/model', data=b''.join(p), headers={'Authorization': 'Bearer ' + LLAVE, 'Content-Type': 'multipart/form-data; boundary=' + lim})
    i = json.loads(urllib.request.urlopen(r, timeout=300).read())['_id']; f.write_text(i); return i


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
    d.text((W / 2, 46), 'TATUAJES · CENTRO DE CANCÚN', font=fu(28, 800), fill=(255, 255, 255, 235), anchor='mt', stroke_width=3, stroke_fill=(0, 0, 0, 200))
    f = fu(44, 900); lineas, l = [], ''
    for w in sub.upper().split():
        if d.textlength((l + ' ' + w).strip(), font=f) > 620: lineas.append(l); l = w
        else: l = (l + ' ' + w).strip()
    lineas.append(l); y = 1000 - 30 * (len(lineas) - 1)
    for ln in lineas:
        d.text((W / 2, y), ln, font=f, fill='white', anchor='mm', stroke_width=7, stroke_fill=ROJO); y += 58
    im.save(ruta)


def tarjeta(ruta):
    im = Image.new('RGB', (W, H), (14, 12, 12)); d = ImageDraw.Draw(im)
    c = lambda t, y, s, col, p=900: d.text((W / 2, y), t, font=fu(s, p), fill=col, anchor='mt')
    c('TATUAJES', 300, 44, (220, 220, 220), 700); c('DISEÑO ÚNICO', 370, 74, (255, 255, 255)); c('Y PERSONALIZADO', 460, 54, ROJO)
    c('Sesiones desde $1,000', 575, 44, (255, 255, 255), 800); c('Cotización según tu diseño', 635, 30, (210, 210, 210), 600); c('Estudio profesional · centro de Cancún', 690, 28, (170, 170, 170), 500)
    a = 520; d.rounded_rectangle(((W - a) / 2, 800, (W + a) / 2, 900), 50, fill=(37, 211, 102)); c('Escríbeme por WhatsApp', 830, 36, (255, 255, 255), 800)
    c('998 331 6522', 960, 64, (255, 255, 255)); c('Te atiendo hasta tarde', 1050, 30, (170, 170, 170), 500)
    im.save(ruta)


def toma(src, ini, seg, ruta):
    base = f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps=30'
    if src.suffix in ('.jpg', '.png'):
        n = int(seg * 30) + 1
        ff(['-i', str(src), '-vf', f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},zoompan=z='min(zoom+0.0012,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps=30,setsar=1",
            '-frames:v', str(n), '-an', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', str(ruta)])
    else:
        ff(['-ss', str(ini), '-i', str(src), '-t', f'{seg:.2f}', '-vf', base, '-an', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', str(ruta)])


vid = voz_id(); print('voz', vid)
segs, voces = [], []
for i, (k, frase, sub, tomas) in enumerate(ESCENAS):
    w = (AQUI.parent / 'video_v2' / 'voz' / f'{k}.wav') if frase is None else TMP / f'{k}.wav'
    if frase: tts(frase, w, vid)
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
sal = AQUI / 'Tatuador_Cancun_v2.mp4'
ff(['-f', 'concat', '-safe', '0', '-i', str(TMP / 'lista.txt'), '-c:v', 'libx264', '-profile:v', 'main', '-crf', '23', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(sal)])
print(sal, round(dur(sal), 1), 's', sal.stat().st_size // 1024, 'KB')
