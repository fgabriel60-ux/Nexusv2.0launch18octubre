"""Reel de Carlos (Visión Agencia): gancho con sticker en llamas → números de campaña → testimonio de Mariano
(con su helicóptero arriba, sobre el video de Carlos trabajando) → IA correcta → CTA 5 clientes."""
import subprocess
from pathlib import Path
import av, imageio_ffmpeg, numpy as np
from faster_whisper import WhisperModel
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
NEG = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
NOR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
W, H = 1080, 1920
TMP = AQUI / 'tmp_armado'; TMP.mkdir(exist_ok=True)
(AQUI / 'final').mkdir(exist_ok=True)
MARIANO_AUDIO = AQUI / 'referencia' / 'LISBETH_231157_YO.ogg'
HELI = AQUI.parent / 'mariano_helicoptero_20261013' / 'final' / 'Mariano_helicoptero_v2_whatsapp.mp4'
FONDO_TESTI = AQUI / 'referencia' / 'ref_testimonio.mp4'
NUMEROS = AQUI / 'fotos' / '02_sin_texto.jpg'


def ff(args):
    r = subprocess.run([FF, '-v', 'error', '-y', *args], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-2000:])


def dur(ruta):
    out = subprocess.run([FF, '-i', str(ruta)], capture_output=True, text=True).stderr
    h, m, s = out.split('Duration: ')[1].split(',')[0].split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)


def palabras(ruta, modelo):
    c = av.open(str(ruta)); rs = av.AudioResampler(format='s16', layout='mono', rate=16000)
    a = np.concatenate([x.to_ndarray().ravel() for fr in c.decode(audio=0) for x in rs.resample(fr)]).astype(np.float32) / 32768
    segs, _ = modelo.transcribe(a, language='es', word_timestamps=True, vad_filter=True)
    return [(w.word.strip(), w.start, w.end) for s in segs for w in s.words]


def png_texto(ruta, texto, y, tam=82, color=(255, 255, 255)):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    f = ImageFont.truetype(NEG, tam)
    while d.textlength(texto, font=f) > W - 100:
        tam -= 4; f = ImageFont.truetype(NEG, tam)
    d.text(((W - d.textlength(texto, font=f)) / 2, y), texto, font=f, fill=color, stroke_width=7, stroke_fill=(0, 0, 0))
    img.save(ruta)


modelo = WhisperModel('small', device='cpu', compute_type='int8')
esc = 'scale=1080:1920:flags=lanczos,setsar=1,fps=30,format=yuv420p'
segmentos = []

# 1, 2, 4, 5: clips de Carlos con su voz limpia (s2-pro), cortados al largo de la voz
for clip, voz in [('P1', 'TC1'), ('P2', 'TC2'), ('P4', 'TC3'), ('P5', 'TC4')]:
    w = AQUI / 'voz' / f'{voz}.wav'
    pausa = 1.4 if clip == 'P1' else 0.0
    largo = dur(w) + (0.3 if clip == 'P2' else 0.15) + pausa
    sal = TMP / f'seg_{clip}.mp4'
    ff(['-i', str(AQUI / 'clips' / f'{clip}.mp4'), '-i', str(w), '-filter_complex',
        f'[0:v]{esc},tpad=start_mode=clone:start_duration={pausa}:stop_mode=clone:stop_duration=3[v];'
        f'[1:a]adelay={int(pausa * 1000)}|{int(pausa * 1000)},apad[a]', '-map', '[v]', '-map', '[a]', '-t', f'{largo:.2f}',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '17', '-c:a', 'aac', '-ar', '48000', '-ac', '2', str(sal)])
    segmentos.append((clip, sal, w))

# 3: testimonio de Mariano (lo mejor: 3.3–9.6 s y 13.6–20.9 s) sobre Carlos trabajando + helicóptero arriba
ma = TMP / 'mariano_mejor.wav'
ff(['-i', str(MARIANO_AUDIO), '-filter_complex',
    '[0:a]atrim=3.3:9.6,asetpts=PTS-STARTPTS[a1];[0:a]atrim=13.6:20.9,asetpts=PTS-STARTPTS[a2];'
    '[a1][a2]concat=n=2:v=0:a=1,highpass=f=90,afftdn=nf=-25,loudnorm=I=-16:TP=-1.5[a]', '-map', '[a]', '-ar', '48000', '-ac', '2', str(ma)])
