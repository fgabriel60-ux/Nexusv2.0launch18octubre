"""Mariano · flyers animados nuevos: «Sotol familia» y «Bugambilia · La mejor opción».
Fondo = clip H3 del cuadro limpio (flyers_nuevos_modal.py) con push-in digital; encima, el texto ORIGINAL del flyer extraído por elementos
(des-mezcla contra el fondo: blanco sobre foto, oscuro sobre blanco, blanco sobre gris; logos de color opacos) que entra escalonado
(pop / deslizamiento / fade / barrido) con destello (brillo que cruza) en el precio. Sonido: música + SFX del sistema v4 (armar_flyers_v4_sonido.py).

TABLAS REUTILIZABLES: ELEMENTOS_<FLYER> = [(nombre, caja_900x1600, modo, t_entrada, animacion, sfx)] y DESTELLO_<FLYER> = (elemento, segundo).
Los eventos de sonido salen de esas tablas (eventos_sfx); para cambiar los SFX basta con reemplazar `construir` o editar SFX_POR_TIPO.
Uso: python3 armar_flyers_nuevos.py [sotol|bugambilia2|ambos] [--clip RUTA] [--version N]"""
import subprocess, sys
from pathlib import Path
import numpy as np, cv2
from PIL import Image
import imageio_ffmpeg
from scipy import ndimage as ndi
from armar_flyers_v4_sonido import construir, escribir_wav

AQUI = Path(__file__).resolve().parent
REC = AQUI.parent / 'flyers_recibidos'
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS, FIN = 1080, 1920, 30, 7.0
K = W / 900                       # flyer 900×1600 → 1080×1920

# ------------------------------------------------------------------ tablas ------------------------------------------------------------------
# modo: 'blanco_foto' (texto blanco sobre foto: des-mezcla con fondo por inpaint) · 'blanco_gris' (blanco sobre franja gris lisa)
#       'oscuro_blanco' (texto de color sobre blanco) · 'caja_azul' (recuadro azul sin su texto) · 'opaco_color' (logo de color: píxeles saturados)
# animacion: 'pop' (escala 0.8→1.06→1) · 'sube' (desliza desde abajo) · 'izq' / 'der' (desliza horizontal) · 'fade' · 'barrido' (revela de izq. a der.)
# sfx: tipo de efecto de armar_flyers_v4_sonido ('punch', 'camara', 'mouse', 'ding', 'riser', 'impacto') o None
ELEMENTOS_SOTOL = [
    ('tit1',      (55, 165, 860, 238),   'blanco_foto',  0.10, 'pop',   'punch'),
    ('tit2',      (130, 240, 790, 305),  'blanco_foto',  0.35, 'sube',  'camara'),
    ('caja',      (612, 1036, 900, 1318), 'caja_azul',   0.85, 'der',   'mouse'),
    ('modelo',    (660, 1060, 860, 1145), 'blanco_azul', 1.05, 'pop',   'camara'),
    ('precio',    (630, 1148, 880, 1222), 'blanco_azul', 1.30, 'pop',   'ding'),
    ('mensual',   (630, 1228, 880, 1285), 'blanco_azul', 1.85, 'sube',  'mouse'),
    ('chip1',     (50, 1342, 230, 1388),  'blanco_foto', 2.25, 'pop',   'mouse'),
    ('chip2',     (247, 1342, 440, 1388), 'blanco_foto', 2.40, 'pop',   'mouse'),
    ('chip3',     (459, 1342, 667, 1388), 'blanco_foto', 2.55, 'pop',   'mouse'),
    ('chip4',     (684, 1342, 857, 1388), 'blanco_foto', 2.70, 'pop',   'mouse'),
    ('logo',      (55, 1405, 285, 1562),  'blanco_foto', 2.95, 'sube',  'camara'),
    ('ubicacion', (300, 1458, 620, 1560), 'blanco_foto', 3.10, 'sube',  'mouse'),
    ('lagsa_ico', (652, 1478, 712, 1540), 'opaco_color', 3.25, 'pop',   None),
    ('lagsa',     (712, 1478, 835, 1540), 'blanco_foto', 3.25, 'sube',  'mouse'),
]
DESTELLO_SOTOL = ('precio', 1.62)
ZOOM_SOTOL = dict(z=0.05, cx=430, cy=760)          # push-in digital extra (H3 ya hace push-in real); centro en coords del flyer

