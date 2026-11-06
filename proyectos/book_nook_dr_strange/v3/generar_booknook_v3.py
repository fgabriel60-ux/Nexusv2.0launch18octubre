#!/usr/bin/env python3
"""Book nook Sanctum Sanctorum (Dr. Strange) v3 (interior segun referencia ArtStation) - generador de piezas para corte laser en MDF.
Uso: python3 generar_booknook_v3.py [salida_dir]
Coordenadas de diseno = coordenadas globales del ensamble (mm):
  x ancho 0..170, y profundidad 0..200 (y=0 frente abierto), z alto 0..240.
"""
import math, os, sys, itertools
from shapely.geometry import box, Point, LineString, Polygon, MultiPolygon
from shapely.ops import unary_union
from shapely import affinity

T = 3.0          # espesor MDF (medir el real y cambiar aqui)
KERF = 0.12      # ancho de corte laser
W, D, H = 170.0, 200.0, 240.0
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
SHEET_W, SHEET_H = 600.0, 400.0
GAP, MARGIN, LABEL = 5.0, 8.0, 6.0
MITRE = 2

AX = {'X': ('y', 'z'), 'Y': ('x', 'z'), 'Z': ('x', 'y')}   # ejes locales (u,v) por plano


class Part:
    def __init__(self, name, kind, c, body, qty=1, desc=''):
        self.name, self.kind, self.c = name, kind, c       # plano en eje kind, de c a c+T
        self.body = body
        self.tabs, self.slots, self.holes, self.engr = [], [], [], []
        self.qty, self.desc = qty, desc

    def geom(self):
        g = unary_union([self.body] + self.tabs)
        cut = unary_union(self.slots + self.holes) if (self.slots or self.holes) else None
        return g.difference(cut) if cut is not None else g


parts = {}


def add(p):
    parts[p.name] = p
    return p


# ---------------------------------------------------------------- utilidades geometricas
def bez(p0, p1, p2, p3, n=40):
    pts = []
    for i in range(n + 1):
        t = i / n
        a = (1 - t) ** 3; b = 3 * (1 - t) ** 2 * t; c = 3 * (1 - t) * t * t; d = t ** 3
        pts.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return pts


def arch(x0, x1, z0, zc, b):
    """abertura: rectangulo x0..x1 de z0 a zc + semielipse de semieje vertical b"""
    a = (x1 - x0) / 2
    el = affinity.scale(Point((x0 + x1) / 2, zc).buffer(1, 64), a, b)
    return unary_union([box(x0, z0, x1, zc), el])


def ring_notches(cx, cy, r, n, w=3.0, l=3.5):
    out = []
    for i in range(n):
        ang = 360.0 / n * i
        out.append(affinity.rotate(box(r - 0.5, -w / 2, r + l, w / 2), ang, origin=(0, 0)))
    return affinity.translate(unary_union(out), cx, cy)


# ---------------------------------------------------------------- uniones (tab + ranura)
def j_H_sides(Hp, z0, yints):
    for a, b in yints:
        Hp.tabs += [box(0, a, T, b), box(W - T, a, W, b)]
        for s in (parts['lado_izq'], parts['lado_der']):
            s.slots.append(box(a, z0, b, z0 + T))


def j_V_sides(Vp, y0, zints):
    for a, b in zints:
        Vp.tabs += [box(0, a, T, b), box(W - T, a, W, b)]
        for s in (parts['lado_izq'], parts['lado_der']):
            s.slots.append(box(y0, a, y0 + T, b))


def j_V_H(Vp, Hp, y0, xints, z, up):
    """tabs de V que entran en la placa horizontal Hp (z = cara de V que toca Hp)"""
    for a, b in xints:
        Vp.tabs.append(box(a, z, b, z + T) if up else box(a, z - T, b, z))
        Hp.slots.append(box(a, y0, b, y0 + T))


def j_rib(R, xr, Hp, yints, zt, up):
    for a, b in yints:
        R.tabs.append(box(a, zt, b, zt + T) if up else box(a, zt - T, b, zt))
        Hp.slots.append(box(xr, a, xr + T, b))


# ---------------------------------------------------------------- helpers de detalle (v2)
import random


def clip_lines(lines, region):
    out = []
    for ln in lines:
        r = ln.intersection(region)
        if not r.is_empty:
            out.append(r)
    return out


def bricks(region, x0, x1, z0, z1, bw=12.0, bh=4.5):
    """ladrillos grabados (juntas) recortados a 'region'"""
    lines = []
    k = 0
    z = z0
    while z < z1 + 0.01:
        lines.append(LineString([(x0, z), (x1, z)]))
        if z + bh <= z1 + 0.01:
            off = (bw / 2) if k % 2 else 0
            x = x0 + off
            while x < x1:
                if x > x0:
                    lines.append(LineString([(x, z), (x, z + bh)]))
                x += bw
        z += bh
        k += 1
    return clip_lines(lines, region)


def ashlar(region, x0, x1, z0, z1, seed=1, bw=(12, 20), bh=(8, 10)):
    """sillares de piedra irregulares grabados"""
    rnd = random.Random(seed)
    lines = []
    z = z0
    while z < z1:
        h = rnd.uniform(*bh)
        lines.append(LineString([(x0, z), (x1, z)]))
        x = x0 + rnd.uniform(0, 8)
        while x < x1:
            lines.append(LineString([(x, z), (x, min(z + h, z1))]))
            x += rnd.uniform(*bw)
        z += h
    return clip_lines(lines, region)


def wavy(u0, u1, v, amp=0.8, per=18.0, step=2.0, phase=0.0):
    pts = []
    u = u0
    while u <= u1 + 1e-6:
        pts.append((u, v + amp * math.sin(2 * math.pi * (u - u0) / per + phase)))
        u += step
    return LineString(pts)


