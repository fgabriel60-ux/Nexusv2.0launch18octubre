"""v5 (30 oct): igual que la v4 pero sin lo rojo — borde de subtítulos azul marino de Grupo JR (Carlos/José 29 oct). Antes: v3 (correcciones de José 28-29 oct, texto suyo casi literal; escenas J1-J6 de obrero_v3). José · Grupo JR Pixar obrero: 6 escenas del obrero (Modal) + voz Fish de José por frase + subtítulos palabra por palabra + letreros + tarjeta final.
Guion = respuesta de Glimmer (28 oct) sin la frase de '80 mensajes' ni '12 años'. Uso: python3 armar_jose_obrero.py"""
import json, subprocess, urllib.request
from pathlib import Path
import av, imageio_ffmpeg, numpy as np
from faster_whisper import WhisperModel
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
RAIZ = Path('/workspaces/Nexusv2.0launch18octubre')
CLIPS = AQUI.parent / 'obrero_v4_20261030' / 'salida'
FF = imageio_ffmpeg.get_ffmpeg_exe()
FUENTE = str(RAIZ / 'visionagenciaIAV2.0-main 2/entregables/modelos_modal/fuentes/Montserrat.ttf')
VOZ_ID = '74cae190c2c84b0caaca073f42f5de54'
W, H = 1080, 1920
AMARILLO, AZUL = (255, 214, 60), (12, 38, 104)
TMP = AQUI / 'tmp_v4'; TMP.mkdir(exist_ok=True)
TARJETA = 3.6
# (clip, frases, letrero)
SEG = [('V1_barre', ['Antes de impermeabilizar una losa de concreto, la preparación de la superficie es clave para lograr una buena adherencia.'], []),
       ('V2_cubetas', ['Al aplicar poliuretano acrílico, doce años, calidad industrial, más primario fibratado elástico de alta resistencia,'], ['POLIURETANO ACRÍLICO 12 AÑOS', '+ Primario fibratado elástico']),
       ('V3_mezcla', ['obtenemos un sistema que mejora la adherencia, la trabajabilidad y la flexibilidad del recubrimiento.'], ['MEJORA ADHERENCIA', 'Trabajabilidad y flexibilidad']),
       ('V4_primario', ['Aplicado correctamente sobre la superficie, ayuda a crear una base sólida y uniforme.'], []),
       ('V5_poliuretano', ['Ayuda a crear una protección impermeabilizante continua y uniforme.'], []),
       ('V6_terminada', ['Ideal para tratar problemas de filtración en losas de concreto.'], ['IDEAL PARA FILTRACIÓN', 'En losas de concreto']),
       ('V7_lluvia', ['Una solución práctica para proteger tu proyecto.'], []),
       ('V8_cierre', ['Contáctanos. Grupo JR, dos dos uno, cinco siete tres, tres uno dos siete.'], ['GRUPO JR', 'WhatsApp 221 573 3127'])]
env = {}
import os
env.update(os.environ)
for l in ((RAIZ / '.env').read_text().splitlines() if (RAIZ / '.env').exists() else []):
    if '=' in l and not l.lstrip().startswith('#'):
        k, v = l.split('=', 1); env[k.strip()] = v.strip().strip('"\'')


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1500:])


def dur(p):
    o = subprocess.run([FF, '-i', str(p)], capture_output=True, text=True).stderr; h, m, s = o.split('Duration: ')[1].split(',')[0].split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)


def fu(t, peso='Black'):
    f = ImageFont.truetype(FUENTE, t); f.set_variation_by_name(peso); return f


def tts(texto, ruta):
    if ruta.exists(): return
    req = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST', data=json.dumps({'text': texto, 'format': 'mp3', 'reference_id': VOZ_ID}).encode(),
                                 headers={'Authorization': 'Bearer ' + env['FISH_API_KEY'], 'Content-Type': 'application/json', 'model': 's1'})
    ruta.write_bytes(urllib.request.urlopen(req, timeout=300).read())


def palabras(mp3):
    c = av.open(str(mp3)); rs = av.AudioResampler(format='s16', layout='mono', rate=16000)
    a = np.concatenate([x.to_ndarray().ravel() for fr in c.decode(audio=0) for x in rs.resample(fr)]).astype(np.float32) / 32768
    segs, _ = WhisperModel('small', device='cpu', compute_type='int8').transcribe(a, language='es', word_timestamps=True)
    return [(w.word.strip(), w.start, w.end) for s in segs for w in s.words]


def sub(txt, ruta):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img); tam = 90
    while d.textlength(txt, font=fu(tam)) > W - 80: tam -= 4
    f = fu(tam); d.text(((W - d.textlength(txt, font=f)) / 2, 1230), txt, font=f, fill=(255, 255, 255), stroke_width=9, stroke_fill=AZUL); img.save(ruta)


