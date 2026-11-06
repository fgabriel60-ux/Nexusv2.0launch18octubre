#!/usr/bin/env python3
"""Render intermedio FIEL del book nook v3: toma las piezas reales de generar_booknook_v3.py y las dibuja
en perspectiva (pintado por capas, cantos de MDF quemados, grabados, sombras entre capas, luz LED trasera y del techo).
No inventa geometria: todo lo que aparece es una pieza de las hojas de corte (mas un fondo neutro y una repisa).
Uso: python3 render_capas_v3.py [vista ...]   vistas: frontal, tres_cuartos, ventana, apagado
Salida: render_<vista>.png (entrada de condicionamiento para Qwen-Image-Edit)."""
import os, sys, math, importlib.util
import numpy as np
import cv2
from PIL import Image, ImageDraw

AQUI = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('bn', os.path.join(AQUI, 'generar_booknook_v3.py'))
bn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bn)
T, W, D, H = bn.T, bn.W, bn.D, bn.H
G = bn.final_geoms()
# para el render: piezas sin pestanas (quedan ocultas dentro de las ranuras) y ranuras rellenas
GR = {n: (p.body.difference(bn.unary_union(p.holes)) if p.holes else p.body) for n, p in bn.parts.items()}
P = bn.parts

# ------------------------------------------------------------------ materiales (pintura segun la referencia)
WALNUT = np.array([0.20, 0.12, 0.075])
DARK = np.array([0.11, 0.075, 0.05])
PARQ = np.array([0.50, 0.27, 0.13])
GOLD = np.array([0.80, 0.60, 0.28])
BRONZE = np.array([0.22, 0.15, 0.09])
EDGE = np.array([0.16, 0.09, 0.05])        # canto quemado del laser
MDF = np.array([0.62, 0.45, 0.30])
GLOW = np.array([1.0, 0.86, 0.66])

MAT = {'lado_izq': WALNUT, 'lado_der': WALNUT, 'piso': PARQ, 'tarima': PARQ, 'tarima_frente': PARQ * 0.8,
       'escalon_1': PARQ, 'escalon_2': PARQ, 'escalon_1_frente': PARQ * 0.8, 'escalon_2_frente': PARQ * 0.8,
       'baranda_primer_plano': GOLD, 'vitral_reticula': DARK, 'aro2_barras': BRONZE, 'aro1_moldura': WALNUT * 1.1,
       'muro_ventana': DARK * 1.3, 'gabinete_izq': DARK * 1.4, 'gabinete_der': DARK * 1.4, 'pilastra_izq': WALNUT * 1.2,
       'pilastra_der': WALNUT * 1.2, 'marco0_proscenio': WALNUT, 'frontis_superior': WALNUT, 'zocalo_frontal': WALNUT}
GOLD_ENGR = {'marco0_proscenio', 'frontis_superior', 'costilla_1', 'costilla_2', 'costilla_3', 'costilla_4', 'costilla_5',
             'lado_izq', 'lado_der', 'muro_ventana', 'aro1_moldura', 'aro2_barras', 'gabinete_der', 'pilastra_izq', 'pilastra_der'}


def mat(n):
    return MAT.get(n, WALNUT)


# ------------------------------------------------------------------ camara
class Cam:
    def __init__(self, pos, tgt, f, w, h, ss=2):
        self.C = np.array(pos, float); self.w, self.h, self.ss = w * ss, h * ss, ss
        fwd = np.array(tgt, float) - self.C; fwd /= np.linalg.norm(fwd)
        right = np.cross(fwd, [0, 0, 1.0]); right /= np.linalg.norm(right)
        up = np.cross(right, fwd)
        self.R = np.stack([right, -up, fwd])     # filas: x pantalla, y pantalla (abajo), profundidad
        self.f = f * ss

    def proj(self, pts):
        q = (np.asarray(pts, float) - self.C) @ self.R.T
        return np.stack([self.f * q[:, 0] / q[:, 2] + self.w / 2, self.f * q[:, 1] / q[:, 2] + self.h / 2], 1)

    def rays(self, x0, y0, x1, y1):
        ys, xs = np.mgrid[y0:y1, x0:x1].astype(float)
        d = np.stack([(xs - self.w / 2) / self.f, (ys - self.h / 2) / self.f, np.ones_like(xs)], -1) @ self.R
        return d


def to3d(kind, c, uv):
    uv = np.asarray(uv, float)
    cc = np.full(len(uv), c)
    if kind == 'X': return np.stack([cc, uv[:, 0], uv[:, 1]], 1)
    if kind == 'Y': return np.stack([uv[:, 0], cc, uv[:, 1]], 1)
    return np.stack([uv[:, 0], uv[:, 1], cc], 1)