def scallops(cx, zc, a, b, off, r, n, ang0=8, ang1=172):
    """agujeros circulares siguiendo un arco (festoneado), separados 'off' del borde del arco"""
    out = []
    for i in range(n):
        t = math.radians(ang0 + (ang1 - ang0) * i / (n - 1))
        out.append(Point(cx + (a + off) * math.cos(t), zc + (b + off) * math.sin(t)).buffer(r, 24))
    return out


def mirror_x(g):
    return affinity.scale(g, xfact=-1, origin=(W / 2, 0))



# =====================================================================================
# v3: interior del Sanctum segun la referencia (render de Harsh Verma): boveda de canon con
# grecas doradas en perspectiva forzada, gran ventana circular al fondo (aro escalonado,
# 4 barras curvas en '#', reticula fina con roseta), pilastras, gabinetes con cuencos,
# tarima de parquet con escalones y baranda de laton en primer plano a la izquierda.
# =====================================================================================

def j_V_side(Vp, y0, zints, side):
    """tabs de una pieza Y parcial solo hacia una pared ('L' o 'R')"""
    for a, b in zints:
        if side == 'L':
            Vp.tabs.append(box(0, a, T, b)); parts['lado_izq'].slots.append(box(y0, a, y0 + T, b))
        else:
            Vp.tabs.append(box(W - T, a, W, b)); parts['lado_der'].slots.append(box(y0, a, y0 + T, b))


def meander_along(a, b, cx, zc, off, h, n_units, ang0=4, ang1=176):
    """greca (meandro) grabada siguiendo el intrados de un arco eliptico (semiejes a,b)
    off = distancia desde el intrados hacia fuera, h = alto de la banda"""
    def P(t, d):
        # punto en el angulo t (grados), desplazado d hacia fuera (aprox. normal radial escalada)
        r = math.radians(t)
        return (cx + (a + d) * math.cos(r), zc + (b + d) * math.sin(r))
    lines = []
    span = (ang1 - ang0) / n_units
    for k in range(n_units):
        t0 = ang0 + k * span
        f = lambda q: t0 + q * span
        # motivo de greca en coordenadas (q a lo largo, d hacia fuera) normalizadas
        motif = [(0, 0), (0, 1), (0.75, 1), (0.75, 0.3), (0.35, 0.3), (0.35, 0.65), (0.55, 0.65)]
        lines.append(LineString([P(f(q), off + d * h) for q, d in motif]))
        lines.append(LineString([P(f(0), off), P(f(1), off)]))
    lines.append(LineString([P(ang0 + (ang1 - ang0) * i / 80, off + h + 0.8) for i in range(81)]))
    return lines


# ---------------------------------------------------------------- piezas estructurales
YI = [(15, 45), (85, 115), (155, 185)]
Z_BOT, Z_FLOOR, Z_LAT, Z_ROOF = 0.0, 15.0, 222.0, 237.0
FLOOR_TOP = Z_FLOOR + T
XQ = [(12, 35), (70, 100), (135, 158)]           # intervalos x de pestanas en placas horizontales

lado = add(Part('lado_izq', 'X', 0, box(0, 0, D, H), desc='pared lateral izquierda'))
lado_d = add(Part('lado_der', 'X', W - T, box(0, 0, D, H), desc='pared lateral derecha (espejo)'))
bottom = add(Part('base_fondo', 'Z', Z_BOT, box(T, 0, W - T, D), desc='tapa inferior (compartimento de cables/pilas)'))
floor = add(Part('piso', 'Z', Z_FLOOR, box(T, 0, W - T, 194), desc='piso de parquet en espiga'))
lattice = add(Part('techo_celosia', 'Z', Z_LAT, box(T, 0, W - T, 194), desc='techo: ranuras de luz LED sobre la boveda'))
roof = add(Part('tapa_superior', 'Z', Z_ROOF, box(T, 0, W - T, D), desc='tapa superior'))
for p, z in ((bottom, Z_BOT), (floor, Z_FLOOR), (lattice, Z_LAT), (roof, Z_ROOF)):
    j_H_sides(p, z, YI)

for i, xr in enumerate((50.0, 117.0)):
    r = add(Part(f'nervio_piso_{i+1}', 'X', xr, box(15, 3, 175, 15), desc='separador compartimento inferior'))
    j_rib(r, xr, floor, [(20, 40), (90, 110), (150, 170)], 15, True)
    j_rib(r, xr, bottom, [(20, 40), (90, 110), (150, 170)], 3, False)
for i, xr in enumerate((6.0, W - 9.0)):
    r = add(Part(f'nervio_techo_{i+1}', 'X', xr, box(15, Z_LAT + T, 175, Z_ROOF), desc='separador camara LED superior'))
    j_rib(r, xr, roof, [(20, 40), (90, 110), (150, 170)], Z_ROOF, True)
    j_rib(r, xr, lattice, [(20, 40), (90, 110), (150, 170)], Z_LAT + T, False)

cover = add(Part('tapa_trasera', 'Y', 194, box(T, 3, W - T, Z_ROOF), desc='tapa trasera (aqui va la tira LED de la ventana)'))
j_V_sides(cover, 194, [(30, 60), (110, 140), (190, 220)])
j_V_H(cover, bottom, 194, XQ, 3, False)
j_V_H(cover, roof, 194, XQ, Z_ROOF, True)
cover.holes.append(Point(85, 30).buffer(4.0, 32))


