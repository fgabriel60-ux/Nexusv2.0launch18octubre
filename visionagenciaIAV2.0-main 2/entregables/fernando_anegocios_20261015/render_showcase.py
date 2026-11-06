"""Anegocios · SHOWCASE de producto (ritmo del reel de referencia: cada pieza del kit con etiqueta azul inclinada animada).
Metraje REAL de Fernando (lector, pantalla, impresora) + piezas recortadas de su imagen del kit. Sin clips nuevos de Modal. Voz Farid dick 2."""
import json, math, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg
sys.path.insert(0, str(Path(__file__).resolve().parent))
import intro_paquete as IP   # CROP, FONDO, pop, pastilla (piezas reales del kit)

A = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 720, 1280, 30
SALIDA = A / 'final' / 'Anegocios_showcase_v1.mp4'
T = A / 'tmp_showcase'; T.mkdir(exist_ok=True)
FD = '/usr/share/fonts/truetype/dejavu/'
fnt = lambda s, b=True: ImageFont.truetype(FD + ('DejaVuSans-Bold.ttf' if b else 'DejaVuSans.ttf'), s)
NEGRO = (17, 17, 17); AZUL = (10, 84, 200); AZUL_CL = (96, 170, 255); BLANCO = (255, 255, 255); AMAR = (255, 230, 0); GRIS = (200, 200, 200)

TI = json.loads((A / 'voz_showcase' / 'tiempos.json').read_text())
ORDEN = list('ABCDEFG')
GAP = 0.3
ini, t = {}, 0.2
for k in ORDEN:
    ini[k] = t; t += TI[k]['dur'] + GAP
FIN = ini['G'] + TI['G']['dur'] + 2.9
TXT = {k: TI[k]['texto'] for k in ORDEN}

def palabras_t(k):
    ws = TXT[k].split(); pw = TI[k]['palabras']
    a, b = ini[k] + pw[0][1], ini[k] + pw[-1][2]
    pausa = lambda w: 4 if w[-1] in ',.:?;' else 0
    pesos = [len(w) + pausa(w) for w in ws]; tot, acc, out = sum(pesos), 0, []
    for w, p in zip(ws, pesos):
        s0 = a + (b - a) * acc / tot; acc += p; out.append((w, s0, a + (b - a) * (acc - pausa(w)) / tot))
    return out
PAL = {k: palabras_t(k) for k in ORDEN}
ease = lambda x: 1 - (1 - min(max(x, 0), 1)) ** 3
clamp = lambda x: min(max(x, 0.0), 1.0)
nueva = lambda: Image.new('RGBA', (W, H), (0, 0, 0, 0))
def mover(capa, a, dx=0, dy=0):
    if a < 1:
        al = capa.getchannel('A').point(lambda v: int(v * a)); capa = capa.copy(); capa.putalpha(al)
    if dx or dy:
        n = Image.new('RGBA', capa.size, (0, 0, 0, 0)); n.alpha_composite(capa, (int(dx), int(dy))); capa = n
    return capa
def sombra(capa, poly, op=90, blur=14, dy=8):
    s = Image.new('RGBA', capa.size, (0, 0, 0, 0)); ImageDraw.Draw(s).polygon([(x, y + dy) for x, y in poly], fill=(0, 0, 0, op))
    capa.alpha_composite(s.filter(ImageFilter.GaussianBlur(blur)))

# ---------- metraje real ----------
def extraer(nombre, ss, dur):
    d = T / nombre; d.mkdir(exist_ok=True)
    if not list(d.glob('*.jpg')):
        vf = f'fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}'
        subprocess.run([FF, '-v', 'error', '-y', '-ss', str(ss), '-t', str(dur), '-i', str(A / 'refs' / 'fernando_video.mp4'), '-vf', vf, '-q:v', '3', str(d / '%04d.jpg')], check=True)
    return sorted(d.glob('*.jpg'))
DUR = {k: TI[k]['dur'] + GAP + 0.4 for k in ORDEN}
CL = {'B': extraer('b', 17.0, DUR['B']), 'C': extraer('c', 0.3, DUR['C']), 'D': extraer('d', 38.6, DUR['D'])}
def fr(fs, t):
    return Image.open(fs[min(max(int(t * FPS), 0), len(fs) - 1)]).convert('RGBA')
LOGO = Image.open(A / 'sitio' / 'logo_azul.png').convert('RGBA')