ELEMENTOS_BUG = [
    ('tit1',      (90, 120, 835, 205),   'oscuro_blanco', 0.10, 'pop',     'punch'),
    ('tit2',      (130, 208, 825, 305),  'oscuro_blanco', 0.35, 'sube',    'camara'),
    ('casa',      (380, 668, 520, 715),  'oscuro_blanco', 0.65, 'pop',     'mouse'),
    ('bugambilia', (0, 0, 0, 0),         'ventana',       0.80, 'barrido', 'punch'),
    ('precio',    (70, 318, 860, 450),   'oscuro_blanco', 1.40, 'pop',     'ding'),
    ('unico',     (170, 468, 755, 522),  'oscuro_blanco', 1.95, 'sube',    'mouse'),
    ('chip1',     (92, 537, 230, 583),   'oscuro_blanco', 2.20, 'pop',     'mouse'),
    ('chip2',     (241, 537, 435, 583),  'oscuro_blanco', 2.35, 'pop',     'mouse'),
    ('chip3',     (448, 537, 654, 583),  'oscuro_blanco', 2.50, 'pop',     'mouse'),
    ('chip4',     (664, 537, 834, 583),  'oscuro_blanco', 2.65, 'pop',     'mouse'),
    ('logo',      (35, 1362, 262, 1525), 'blanco_gris',   2.90, 'sube',    'camara'),
    ('ubicacion', (300, 1478, 520, 1520), 'blanco_gris',  3.05, 'sube',    'mouse'),
    ('restr',     (560, 1488, 705, 1508), 'blanco_gris',  3.15, 'fade',    None),
    ('desarr',    (735, 1452, 855, 1475), 'blanco_gris',  3.25, 'fade',    None),
    ('lagsa_ico', (738, 1480, 782, 1524), 'opaco_color',  3.25, 'pop',     'mouse'),
    ('lagsa',     (782, 1480, 862, 1524), 'blanco_gris',  3.25, 'sube',    None),
]
DESTELLO_BUG = ('precio', 1.72)
ZOOM_BUG = dict(z=0.14, cx=450, cy=1100)           # push-in a la casa (la escena es una "ventana": panel blanco arriba y franja gris abajo fijos)
BANDA_BUG = (722, 831)                             # filas de BUGAMBILIA (letras-ventana) en el flyer
GRIS_DESDE = 1357                                  # fila donde empieza la franja gris (fija)

SFX_POR_TIPO = {'punch': [('punch', 0.85), ('camara', 0.8)], 'camara': [('camara', 0.8)], 'mouse': [('mouse', 0.9)],
                'ding': [('riser', 0.8), ('ding', 0.8)]}


# ------------------------------------------------------------------ extracción ------------------------------------------------------------------
def _inpaint(a, mascara, r=7):
    return cv2.inpaint(np.ascontiguousarray(a[..., ::-1]).astype(np.uint8), mascara.astype(np.uint8) * 255, r, cv2.INPAINT_TELEA)[..., ::-1].astype(float)


def _blanco_sobre(a, caja, umbral, fondo=None):
    """Des-mezcla texto blanco: I = α·255 + (1-α)·F. F = inpaint del fondo (o color fijo). Devuelve α (H×W)."""
    x0, y0, x1, y1 = caja
    sub = a[y0:y1, x0:x1].astype(float)
    m = sub.min(2) > umbral
    m = ndi.binary_opening(m, iterations=0) if False else m
    mg = ndi.binary_dilation(m, iterations=3)
    F = _inpaint(sub, mg, 9) if fondo is None else np.broadcast_to(np.array(fondo, float), sub.shape)
    al = ((sub - F).sum(2) / np.maximum((255 - F).sum(2), 60)).clip(0, 1)
    al[~mg] = 0
    out = np.zeros(a.shape[:2]); out[y0:y1, x0:x1] = al
    return out


