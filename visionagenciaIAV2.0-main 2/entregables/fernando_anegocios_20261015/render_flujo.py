"""Anegocios · FLUJO DE TRABAJO paso a paso (estilo motion graphics tipo Uriel, proceso visible).
Pasos 1-4 = metraje REAL de Fernando (lector, compra total, cobro, ticket). Paso 5 = esquema (texto del sitio anegocios.com).
Paso 6 = clip Modal M3 (vendedor de ruta con app Android; texto del sitio). Cierre con 'Pago contra entrega' y 'Confirma tu entrega en WhatsApp'."""
import json, math, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg

A = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 720, 1280, 30
SALIDA = A / 'final' / 'Anegocios_flujo_trabajo_v1.mp4'
T = A / 'tmp_flujo'; T.mkdir(exist_ok=True)
FD = '/usr/share/fonts/truetype/dejavu/'
def fnt(s, b=True, mono=False):
    return ImageFont.truetype(FD + ('DejaVuSansMono-Bold.ttf' if mono else ('DejaVuSans-Bold.ttf' if b else 'DejaVuSans.ttf')), s)
BG = (238, 238, 236); NEGRO = (17, 17, 17); GRIS = (165, 165, 165); AZUL = (10, 84, 200); AZUL_CL = (96, 170, 255)
VERDE = (37, 170, 90); BLANCO = (255, 255, 255)

TI = json.loads((A / 'voz_flujo' / 'tiempos.json').read_text())
ORDEN = ['H', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'E', 'F']
TXT = {k: TI[k]['texto'] for k in ORDEN}
ini, t = {}, 0.2
for k in ORDEN:
    ini[k] = t; t += TI[k]['dur'] + 0.12