def vfull(name, y0, holes, desc, sz, bx=((12, 30), (60, 80), (140, 158)), top=True):
    f = add(Part(name, 'Y', y0, box(T, FLOOR_TOP, W - T, Z_LAT), desc=desc))
    j_V_sides(f, y0, sz)
    j_V_H(f, floor, y0, list(bx), FLOOR_TOP, False)
    if top:
        j_V_H(f, lattice, y0, [(40, 60), (110, 130)], Z_LAT, True)
    f.holes += holes
    return f


# ---------------------------------------------------------------- ventana del Sanctum (4 capas)
WCX, WCZ = 85.0, 104.0
RG = 48.0                       # radio del vidrio
R_A2, R_A1, R_MU = RG, 53.0, 58.0

# (a) vitral: reticula GRUESA en MDF (roseta, 2 anillos, 12 radios). La reticula fina de plomo de la referencia
#     no se puede cortar en MDF (barras <2 mm): va IMPRESA en la lamina difusora (vitral_impreso.svg, escala 1:1)
ret = [Point(0, 0).buffer(r + 1.2, 96).difference(Point(0, 0).buffer(r - 1.2, 96)) for r in (7.5, 26)]
for i in range(12):
    ret.append(affinity.rotate(box(7.5, -1.2, RG + 1, 1.2), 15 + 30 * i, origin=(0, 0)))
for i in range(8):     # petalos de la roseta
    ret.append(affinity.rotate(box(0, -1.2, 7.5, 1.2), 22.5 + 45 * i, origin=(0, 0)))
glass = Point(0, 0).buffer(RG, 128).difference(unary_union(ret))
glass = unary_union([q for q in (glass.geoms if hasattr(glass, 'geoms') else [glass]) if q.area >= 3.0])


def lineas_vitral_impreso():
    """reticula fina (plomo) para imprimir en la lamina difusora, en coordenadas de la ventana (mm)"""
    L = []
    for r in [3, 5] + list(range(9, 48, 4)):
        L.append(Point(WCX, WCZ).buffer(r, 128).exterior)
    for (r0, r1, n) in ((5, 13, 12), (13, 25, 24), (25, RG, 48)):
        for i in range(n):
            a = math.radians(360 / n * i + 360 / n / 2)
            L.append(LineString([(WCX + r0 * math.cos(a), WCZ + r0 * math.sin(a)), (WCX + r1 * math.cos(a), WCZ + r1 * math.sin(a))]))
    for i in range(16):   # rombos decorativos en el anillo medio
        a = math.radians(22.5 * i); r = 31.0
        cx_, cz_ = WCX + r * math.cos(a), WCZ + r * math.sin(a)
        L.append(affinity.rotate(Polygon([(cx_ - 1.6, cz_), (cx_, cz_ + 2.4), (cx_ + 1.6, cz_), (cx_, cz_ - 2.4)]), 22.5 * i - 90, origin=(cx_, cz_)).exterior)
    return L


GLASS = affinity.translate(glass, WCX, WCZ)
vit = vfull('vitral_reticula', 178, [GLASS], 'reticula del vitral con roseta (papel difusor detras)', [(40, 70), (150, 180)])

# (b) barras curvas en '#' (sello de la ventana) unidas a un aro
BANDS_U = [((-0.46, 1.08), (-0.16, 0.35), (-0.18, -0.30), (-0.62, -1.02)),
           ((0.92, 0.62), (0.34, 0.12), (0.10, -0.45), (-0.10, -1.08)),
           ((-1.08, 0.40), (-0.42, -0.02), (0.38, -0.14), (1.08, -0.06)),
           ((-1.05, -0.42), (-0.46, -0.40), (0.22, -0.50), (0.74, -0.86))]
bands = unary_union([LineString(bez(*[(WCX + RG * u, WCZ + RG * v) for u, v in pts])).buffer(3.4, cap_style=1) for pts in BANDS_U])
bands = bands.intersection(Point(WCX, WCZ).buffer(RG + 2, 128))
a2_open = Point(WCX, WCZ).buffer(RG, 128).difference(bands)
a2_open = [q for q in (a2_open.geoms if hasattr(a2_open, 'geoms') else [a2_open]) if q.area >= 3.0]
BANDS = bands.intersection(Point(WCX, WCZ).buffer(RG, 128))
a2 = vfull('aro2_barras', 172, a2_open, 'aro interior con las 4 barras curvas del sello', [(40, 70), (150, 180)])
a2.engr += [Point(WCX, WCZ).buffer(RG + 2.5, 128).exterior]

# (c) aro 1: moldura escalonada con cuentas caladas
a1 = vfull('aro1_moldura', 166, [Point(WCX, WCZ).buffer(R_A1, 128)], 'aro de moldura de la ventana', [(40, 70), (150, 180)])
a1.engr += [Point(WCX, WCZ).buffer(R_A1 + 2.5, 128).exterior]

# (d) muro de la luneta: abertura mayor, paneles grabados, arco de la luneta
mu = vfull('muro_ventana', 160, [Point(WCX, WCZ).buffer(R_MU, 128)], 'muro del fondo (luneta) con la ventana', [(40, 70), (150, 180)])
mu.engr += [Point(WCX, WCZ).buffer(r, 128).exterior for r in (R_MU + 3, R_MU + 7)]
mu.engr += [LineString([(WCX + (R_MU + 3) * math.cos(math.radians(t)), WCZ + (R_MU + 3) * math.sin(math.radians(t))),
                        (WCX + (R_MU + 7) * math.cos(math.radians(t)), WCZ + (R_MU + 7) * math.sin(math.radians(t)))]) for t in range(0, 360, 8)]
mu.engr += [box(8, 40, 22, 110).exterior, box(148, 40, 162, 110).exterior]