# ---------- etiqueta azul inclinada (estilo del reel) ----------
def etiqueta(t_rel, titulo, spec, y=240):
    k = ease(t_rel / 0.4)
    if k <= 0: return nueva()
    capa = nueva(); d = ImageDraw.Draw(capa)
    ft, fs = fnt(40), fnt(26, False)
    w = max(d.textlength(titulo, font=ft), d.textlength(spec, font=fs)) + 90; h = 118; sk = 26
    x0 = -w + (w + 24) * k
    poly = [(x0 + sk, y), (x0 + w + sk, y), (x0 + w, y + h), (x0, y + h)]
    sombra(capa, poly); d = ImageDraw.Draw(capa)
    d.polygon(poly, fill=AZUL)
    d.polygon([(x0 + sk, y), (x0 + sk + 10, y), (x0 + 10, y + h), (x0, y + h)], fill=AZUL_CL)
    d.text((x0 + 46, y + 38), titulo, font=ft, fill=BLANCO, anchor='lm'); d.text((x0 + 46, y + 86), spec, font=fs, fill=(205, 225, 255), anchor='lm')
    return capa

def con_oscuro(im):
    v = nueva(); ImageDraw.Draw(v).rectangle((0, 0, W, 360), fill=(0, 0, 0, 80)); ImageDraw.Draw(v).rectangle((0, H - 420, W, H), fill=(0, 0, 0, 90))
    im.alpha_composite(v.filter(ImageFilter.GaussianBlur(50))); return im

# ---------- escenas ----------
def esc_video(k, t, titulo, spec):
    tl = t - ini[k]; im = con_oscuro(fr(CL[k], max(tl, 0)))
    im.alpha_composite(etiqueta(tl - 0.1, titulo, spec)); return im