DUR_ESC = {k: max(TI[k]['dur'] + 0.2, 1.9) for k in ['H', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6']}
# cada escena arranca cuando arranca su voz; S3 dura un poco más que su voz (el cobro necesita verse)
FIN = ini['F'] + TI['F']['dur'] + 2.9

def palabras_t(k):
    ws = TXT[k].split(); pw = TI[k]['palabras']
    a, b = ini[k] + pw[0][1], ini[k] + pw[-1][2]
    pausa = lambda w: 4 if w[-1] in ',.:?;' else 0
    pesos = [len(w) + pausa(w) for w in ws]; tot, acc, out = sum(pesos), 0, []
    for w, p in zip(ws, pesos):
        s0 = a + (b - a) * acc / tot; acc += p; out.append((w, s0, a + (b - a) * (acc - pausa(w)) / tot))
    return out
PAL = {k: palabras_t(k) for k in ORDEN}
def tw(k, inicio):
    for w, a, b in PAL[k]:
        if w.lower().strip(',.:?;').startswith(inicio): return a
    raise KeyError(inicio)

ease = lambda x: 1 - (1 - min(max(x, 0), 1)) ** 3
clamp = lambda x: min(max(x, 0.0), 1.0)
pop = lambda x: 1 + 0.08 * math.sin(clamp(x) * math.pi) * (1 - clamp(x)) if x < 1 else 1

def sombra(capa, caja, r, op=70, blur=22, dy=14):
    s = Image.new('RGBA', capa.size, (0, 0, 0, 0)); ImageDraw.Draw(s).rounded_rectangle((caja[0], caja[1] + dy, caja[2], caja[3] + dy), r, fill=(0, 0, 0, op))
    capa.alpha_composite(s.filter(ImageFilter.GaussianBlur(blur)))
def tarjeta(capa, caja, r=34, color=BLANCO):
    sombra(capa, caja, r); ImageDraw.Draw(capa).rounded_rectangle(caja, r, fill=color)
def texto(d, xy, s, f, fill, anchor='la'): d.text(xy, s, font=f, fill=fill, anchor=anchor)
def nueva(): return Image.new('RGBA', (W, H), (0, 0, 0, 0))
def mover(capa, a, dx=0, dy=0):
    if a < 1:
        al = capa.getchannel('A').point(lambda v: int(v * a)); capa = capa.copy(); capa.putalpha(al)
    if dx or dy:
        n = Image.new('RGBA', capa.size, (0, 0, 0, 0)); n.alpha_composite(capa, (int(dx), int(dy))); capa = n
    return capa

# ---------------- clips (metraje real y M3) ----------------
def extraer(nombre, fuente, ss, dur, vf_extra=''):
    d = T / nombre; d.mkdir(exist_ok=True)
    if not list(d.glob('*.jpg')):
        vf = (vf_extra + ',' if vf_extra else '') + f'fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}'
        subprocess.run([FF, '-v', 'error', '-y', '-ss', str(ss), '-t', str(dur), '-i', str(fuente), '-vf', vf, '-q:v', '3', str(d / '%04d.jpg')], check=True)
    return sorted(d.glob('*.jpg'))
REAL = A / 'refs' / 'fernando_video.mp4'
CL = {'S1': extraer('s1', REAL, 0.3, 3.0), 'S2': extraer('s2', REAL, 17.0, 3.6), 'S3': extraer('s3', REAL, 27.0, 2.2),
      'S4': extraer('s4', REAL, 38.6, 2.8), 'S6': extraer('s6', A / 'clips_v3' / 'M3.mp4', 0, 5.17)}
def fr(fs, t):
    i = min(max(int(t * FPS), 0), len(fs) - 1); return Image.open(fs[i]).convert('RGBA')
LOGO = Image.open(A / 'sitio' / 'logo_azul.png').convert('RGBA')

# ---------------- subtítulos kinéticos ----------------
CHUNKS = []
for k in ORDEN:
    cur = []
    for i, (w, a, b) in enumerate(PAL[k]):
        cur.append((w, a, b))
        if w[-1] in ',.:?;' or len(cur) >= 4 or sum(len(x[0]) + 1 for x in cur) > 21 or i == len(PAL[k]) - 1:
            CHUNKS.append(cur); cur = []
def subtitulo(t, oscuro):
    ch = None
    for i, c in enumerate(CHUNKS):
        a0 = c[0][1] - 0.05; a1 = CHUNKS[i + 1][0][1] - 0.05 if i + 1 < len(CHUNKS) else c[-1][2] + 0.6
        if a0 <= t < a1: ch = c; kin = clamp((t - a0) / 0.14); break
    if not ch: return None
    capa = nueva(); d = ImageDraw.Draw(capa); f = fnt(58)
    ws = [w for w, _, _ in ch]; an = [d.textlength(w + ' ', font=f) for w in ws]; tot = sum(an) - d.textlength(' ', font=f)
    if tot > W - 70: f = fnt(int(58 * (W - 70) / tot)); an = [d.textlength(w + ' ', font=f) for w in ws]; tot = sum(an) - d.textlength(' ', font=f)
    y = 1000
    if oscuro: d.rounded_rectangle((W / 2 - tot / 2 - 28, y - 52, W / 2 + tot / 2 + 28, y + 52), 30, fill=(0, 0, 0, 150))
    x = W / 2 - tot / 2
    for (w, a, b), n in zip(ch, an):
        yy = y
        if a - 0.02 <= t < b + 0.02: col = AZUL_CL if oscuro else AZUL; yy = y - 5 * math.sin(clamp((t - a) / 0.16) * math.pi)
        elif t >= b: col = BLANCO if oscuro else NEGRO
        else: col = (200, 200, 200) if oscuro else (178, 178, 176)
        d.text((x, yy), w, font=f, fill=col, anchor='lm'); x += n
    return mover(capa, kin * 0.7 + 0.3, 0, (1 - kin) * 14)

# ---------------- elementos de paso ----------------
PASOS = [('S1', 'ESCANEA'), ('S2', 'COMPRA TOTAL'), ('S3', 'COBRA'), ('S4', 'TICKET'), ('S5', 'INVENTARIO Y CAJA'), ('S6', 'EN RUTA')]
def chip_paso(k, t):
    n = [p[0] for p in PASOS].index(k) + 1; et = dict(PASOS)[k]
    kk = ease((t - ini[k] + 0.1) / 0.35); capa = nueva(); d = ImageDraw.Draw(capa); f = fnt(36)
    w = d.textlength(et, font=f) + 150; y = 215
    sombra(capa, (W / 2 - w / 2, y - 40, W / 2 + w / 2, y + 40), 40, 60, 14, 8); d = ImageDraw.Draw(capa)
    d.rounded_rectangle((W / 2 - w / 2, y - 40, W / 2 + w / 2, y + 40), 40, fill=AZUL)
    d.ellipse((W / 2 - w / 2 + 8, y - 32, W / 2 - w / 2 + 72, y + 32), fill=BLANCO); texto(d, (W / 2 - w / 2 + 40, y), str(n), fnt(40), AZUL, 'mm')
    texto(d, (W / 2 - w / 2 + 90, y), et, f, BLANCO, 'lm')
    # barra de progreso de 6 pasos
    bw = 56; gap = 10; x0 = W / 2 - (6 * bw + 5 * gap) / 2
    for i in range(6):
        d.rounded_rectangle((x0 + i * (bw + gap), 275, x0 + i * (bw + gap) + bw, 285), 5, fill=AZUL_CL if i < n else (255, 255, 255, 110))
    return mover(capa, kk, 0, -(1 - kk) * 40)
def pastilla(capa, y, texto_, color, icono, kk):
    if kk <= 0: return
    c = nueva(); d = ImageDraw.Draw(c); f = fnt(34); w = d.textlength(texto_, font=f) + 110
    sombra(c, (W / 2 - w / 2, y - 40, W / 2 + w / 2, y + 40), 40, 70, 12, 8); d = ImageDraw.Draw(c)
    d.rounded_rectangle((W / 2 - w / 2, y - 40, W / 2 + w / 2, y + 40), 40, fill=NEGRO)
    d.ellipse((W / 2 - w / 2 + 14, y - 26, W / 2 - w / 2 + 66, y + 26), fill=color); texto(d, (W / 2 - w / 2 + 40, y), icono, fnt(30), BLANCO, 'mm')
    texto(d, (W / 2 - w / 2 + 84, y), texto_, f, BLANCO, 'lm')
    capa.alpha_composite(mover(c, clamp(kk * 1.4), 0, (1 - clamp(kk)) * 30))
PAST = {'S1': ('Lector de códigos', 'lector'), 'S2': ('Total al instante', 'total'), 'S3': ('Confirmas el cobro', 'cobras'), 'S4': ('Ticket impreso', 'ticket'), 'S6': ('App Android → Tienda · en tiempo real', 'tiempo')}
def escena_video(k, t):
    tl = t - ini[k]; im = fr(CL[k], max(tl, 0))
    v = nueva(); ImageDraw.Draw(v).rectangle((0, 0, W, 330), fill=(0, 0, 0, 90)); ImageDraw.Draw(v).rectangle((0, H - 560, W, H), fill=(0, 0, 0, 80))
    im.alpha_composite(v.filter(ImageFilter.GaussianBlur(50)))
    im.alpha_composite(chip_paso(k, t))
    capa = nueva(); et, clave = PAST[k]; t0 = tw(k, clave) if clave in TXT[k].lower() else ini[k] + 0.6
    pastilla(capa, 860, et, VERDE if k != 'S6' else AZUL, '✓' if k != 'S6' else '→', (t - t0 + 0.05) / 0.3)
    im.alpha_composite(capa); return im

# ---------------- intro ----------------
def escena_h(t):
    im = Image.new('RGBA', (W, H), BG + (255,)); capa = nueva(); tl = t - ini['H']; k = ease(tl / 0.5)
    lg = LOGO.resize((int(420 * pop(tl / 0.5)), int(420 * LOGO.height / LOGO.width * pop(tl / 0.5))), Image.LANCZOS)
    tarjeta(capa, (60, 330, W - 60, 760), 40); capa.alpha_composite(lg, (W // 2 - lg.width // 2, 470 - lg.height // 2 + 20))
    d = ImageDraw.Draw(capa); texto(d, (W // 2, 640), 'Punto de venta paso a paso', fnt(34, False), (90, 90, 90), 'mm')
    bw = 70; gap = 14; x0 = W / 2 - (6 * bw + 5 * gap) / 2
    for i in range(6):
        pk = ease((t - (ini['H'] + 0.15 + i * 0.12)) / 0.3); d.rounded_rectangle((x0 + i * (bw + gap), 700, x0 + i * (bw + gap) + bw * pk, 712), 6, fill=AZUL)
    im.alpha_composite(mover(capa, k, 0, (1 - k) * 30)); return im

# ---------------- paso 5: esquema inventario + corte de caja (texto del sitio) ----------------
def barra(d, x, y, w, frac, color, etiqueta):
    texto(d, (x, y - 30), etiqueta, fnt(26, False), (90, 90, 90), 'lm')
    d.rounded_rectangle((x, y, x + w, y + 24), 12, fill=(228, 228, 226)); d.rounded_rectangle((x, y, x + max(24, w * frac), y + 24), 12, fill=color)
def escena_s5(t):
    im = Image.new('RGBA', (W, H), BG + (255,)); tl = t - ini['S5']; capa = nueva()
    k1 = ease((tl - 0.1) / 0.45); k2 = ease((tl - 0.9) / 0.45)
    c1 = nueva(); tarjeta(c1, (60, 340, W - 60, 640)); d = ImageDraw.Draw(c1)
    texto(d, (100, 380), 'Inventario actualizado', fnt(34), NEGRO, 'lm')
    for i, (et, fr_, col) in enumerate([('Entradas', .72, VERDE), ('Salidas', .45, (230, 140, 40)), ('Existencias', .6, AZUL)]):
        barra(d, 100, 460 + i * 68, 520, fr_ * ease((tl - 0.3 - i * .15) / 0.6), col, et)
    capa.alpha_composite(mover(c1, k1, 0, (1 - k1) * 40))
    c2 = nueva(); tarjeta(c2, (60, 680, W - 60, 960)); d = ImageDraw.Draw(c2)
    texto(d, (100, 720), 'Corte de caja claro', fnt(34), NEGRO, 'lm')
    barra(d, 100, 810, 520, .8 * ease((tl - 1.1) / 0.6), AZUL, 'Vendido'); barra(d, 100, 880, 520, .8 * ease((tl - 1.3) / 0.6), VERDE, 'Cobrado')
    texto(d, (W // 2, 935), 'Compara lo vendido con lo cobrado', fnt(24, False), (110, 110, 110), 'mm')
    capa.alpha_composite(mover(c2, k2, 0, (1 - k2) * 40))
    d = ImageDraw.Draw(capa); texto(d, (W // 2, 330), 'ESQUEMA ILUSTRATIVO', fnt(18), GRIS, 'mm')
    im.alpha_composite(capa); im.alpha_composite(chip_paso('S5', t)); return im

# ---------------- cierre ----------------
T_E = ini['E'] - 0.3; T_F = ini['F'] - 0.4
def escena_e(t):
    tl = t - T_E; k = ease(tl / 0.45); capa = nueva(); d = ImageDraw.Draw(capa)
    d.ellipse((W // 2 - 44, 190, W // 2 + 44, 278), fill=AZUL); texto(d, (W // 2, 234), '✓', fnt(58), BLANCO, 'mm')
    texto(d, (W // 2, 340), 'Pago contra entrega', fnt(52), AZUL, 'mm')
    for i, l in enumerate(['Pagas hasta recibir tu', 'impresora, lector y estar', 'capacitado.']): texto(d, (W // 2, 430 + i * 56), l, fnt(42), NEGRO, 'mm')
    tb = t - T_F; kb = ease(tb / 0.45); esc = pop(tb / 0.45) if tb > 0 else 0
    if tb > 0:
        bw, bh = 620 * esc, 130 * esc; b = nueva(); sombra(b, (W / 2 - bw / 2, 700 - bh / 2, W / 2 + bw / 2, 700 + bh / 2), 60); bd = ImageDraw.Draw(b)
        bd.rounded_rectangle((W / 2 - bw / 2, 700 - bh / 2, W / 2 + bw / 2, 700 + bh / 2), 60, fill=(37, 211, 102)); texto(bd, (W // 2, 700), 'Confirma tu entrega en WhatsApp', fnt(30), BLANCO, 'mm')
        capa.alpha_composite(mover(b, kb, 0, (1 - kb) * 30))
    lg = LOGO.resize((300, int(300 * LOGO.height / LOGO.width)), Image.LANCZOS); capa.alpha_composite(lg, (W // 2 - 150, 800))
    d = ImageDraw.Draw(capa); texto(d, (W // 2, 930), 'anegocios.com', fnt(34, False), (90, 90, 90), 'mm')
    return mover(capa, k, 0, (1 - k) * 30)

def componer(t):
    if t < ini['S1'] - 0.05: im = escena_h(t); s = subtitulo(t, False)
    elif t < ini['S2'] - 0.05: im = escena_video('S1', t); s = subtitulo(t, True)
    elif t < ini['S3'] - 0.05: im = escena_video('S2', t); s = subtitulo(t, True)
    elif t < ini['S4'] - 0.05: im = escena_video('S3', t); s = subtitulo(t, True)
    elif t < ini['S5'] - 0.05: im = escena_video('S4', t); s = subtitulo(t, True)
    elif t < ini['S6'] - 0.05: im = escena_s5(t); s = subtitulo(t, False)
    elif t < T_E: im = escena_video('S6', t); s = subtitulo(t, True)
    else:
        im = Image.new('RGBA', (W, H), BG + (255,)); im.alpha_composite(escena_e(t)); s = subtitulo(t, False)
    if s: im.alpha_composite(s)
    return im.convert('RGB')

def musica():
    import numpy as np, wave
    sr = 44100; n = int((FIN + 1) * sr); tt = np.arange(n) / sr; bpm = 84; beat = 60 / bpm
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
    ins = sum([['-i', str(A / 'voz_flujo' / f'{k}.wav')] for k in ORDEN], []) + ['-i', str(T / 'musica.wav')]
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(mudo), *ins, '-filter_complex', fa + ''.join(f'[a{i}]' for i in range(n)) + f'amix=inputs={n}:normalize=0:duration=longest,volume=1.6[mix];[{n + 1}:a]afade=t=in:st=3:d=1.5,afade=t=out:st={FIN - 1.5:.2f}:d=1.5,volume=0.1[mus];[mix][mus]amix=inputs=2:normalize=0[aud]',
                    '-map', '0:v', '-map', '[aud]', '-t', f'{FIN:.2f}', '-c:v', 'libx264', '-profile:v', 'main', '-level', '4.0', '-pix_fmt', 'yuv420p', '-crf', '23', '-preset', 'medium',
                    '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(SALIDA)], check=True)
    print('listo', SALIDA, round(SALIDA.stat().st_size / 1e6, 1), 'MB', round(FIN, 1), 's')

if __name__ == '__main__':
    print('inicios', {k: round(v, 2) for k, v in ini.items()}, 'fin', round(FIN, 2))
    if '--prueba' in sys.argv:
        puntos = [('h', ini['H'] + 1.2), ('s1', ini['S1'] + 1.5), ('s2', ini['S2'] + 1.8), ('s3', ini['S3'] + 1.2), ('s4', ini['S4'] + 1.5), ('s5', ini['S5'] + 2.2), ('s6', ini['S6'] + 3.5), ('e', ini['E'] + 1.0), ('f', ini['F'] + 0.9)]
        for n, tt in puntos: componer(tt).save(T / f'p_{n}.png')
        hoja = Image.new('RGB', (5 * 360, 2 * 640))
        for i, (n, _) in enumerate(puntos): hoja.paste(Image.open(T / f'p_{n}.png').resize((360, 640)), ((i % 5) * 360, (i // 5) * 640))
        hoja.save(T / 'hoja_flujo.jpg', quality=85); print('pruebas listas')
    else:
        main()