# ---------------------------------------------------------------- tarima (estrado) y escalones
tarima = add(Part('tarima', 'Z', 31, box(T, 60, W - T, 158), desc='estrado de parquet frente a la ventana'))
j_H_sides(tarima, 31, [(80, 100), (125, 145)])
tf = add(Part('tarima_frente', 'Y', 63, box(T, FLOOR_TOP, W - T, 31), desc='contrahuella del estrado (espiga grabada)'))
j_V_sides(tf, 63, [(21, 28)])
j_V_H(tf, floor, 63, [(20, 40), (75, 95), (130, 150)], FLOOR_TOP, False)
j_V_H(tf, tarima, 63, [(20, 40), (75, 95), (130, 150)], 31, True)
tf.engr += [LineString([(x, FLOOR_TOP + 1), (x + 6, 30), (x + 12, FLOOR_TOP + 1)]) for x in range(5, 160, 12)]
for k in range(0, 9):                         # espiga en el estrado
    y0 = 64 + 11 * k
    pts, x, i = [], T, 0
    while x <= W - T + 1e-6:
        pts.append((x, y0 + (5 if i % 2 else 0))); x += 6; i += 1
    tarima.engr.append(LineString(pts))

for i, (xa, xb) in enumerate(((36.0, 100.0), (114.0, 154.0))):
    st = add(Part(f'escalon_{i+1}', 'Z', 25, box(xa, 46, xb, 60), desc='huella de escalon (se pega al frente del estrado)'))
    sr = add(Part(f'escalon_{i+1}_frente', 'Y', 49, box(xa, FLOOR_TOP, xb, 25), desc='contrahuella de escalon'))
    m = (xa + xb) / 2
    j_V_H(sr, floor, 49, [(xa + 5, xa + 15), (xb - 15, xb - 5)], FLOOR_TOP, False)
    j_V_H(sr, st, 49, [(xa + 5, xa + 15), (xb - 15, xb - 5)], 25, True)
    st.engr += [LineString([(xa + 1, y), (xb - 1, y)]) for y in (51, 55)]

# ---------------------------------------------------------------- boveda: proscenio + 5 costillas en perspectiva forzada
Z_SPR, Z_LEG = 128.0, 118.0
pro_open = arch(12, W - 12, 10, Z_SPR, 216 - Z_SPR)
pro = add(Part('marco0_proscenio', 'Y', 4, box(T, FLOOR_TOP, W - T, Z_LAT).difference(pro_open), desc='marco frontal (pilastras estriadas y arco)'))
j_V_sides(pro, 4, [(40, 70), (160, 190)])
j_V_H(pro, floor, 4, [(6, 11), (W - 11, W - 6)], FLOOR_TOP, False)
j_V_H(pro, lattice, 4, [(40, 60), (110, 130)], Z_LAT, True)
pro.engr += [LineString([(x, 24), (x, 112)]) for x in (6.5, 9)] + [LineString([(W - x, 24), (W - x, 112)]) for x in (6.5, 9)]
pro.engr += [LineString([(T, z), (12, z)]) for z in (24, 112, 116)] + [LineString([(W - 12, z), (W - T, z)]) for z in (24, 112, 116)]
pro.engr += meander_along(73, 88, W / 2, Z_SPR, 1.2, 4.5, 15)

RIBS = [(28, 16, 208), (50, 20, 200), (72, 24, 192), (94, 28, 184), (116, 32, 176)]
RIB_OPEN = {}
for k, (y0, x0, crown) in enumerate(RIBS, 1):
    a, b = (W - 2 * x0) / 2, crown - Z_SPR
    op = arch(x0, W - x0, 100, Z_SPR, b)
    rb = add(Part(f'costilla_{k}', 'Y', y0, box(T, Z_LEG, W - T, Z_LAT).difference(op), desc=f'costilla {k} de la boveda con greca'))
    j_V_sides(rb, y0, [(150, 172)])
    j_V_H(rb, lattice, y0, [(12, 18), (W - 18, W - 12), (78, 92)], Z_LAT, True)
    rb.engr += meander_along(a, b, W / 2, Z_SPR, 1.0, min(5.0, (Z_LAT - crown) - 3.5), 13 + k)
    rb.engr += [LineString([(T, Z_LEG + 3), (x0, Z_LEG + 3)]), LineString([(W - x0, Z_LEG + 3), (W - T, Z_LEG + 3)])]
    RIB_OPEN[k] = op

# ranuras de luz en el techo (entre costillas) y sobre la luneta
for (ya, yb) in ((10, 26), (33, 48), (55, 70), (77, 92), (99, 114), (121, 156)):
    for (xa, xb) in ((22, 75), (95, 148)):
        lattice.holes.append(box(xa, ya, xb, yb))
roof.holes.append(Point(85, 180).buffer(4.0, 32))

# ---------------------------------------------------------------- pilastras bajo la primera costilla
pil = unary_union([box(T, FLOOR_TOP, 21, 26), box(T, 26, 18, 108), box(T, 108, 21, Z_LEG)])
for side, g in (('L', pil), ('R', mirror_x(pil))):
    p = add(Part(f'pilastra_{"izq" if side == "L" else "der"}', 'Y', 34, g, desc='pilastra estriada'))
    j_V_side(p, 34, [(50, 80)], side)
    xs = (6, 13) if side == 'L' else (W - 13, W - 6)
    j_V_H(p, floor, 34, [xs], FLOOR_TOP, False)
    fl = [LineString([(x, 30), (x, 104)]) for x in (7, 10.5, 14)]
    p.engr += fl if side == 'L' else [mirror_x(q) for q in fl]

# ---------------------------------------------------------------- gabinetes con cuencos sobre el estrado
cab = unary_union([box(T, 34, 30, 74), box(T, 74, 32, 77), box(14, 77, 19, 80),
                   Polygon([(6, 80), (27, 80), (24, 87), (9, 87)])])