AXI = {'X': 0, 'Y': 1, 'Z': 2}

# ruido de textura (MDF pintado: grano fino + manchas suaves)
rng = np.random.default_rng(3)
N1 = cv2.GaussianBlur(rng.standard_normal((1024, 1024)).astype(np.float32), (0, 0), 1.2)
N2 = cv2.GaussianBlur(rng.standard_normal((1024, 1024)).astype(np.float32), (0, 0), 14)
N1 /= N1.std(); N2 /= N2.std()


def tex(u, v, k=1.0):
    iu = (np.mod(u * 4.0, 1024)).astype(np.int32); iv = (np.mod(v * 4.0, 1024)).astype(np.int32)
    return 1 + k * (0.06 * N1[iv, iu] + 0.08 * N2[iv, iu])


class Scene:
    def __init__(self, cam, lit=True, bg=(0.07, 0.055, 0.045)):
        self.cam, self.lit = cam, lit
        self.img = np.zeros((cam.h, cam.w, 3), np.float32) + np.array(bg, np.float32)
        yy = np.linspace(0, 1, cam.h)[:, None, None]
        self.img *= (0.8 + 0.4 * yy).astype(np.float32)
        self.emis = np.zeros((cam.h, cam.w), np.float32)

    # ---- mascara de un poligono shapely (o lista) proyectado
    def mask(self, kind, c, geom):
        m = Image.new('L', (self.cam.w, self.cam.h), 0)
        d = ImageDraw.Draw(m)
        geoms = list(geom.geoms) if hasattr(geom, 'geoms') else [geom]
        for g in geoms:
            if g.is_empty or g.geom_type != 'Polygon': continue
            d.polygon([tuple(p) for p in self.cam.proj(to3d(kind, c, g.exterior.coords))], fill=255)
            for r in g.interiors:
                d.polygon([tuple(p) for p in self.cam.proj(to3d(kind, c, r.coords))], fill=0)
        return np.asarray(m, np.float32) / 255.0

    def lines(self, kind, c, lines, width):
        m = Image.new('L', (self.cam.w, self.cam.h), 0)
        d = ImageDraw.Draw(m)
        for ln in lines:
            for r in bn.rings(ln):
                pts = self.cam.proj(to3d(kind, c, r))
                d.line([tuple(p) for p in pts], fill=255, width=width)
        return np.asarray(m, np.float32) / 255.0

    # ---- iluminacion por pixel
    def shade(self, kind, c, normal, m, base, tex_k=1.0, emissive=None):
        ys, xs = np.nonzero(m > 0.003)
        if len(ys) == 0: return None, None
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        d = self.cam.rays(x0, y0, x1, y1)
        ax = AXI[kind]
        t = (c - self.cam.C[ax]) / np.where(np.abs(d[..., ax]) < 1e-9, 1e-9, d[..., ax])
        Pw = self.cam.C + t[..., None] * d
        x, y, z = Pw[..., 0], Pw[..., 1], Pw[..., 2]
        u, v = {'X': (y, z), 'Y': (x, z), 'Z': (x, y)}[kind]
        n = np.array(normal, float)
        if self.lit:
            amb = 0.10
            # luz de la ventana (sale por el circulo hacia el frente)
            L = np.array([bn.WCX, 182.0, bn.WCZ])
            lv = L - Pw; dist = np.linalg.norm(lv, axis=-1); lv /= dist[..., None]
            ndl = np.clip(lv @ n, 0, 1)
            win = 2.2 * ndl / (1 + (dist / 70.0) ** 2) * (y < 160)
            # LED del techo (ranuras entre costillas): lava las caras de arriba hacia abajo
            top = 0.55 * np.clip((z - 95) / 120, 0, 1) ** 1.6 * (1.0 if n[2] <= 0 else 0.3)
            # luz de la habitacion (relleno calido desde el frente-arriba)
            fill = 0.32 * np.clip(n @ np.array([0.2, -0.8, 0.55]) / 1.0, 0, 1) + 0.05
            light = amb + win + top + fill
            col = base[None, None, :] * light[..., None] * GLOW_TINT[None, None, :]
        else:
            # apagado: luz de dia difusa desde la ventana de la habitacion (izquierda-frente)
            kd = np.clip(n @ np.array([-0.5, -0.7, 0.5]) / np.linalg.norm([-0.5, -0.7, 0.5]), 0, 1)
            light = 0.35 + 0.75 * kd
            depth_ao = 1 - 0.55 * np.clip(y / 190, 0, 1) * (1 if abs(n[1]) > 0.5 or n[2] != 0 else 0.6)
            col = base[None, None, :] * (light * depth_ao)[..., None]
        col = col * tex(u, v, tex_k)[..., None]
        if emissive is not None:
            col = col + emissive(x, y, z)[..., None] * GLOW[None, None, :]
        return (y0, y1, x0, x1), col.astype(np.float32)

    def paint(self, m, box_, col, alpha=1.0):
        if box_ is None: return
        y0, y1, x0, x1 = box_
        a = (m[y0:y1, x0:x1] * alpha)[..., None]
        self.img[y0:y1, x0:x1] = self.img[y0:y1, x0:x1] * (1 - a) + col * a

    def face(self, kind, c, geom, normal, base, tex_k=1.0, emissive=None):
        m = self.mask(kind, c, geom)
        b, col = self.shade(kind, c, normal, m, base, tex_k, emissive)
        self.paint(m, b, col)
        return m

    def engrave(self, kind, c, lines, normal, color, width=2, alpha=0.85):
        if not lines: return
        m = self.lines(kind, c, lines, width)
        b, col = self.shade(kind, c, normal, m, color, 0.3)
        self.paint(m, b, col, alpha)

    def shadow(self, m, dx, dy, blur, k):
        s = np.roll(np.roll(m, int(dy), 0), int(dx), 1)
        s = cv2.GaussianBlur(s, (0, 0), blur)
        self.img *= (1 - k * s)[..., None]