lt = dur(ma)
vel = dur(FONDO_TESTI) / lt
etq = Image.new('RGBA', (W, H), (0, 0, 0, 0)); de = ImageDraw.Draw(etq)
de.rounded_rectangle((50, 300, 50 + 480, 300 + 860), 30, fill=(0, 0, 0, 230))
de.text((70, 1175), 'Mariano Herrera', font=ImageFont.truetype(NEG, 40), fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0))
de.text((70, 1225), 'cliente · San Marino', font=ImageFont.truetype(NOR, 34), fill=(230, 230, 230), stroke_width=3, stroke_fill=(0, 0, 0))
etq.save(TMP / 'etq_testi.png')
# nota de voz de WhatsApp animada (10 cuadros por segundo)
notas = TMP / 'nota'; notas.mkdir(exist_ok=True)
rng = np.random.default_rng(7); barras = (0.25 + 0.75 * rng.random(42)).tolist()
nfr = int(lt * 10) + 1
for k in range(nfr):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 90, 1560, W - 90, 1730
    d.rounded_rectangle((x0, y0, x1, y1), 34, fill=(0, 92, 75, 245))
    d.ellipse((x0 + 22, y0 + 28, x0 + 136, y0 + 142), fill=(120, 130, 140))
    d.text((x0 + 52, y0 + 50), 'MH', font=ImageFont.truetype(NEG, 36), fill=(255, 255, 255))
    d.polygon([(x0 + 160, y0 + 55), (x0 + 160, y0 + 115), (x0 + 205, y0 + 85)], fill=(230, 240, 235))
    avance = k / max(1, nfr - 1)
    bx = x0 + 230
    for b, alto in enumerate(barras):
        h = int(alto * 70); xx = bx + b * 14
        color = (83, 189, 235) if b / len(barras) <= avance else (180, 200, 195)
        d.rounded_rectangle((xx, y0 + 85 - h // 2, xx + 7, y0 + 85 + h // 2), 3, fill=color)
    px = bx + int(avance * (len(barras) - 1) * 14)
    d.ellipse((px - 11, y0 + 74, px + 11, y0 + 96), fill=(83, 189, 235))
    seg = int(avance * lt)
    d.text((bx, y0 + 122), f'0:{seg:02d}', font=ImageFont.truetype(NOR, 30), fill=(220, 235, 230))
    d.text((x1 - 120, y0 + 122), '✓✓', font=ImageFont.truetype(NOR, 30), fill=(83, 189, 235))
    img.save(notas / f'n{k:04d}.png')
sal3 = TMP / 'seg_P3.mp4'
ff(['-i', str(FONDO_TESTI), '-i', str(HELI), '-i', str(ma), '-i', str(TMP / 'etq_testi.png'), '-framerate', '10', '-i', str(notas / 'n%04d.png'),
    '-filter_complex',
    f'[0:v]setpts=PTS/{vel:.4f},{esc},eq=brightness=-0.08,split[fa][fb];'
    f'[fb]crop=1080:760:0:560,boxblur=28:3[bl];[fa][bl]overlay=0:560[fondo];'
    f'[fondo][3:v]overlay=0:0[f2];'
    f'[1:v]scale=440:-2,setsar=1,fps=30,trim=0:{lt:.2f},setpts=PTS-STARTPTS[heli];'
    f'[f2][heli]overlay=70:320[f3];[4:v]fps=30,format=rgba[nota];[f3][nota]overlay=0:0:shortest=0[v];[2:a]apad[a]',
    '-map', '[v]', '-map', '[a]', '-t', f'{lt:.2f}', '-c:v', 'libx264', '-preset', 'fast', '-crf', '17', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-ar', '48000', '-ac', '2', str(sal3)])
segmentos.insert(2, ('P3', sal3, ma))

# capas: números de campaña en P2, subtítulos de todo, cierre en P5
ini, t = {}, 0.0
for nombre, sal, _ in segmentos:
    ini[nombre] = t; t += dur(sal)
total = t
capas = []
num = Image.open(NUMEROS).convert('RGB'); nw, nh = num.size
card = num.crop((0, 0, nw, int(nh * 0.50))).resize((960, int(960 * nh * 0.50 / nw)), Image.LANCZOS)
lienzo = Image.new('RGBA', (W, H), (0, 0, 0, 0)); lienzo.paste(card, (60, 380))
ImageDraw.Draw(lienzo).rounded_rectangle((60, 380, 1020, 380 + card.height), 26, outline=(37, 211, 102), width=6)
lienzo.save(TMP / 'numeros.png')
png_texto(TMP / 'cierre1.png', 'SOLO 5 CLIENTES POR SEMANA', 300, 80, (255, 214, 64))
capas.append((TMP / 'cierre1.png', ini['P5'] + dur(segmentos[-1][1]) - 3.2, total))
k = 0
for nombre, sal, voz in segmentos:
    for p, a, b in palabras(voz, modelo):
        ruta = TMP / f'w{k}.png'
        png_texto(ruta, p, 1420 if nombre != 'P3' else 1330)
        capas.append((ruta, ini[nombre] + a + (1.4 if nombre == 'P1' else 0), ini[nombre] + b + 0.12 + (1.4 if nombre == 'P1' else 0))); k += 1

lista = TMP / 'lista.txt'
lista.write_text(''.join(f"file '{s}'\n" for _, s, _ in segmentos))
base = TMP / 'base.mp4'
ff(['-f', 'concat', '-safe', '0', '-i', str(lista), '-c:v', 'libx264', '-preset', 'fast', '-crf', '17', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-ar', '48000', str(base)])
actual = base
for t0 in range(0, len(capas), 18):
    tanda = capas[t0:t0 + 18]
    entradas = ['-i', str(actual)] + sum([['-i', str(r)] for r, _, _ in tanda], [])
    f, prev = '', '0:v'
    for j, (_, a, b) in enumerate(tanda):
        f += f"[{prev}][{j + 1}:v]overlay=0:0:enable='between(t,{a:.2f},{b:.2f})'[s{j}];"; prev = f's{j}'
    sig = TMP / f'paso_{t0}.mp4'
    ff([*entradas, '-filter_complex', f.rstrip(';'), '-map', f'[{prev}]', '-map', '0:a', '-c:v', 'libx264', '-preset', 'fast',
        '-crf', '17', '-pix_fmt', 'yuv420p', '-c:a', 'copy', str(sig)])
    actual = sig
salida = AQUI / 'final' / 'Carlos_VisionAgencia_v2.mp4'
ff(['-i', str(actual), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1',
    '-pix_fmt', 'yuv420p', '-preset', 'slow', '-crf', '21', '-maxrate', '2800k', '-bufsize', '5600k', '-c:a', 'aac',
    '-af', 'loudnorm=I=-15:TP=-1.5', '-ar', '44100', '-ac', '2', '-b:a', '128k', '-movflags', '+faststart', str(salida)])
print(salida, f'{total:.1f} s')