for side, g in (('L', cab), ('R', mirror_x(cab))):
    p = add(Part(f'gabinete_{"izq" if side == "L" else "der"}', 'Y', 140, g, desc='gabinete con cuenco'))
    j_V_side(p, 140, [(44, 64)], side)
    xs = (8, 22) if side == 'L' else (W - 22, W - 8)
    j_V_H(p, tarima, 140, [xs], 34, False)
    if side == 'R':      # cajonera (como en la referencia)
        dr = []
        for c in range(3):
            for r_ in range(6):
                x0 = W - 28 + c * 8; z0 = 38 + r_ * 6
                dr.append(box(x0, z0, x0 + 6, z0 + 4.5).exterior)
        p.engr += dr
    else:
        p.engr += [box(8, 39, 25, 70).exterior]

# ---------------------------------------------------------------- baranda de laton en primer plano (izquierda)
rail_body = box(T, FLOOR_TOP, 58, 66)
rail_open = []
x = T + 4
while x + 4 <= 56:
    rail_open.append(box(x, 24, x + 4.4, 58)); x += 4.4 + 2.6
rail = add(Part('baranda_primer_plano', 'Y', 16, rail_body.difference(unary_union(rail_open)), desc='baranda de laton (pintar dorado)'))
j_V_side(rail, 16, [(30, 50)], 'L')
j_V_H(rail, floor, 16, [(10, 16), (44, 50)], FLOOR_TOP, False)
rail.engr += [LineString([(T, 62), (58, 62)])]

# ---------------------------------------------------------------- frontis superior y zocalo (tapan las camaras LED/cables desde el frente)
fr = add(Part('frontis_superior', 'Y', 4, box(T, Z_LAT + T, W - T, Z_ROOF), desc='frontis superior con greca'))
j_V_sides(fr, 4, [(227, 233)])
j_V_H(fr, lattice, 4, [(20, 32), (138, 150)], Z_LAT + T, False)
j_V_H(fr, roof, 4, [(70, 100)], Z_ROOF, True)
fr.engr += [LineString([(T, 226.5), (W - T, 226.5)]), LineString([(T, 235.5), (W - T, 235.5)])]
for k in range(14):
    x0 = 8 + k * 11.2
    fr.engr.append(LineString([(x0, 228), (x0, 234), (x0 + 8, 234), (x0 + 8, 230), (x0 + 3, 230), (x0 + 3, 232), (x0 + 5.5, 232)]))
zo = add(Part('zocalo_frontal', 'Y', 4, box(T, 3, W - T, Z_FLOOR), desc='zocalo frontal (tapa el compartimento inferior)'))
j_V_sides(zo, 4, [(6, 12)])
j_V_H(zo, bottom, 4, [(30, 50), (120, 140)], 3, False)
j_V_H(zo, floor, 4, [(30, 50), (120, 140)], Z_FLOOR, True)
zo.engr += [LineString([(T, 5.5), (W - T, 5.5)]), LineString([(T, 12.5), (W - T, 12.5)])]

# ---------------------------------------------------------------- grabados: piso, paredes (zocalo dorado, paneles, hachas cruzadas)
for k in range(0, 6):
    z0 = 3 + 10 * k
    pts, x, i = [], T, 0
    while x <= W - T + 1e-6:
        pts.append((x, z0 + (5 if i % 2 else 0))); x += 6; i += 1
    floor.engr.append(LineString(pts))
for s in (lado, lado_d):
    s.engr += [LineString([(4, z), (196, z)]) for z in (22, 50, 53, 116, 120)]
    for yy in range(8, 190, 8):
        s.engr.append(LineString([(yy, 26), (yy, 48)]))
    for (ya, yb) in ((8, 40), (60, 110), (124, 156)):
        s.engr += [box(ya, 58, yb, 112).exterior]
axes = []
for sgn in (1, -1):
    ax_line = affinity.rotate(box(-1, -24, 1, 24), 35 * sgn, origin=(0, 0))
    head = affinity.rotate(Polygon([(1, 14), (8, 20), (9, 12), (8, 6), (1, 10)]), 35 * sgn, origin=(0, 0))
    axes += [ax_line.exterior, head.exterior]
lado_d.engr += [affinity.translate(a_, 85, 85) for a_ in axes]
# --------------------------------------------------------------- verificaciones
def final_geoms():
    return {n: p.geom() for n, p in parts.items()}


def slab_axes(p):
    return p.kind


def material_len(p, g, fixed_axis, fixed_val, w_axis):
    """intervalos [(w0,w1)] de material de p a lo largo de w_axis en la linea fixed_axis=fixed_val"""
    ua, va = AX[p.kind]
    if ua == fixed_axis and va == w_axis:
        line = LineString([(fixed_val, -50), (fixed_val, 500)]); wi = 1
    elif va == fixed_axis and ua == w_axis:
        line = LineString([(-50, fixed_val), (500, fixed_val)]); wi = 0
    else:
        raise ValueError
    r = g.intersection(line)
    segs = list(r.geoms) if hasattr(r, 'geoms') else ([r] if not r.is_empty else [])
    return [tuple(sorted((c[0][wi], c[-1][wi]))) for c in (list(s.coords) for s in segs if s.geom_type == 'LineString')]


def ov(ia, ib):
    t = 0.0
    for a0, a1 in ia:
        for b0, b1 in ib:
            t += max(0.0, min(a1, b1) - max(a0, b0))
    return t