GLOW_TINT = np.array([1.0, 0.93, 0.82])


def y_piece(sc, n, front_normal=(0, -1, 0), shadow=True):
    p, g = P[n], GR[n]
    base = mat(n)
    cam = sc.cam
    # sombra proyectada sobre lo que hay detras (capas)
    m_front = sc.mask('Y', p.c, g)
    if shadow:
        s = cam.ss
        sc.shadow(m_front, 3 * s, 7 * s, 6 * s, 0.55 if sc.lit else 0.35)
    # cara trasera -> se ve como canto quemado en el grosor
    sc.face('Y', p.c + T, g, (0, -1, 0), EDGE, 0.5)
    sc.face('Y', p.c, g, front_normal, base)
    if p.engr:
        gold = n in GOLD_ENGR
        col = GOLD if gold else base * 0.45
        sc.engrave('Y', p.c, p.engr, (0, -1, 0), col, width=max(2, cam.ss + (1 if gold else 0)), alpha=0.9 if gold else 0.7)


def z_piece_top(sc, n):
    p, g = P[n], GR[n]
    zt = p.c + T
    sc.face('Z', zt, g, (0, 0, 1), mat(n))
    if p.engr:
        sc.engrave('Z', zt, p.engr, (0, 0, 1), mat(n) * 0.5, width=sc.cam.ss, alpha=0.6)
    # canto frontal
    mnx, mny, mxx, mxy = g.bounds
    from shapely.geometry import box as sbox
    sc.face('Y', mny, sbox(mnx, p.c, mxx, zt), (0, -1, 0), EDGE * 1.4, 0.5)