def extraer(a, caja, modo):
    """→ RGBA float (H900×W900 completo) del elemento."""
    x0, y0, x1, y1 = caja
    rgba = np.zeros(a.shape[:2] + (4,))
    if modo in ('blanco_foto', 'blanco_azul'):
        al = _blanco_sobre(a, caja, 200 if modo == 'blanco_foto' else 215)
        rgba[..., :3] = 255; rgba[..., 3] = al
    elif modo == 'blanco_gris':
        al = _blanco_sobre(a, caja, 140, fondo=(94, 92, 95))
        rgba[..., :3] = 255; rgba[..., 3] = al
    elif modo == 'oscuro_blanco':
        sub = a[y0:y1, x0:x1].astype(float)
        fuerte = sub.min(2) < 150
        C = np.median(sub[fuerte], 0) if fuerte.sum() > 20 else sub.reshape(-1, 3).min(0)
        al = ((254 - sub).sum(2) / max((254 - C).sum(), 1)).clip(0, 1)
        al[al < 0.04] = 0
        rgba[y0:y1, x0:x1, :3] = C; rgba[y0:y1, x0:x1, 3] = al
    elif modo == 'caja_azul':
        sub = a[y0:y1, x0:x1].astype(int)
        azul = (sub[..., 2] - sub[..., 0] > 70) & (sub[..., 2] > 150)
        m = ndi.binary_fill_holes(ndi.binary_closing(azul, iterations=4))
        m = ndi.binary_opening(m, iterations=2)
        letras = m & (sub.min(2) > 150)                   # el texto blanco se quita: la caja entra vacía y su texto llega después
        limpio = _inpaint(sub.astype(float), ndi.binary_dilation(letras, iterations=3), 6)
        al = cv2.GaussianBlur(m.astype(np.float32), (3, 3), 0.7)
        rgba[y0:y1, x0:x1, :3] = limpio; rgba[y0:y1, x0:x1, 3] = al
    elif modo == 'opaco_color':
        sub = a[y0:y1, x0:x1].astype(int)
        sat = sub.max(2) - sub.min(2)
        m = ndi.binary_fill_holes(ndi.binary_closing((sat > 45) | (sub.min(2) > 200), iterations=2))
        lab, n = ndi.label(m)
        if n: m = lab == (np.bincount(lab.ravel())[1:].argmax() + 1)
        rgba[y0:y1, x0:x1, :3] = sub; rgba[y0:y1, x0:x1, 3] = cv2.GaussianBlur(m.astype(np.float32), (3, 3), 0.7)
    return rgba


def con_sombra(rgba, fuerza=0.55, radio=5, dy=2):
    """Sombra suave bajo el texto blanco (legibilidad sobre el video). Devuelve RGBA con la sombra integrada (operador 'over')."""
    s = cv2.GaussianBlur(np.roll(rgba[..., 3], dy, axis=0).astype(np.float32), (0, 0), radio) * fuerza
    a_t = rgba[..., 3]; a_o = a_t + s * (1 - a_t)
    rgb = (rgba[..., :3] * a_t[..., None]) / np.maximum(a_o, 1e-4)[..., None]
    out = np.dstack([rgb, a_o]); return out


def a_capa(rgba900):
    """RGBA 900 completo → (recorte RGBA uint8 en 1080, x, y) con margen para el pop."""
    al = rgba900[..., 3]
    ys, xs = np.where(al > 0.02)
    x0, x1, y0, y1 = max(xs.min() - 8, 0), min(xs.max() + 9, 900), max(ys.min() - 8, 0), min(ys.max() + 9, 1600)
    c = rgba900[y0:y1, x0:x1].clip(0, 255)
    c = np.dstack([c[..., :3], c[..., 3] * 255]).astype(np.uint8)
    im = Image.fromarray(c, 'RGBA').resize((round((x1 - x0) * K), round((y1 - y0) * K)), Image.LANCZOS)
    return np.asarray(im).astype(np.float32) / 255, round(x0 * K), round(y0 * K)


# ------------------------------------------------------------------ animación ------------------------------------------------------------------
def _ease_out_back(p, s=1.9): p -= 1; return 1 + (s + 1) * p ** 3 + s * p ** 2
def _ease_out_cubic(p): return 1 - (1 - p) ** 3


def estado(anim, t, t0, dur=0.38):
    """→ (opacidad, escala, dx, dy, revelado_x 0..1)"""
    if t < t0: return 0, 1, 0, 0, 0
    p = min((t - t0) / dur, 1)
    op = min(1, (t - t0) / 0.18)
    if anim == 'pop': return op, 0.8 + 0.2 * _ease_out_back(p), 0, 0, 1
    if anim == 'sube': return op, 1, 0, 46 * (1 - _ease_out_cubic(p)), 1
    if anim == 'der': return op, 1, 260 * (1 - _ease_out_cubic(p)), 0, 1
    if anim == 'izq': return op, 1, -260 * (1 - _ease_out_cubic(p)), 0, 1
    if anim == 'barrido': return 1, 1, 0, 0, _ease_out_cubic(min((t - t0) / 0.55, 1))
    return op, 1, 0, 0, 1


