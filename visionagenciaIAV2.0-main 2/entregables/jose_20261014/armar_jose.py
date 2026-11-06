"""José · Grupo JR «Puede llover»: 4 escenas de cine (Modal) + su voz real (Fish) + subtítulos palabra por palabra + tarjeta final con precio."""
import subprocess
from pathlib import Path
import av, imageio_ffmpeg, numpy as np
from faster_whisper import WhisperModel
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
FUENTE = str(AQUI.parent / 'modelos_modal' / 'fuentes' / 'Montserrat.ttf')
W, H = 1080, 1920
ORO, AZUL, AMARILLO = (232, 190, 110), (12, 38, 104), (255, 214, 60)
TMP = AQUI / 'tmp'; TMP.mkdir(exist_ok=True)
VOZ = AQUI / 'voz' / 'jose.mp3'
ESC = [('J1', ['QUE LLUEVA']), ('J2', ['SELLADOR + 2 CAPAS', 'POLIURETANO ACRÍLICO AFIBRATADO']), ('J3', ['CALIDAD INDUSTRIAL', 'UN BLANCO QUE REBOTA EL SOL']),
       ('J4', ['12 AÑOS', 'DE VIDA ÚTIL'])]
DUR = 5.75; TARJETA = 3.6


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1500:])


def fu(t, peso='Black'):
    f = ImageFont.truetype(FUENTE, t); f.set_variation_by_name(peso); return f


def palabras():
    c = av.open(str(VOZ)); rs = av.AudioResampler(format='s16', layout='mono', rate=16000)
    a = np.concatenate([x.to_ndarray().ravel() for fr in c.decode(audio=0) for x in rs.resample(fr)]).astype(np.float32) / 32768
    segs, _ = WhisperModel('small', device='cpu', compute_type='int8').transcribe(a, language='es', word_timestamps=True)
    return [(w.word.strip(), w.start + 0.3, w.end + 0.3) for s in segs for w in s.words]


def sub(txt, ruta):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img); tam = 90
    while d.textlength(txt, font=fu(tam)) > W - 80: tam -= 4
    f = fu(tam); d.text(((W - d.textlength(txt, font=f)) / 2, 1230), txt, font=f, fill=(255, 255, 255), stroke_width=8, stroke_fill=(10, 20, 50)); img.save(ruta)


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
    logo = Image.open(AQUI / 'refs' / 'logo_jr.png').convert('RGB').resize((250, 250), Image.LANCZOS); img.paste(logo, ((W - 250) // 2, 120))
    c('QUE LLUEVA,', 440, 100, (255, 255, 255)); c('TU AZOTEA AGUANTA', 560, 84, AMARILLO)
    c('DESDE', 700, 40, (255, 255, 255), 'Bold'); c('$150', 740, 210, AMARILLO); c('POR M²', 965, 60, (255, 255, 255))
    for i, (a, b) in enumerate([('12 años de vida útil', 'Poliuretano acrílico afibratado'), ('Calidad industrial', 'Sellador + 2 manos, blanco que rebota el sol'),
                                ('Precio claro', 'Desde $150 por m²'), ('10 % de descuento', 'en más de 100 m²')]):
        y = 1115 + i * 100; d.rounded_rectangle((90, y, W - 90, y + 88), 18, fill=(255, 255, 255))
        d.text((125, y + 8), a, font=fu(37, 'ExtraBold'), fill=(12, 30, 80)); d.text((125, y + 54), b, font=fu(26, 'Medium'), fill=(70, 80, 110))
    t = 'Escríbeme por WhatsApp'; f = fu(48, 'ExtraBold'); a = d.textlength(t, font=f) + 110
    d.rounded_rectangle(((W - a) / 2, 1540, (W + a) / 2, 1656), 58, fill=(37, 211, 102)); d.text(((W - a) / 2 + 55, 1568), t, font=f, fill=(255, 255, 255))
    c('Puebla y alrededores', 1710, 36, (200, 215, 255), 'Medium'); img.save(ruta)


segs = []
for k, (n, lineas) in enumerate(ESC):
    src = AQUI / 'clips' / f'{n}.mp4'; s = TMP / f'{n}.mp4'
    o = subprocess.run([FF, '-i', str(src)], capture_output=True, text=True).stderr; h, m, sg = o.split('Duration: ')[1].split(',')[0].split(':'); real = int(h) * 3600 + int(m) * 60 + float(sg)
    ff(['-i', str(src), '-vf', f'setpts=PTS*{DUR / real:.4f},scale={W}:{H}:flags=lanczos,setsar=1,fps=30,format=yuv420p', '-t', f'{DUR:.2f}', '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '17', str(s)])
    segs.append(s); letrero(lineas, TMP / f'l{k}.png')
total = DUR * len(ESC)
tarjeta(TMP / 'tarjeta.png'); (TMP / 'lista.txt').write_text(''.join(f"file '{s}'\n" for s in segs))
lista = palabras()
entr = ['-f', 'concat', '-safe', '0', '-i', str(TMP / 'lista.txt'), '-i', str(VOZ), '-loop', '1', '-t', str(TARJETA), '-i', str(TMP / 'tarjeta.png')] + sum([['-i', str(TMP / f'l{k}.png')] for k in range(len(ESC))], [])
fl, prev = '', '0:v'
for k in range(len(ESC)):
    fl += f"[{prev}][{3 + k}:v]overlay=0:0:enable='between(t,{k * DUR + .3:.2f},{(k + 1) * DUR - .2:.2f})'[c{k}];"; prev = f'c{k}'
base = 3 + len(ESC)
for i, (p, a, b) in enumerate(lista):
    sub(p, TMP / f'p{i}.png'); entr += ['-i', str(TMP / f'p{i}.png')]
    fin = lista[i + 1][1] if i + 1 < len(lista) else b + 0.3
    fl += f"[{prev}][{base + i}:v]overlay=0:0:enable='between(t,{a:.2f},{fin:.2f})'[s{i}];"; prev = f's{i}'
fl += (f"[{prev}]format=yuv420p,settb=1/30,fps=30[vh];[2:v]scale={W}:{H},setsar=1,fps=30,format=yuv420p,settb=1/30[vt];"
       f"[vh][vt]xfade=transition=fade:duration=0.4:offset={total - 0.4:.2f}[v];[1:a]adelay=300|300,loudnorm=I=-15:TP=-1.5,apad[a]")
hd = TMP / 'hd.mp4'; sal = AQUI / 'final' / 'Jose_GrupoJR_PuedeLlover_v1.mp4'
ff([*entr, '-filter_complex', fl, '-map', '[v]', '-map', '[a]', '-t', f'{total + TARJETA - 0.4:.2f}', '-c:v', 'libx264', '-profile:v', 'main', '-preset', 'slow', '-crf', '22',
    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', '44100', '-b:a', '128k', '-movflags', '+faststart', str(hd)])
ff(['-i', str(hd), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p', '-crf', '23', '-c:a', 'copy',
    '-movflags', '+faststart', str(sal)])
print(sal, f'{total:.1f}+{TARJETA}s', sal.stat().st_size // 1024, 'KB', len(lista), 'palabras')