def interferences(G):
    errs = []
    names = list(parts)
    for a, b in itertools.combinations(names, 2):
        A, B = parts[a], parts[b]
        if A.kind == B.kind:
            continue
        ax, bx = A.kind.lower(), B.kind.lower()
        third = ({'x', 'y', 'z'} - {ax, bx}).pop()
        # slab overlap
        if not (A.c < B.c + T and B.c < A.c + T) and False:
            continue
        fa, fb = bx, ax                      # A se sondea en el eje de B y viceversa
        la = material_len(A, G[a], fa, B.c + T / 2, third)
        lb = material_len(B, G[b], fb, A.c + T / 2, third)
        o = ov(la, lb)
        if o > 0.01:
            errs.append((a, b, round(o, 2)))
    return errs


def thin_regions(g, r=1.0):
    op = g.buffer(-r, join_style=MITRE).buffer(r, join_style=MITRE)
    d = g.difference(op)
    out = []
    geoms = list(d.geoms) if hasattr(d, 'geoms') else [d]
    for q in geoms:
        if q.area > 2.0 and not q.is_empty:
            out.append((round(q.area, 1), tuple(round(v, 1) for v in q.centroid.coords[0])))
    return out


def run_checks(G):
    rep = []
    for n, g in G.items():
        if isinstance(g, MultiPolygon):
            rep.append(f'ISLA/PIEZA PARTIDA en {n}: {[round(x.area,1) for x in g.geoms]}')
        elif not g.is_valid:
            rep.append(f'geometria invalida en {n}')
        t = thin_regions(g)
        if t:
            rep.append(f'puentes <2 mm en {n}: {t[:6]}')
    for e in interferences(G):
        rep.append(f'INTERFERENCIA {e}')
    return rep




# --------------------------------------------------------------- hojas de corte (v2: MaxRects + capa de etiquetas aparte)
def norm_sheet(p, g):
    items = [g] + p.engr
    if p.name == 'lado_der':
        items = [affinity.scale(i, xfact=-1, origin=(D / 2, 0)) for i in items]
    fl = [affinity.scale(i, yfact=-1, origin=(0, 0)) for i in items]
    mnx, mny, mxx, mxy = fl[0].bounds
    fl = [affinity.translate(i, -mnx, -mny) for i in fl]
    return fl[0], fl[1:], mxx - mnx, mxy - mny


class MaxRects:
    def __init__(self, w, h):
        self.free = [(0.0, 0.0, w, h)]

    def score(self, bw, bh):
        best = None
        for (x, y, w, h) in self.free:
            if bw <= w + 1e-9 and bh <= h + 1e-9:
                sc = (min(w - bw, h - bh), max(w - bw, h - bh))
                if best is None or sc < best: best = sc
        return best

    def insert(self, bw, bh):
        best = None
        for (x, y, w, h) in self.free:
            if bw <= w + 1e-9 and bh <= h + 1e-9:
                sc = (min(w - bw, h - bh), max(w - bw, h - bh))
                if best is None or sc < best[0]:
                    best = (sc, x, y)
        if best is None:
            return None
        _, x, y = best
        new = []
        for (fx, fy, fw, fh) in self.free:
            if x >= fx + fw or x + bw <= fx or y >= fy + fh or y + bh <= fy:
                new.append((fx, fy, fw, fh)); continue
            if x > fx: new.append((fx, fy, x - fx, fh))
            if x + bw < fx + fw: new.append((x + bw, fy, fx + fw - x - bw, fh))
            if y > fy: new.append((fx, fy, fw, y - fy))
            if y + bh < fy + fh: new.append((fx, y + bh, fw, fy + fh - y - bh))
        keep = []
        for i, a in enumerate(new):
            dup = False
            for j, b in enumerate(new):
                if i == j: continue
                inside = b[0] <= a[0] + 1e-9 and b[1] <= a[1] + 1e-9 and b[0] + b[2] >= a[0] + a[2] - 1e-9 and b[1] + b[3] >= a[1] + a[3] - 1e-9
                if inside and (b != a or j < i):
                    dup = True; break
            if not dup: keep.append(a)
        self.free = keep
        return x, y


def pack(G):
    best = None
    rnd = random.Random(5)
    for key in ['area', 'maxdim', 'h', 'w'] + list(range(1200)):
        sh = pack_with(G, key, rnd)
        sc = (len(sh), -min(100 * sum(i[0]['w'] * i[0]['h'] for i in s_['items']) for s_ in sh[-1:]))
        if best is None or sc < best[0]: best = (sc, sh)
    return best[1]


def pack_with(G, key, rnd=None):
    items = []
    for n, p in parts.items():
        cut, eng, w, h = norm_sheet(p, G[n])
        for q in range(p.qty):
            items.append(dict(name=n, cut=cut, eng=eng, w=w, h=h))
    if isinstance(key, int):
        items.sort(key=lambda i: -i['w'] * i['h'] * rnd.uniform(0.4, 1.6))
        key = None
    kf = {None: lambda i: 0, 'area': lambda i: -i['w'] * i['h'], 'maxdim': lambda i: -max(i['w'], i['h']), 'h': lambda i: -i['h'], 'w': lambda i: -i['w']}[key]
    items.sort(key=kf)
    uw, uh = SHEET_W - 2 * MARGIN + GAP, SHEET_H - 2 * MARGIN + GAP
    sheets = []
    for it in items:
        done = False
        for sh in sheets:
            c = []
            for rot in (False, True):
                w, h = (it['h'], it['w']) if rot else (it['w'], it['h'])
                sc = sh['mr'].score(w + GAP, h + GAP + LABEL)
                if sc is not None: c.append((sc, rot, w, h))
            if c:
                sc, rot, w, h = min(c)
                r = sh['mr'].insert(w + GAP, h + GAP + LABEL)
                sh['items'].append((it, r[0], r[1], rot)); done = True; break
        if not done:
            sh = dict(mr=MaxRects(uw, uh), items=[]); sheets.append(sh)
            for rot in (False, True):
                w, h = (it['h'], it['w']) if rot else (it['w'], it['h'])
                r = sh['mr'].insert(w + GAP, h + GAP + LABEL)
                if r:
                    sh['items'].append((it, r[0], r[1], rot)); done = True; break
            if not done:
                raise RuntimeError('pieza mas grande que la hoja: ' + it['name'])
    return sheets