def pegar(frame, capa, x, y, op, esc=1.0, dx=0, dy=0, brillo=None):
    """Mezcla 'over' de la capa (RGBA float 0..1) sobre frame (float 0..255) con escala alrededor de su centro."""
    if op <= 0: return
    h, w = capa.shape[:2]
    if abs(esc - 1) > 1e-3:
        nw, nh = max(2, round(w * esc)), max(2, round(h * esc))
        capa = cv2.resize(capa, (nw, nh), interpolation=cv2.INTER_LINEAR if esc < 1 else cv2.INTER_CUBIC).clip(0, 1)
        x += (w - nw) / 2; y += (h - nh) / 2; h, w = nh, nw
    x, y = int(round(x + dx)), int(round(y + dy))
    X0, Y0, X1, Y1 = max(x, 0), max(y, 0), min(x + w, W), min(y + h, H)
    if X1 <= X0 or Y1 <= Y0: return
    c = capa[Y0 - y:Y1 - y, X0 - x:X1 - x]
    rgb = c[..., :3] * 255; a = c[..., 3:4] * op
    if brillo is not None: rgb = np.minimum(rgb + brillo[Y0 - y:Y1 - y, X0 - x:X1 - x, None] * 255, 255)
    frame[Y0:Y1, X0:X1] = rgb * a + frame[Y0:Y1, X0:X1] * (1 - a)


def banda_brillo(h, w, p):
    """Destello: franja diagonal clara que cruza el elemento (p 0..1)."""
    yy, xx = np.mgrid[0:h, 0:w]
    centro = -0.3 * w + p * 1.6 * w + 0.35 * (yy - h / 2)
    return np.exp(-((xx - centro) / (0.09 * w)) ** 2) * 0.75


# ------------------------------------------------------------------ fondo ------------------------------------------------------------------
def leer_clip(ruta):
    g = imageio_ffmpeg.read_frames(str(ruta)); meta = next(g)
    w, h = meta['size']
    fr = [np.frombuffer(b, np.uint8).reshape(h, w, 3) for b in g]
    return fr, meta.get('fps', 24)


def fondo_en(fr, fps_clip, t, zoom):
    """Cuadro del clip en t, escalado a 1080×1920 (deshace la compresión 704→720) con push-in digital (rápido al inicio = gancho)."""
    f = fr[min(int(t * fps_clip), len(fr) - 1)]
    h, w = f.shape[:2]
    z = 1 + zoom['z'] * (1 - (1 - t / FIN) ** 2.2)
    cx, cy = zoom['cx'] * K, zoom['cy'] * K
    sx, sy = W / w * z, H / h * z
    M = np.float32([[sx, 0, cx - cx * z], [0, sy, cy - cy * z]])
    return cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT).astype(np.float32)


def vineta():
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    return (1 - 0.22 * np.clip(r - 0.55, 0, 1) ** 1.6)[..., None].astype(np.float32)


# ------------------------------------------------------------------ flyers ------------------------------------------------------------------
def preparar(nombre):
    """→ dict con capas por elemento, extras de fondo (degradados/paneles) y parámetros."""
    if nombre == 'sotol':
        a = np.asarray(Image.open(REC / '1018_005111_BA9020.jpg').convert('RGB'))
        tabla, dest, zoom = ELEMENTOS_SOTOL, DESTELLO_SOTOL, ZOOM_SOTOL
    else:
        a = np.asarray(Image.open(REC / '1020_210408_4AF9D8.jpg').convert('RGB'))
        tabla, dest, zoom = ELEMENTOS_BUG, DESTELLO_BUG, ZOOM_BUG
    capas = {}
    for n, caja, modo, t0, anim, _ in tabla:
        if modo == 'ventana': continue
        rgba = extraer(a, caja, modo)
        if modo in ('blanco_foto',): rgba = con_sombra(rgba)
        capas[n] = a_capa(rgba)
    fijo = None
    if nombre == 'bugambilia2':
        # panel blanco fijo arriba (con las letras de BUGAMBILIA como ventana) y franja gris fija abajo
        y0, y1 = BANDA_BUG
        letras = np.zeros(a.shape[:2], np.float32)
        letras[y0:y1] = ((250 - a[y0:y1].min(2).astype(float)) / 40).clip(0, 1)
        panel = np.zeros(a.shape[:2], np.float32); panel[:y1] = 1; panel[y1] = 0.5
        gris = np.zeros(a.shape[:2], np.float32); gris[GRIS_DESDE:] = 1
        up = lambda m: cv2.resize(m, (W, H), interpolation=cv2.INTER_LINEAR)
        plato = np.asarray(Image.open(AQUI / 'nuevos' / 'bugambilia2' / 'plato_900.png').convert('RGB').resize((W, H), Image.LANCZOS)).astype(np.float32)
        fijo = dict(letras=up(letras), panel=up(panel), gris=up(gris), plato=plato)
    return dict(a=a, tabla=tabla, capas=capas, destello=dest, zoom=zoom, fijo=fijo)