def esc_A(t):
    tl = t - ini['A']; im = IP.FONDO.copy(); capa = nueva()
    celdas = {'caja': (185, 560), 'lector': (535, 560), 'impresora': (185, 800), 'rollos': (535, 800)}
    for i, (clave, caja, etq, cx, cy, hmax) in enumerate(IP.PIEZAS):
        cx, cy = celdas[clave]; e = IP.pop((tl - 0.15 - i * 0.3) / 0.45)
        if tl < 0.15 + i * 0.3: continue
        c = IP.CROP[clave]; p = c.resize((max(1, int(c.width * e)), max(1, int(c.height * e))), Image.LANCZOS)
        sh = Image.new('RGBA', p.size, (0, 0, 0, 0)); sh.putalpha(p.getchannel('A').point(lambda v: int(v * 0.35)))
        capa.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), (int(cx - p.width / 2), int(cy - p.height / 2 + 14)))
        capa.alpha_composite(p, (int(cx - p.width / 2), int(cy - p.height / 2)))
    im.alpha_composite(capa)
    lg = LOGO.resize((330, int(330 * LOGO.height / LOGO.width)), Image.LANCZOS); k = ease(tl / 0.5)
    cc = nueva(); tarj = Image.new('RGBA', (lg.width + 50, lg.height + 40), (255, 255, 255, 235)); m = Image.new('L', tarj.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, tarj.width - 1, tarj.height - 1), 28, fill=255); tarj.putalpha(m)
    tarj.alpha_composite(lg, (25, 20)); cc.alpha_composite(tarj, (W // 2 - tarj.width // 2, 345)); im.alpha_composite(mover(cc, k, 0, (1 - k) * 20))
    im.alpha_composite(etiqueta(tl - 0.05, 'Punto de Venta Anegocios', 'Kit completo', y=170)); return im

def esc_E(t):
    tl = t - ini['E']; im = IP.FONDO.copy(); capa = nueva()
    for i, (txt, y) in enumerate([('Instalación', 520), ('Capacitación', 650), ('Soporte 1 año', 780)]):
        IP.pastilla(capa, W // 2, y, txt, fnt(46), IP.pop((tl - 0.25 - i * 0.45) / 0.45) if tl > 0.25 + i * 0.45 else 0)
    im.alpha_composite(capa); im.alpha_composite(etiqueta(tl - 0.05, 'Todo incluido', 'Instalación · Capacitación · Soporte 1 año', y=200)); return im

def esc_F(t):
    tl = t - ini['F']; im = IP.FONDO.copy(); capa = nueva()
    tp = tl - 0.2
    if tp >= 0:
        esc = IP.pop(tp / 0.5) * (1 + 0.04 * math.sin(max(tp - 0.5, 0) * 8)); pw, ph = 520 * esc, 150 * esc
        s = Image.new('RGBA', (int(pw), int(ph)), (0, 0, 0, 0)); sd = ImageDraw.Draw(s)
        sd.rounded_rectangle((0, 0, pw - 1, ph - 1), int(ph / 2), fill=AMAR); sd.text((pw / 2, ph / 2), '$3,500', font=fnt(max(10, int(104 * esc))), fill=NEGRO, anchor='mm')
        capa.alpha_composite(s, (int(W / 2 - pw / 2), int(520 - ph / 2)))
    k = ease((tl - 1.2) / 0.4)
    if k > 0:
        c2 = nueva(); d = ImageDraw.Draw(c2); d.rounded_rectangle((70, 650, W - 70, 850), 36, fill=(255, 255, 255, 245))
        d.text((W // 2, 700), 'Pago contra entrega', font=fnt(44), fill=AZUL, anchor='mm')
        for i, l in enumerate(['Pagas hasta recibir todo', 'y estar capacitado']): d.text((W // 2, 758 + i * 42), l, font=fnt(32, False), fill=NEGRO, anchor='mm')
        capa.alpha_composite(mover(c2, k, 0, (1 - k) * 30))
    im.alpha_composite(capa); im.alpha_composite(etiqueta(tl - 0.05, 'Precio del kit', 'Software, lector e impresora', y=200)); return im

T_G = ini['G'] - 0.4
def esc_G(t):
    im = IP.FONDO.copy(); tl = t - T_G; k = ease(tl / 0.45); capa = nueva(); esc = IP.pop(tl / 0.45) if tl > 0 else 0
    bw, bh = 620 * esc, 130 * esc; d = ImageDraw.Draw(capa)
    if tl > 0:
        d.rounded_rectangle((W / 2 - bw / 2, 560 - bh / 2, W / 2 + bw / 2, 560 + bh / 2), 60, fill=(37, 211, 102))
        d.text((W // 2, 560), 'Confirma tu entrega en WhatsApp', font=fnt(30), fill=BLANCO, anchor='mm')
    tarj = Image.new('RGBA', (400, int(400 * LOGO.height / LOGO.width) + 40), (255, 255, 255, 240)); m = Image.new('L', tarj.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, tarj.width - 1, tarj.height - 1), 28, fill=255); tarj.putalpha(m)
    lg = LOGO.resize((340, int(340 * LOGO.height / LOGO.width)), Image.LANCZOS); tarj.alpha_composite(lg, (30, 20)); capa.alpha_composite(tarj, (W // 2 - 200, 700))
    d = ImageDraw.Draw(capa); d.text((W // 2, 700 + tarj.height + 50), 'anegocios.com', font=fnt(36, False), fill=BLANCO, anchor='mm')
    im.alpha_composite(mover(capa, k, 0, (1 - k) * 30)); return im

# ---------- subtítulos kinéticos ----------
CHUNKS = []
for k in ORDEN:
    cur = []
    for i, (w, a, b) in enumerate(PAL[k]):
        cur.append((w, a, b))
        if w[-1] in ',.:?;' or len(cur) >= 4 or sum(len(x[0]) + 1 for x in cur) > 21 or i == len(PAL[k]) - 1:
            CHUNKS.append(cur); cur = []
def subtitulo(t):
    ch = None
    for i, c in enumerate(CHUNKS):
        a0 = c[0][1] - 0.05; a1 = CHUNKS[i + 1][0][1] - 0.05 if i + 1 < len(CHUNKS) else c[-1][2] + 0.6
        if a0 <= t < a1: ch = c; kin = clamp((t - a0) / 0.14); break
    if not ch: return None
    capa = nueva(); d = ImageDraw.Draw(capa); f = fnt(58)
    ws = [w for w, _, _ in ch]; an = [d.textlength(w + ' ', font=f) for w in ws]; tot = sum(an) - d.textlength(' ', font=f)
    if tot > W - 70: f = fnt(int(58 * (W - 70) / tot)); an = [d.textlength(w + ' ', font=f) for w in ws]; tot = sum(an) - d.textlength(' ', font=f)
    y = 1000
    d.rounded_rectangle((W / 2 - tot / 2 - 28, y - 52, W / 2 + tot / 2 + 28, y + 52), 30, fill=(0, 0, 0, 150))
    x = W / 2 - tot / 2
    for (w, a, b), n in zip(ch, an):
        yy = y
        if a - 0.02 <= t < b + 0.02: col = AZUL_CL; yy = y - 5 * math.sin(clamp((t - a) / 0.16) * math.pi)
        elif t >= b: col = BLANCO
        else: col = GRIS
        d.text((x, yy), w, font=f, fill=col, anchor='lm'); x += n
    return mover(capa, kin * 0.7 + 0.3, 0, (1 - kin) * 14)

def componer(t):
    lim = lambda k: ini[k] - 0.05
    if t < lim('B'): im = esc_A(t)
    elif t < lim('C'): im = esc_video('B', t, 'Software · 1 año', 'Ventas · Inventario · Corte de caja')
    elif t < lim('D'): im = esc_video('C', t, 'Lector de códigos', 'Escaneas y cobras en segundos')
    elif t < lim('E'): im = esc_video('D', t, 'Impresora de tickets', 'Comprobante al instante')
    elif t < lim('F'): im = esc_E(t)
    elif t < T_G: im = esc_F(t)
    else: im = esc_G(t)
    s = subtitulo(t)
    if s: im.alpha_composite(s)
    return im.convert('RGB')

def musica():
    import numpy as np, wave
    sr = 44100; n = int((FIN + 1) * sr); tt = np.arange(n) / sr; bpm = 92; beat = 60 / bpm
    acordes = [(220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (261.63, 329.63, 392.0), (196.0, 246.94, 293.66)]
    y = np.zeros(n)
    for i in range(int((FIN + 1) / (beat * 4)) + 1):
        a, b = int(i * beat * 4 * sr), min(n, int((i + 1) * beat * 4 * sr))
        if a >= n: break
        seg = tt[a:b] - tt[a]; env = np.minimum(1, seg / 0.4) * np.minimum(1, (tt[b - 1] - tt[a:b] + 0.001) / 0.5)
        for f0 in acordes[i % 4]: y[a:b] += env * (np.sin(2 * np.pi * f0 * seg) + 0.5 * np.sin(2 * np.pi * (f0 * 1.003) * seg)) * 0.12
        for j in range(8):
            s0 = int(a + j * beat / 2 * sr)
            if s0 >= n: break
            m = min(int(0.5 * sr), n - s0); ts = np.arange(m) / sr; f0 = acordes[i % 4][j % 3] * 2
            y[s0:s0 + m] += np.sin(2 * np.pi * f0 * ts) * np.exp(-ts * 6) * 0.10
    y = y / (np.abs(y).max() + 1e-9) * 0.8
    with wave.open(str(T / 'musica.wav'), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((y * 32767).astype('<i2').tobytes())

def main():
    N = int(FIN * FPS); mudo = T / 'mudo.mp4'
    p = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'fast', str(mudo)], stdin=subprocess.PIPE)
    for i in range(N):
        p.stdin.write(componer(i / FPS).tobytes())
        if i % 150 == 0: print('frame', i, '/', N, flush=True)
    p.stdin.close(); p.wait(); musica()
    n = len(ORDEN); fa = ''.join(f'[{i + 1}:a]adelay={int(ini[k] * 1000)}|{int(ini[k] * 1000)}[a{i}];' for i, k in enumerate(ORDEN))
    ins = sum([['-i', str(A / 'voz_showcase' / f'{k}.wav')] for k in ORDEN], []) + ['-i', str(T / 'musica.wav')]
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(mudo), *ins, '-filter_complex', fa + ''.join(f'[a{i}]' for i in range(n)) + f'amix=inputs={n}:normalize=0:duration=longest,volume=1.6[mix];[{n + 1}:a]afade=t=in:st=3:d=1.5,afade=t=out:st={FIN - 1.5:.2f}:d=1.5,volume=0.1[mus];[mix][mus]amix=inputs=2:normalize=0[aud]',
                    '-map', '0:v', '-map', '[aud]', '-t', f'{FIN:.2f}', '-c:v', 'libx264', '-profile:v', 'main', '-level', '4.0', '-pix_fmt', 'yuv420p', '-crf', '23', '-preset', 'medium',
                    '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(SALIDA)], check=True)
    print('listo', SALIDA, round(SALIDA.stat().st_size / 1e6, 1), 'MB', round(FIN, 1), 's')

if __name__ == '__main__':
    print('inicios', {k: round(v, 2) for k, v in ini.items()}, 'fin', round(FIN, 2))
    if '--prueba' in sys.argv:
        puntos = [('A', ini['A'] + 1.8), ('B', ini['B'] + 1.8), ('C', ini['C'] + 1.5), ('D', ini['D'] + 1.5), ('E', ini['E'] + 2.2), ('F1', ini['F'] + 1.0), ('F2', ini['F'] + 3.0), ('G', ini['G'] + 1.2)]
        for n, tt in puntos: componer(tt).save(T / f'p_{n}.png')
        hoja = Image.new('RGB', (4 * 360, 2 * 640))
        for i, (n, _) in enumerate(puntos): hoja.paste(Image.open(T / f'p_{n}.png').resize((360, 640)), ((i % 4) * 360, (i // 4) * 640))
        hoja.save(T / 'hoja_showcase.jpg', quality=85); print('pruebas listas')
    else:
        main()