def place(it, x, y, rot):
    cut, eng = it['cut'], it['eng']
    if rot:
        cut = affinity.rotate(cut, 90, origin=(0, 0)); eng = [affinity.rotate(e, 90, origin=(0, 0)) for e in eng]
        mnx, mny = cut.bounds[:2]
        cut = affinity.translate(cut, -mnx, -mny); eng = [affinity.translate(e, -mnx, -mny) for e in eng]
    dx, dy = MARGIN + x, MARGIN + y + LABEL
    return affinity.translate(cut, dx, dy), [affinity.translate(e, dx, dy) for e in eng]


def rings(g):
    out = []
    if g.is_empty: return out
    if g.geom_type == 'Polygon':
        out.append(list(g.exterior.coords)); out += [list(i.coords) for i in g.interiors]
    elif g.geom_type in ('LineString', 'LinearRing'):
        out.append(list(g.coords))
    elif hasattr(g, 'geoms'):
        for q in g.geoms: out += rings(q)
    return out


def path_d(coords, closed):
    s = 'M' + ' L'.join(f'{x:.3f},{y:.3f}' for x, y in coords)
    return s + (' Z' if closed else '')


def write_outputs(G):
    import ezdxf
    sheets = pack(G)
    comp, stats = [], []
    for si, sh in enumerate(sheets, 1):
        svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{SHEET_W}mm" height="{SHEET_H}mm" viewBox="0 0 {SHEET_W} {SHEET_H}">',
               f'<rect width="{SHEET_W}" height="{SHEET_H}" fill="white" stroke="none"/>',
               '<g id="CORTE" fill="none" stroke="#ff0000" stroke-width="0.1">']
        eng, lab = [], []
        doc = ezdxf.new('R2010', setup=True); doc.units = 4
        doc.layers.add('CORTE', color=1); doc.layers.add('GRABADO', color=5); doc.layers.add('ETIQUETAS', color=3)
        msp = doc.modelspace()
        placed, labels = [], []
        area = 0.0
        for it, x, y, rot in sh['items']:
            cut, en = place(it, x, y, rot)
            placed.append((it['name'], cut)); area += cut.area
            ccut = cut.buffer(KERF / 2, join_style=MITRE)
            for r in rings(ccut):
                svg.append(f'<path d="{path_d(r, True)}"/>')
                msp.add_lwpolyline([(a, SHEET_H - b) for a, b in r], close=True, dxfattribs={'layer': 'CORTE'})
            for e in en:
                for r in rings(e):
                    eng.append(f'<path d="{path_d(r, False)}"/>')
                    msp.add_lwpolyline([(a, SHEET_H - b) for a, b in r], dxfattribs={'layer': 'GRABADO'})
            mnx, mny = cut.bounds[:2]
            lab.append(f'<text x="{mnx:.2f}" y="{mny-1.5:.2f}">{it["name"]}</text>')
            msp.add_text(it['name'], height=2.8, dxfattribs={'layer': 'ETIQUETAS'}).set_placement((mnx, SHEET_H - (mny - 1.5)))
            labels.append((it['name'], box(mnx, mny - 1.5 - 2.8, mnx + 1.7 * len(it['name']), mny - 1.5)))
        svg.append('</g><g id="GRABADO" fill="none" stroke="#0000ff" stroke-width="0.1">' + ''.join(eng) + '</g>')
        svg.append('<g id="ETIQUETAS" fill="#00aa00" stroke="none" font-size="2.8" font-family="sans-serif">' + ''.join(lab) + '</g></svg>')
        open(os.path.join(OUT, f'hoja_{si}_corte.svg'), 'w').write('\n'.join(svg))
        doc.saveas(os.path.join(OUT, f'hoja_{si}_corte.dxf'))
        comp.append((placed, labels))
        stats.append((si, len(placed), 100 * area / (SHEET_W * SHEET_H)))
    rep = []
    for si, (placed, labels) in enumerate(comp, 1):
        for (a, ga), (b, gb) in itertools.combinations(placed, 2):
            d = ga.distance(gb)
            if d < 2.0:
                rep.append(f'hoja {si}: {a} y {b} a {d:.2f} mm')
        for n, g in placed:
            mnx, mny, mxx, mxy = g.bounds
            if mnx < 5 or mny < 5 or mxx > SHEET_W - 5 or mxy > SHEET_H - 5:
                rep.append(f'hoja {si}: {n} fuera de margen')
        for ln, lb in labels:
            for n, g in placed:
                if g.distance(lb) < 0.5:
                    rep.append(f'hoja {si}: etiqueta {ln} toca pieza {n}')
    return len(sheets), rep, stats


# --------------------------------------------------------------- previsualizaciones
def p3(p, u, v):
    return {'X': (p.c + T / 2, u, v), 'Y': (u, p.c + T / 2, v), 'Z': (u, v, p.c + T / 2)}[p.kind]


def svg_path_from(poly, proj):
    d = ''
    for r in rings(poly):
        d += 'M' + ' L'.join('%.2f,%.2f' % proj(c) for c in r) + ' Z '
    return d


def eng_path(p, proj):
    d = ''
    for e in p.engr:
        for r in rings(e):
            d += 'M' + ' L'.join('%.2f,%.2f' % proj(c) for c in r) + ' '
    return d