def degradados_sotol():
    """Oscurecido suave arriba (titular) y abajo (etiquetas y pie), como el flyer original, para legibilidad sobre el video."""
    y = np.arange(H)[:, None].astype(np.float32)
    arriba = 0.30 * np.clip(1 - y / (420 * K), 0, 1) ** 1.5
    abajo = 0.55 * np.clip((y - 1270 * K) / (330 * K), 0, 1) ** 1.2
    return (1 - arriba - abajo)[..., None]


def render(nombre, clip, salida, version):
    P = preparar(nombre)
    fr, fps_clip = leer_clip(clip)
    vin = vineta()
    oscuro = degradados_sotol() if nombre == 'sotol' else None
    ev = eventos_sfx(P['tabla'], P['destello'])
    mix, _ = construir(ev)
    wav = AQUI / 'nuevos' / nombre / f'audio_v{version}.wav'; escribir_wav(mix, wav)
    cmd = [FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', str(wav),
           '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-profile:v', 'main', '-pix_fmt', 'yuv420p', '-crf', '19', '-preset', 'slow',
           '-c:a', 'aac', '-b:a', '160k', '-t', str(FIN), '-movflags', '+faststart', str(salida)]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    dn, dt = P['destello']
    for i in range(int(FIN * FPS)):
        t = i / FPS
        f = fondo_en(fr, fps_clip, t, P['zoom'])
        f = np.clip((f - 128) * 1.04 + 128 + np.array([4, 1, -3], np.float32), 0, 255) * vin    # color cálido + contraste + viñeta
        if oscuro is not None: f *= oscuro
        if P['fijo'] is not None:
            fj = P['fijo']
            rev = next((e for e in P['tabla'] if e[2] == 'ventana'), None)
            _, _, _, _, revx = estado('barrido', t, rev[3]) if rev else (0, 0, 0, 0, 1)
            corte = (-0.15 + revx * 1.3) * W                                    # barrido izq→der con borde suave
            xs = np.arange(W, dtype=np.float32)[None, :]
            ver = np.clip((corte - xs) / (0.15 * W), 0, 1) * fj['letras']
            al = (fj['panel'] * (1 - ver))[..., None]
            f = 254 * al + f * (1 - al)
            g = fj['gris'][..., None]; f = fj['plato'] * g + f * (1 - g)
        for n, caja, modo, t0, anim, _ in P['tabla']:
            if modo == 'ventana': continue
            capa, x, y = P['capas'][n]
            op, esc, dx, dy, _ = estado(anim, t, t0)
            br = None
            if n == dn and dt <= t <= dt + 0.5:
                br = banda_brillo(capa.shape[0], capa.shape[1], (t - dt) / 0.5)
                if esc != 1: br = None
            pegar(f, capa, x, y, op, esc, dx, dy, br)
        if dt <= t <= dt + 0.12: f = f + 22 * (1 - (t - dt) / 0.12)                           # golpe de brillo global corto al destello
        pr.stdin.write(np.clip(f, 0, 255).astype(np.uint8).tobytes())
    pr.stdin.close(); pr.wait()
    print(salida.name, salida.stat().st_size // 1024, 'KB')


def eventos_sfx(tabla, destello):
    """Tabla de elementos → eventos [(segundo, tipo, ganancia, pan)] para construir() de v4. Pan alterno por posición horizontal."""
    ev = []
    for n, caja, modo, t0, anim, sfx in tabla:
        if not sfx: continue
        cx = (caja[0] + caja[2]) / 2 if caja[2] else 450
        pan = round((cx - 450) / 450 * 0.35, 2)
        for tipo, g in SFX_POR_TIPO[sfx]: ev.append((t0, tipo, g, pan))
    ev.append((destello[1], 'impacto', 0.95, 0.0))
    return sorted(ev)


def main():
    quien = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else 'ambos'
    ver = sys.argv[sys.argv.index('--version') + 1] if '--version' in sys.argv else '1'
    nombres = {'sotol': 'Sotol_familia', 'bugambilia2': 'Bugambilia_mejor_opcion'}
    for n in (['sotol', 'bugambilia2'] if quien == 'ambos' else [quien]):
        clip = Path(sys.argv[sys.argv.index('--clip') + 1]) if '--clip' in sys.argv else AQUI / 'nuevos' / n / 'clip_ok.mp4'
        render(n, clip, AQUI / f'Mariano_flyer_{nombres[n]}_v{ver}.mp4', ver)


if __name__ == '__main__':
    main()