def render(view, out):
    from shapely.geometry import box as sbox, Point
    lit = view != 'apagado'
    if view == 'frontal':
        cam = Cam((85, -390, 128), (85, 100, 120), 1250, 1024, 1024)
    elif view in ('tres_cuartos', 'apagado'):
        cam = Cam((-150, -330, 205), (88, 95, 112), 1220, 1024, 1024)
    elif view == 'ventana':
        cam = Cam((95, -95, 118), (85, 170, 104), 1650, 1024, 1024)
    else:
        raise SystemExit('vista desconocida ' + view)
    sc = Scene(cam, lit, bg=(0.06, 0.05, 0.045) if lit else (0.55, 0.52, 0.48))

    # repisa / mesa (plano neutro bajo la caja) para que la IA tenga donde apoyar
    shelf = sbox(-300, cam.C[1] + 60, 470, 700)
    sc.face('Z', -0.01, shelf, (0, 0, 1), np.array([0.30, 0.18, 0.10]) if lit else np.array([0.55, 0.40, 0.27]), 1.5)
    # sombra de contacto de la caja
    m = sc.mask('Z', 0.0, sbox(-6, -4, W + 6, D + 6)); sc.shadow(m, 0, 0, 10 * cam.ss, 0.6)

    # interior del techo LED (se ve por las ranuras) y emision
    led_e = (lambda x, y, z: np.full_like(x, 0.9)) if lit else None
    sc.face('Z', bn.Z_ROOF, sbox(T, 0, W - T, D), (0, 0, -1), np.array([0.5, 0.4, 0.3]), 0.2, led_e)
    sc.face('Z', bn.Z_LAT, GR['techo_celosia'], (0, 0, -1), DARK, 0.6)

    # paredes laterales, cara interior
    sc.face('X', T, GR['lado_izq'], (1, 0, 0), WALNUT)
    sc.engrave('X', T, P['lado_izq'].engr, (1, 0, 0), GOLD * 0.8, cam.ss, 0.6)
    sc.face('X', W - T, GR['lado_der'], (-1, 0, 0), WALNUT)
    sc.engrave('X', W - T, P['lado_der'].engr, (-1, 0, 0), GOLD * 0.8, cam.ss, 0.6)

    # vidrio difusor iluminado (papel detras del vitral)
    if lit:
        cx, cz = bn.WCX, bn.WCZ
        emi = lambda x, y, z: 2.6 + 1.6 * np.exp(-(((x - cx) ** 2 + (z - cz) ** 2) / (2 * 30.0 ** 2)))
        sc.face('Y', 183.0, Point(cx, cz).buffer(60, 128), (0, -1, 0), np.array([0.9, 0.85, 0.75]), 0.15, emi)
    else:
        sc.face('Y', 183.0, Point(bn.WCX, bn.WCZ).buffer(60, 128), (0, -1, 0), np.array([0.86, 0.80, 0.68]), 0.4)

    order = []
    for n, p in P.items():
        if n in ('lado_izq', 'lado_der', 'techo_celosia', 'tapa_superior', 'base_fondo', 'tapa_trasera') or n.startswith('nervio'):
            continue
        if p.kind == 'Y':
            order.append((p.c, n))
        elif p.kind == 'Z':
            order.append((G[n].bounds[3] + 0.5, n))   # se dibuja antes que lo que esta encima
    order.sort(reverse=True)
    for _, n in order:
        if P[n].kind == 'Z':
            z_piece_top(sc, n)
        else:
            y_piece(sc, n, shadow=n not in ('zocalo_frontal', 'frontis_superior'))

    # cantos frontales de la caja (paredes, base, tapa)
    for x0 in (0, W - T):
        sc.face('Y', 0, sbox(x0, 0, x0 + T, H), (0, -1, 0), EDGE * 1.6, 0.5)
    for z0 in (0, bn.Z_ROOF):
        sc.face('Y', 0, sbox(T, z0, W - T, z0 + T), (0, -1, 0), EDGE * 1.6, 0.5)
    if cam.C[2] > H:
        sc.face('Z', H, sbox(0, 0, W, D), (0, 0, 1), WALNUT * 1.3)
    # pared izquierda exterior (vista 3/4), con las puntas de pestanas visibles
    if cam.C[0] < 0:
        gL = bn.box(0, 0, D, H)
        sc.face('X', 0, gL, (-1, 0, 0), WALNUT * 1.15)
        slots = [s for s in P['lado_izq'].slots]
        sc.face('X', 0, bn.unary_union(slots), (-1, 0, 0), EDGE * 1.8, 0.5)
        sc.engrave('X', 0, [bn.box(10, 10, 190, 230).exterior, bn.box(14, 14, 186, 226).exterior], (-1, 0, 0), GOLD, cam.ss + 1, 0.8)

    img = sc.img
    if lit:   # bloom de la luz de la ventana
        br = np.clip(img - 0.9, 0, None)
        img = img + 0.25 * cv2.GaussianBlur(br, (0, 0), 5 * cam.ss) + 0.12 * cv2.GaussianBlur(br, (0, 0), 40 * cam.ss)
        img = img / (1 + 0.35 * img)      # tone map suave
        img = img * 1.3
    out_im = np.clip(img, 0, 1) ** (1 / 1.15)
    out_im = (out_im * 255).astype(np.uint8)
    im = Image.fromarray(out_im).resize((cam.w // cam.ss, cam.h // cam.ss), Image.LANCZOS)
    im.save(out)
    print('guardado', out)


if __name__ == '__main__':
    vistas = sys.argv[1:] or ['frontal', 'tres_cuartos', 'ventana', 'apagado']
    os.makedirs(os.path.join(AQUI, 'render_intermedio'), exist_ok=True)
    for v in vistas:
        render(v, os.path.join(AQUI, 'render_intermedio', f'render_{v}.png'))
