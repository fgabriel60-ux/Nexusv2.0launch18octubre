"""Giovanni Pulido: 2 clips hablando (su voz clonada, MiniMax H3) con zooms que MANTIENEN LA LÍNEA DE LOS OJOS (cada zoom escala alrededor
del punto de los ojos, así los ojos no se mueven en pantalla), subtítulos palabra por palabra y tarjeta final con la fórmula de sus flyers."""
import subprocess
from pathlib import Path
import av, imageio_ffmpeg, numpy as np
from faster_whisper import WhisperModel
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
FUENTE = str(AQUI.parent / 'modelos_modal' / 'fuentes' / 'Montserrat.ttf')
W, H = 1080, 1920
ORO, ROJO, NEGRO = (232, 190, 110), (176, 32, 38), (9, 12, 26)
TMP = AQUI / 'tmp'; TMP.mkdir(exist_ok=True)
EX, EY = 0.55, 0.295   # punto de los ojos (fracción del cuadro)
ZOOMS = {'G1': [1.0, 1.22, 1.08, 1.32], 'G2': [1.12, 1.0, 1.28, 1.15]}
TARJETA = 3.4


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1500:])


def dur(p):
    o = subprocess.run([FF, '-i', str(p)], capture_output=True, text=True).stderr
    h, m, s = o.split('Duration: ')[1].split(',')[0].split(':'); return int(h) * 3600 + int(m) * 60 + float(s)


def fu(t, peso='Black'):
    f = ImageFont.truetype(FUENTE, t); f.set_variation_by_name(peso); return f


def palabras(ruta, desfase, modelo):
    c = av.open(str(ruta)); rs = av.AudioResampler(format='s16', layout='mono', rate=16000)
    a = np.concatenate([x.to_ndarray().ravel() for fr in c.decode(audio=0) for x in rs.resample(fr)]).astype(np.float32) / 32768
    segs, _ = modelo.transcribe(a, language='es', word_timestamps=True)
    return [(w.word.strip(), w.start + desfase, w.end + desfase) for s in segs for w in s.words]


def subtitulo(txt, ruta):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img); tam = 92
    while d.textlength(txt, font=fu(tam)) > W - 80: tam -= 4
    f = fu(tam); d.text(((W - d.textlength(txt, font=f)) / 2, 1290), txt, font=f, fill=ORO, stroke_width=7, stroke_fill=(10, 10, 10)); img.save(ruta)


def franja(ruta):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle((60, 1560, W - 60, 1710), 26, fill=(9, 12, 26, 225), outline=ORO, width=3)
    for t, y, tam, c in [('LIC. GIOVANNI PULIDO', 1580, 50, (255, 255, 255)), ('ABOGADO · DIVORCIOS EN LÍNEA · LOS CABOS, BCS', 1648, 27, ORO)]:
        f = fu(tam, 'ExtraBold'); d.text(((W - d.textlength(t, font=f)) / 2, y), t, font=f, fill=c)
    img.save(ruta)


def tarjeta(ruta):
    """Fórmula de los flyers: TU ___ MERECE ___ + subtítulo + precio + 3 datos + WhatsApp."""
    img = Image.new('RGB', (W, H), NEGRO); d = ImageDraw.Draw(img)
    for y in range(H):
        d.line([(0, y), (W, y)], fill=tuple(int(NEGRO[i] + (30, 6, 10)[i] * (1 - abs(y - 700) / 1000)) for i in range(3)))
    def c(t, y, tam, col, peso='Black'):
        f = fu(tam, peso)
        while d.textlength(t, font=f) > W - 100: tam -= 2; f = fu(tam, peso)
        d.text(((W - d.textlength(t, font=f)) / 2, y), t, font=f, fill=col)
    c('LIC. GIOVANNI PULIDO · ABOGADO', 150, 34, ORO, 'Bold'); c('DIVORCIOS EN LÍNEA · LOS CABOS', 196, 30, (255, 255, 255), 'Medium')
    c('TU TRANQUILIDAD', 330, 104, (255, 255, 255)); c('MERECE UN', 450, 104, ORO); c('PROCESO CLARO', 570, 104, ORO)
    c('Nosotros llevamos el trámite del divorcio.', 740, 40, (255, 255, 255), 'Medium'); c('Tú recuperas tu paz.', 796, 40, ORO, 'Bold')
    d.rounded_rectangle((70, 900, W - 70, 1130), 30, fill=(18, 20, 36), outline=ORO, width=4)
    c('VOLUNTARIO DESDE', 925, 34, ORO, 'Bold'); c('$18,000', 975, 120, (255, 255, 255)); 
    xs = [(70, 'MÁS DE 90', 'divorcios resueltos'), (385, '+15 AÑOS', 'de experiencia'), (700, 'DISCRECIÓN', 'total, por WhatsApp')]
    for x, a, b in xs:
        d.rounded_rectangle((x, 1170, x + 310, 1340), 24, fill=(18, 20, 36), outline=ORO, width=3)
        f = fu(40, 'ExtraBold'); d.text((x + (310 - d.textlength(a, font=f)) / 2, 1200), a, font=f, fill=(255, 255, 255))
        f = fu(26, 'Medium'); d.text((x + (310 - d.textlength(b, font=f)) / 2, 1268), b, font=f, fill=ORO)
    t = 'ESCRÍBENOS · 624 136 33 28'; f = fu(50, 'ExtraBold'); a = d.textlength(t, font=f) + 110
    d.rounded_rectangle(((W - a) / 2, 1440, (W + a) / 2, 1560), 60, fill=(37, 211, 102)); d.text(((W - a) / 2 + 55, 1470), t, font=f, fill=(255, 255, 255))
    c('Los tiempos varían según el juzgado.', 1620, 26, (190, 195, 215), 'Medium')
    img.save(ruta)


