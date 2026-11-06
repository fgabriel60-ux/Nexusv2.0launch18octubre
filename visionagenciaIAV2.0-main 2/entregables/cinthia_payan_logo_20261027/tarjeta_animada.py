"""Tarjeta digital animada de Cinthia Payán (1080x1920, 12 s, 30 fps): el logo se revela en barrido circular, el tallo de la
peonía se dibuja solo (la apertura de la mente) y termina en la flor que florece; la información entra en secuencia y el botón
de WhatsApp late al final. Uso: python3 tarjeta_animada.py"""
import math, random, subprocess
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter
import sys
from armar_logo import AQUI, LILA, ROSA, TURQ, degradado, icono_rgba
from armar_tarjeta import fuente, SERVICIOS, GRIS

W, H, FPS, DUR = 1080, 1920, 30, 12.0
SS = 2  # supersampling del tallo
VERDE = (37, 176, 102)


def capa_texto(txt, f, cols, espacio=0):
    d = ImageDraw.Draw(Image.new('L', (1, 1)))
    anchos = [d.textlength(c, font=f) + espacio for c in txt]
    w = int(sum(anchos) - espacio) + 6; asc, desc = f.getmetrics(); h = asc + desc + 4
    m = Image.new('L', (w, h)); dm = ImageDraw.Draw(m); x = 0
    for c, a in zip(txt, anchos):
        dm.text((x, 0), c, font=f, fill=255); x += a
    rgb = degradado(w, h, cols) if len(cols) > 1 else Image.new('RGB', (w, h), cols[0])
    rgb.putalpha(m); return rgb