def color(t, a=(184, 138, 86), b=(66, 40, 26)):
    return '#%02x%02x%02x' % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def preview(G, mode, path):
    if mode == 'front':
        S = 3.0
        sx = lambda x, y, z: (x * S, (H - z) * S + 20)
        vw, vh = W * S, H * S + 40
    else:
        k1, k2, S = 0.62, 0.42, 2.2
        sx = lambda x, y, z: (S * (x + k1 * y) + 20, S * ((H - z) - k2 * y) + S * k2 * D + 20)
        vw, vh = S * (W + k1 * D) + 40, S * (H + k2 * D) + 40
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{vw:.0f}" height="{vh:.0f}" viewBox="0 0 {vw:.0f} {vh:.0f}">',
           '<rect width="100%" height="100%" fill="#1b1612"/>']
    order = []
    for n, p in parts.items():
        if mode == 'front':
            order.append((-(1000 if p.kind == 'X' else p.c), n, 1.0))
        else:
            if n in ('lado_der', 'techo_celosia', 'tapa_superior', 'nervio_techo_1', 'nervio_techo_2'):
                rank, op = 1000 + {'lado_der': 0, 'techo_celosia': 1, 'nervio_techo_1': 2, 'nervio_techo_2': 2, 'tapa_superior': 3}[n], 0.42
            else:
                rank = {'lado_izq': -100, 'base_fondo': -90, 'nervio_piso_1': -80, 'nervio_piso_2': -80, 'piso': -70}.get(n, -p.c)
                op = 0.97
            order.append((rank, n, op))
    order.sort()
    for rank, n, op in order:
        p = parts[n]; g = G[n]
        if mode == 'front':
            if p.kind == 'Y':
                proj = (lambda c, p=p: sx(c[0], p.c, c[1]))
                t = min(1, p.c / 200.0)
                if n == 'vitral_reticula':
                    out.append(f'<path d="{svg_path_from(GLASS, proj)}" fill="#ffe3a0" fill-rule="evenodd"/>')
                out.append(f'<path d="{svg_path_from(g, proj)}" fill="{color(t)}" fill-rule="evenodd" stroke="#2a1a10" stroke-width="0.8"/>')
                out.append(f'<path d="{eng_path(p, proj)}" fill="none" stroke="#2a1a10" stroke-width="0.35" stroke-opacity="0.55"/>')
            else:
                if p.kind == 'X': pts = [sx(p.c, 0, 0), sx(p.c + T, 0, 0), sx(p.c + T, 0, H), sx(p.c, 0, H)]
                else: pts = [sx(T, 0, p.c), sx(W - T, 0, p.c), sx(W - T, 0, p.c + T), sx(T, 0, p.c + T)]
                out.append('<path d="M' + ' L'.join('%.1f,%.1f' % q for q in pts) + ' Z" fill="#5b3b25" stroke="#2a1a10" stroke-width="0.8"/>')
        else:
            proj = (lambda c, p=p: sx(*p3(p, c[0], c[1])))
            t = 0.2 if p.kind in 'XZ' else min(1, p.c / 200.0)
            if n == 'vitral_reticula':
                out.append(f'<path d="{svg_path_from(GLASS, proj)}" fill="#ffe3a0" fill-rule="evenodd"/>')
            out.append(f'<path d="{svg_path_from(g, proj)}" fill="{color(t)}" fill-opacity="{op}" fill-rule="evenodd" stroke="#2a1a10" stroke-width="0.6" stroke-opacity="{op}"/>')
            if p.kind == 'Y':
                out.append(f'<path d="{eng_path(p, proj)}" fill="none" stroke="#2a1a10" stroke-width="0.3" stroke-opacity="0.5"/>')
    out.append('</svg>')
    open(path, 'w').write('\n'.join(out))


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    G = final_geoms()
    rep = run_checks(G)
    ns, rep2, stats = write_outputs(G)
    preview(G, 'front', os.path.join(OUT, 'vista_frontal.svg'))
    preview(G, 'obl', os.path.join(OUT, 'vista_completa.svg'))
    import cairosvg
    for n in ('vista_frontal', 'vista_completa'):
        cairosvg.svg2png(url=os.path.join(OUT, n + '.svg'), write_to=os.path.join(OUT, n + '.png'))
    for i in range(1, ns + 1):
        s = open(os.path.join(OUT, f'hoja_{i}_corte.svg')).read().replace('stroke-width="0.1"', 'stroke-width="0.35"')
        cairosvg.svg2png(bytestring=s.encode(), write_to=os.path.join(OUT, f'hoja_{i}_preview.png'), output_width=1800)
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="110mm" height="110mm" viewBox="%.1f %.1f 110 110">' % (WCX - 55, -WCZ - 55),
           '<circle cx="%.2f" cy="%.2f" r="%.1f" fill="#fffaf0" stroke="#888" stroke-width="0.2"/>' % (WCX, -WCZ, RG + 4),
           '<g fill="none" stroke="#2b1d12" stroke-width="0.45" stroke-linecap="round">']
    for ln in lineas_vitral_impreso():
        for r_ in rings(ln):
            svg.append('<path d="%s"/>' % path_d([(x_, -z_) for x_, z_ in r_], False))
    svg.append('</g></svg>')
    open(os.path.join(OUT, 'vitral_impreso.svg'), 'w').write('\n'.join(svg))
    cairosvg.svg2png(url=os.path.join(OUT, 'vitral_impreso.svg'), write_to=os.path.join(OUT, 'vitral_impreso.png'), output_width=1300)
    print('hojas:', ns, '; piezas distintas:', len(parts), '; kerf', KERF, '; T', T)
    for s in stats: print('  hoja %d: %d piezas, %.0f%% de la hoja es material' % s)
    print('--- verificaciones ---')
    for r in rep + rep2: print(r)
    print('OK' if not (rep or rep2) else f'{len(rep)+len(rep2)} avisos')