def con_zoom(src, k, z, ini, fin, sal):
    """Recorte que escala alrededor del punto de los ojos: los ojos quedan en el mismo lugar de la pantalla."""
    cw, ch = 576 / z, 1024 / z; x0, y0 = EX * 576 * (1 - 1 / z), EY * 1024 * (1 - 1 / z)
    ff(['-ss', f'{ini:.3f}', '-t', f'{fin - ini:.3f}', '-i', str(src), '-vf', f'crop={cw:.2f}:{ch:.2f}:{x0:.2f}:{y0:.2f},scale={W}:{H}:flags=lanczos,setsar=1,fps=30,format=yuv420p',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '16', '-c:a', 'aac', '-ar', '44100', '-ac', '2', '-b:a', '160k', str(sal)])


modelo = WhisperModel('small', device='cpu', compute_type='int8')
segs, lista, t0 = [], [], 0.0
for nombre in ('G1', 'G2'):
    src = AQUI / 'clips' / f'{nombre}.mp4'; d = dur(src); lista += palabras(src, t0, modelo)
    z = ZOOMS[nombre]; paso = d / len(z)
    for i, zz in enumerate(z):
        s = TMP / f'{nombre}_{i}.mp4'; con_zoom(src, i, zz, i * paso, (i + 1) * paso if i < len(z) - 1 else d, s); segs.append(s)
    t0 += d
total = t0
tarjeta(TMP / 'tarjeta.png'); franja(TMP / 'franja.png')
(TMP / 'lista.txt').write_text(''.join(f"file '{s}'\n" for s in segs))
entr = ['-f', 'concat', '-safe', '0', '-i', str(TMP / 'lista.txt'), '-loop', '1', '-t', str(TARJETA), '-i', str(TMP / 'tarjeta.png'), '-i', str(TMP / 'franja.png')]
fl = f"[1:v]scale={W}:{H},setsar=1,fps=30,format=yuv420p[vt];[0:v][2:v]overlay=0:0:enable='between(t,0.3,{total - 0.2:.2f})'[xf];"
prev = 'xf'
for i, (p, a, b) in enumerate(lista):
    subtitulo(p, TMP / f'p{i}.png'); entr += ['-i', str(TMP / f'p{i}.png')]
    fin = lista[i + 1][1] if i + 1 < len(lista) else b + 0.3
    fl += f"[{prev}][{3 + i}:v]overlay=0:0:enable='between(t,{a:.2f},{fin:.2f})'[s{i}];"; prev = f's{i}'
fl += f"[{prev}]format=yuv420p,settb=1/30,fps=30[vh];[vt]settb=1/30[vt2];[vh][vt2]xfade=transition=fade:duration=0.4:offset={total - 0.4:.2f}[v];[0:a]apad[a]"
sal = AQUI / 'final' / 'Giovanni_divorcios_v1.mp4'
ff([*entr, '-filter_complex', fl + '', '-map', '[v]', '-map', '[a]', '-t', f'{total + TARJETA - 0.4:.2f}', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1',
    '-pix_fmt', 'yuv420p', '-preset', 'slow', '-crf', '24', '-maxrate', '2500k', '-bufsize', '5000k', '-c:a', 'aac', '-ar', '44100', '-ac', '2', '-b:a', '128k',
    '-movflags', '+faststart', str(TMP / 'hd.mp4')])
ff(['-i', str(TMP / 'hd.mp4'), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p', '-crf', '23',
    '-c:a', 'copy', '-movflags', '+faststart', str(sal)])
print(sal, f'{total:.1f}+{TARJETA}s', sal.stat().st_size // 1024, 'KB', len(lista), 'palabras')