def boton():
    f = fuente('Montserrat.ttf', 44, 600); t = capa_texto('WhatsApp  631 132 9429', f, [(255, 255, 255)])
    b = Image.new('RGBA', (t.width + 120, t.height + 46)); d = ImageDraw.Draw(b)
    d.rounded_rectangle((0, 0, b.width - 1, b.height - 1), radius=b.height // 2, fill=VERDE + (255,))
    d.ellipse((34, b.height // 2 - 16, 66, b.height // 2 + 16), outline=(255, 255, 255), width=5)
    b.alpha_composite(t, (88, 21)); return b


def ease(t): return 1 - (1 - max(0, min(1, t))) ** 3
def ease_back(t):
    t = max(0, min(1, t)); c = 1.7; return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


def catmull(puntos, n=60):
    P = [puntos[0]] + puntos + [puntos[-1]]; out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in range(2)))
    return out + [puntos[-1]]


# ---------- capas fijas ----------
VERDE_FONDO = 'verde' in sys.argv
ARRIBA, ABAJO = ((240, 248, 242), (222, 240, 228)) if VERDE_FONDO else ((255, 255, 255), (244, 236, 248))
fondo = Image.new('RGB', (W, H))
for y in range(H):
    t = y / H; ImageDraw.Draw(fondo).line((0, y, W, y), fill=tuple(int(a + (b - a) * t) for a, b in zip(ARRIBA, ABAJO)))
fondo = fondo.convert('RGBA')

ic = icono_rgba('b2p'); ic = ic.resize((int(ic.width * 440 / ic.height), 440), Image.LANCZOS)
IC_XY = ((W - ic.width) // 2, 110)

X0 = 110
ELEM = []  # (capa, (x, y), t_inicio)
def centrado(capa, y, t): ELEM.append((capa, ((W - capa.width) // 2, y), t))
centrado(capa_texto('Cinthia Payán', fuente('Cormorant.ttf', 130, 600), [LILA, ROSA, TURQ]), 565, 1.3)
centrado(capa_texto('Lic. Psicología', fuente('Cormorant.ttf', 68, 500), [GRIS]), 718, 1.7)
centrado(capa_texto('ENTENDER · SANAR · CRECER', fuente('Montserrat.ttf', 34, 500), [LILA, TURQ], espacio=8), 808, 2.0)
y = 900
ELEM.append((capa_texto('Terapia Psicológica', fuente('Cormorant.ttf', 92, 600), [LILA, ROSA, TURQ]), (X0, y), 2.8)); y += 105
ELEM.append((capa_texto('ADOLESCENTES Y ADULTOS', fuente('Montserrat.ttf', 30, 600), [LILA, TURQ], espacio=6), (X0 + 4, y), 3.1)); y += 62
fs = fuente('Montserrat.ttf', 37, 400)
for k, s in enumerate(SERVICIOS):
    rs = [capa_texto(r, fs, [GRIS]) for r in s.split('\n')]
    c = Image.new('RGBA', (max(r.width for r in rs) + 40, sum(r.height for r in rs) - 4 * (len(rs) - 1)))
    ImageDraw.Draw(c).ellipse((2, 18, 15, 31), fill=ROSA); yy = 0
    for r in rs: c.alpha_composite(r, (36, yy)); yy += r.height - 4
    ELEM.append((c, (X0, y), 3.4 + 0.28 * k)); y += c.height + 10
y += 22
ELEM.append((capa_texto('Agenda tu consulta', fuente('Cormorant.ttf', 72, 600), [LILA, TURQ]), (X0, y), 5.0)); y += 92
BOTON = boton(); BOTON_XY = (X0, y); T_BOTON = 5.4; y += BOTON.height + 24
fp = fuente('Montserrat.ttf', 34, 400)
for k, s in enumerate(['Calle Lago Espejo #69', 'Col. Jardines de la Montaña']):
    ELEM.append((capa_texto(s, fp, [GRIS]), (X0, y), 5.8 + 0.2 * k)); y += 44
ELEM.append((capa_texto('Cédula Profesional 5455037', fp, [GRIS]), (X0, y + 10), 6.3))
# logo de Jayil chiquito abajo a la derecha del texto, con «Somos Jayil» (mismo logo de las tarjetas impresas)
jay = Image.open(AQUI / 'refs' / 'jayil_logo.png').convert('RGBA'); jay = jay.resize((int(jay.width * 140 / jay.height), 140), Image.LANCZOS)
somos = capa_texto('Somos Jayil', fuente('Cormorant.ttf', 40, 600), [LILA, TURQ])
ELEM.append((jay, (745 - jay.width // 2, 1660), 6.6))
ELEM.append((somos, (745 - somos.width // 2, 1806), 6.9))
print('fin del texto', y + 60)

# tallo: nace abajo a la izquierda, ondula y sube por la derecha hasta la peonía
PEONIA_C = (968, 1005)
pts = catmull([(-30, 1875), (260, 1850), (520, 1900), (800, 1860), (975, 1730), (1015, 1500), (995, 1250), (PEONIA_C[0], PEONIA_C[1] + 75)])
largos = [0]
for a, b in zip(pts, pts[1:]): largos.append(largos[-1] + math.dist(a, b))
TOTAL = largos[-1]
GRAD = degradado(W * SS, H * SS, [TURQ, LILA, ROSA]).convert('RGBA')
T_TALLO = (2.4, 4.6)

flor = Image.open(AQUI / 'refs' / 'peonia_flor.png').convert('RGB')
flor = flor.resize((int(flor.width * 170 / flor.height), 170), Image.LANCZOS)
fm = Image.eval(flor.convert('L'), lambda v: min(255, (255 - v) * 5)); flor = flor.convert('RGBA'); flor.putalpha(fm)
T_FLOR = 4.3

random.seed(7)
PETALOS = [(random.uniform(0, W), random.uniform(0, H), random.uniform(5, 11), random.uniform(18, 45), random.uniform(0, 6.28)) for _ in range(14)]


def hoja(d, base, ang, largo, color, esc):
    a = math.radians(ang); n = (math.cos(a), math.sin(a)); p = (-n[1], n[0]); c = []
    for k in list(range(21)) + list(range(20, -1, -1)):
        t = k / 20; s = 1 if len(c) < 21 else -1; w = math.sin(math.pi * t) * largo * 0.28 * s
        c.append(((base[0] + n[0] * largo * t + p[0] * w) * esc, (base[1] + n[1] * largo * t + p[1] * w) * esc))
    d.line(c + [c[0]], fill=color, width=3 * esc)


def cuadro(t):
    L = fondo.copy()
    # pétalos flotando (muy sutiles)
    pc = Image.new('RGBA', (W, H)); pd = ImageDraw.Draw(pc)
    for x, y0, r, vel, fase in PETALOS:
        y = (y0 - vel * t) % H; xx = x + 18 * math.sin(t * 0.8 + fase)
        pd.ellipse((xx - r, y - r * 0.55, xx + r, y + r * 0.55), fill=(236, 150, 195, int(75 * min(1, t / 1.5))))
    L.alpha_composite(pc.filter(ImageFilter.GaussianBlur(2)))
    # logo: barrido circular + leve escala
    p = ease((t - 0.1) / 1.4)
    if p > 0:
        m = Image.new('L', ic.size); ImageDraw.Draw(m).pieslice((-ic.width, -ic.height, ic.width * 2, ic.height * 2), -90, -90 + 360 * p, fill=255)
        capa = ic.copy(); capa.putalpha(Image.composite(ic.getchannel('A'), Image.new('L', ic.size), m))
        s = 0.94 + 0.06 * p; cw, ch = int(ic.width * s), int(ic.height * s)
        L.alpha_composite(capa.resize((cw, ch), Image.LANCZOS), (IC_XY[0] + (ic.width - cw) // 2, IC_XY[1] + (ic.height - ch) // 2))
    # textos
    for capa, (x, y), t0 in ELEM:
        q = ease((t - t0) / 0.7)
        if q <= 0: continue
        c = capa.copy(); c.putalpha(c.getchannel('A').point(lambda v: int(v * q)))
        L.alpha_composite(c, (x, int(y + 34 * (1 - q))))
    # tallo que se dibuja
    f = ease((t - T_TALLO[0]) / (T_TALLO[1] - T_TALLO[0]))
    if f > 0:
        lim = TOTAL * f; vis = [pt for pt, l in zip(pts, largos) if l <= lim]
        m = Image.new('L', (W * SS, H * SS)); d = ImageDraw.Draw(m)
        if len(vis) > 1: d.line([(x * SS, y * SS) for x, y in vis], fill=255, width=7 * SS, joint='curve')
        for base, ang, lg, umbral in [((560, 1885), -70, 75, 0.35), ((1000, 1620), -160, 85, 0.62), ((1008, 1330), -20, 80, 0.8)]:
            if f > umbral: hoja(d, base, ang, lg * ease((f - umbral) / 0.15), 255, SS)
        g = GRAD.copy(); g.putalpha(m); L.alpha_composite(g.resize((W, H), Image.LANCZOS))
    # la peonía florece
    q = ease_back((t - T_FLOR) / 1.0)
    if q > 0:
        s = max(0.05, q); fl = flor.resize((max(1, int(flor.width * s)), max(1, int(flor.height * s))), Image.LANCZOS)
        fl = fl.rotate(12 * (1 - min(1, q)) + 2 * math.sin(t * 1.2), resample=Image.BICUBIC, expand=True)
        a = min(1, (t - T_FLOR) / 0.4); fl.putalpha(fl.getchannel('A').point(lambda v: int(v * a)))
        L.alpha_composite(fl, (PEONIA_C[0] - fl.width // 2, PEONIA_C[1] - fl.height // 2))
    # botón de WhatsApp: entra y luego late
    q = ease_back((t - T_BOTON) / 0.6)
    if q > 0:
        late = 1 + (0.035 * math.sin((t - T_BOTON - 0.6) * 5.5) if t > T_BOTON + 0.8 else 0)
        s = q * late; b = BOTON.resize((max(1, int(BOTON.width * s)), max(1, int(BOTON.height * s))), Image.LANCZOS)
        if t > T_BOTON + 0.8:
            brillo = Image.new('RGBA', (BOTON.width + 60, BOTON.height + 60))
            ImageDraw.Draw(brillo).rounded_rectangle((30, 30, BOTON.width + 29, BOTON.height + 29), radius=BOTON.height // 2,
                                                     fill=VERDE + (int(60 + 40 * math.sin((t - T_BOTON) * 5.5)),))
            L.alpha_composite(brillo.filter(ImageFilter.GaussianBlur(18)), (BOTON_XY[0] - 30, BOTON_XY[1] - 30))
        L.alpha_composite(b, (BOTON_XY[0] + (BOTON.width - b.width) // 2, BOTON_XY[1] + (BOTON.height - b.height) // 2))
    return L.convert('RGB')


if __name__ == '__main__':
    out = AQUI / 'tarjeta' / ('tarjeta_cinthia_animada_verde.mp4' if VERDE_FONDO else 'tarjeta_cinthia_animada.mp4')
    ff = subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-i', str(AQUI / 'tarjeta' / 'sonidos_tarjeta.wav'), '-shortest', '-vf', 'scale=720:1280:flags=lanczos',
                           '-c:v', 'libx264', '-profile:v', 'main', '-pix_fmt', 'yuv420p', '-crf', '20', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', str(out)],
                          stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)):
        ff.stdin.write(cuadro(i / FPS).tobytes())
    ff.stdin.close(); ff.wait()
    cuadro(DUR - 0.5).save(out.with_suffix('.png'))
    print(out, out.stat().st_size // 1024, 'KB')