def letrero(lineas, ruta, y=1470, tam=50):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    for yy in range(y - 90, H): d.line([(0, yy), (W, yy)], fill=(4, 12, 30, int(170 * min(1, (yy - y + 90) / 200))))
    d.rectangle((70, y, 76, y + len(lineas) * (tam + 6) + 8), fill=AMARILLO)
    for i, l in enumerate(lineas):
        f = fu(tam if i == 0 else int(tam * .72), 'Bold' if i == 0 else 'Medium')
        while d.textlength(l, font=f) > W - 190: f = fu(f.size - 2, 'Bold' if i == 0 else 'Medium')
        d.text((105, y + i * (tam + 8)), l, font=f, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
    img.save(ruta)


def tarjeta(ruta):
    img = Image.new('RGB', (W, H), AZUL); d = ImageDraw.Draw(img)
    def c(t, y, tam, col, peso='Black'):
        f = fu(tam, peso)
        while d.textlength(t, font=f) > W - 100: tam -= 2; f = fu(tam, peso)
        d.text(((W - d.textlength(t, font=f)) / 2, y), t, font=f, fill=col)
    c('GRUPO JR', 220, 130, (255, 255, 255)); c('IMPERMEABILIZANTES', 380, 62, AMARILLO, 'Bold')
    c('SECADO RÁPIDO', 560, 100, (255, 255, 255)); c('QUE LLUEVA, TU LOSA AGUANTA', 680, 62, AMARILLO)
    c('DESDE', 860, 40, (255, 255, 255), 'Bold'); c('$150', 900, 210, AMARILLO); c('POR M²', 1125, 60, (255, 255, 255))
    for i, (a, b) in enumerate([('Sellador + 2 capas', 'Poliuretano acrílico afibratado'), ('10 % de descuento', 'en más de 100 m²')]):
        y = 1260 + i * 100; d.rounded_rectangle((90, y, W - 90, y + 88), 18, fill=(255, 255, 255))
        d.text((125, y + 8), a, font=fu(37, 'ExtraBold'), fill=(12, 30, 80)); d.text((125, y + 54), b, font=fu(26, 'Medium'), fill=(70, 80, 110))
    t = 'Escríbeme por WhatsApp'; f = fu(48, 'ExtraBold'); a = d.textlength(t, font=f) + 110
    d.rounded_rectangle(((W - a) / 2, 1540, (W + a) / 2, 1656), 58, fill=(37, 211, 102)); d.text(((W - a) / 2 + 55, 1568), t, font=f, fill=(255, 255, 255))
    c('WhatsApp 221 573 3127 · Puebla y alrededores', 1710, 36, (200, 215, 255), 'Medium'); img.save(ruta)


# voz por frase -> un solo audio con pausa de 0.35 s entre segmentos y la duración de cada escena = su voz
(AQUI / 'voz_v4').mkdir(exist_ok=True)
GAP, LEAD = 0.35, 0.25
tramos, partes, t = [], [], LEAD
for k, (clip, frases, _) in enumerate(SEG):
    rutas = []
    for j, fr in enumerate(frases):
        r = AQUI / 'voz_v4' / f's{k}_{j}.mp3'; tts(fr, r); rutas.append(r)
    d = sum(dur(r) for r in rutas)
    tramos.append((t, t + d + GAP)); partes.append(rutas); t += d + GAP
total = t
ent = sum([['-i', str(r)] for rs in partes for r in rs], [])
n = sum(len(rs) for rs in partes)
ff([*ent, '-filter_complex', ''.join(f'[{i}:a]aresample=44100,aformat=channel_layouts=mono[a{i}];' for i in range(n)) + ''.join(f'[a{i}]' for i in range(n)) + f'concat=n={n}:v=0:a=1[v]', '-map', '[v]', str(TMP / 'voz_sin_pausas.wav')])
# reconstruye con pausas por segmento
lista, i0 = [], 0
fl, ent2 = '', []
idx = 0
for k, rs in enumerate(partes):
    for r in rs:
        ent2 += ['-i', str(r)]; fl += f'[{idx}:a]aresample=44100,aformat=channel_layouts=mono[b{idx}];'; idx += 1
orden = ''.join(f'[b{i}]' for i in range(idx))
# las pausas se insertan con adelay por segmento: cada segmento se mezcla en su inicio
mez, idx = '', 0
for k, rs in enumerate(partes):
    ini = tramos[k][0] + 0
    acum = 0.0
    for r in rs:
        mez += f'[b{idx}]adelay={int((ini + acum) * 1000)}|{int((ini + acum) * 1000)}[m{idx}];'; acum += dur(r); idx += 1
fl += mez + ''.join(f'[m{i}]' for i in range(idx)) + f'amix=inputs={idx}:normalize=0,loudnorm=I=-15:TP=-1.5[v]'
vozwav = TMP / 'voz.wav'
ff([*ent2, '-filter_complex', fl, '-map', '[v]', '-t', f'{total:.2f}', str(vozwav)])
pal = palabras(vozwav)
fus, i = [], 0
while i < len(pal):
    w = pal[i][0].strip('¿?¡!,.').lower()
    if w in ('ge', 'je', 'ye') and i + 1 < len(pal) and pal[i + 1][0].strip('¿?¡!,.').lower() in ('erre', 'ere', 'r', 'rre'):
        fus.append(('GR', pal[i][1], pal[i + 1][2])); i += 2
    else:
        fus.append(pal[i]); i += 1
pal = fus
_fix = {'joárez': 'JR', 'juárez': 'JR', 'joarez': 'JR', 'jóarez': 'JR', 'loza': 'losa', 'lozas': 'losas', 'crílico': 'acrílico', 'jogarre': 'JR', 'jotaerre': 'JR', 'jota': 'J'}
pal = [(_fix.get(w.strip('¿?¡!,.-').lower(), w.strip('-')), a, b) for w, a, b in pal]
print(f'voz {total:.1f}s, {len(pal)} palabras', [p[0] for p in pal])

segs = []
for k, (clip, _, let) in enumerate(SEG):
    src = CLIPS / f'{clip}.mp4'; s = TMP / f'{clip}.mp4'; L = tramos[k][1] - tramos[k][0]
    ff(['-i', str(src), '-vf', f'setpts=PTS*{L / dur(src):.4f},scale={W}:{H}:flags=lanczos,setsar=1,fps=30,format=yuv420p', '-t', f'{L:.2f}', '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '17', str(s)])
    segs.append(s); letrero(let or [' '], TMP / f'l{k}.png') if let else Image.new('RGBA', (W, H), (0, 0, 0, 0)).save(TMP / f'l{k}.png')
(TMP / 'lista.txt').write_text(''.join(f"file '{s}'\n" for s in segs)); tarjeta(TMP / 'tarjeta.png')
_b = Image.new('RGBA', (W, H), (0, 0, 0, 0)); _d = ImageDraw.Draw(_b); _f = fu(72, 'Black'); _t = 'SECADO RÁPIDO'; _w = _d.textlength(_t, font=_f) + 110
_d.rounded_rectangle(((W - _w) / 2, 215, (W + _w) / 2, 330), 58, fill=(12, 38, 104, 235), outline=AMARILLO + (255,), width=6); _d.text(((W - _w) / 2 + 55, 233), _t, font=_f, fill=AMARILLO); _b.save(TMP / 'secado.png')
ff(['-f', 'concat', '-safe', '0', '-i', str(TMP / 'lista.txt'), '-i', str(TMP / 'secado.png'), '-filter_complex', '[0:v][1:v]overlay=0:0:format=auto[v]', '-map', '[v]', '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '17', str(TMP / 'base.mp4')])
entr = ['-i', str(TMP / 'base.mp4'), '-i', str(vozwav), '-loop', '1', '-t', str(TARJETA), '-i', str(TMP / 'tarjeta.png')] + sum([['-i', str(TMP / f'l{k}.png')] for k in range(len(SEG))], [])
fl, prev = '', '0:v'
for k in range(len(SEG)):
    a0, a1 = tramos[k]; fl += f"[{prev}][{3 + k}:v]overlay=0:0:enable='between(t,{a0 + .2:.2f},{a1 - .1:.2f})'[c{k}];"; prev = f'c{k}'
base = 3 + len(SEG)
for i, (p, a, b) in enumerate(pal):
    sub(p.strip('¿?¡!,.').upper(), TMP / f'p{i}.png'); entr += ['-i', str(TMP / f'p{i}.png')]
    fin = pal[i + 1][1] if i + 1 < len(pal) else b + 0.3
    fl += f"[{prev}][{base + i}:v]overlay=0:0:enable='between(t,{a:.2f},{fin:.2f})'[s{i}];"; prev = f's{i}'
fl += (f"[{prev}]format=yuv420p,settb=1/30,fps=30[vh];[2:v]scale={W}:{H},setsar=1,fps=30,format=yuv420p,settb=1/30[vt];"
       f"[vh][vt]xfade=transition=fade:duration=0.4:offset={total - 0.4:.2f}[v];[1:a]apad[a]")
hd = TMP / 'hd.mp4'; sal = AQUI.parent / 'Jose_GrupoJR_Pixar_obrero_v5.mp4'
ff([*entr, '-filter_complex', fl, '-map', '[v]', '-map', '[a]', '-t', f'{total + TARJETA - 0.4:.2f}', '-c:v', 'libx264', '-profile:v', 'main', '-preset', 'medium', '-crf', '22',
    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', '44100', '-b:a', '128k', '-movflags', '+faststart', str(hd)])
ff(['-i', str(hd), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p', '-crf', '23', '-c:a', 'copy', '-movflags', '+faststart', str(sal)])
print(sal, sal.stat().st_size // 1024, 'KB')
