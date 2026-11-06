#!/usr/bin/env python3
"""Book nook Sanctum Sanctorum (Dr. Strange) v2 (mas detalle) - generador de piezas para corte laser en MDF.
Uso: python3 generar_booknook.py [salida_dir]
Coordenadas de diseno = coordenadas globales del ensamble (mm):
  x ancho 0..150, y profundidad 0..200 (y=0 frente abierto), z alto 0..255.
"""
import math, os, sys, itertools
from shapely.geometry import box, Point, LineString, Polygon, MultiPolygon
from shapely.ops import unary_union
from shapely import affinity

T = 3.0          # espesor MDF (medir el real y cambiar aqui)
KERF = 0.12      # ancho de corte laser
W, D, H = 150.0, 200.0, 255.0
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


# ---------------------------------------------------------------- piezas estructurales
YI = [(15, 45), (85, 115), (155, 185)]
Z_BOT, Z_FLOOR, Z_LAT, Z_ROOF = 0.0, 15.0, 240.0, 252.0
FLOOR_TOP, LAT_BOT = Z_FLOOR + T, Z_LAT

lado = add(Part('lado_izq', 'X', 0, box(0, 0, D, H), desc='pared lateral izquierda'))
lado_d = add(Part('lado_der', 'X', W - T, box(0, 0, D, H), desc='pared lateral derecha (espejo)'))
bottom = add(Part('base_fondo', 'Z', Z_BOT, box(T, 0, W - T, D), desc='tapa inferior del compartimento LED'))
floor = add(Part('piso', 'Z', Z_FLOOR, box(T, 0, W - T, 194), desc='piso (parquet grabado)'))
lattice = add(Part('techo_celosia', 'Z', Z_LAT, box(T, 0, W - T, 194), desc='techo con celosia (luz LED desde arriba)'))
roof = add(Part('tapa_superior', 'Z', Z_ROOF, box(T, 0, W - T, D), desc='tapa superior'))
for p, z in ((bottom, Z_BOT), (floor, Z_FLOOR), (lattice, Z_LAT), (roof, Z_ROOF)):
    j_H_sides(p, z, YI)

for i, xr in enumerate((36.0, 108.0)):
    r = add(Part(f'nervio_piso_{i+1}', 'X', xr, box(15, 3, 175, 15), desc='separador compartimento LED inferior'))
    j_rib(r, xr, floor, [(20, 40), (90, 110), (150, 170)], 15, True)
    j_rib(r, xr, bottom, [(20, 40), (90, 110), (150, 170)], 3, False)
for i, xr in enumerate((6.0, 141.0)):
    r = add(Part(f'nervio_techo_{i+1}', 'X', xr, box(15, 243, 175, 252), desc='separador camara LED superior'))
    j_rib(r, xr, roof, [(20, 40), (90, 110), (150, 170)], 252, True)
    j_rib(r, xr, lattice, [(20, 40), (90, 110), (150, 170)], 243, False)

cover = add(Part('tapa_trasera', 'Y', 194, box(T, 3, W - T, 252), desc='tapa trasera (camara de luz)'))
j_V_sides(cover, 194, [(30, 60), (110, 140), (190, 220)])
j_V_H(cover, bottom, 194, [(10, 30), (60, 90), (120, 140)], 3, False)
j_V_H(cover, roof, 194, [(10, 30), (60, 90), (120, 140)], 252, True)
cover.holes.append(Point(75, 30).buffer(4.0, 32))
cover.engr += [box(20, 40, 130, 240).exterior, box(24, 44, 126, 236).exterior]

backw = add(Part('fondo_ventana', 'Y', 164, box(T, FLOOR_TOP, W - T, LAT_BOT), desc='pared de fondo con ventana circular'))
j_V_sides(backw, 164, [(40, 70), (110, 140), (190, 220)])
BX = [(14, 30), (60, 90), (120, 134)]
j_V_H(backw, floor, 164, BX, FLOOR_TOP, False)
j_V_H(backw, lattice, 164, BX, LAT_BOT, True)

# ---- ventana del Sanctum: aro, radios, retícula de vidrio y barras curvas
WCX, WCZ, RG = 75.0, 140.0, 37.0
bars = []
for pts, wd in [(((-18, 40), (-4, 16), (-7, -14), (-20, -40)), 2.4),
                (((40, 16), (14, -4), (-10, 6), (-40, -8)), 2.4),
                (((22, 40), (28, 16), (14, -16), (26, -40)), 1.9),
                (((-40, 20), (-26, 22), (-14, 12), (-6, 3)), 1.4)]:
    bars.append(LineString(bez(*pts)).buffer(wd, cap_style=1))
bars = unary_union(bars)
fine = [Point(0, 0).buffer(26 + 1.2).difference(Point(0, 0).buffer(26 - 1.2)),
        Point(0, 0).buffer(16 + 1.2).difference(Point(0, 0).buffer(16 - 1.2))]
for i in range(16):
    r0 = 8 if i % 2 == 0 else 16
    fine.append(affinity.rotate(box(r0, -1.2, RG + 1, 1.2), 11.25 + 22.5 * i, origin=(0, 0)))
hub = Point(0, 0).buffer(7.5).difference(Point(0, 0).buffer(4.2))
glass = Point(0, 0).buffer(RG, 96).difference(unary_union([bars, hub] + fine))
glass = unary_union([q for q in (glass.geoms if hasattr(glass, 'geoms') else [glass]) if q.area >= 14.0])
glass = affinity.translate(glass, WCX, WCZ)
backw.holes.append(glass)
GLASS = glass
# aro ornamental grabado: anillos + radios cortos (sello)
backw.engr += [Point(WCX, WCZ).buffer(r, 96).exterior for r in (RG + 2.5, RG + 5, RG + 11)]
backw.engr += [LineString([(WCX + (RG + 5) * math.cos(math.radians(a)), WCZ + (RG + 5) * math.sin(math.radians(a))),
                           (WCX + (RG + 11) * math.cos(math.radians(a)), WCZ + (RG + 11) * math.sin(math.radians(a)))])
               for a in range(0, 360, 10)]
backw.engr += ashlar(box(T, FLOOR_TOP, W - T, LAT_BOT).difference(Point(WCX, WCZ).buffer(RG + 13)), T, W - T, FLOOR_TOP, LAT_BOT, seed=7)


# ---------------------------------------------------------------- marcos de profundidad
def vframe(name, y0, body, sz, bx, holes, desc, zb=FLOOR_TOP):
    f = add(Part(name, 'Y', y0, body, desc=desc))
    j_V_sides(f, y0, sz)
    j_V_H(f, floor, y0, bx, zb, False)
    f.holes += holes
    return f


FULL = box(T, FLOOR_TOP, W - T, 240)

# F1 fachada de ladrillo: columnas, arco, denticulos, cornisa
op1 = arch(20, 130, 26, 180, 36)
dent1 = [box(10 + 8 * i, 227, 14 + 8 * i, 231) for i in range(17)]
f1 = vframe('marco1_fachada', 8, FULL, [(50, 80), (150, 180)], [(10, 30), (58, 86), (114, 134)],
            [op1] + dent1, 'fachada de ladrillo con portico')
reg = FULL.difference(unary_union([op1.buffer(2.0)] + [d.buffer(1.5) for d in dent1])).intersection(box(T + 1.2, FLOOR_TOP + 8, W - T - 1.2, 224))
f1.engr += bricks(reg, T, W - T, FLOOR_TOP + 8, 224)
f1.engr += [LineString([(T, z), (W - T, z)]) for z in (225, 237, 239)] + \
           [LineString([(T, z), (W - T, z)]) for z in (18 + 6, 18 + 8)] + \
           [LineString([(T, 233.5), (W - T, 233.5)])]
f1.engr += [LineString([(x, 26), (x, 224)]) for x in (6, 8)] + [LineString([(x, 26), (x, 224)]) for x in (142, 144)]

# F1b arco interior con festoneado calado
op1b = arch(23, 127, 26, 176, 34)
sc1 = scallops(75, 176, 52, 34, 6.5, 2.2, 15)
f1b = vframe('marco1b_arco', 22, FULL, [(60, 90), (170, 200)], [(10, 30), (58, 86), (114, 134)],
             [op1b] + sc1, 'arco interior con festoneado')
f1b.engr += [LineString([(x, 30), (x, 200)]) for x in (7, 11, 15, 19)] + [LineString([(x, 30), (x, 200)]) for x in (131, 135, 139, 143)] + \
            [LineString([(T, 236), (W - T, 236)])]

# F2 balcon: barandilla fina (barrotes 2.4 mm), pasamanos, riel medio y faroles
bars2 = []
n2 = 20
for k in range(n2):
    xc = 13 + 3.1 + k * 6.2
    w = 4.4 if k % 5 == 0 else 2.4
    bars2.append(box(xc - w / 2, 24, xc + w / 2, 62))
mid = box(13, 41.0, 137, 43.4)
op2 = box(13, 24, 137, 62).difference(unary_union(bars2 + [mid]))
lampL = unary_union([box(6, 68, 9, 92), box(4.5, 90, 13.5, 92), box(4, 92, 14, 108), Polygon([(3, 108), (15, 108), (9, 118)])])
lampL = affinity.translate(lampL.difference(box(6.5, 95, 11.5, 105)), 24, 0)   # faroles dentro de la abertura visible
lampR = mirror_x(lampL)
lamp_hole = [box(30.5, 95, 35.5, 105), mirror_x(box(30.5, 95, 35.5, 105))]
body2 = unary_union([box(T, FLOOR_TOP, W - T, 68), lampL, lampR])
f2 = vframe('marco2_balcon', 38, body2, [(30, 48)], [(10, 30), (58, 86), (114, 134)], [op2] + lamp_hole,
            'balcon con barandilla y faroles')
f2.engr += [LineString([(T, 65), (W - T, 65)]), LineString([(T, 63), (W - T, 63)]), LineString([(T, 21), (W - T, 21)])]

# F3 escalera, cofre y pedestales con cuencos
steps = unary_union([box(T, FLOOR_TOP, W - T, 28), box(22, 28, 128, 38), box(32, 38, 118, 48), box(42, 48, 108, 58)])
posts = unary_union([box(32, 38, 35, 62), Point(33.5, 64.5).buffer(3.0, 24), box(115, 38, 118, 62), Point(116.5, 64.5).buffer(3.0, 24)])
chest = unary_union([box(52, 58, 98, 72), affinity.scale(Point(75, 72).buffer(1, 48), 23, 9)])
chest = chest.difference(unary_union([box(52, 58, 56, 61), box(94, 58, 98, 61)]))
ped = unary_union([box(T, 28, 29, 100), box(121, 28, W - T, 100)])
bowl = unary_union([Polygon([(3, 100), (31, 100), (27, 110), (7, 110)]),
                    Polygon([(119, 100), (147, 100), (143, 110), (123, 110)])])
f3 = add(Part('marco3_escalera_cofre', 'Y', 72, unary_union([steps, posts, chest, ped, bowl]), desc='escalera, cofre y pedestales'))
j_V_sides(f3, 72, [(45, 60), (72, 87)])
j_V_H(f3, floor, 72, [(8, 26), (60, 90), (120, 138)], FLOOR_TOP, False)
f3.holes += [box(6, 36, 9, 40), box(6, 44, 9, 48)]   # cajones (hendiduras)
f3.holes += [box(141, 36, 144, 40), box(141, 44, 144, 48)]
f3.engr += [LineString([(a, z), (b, z)]) for (a, b, z) in ((22, 32, 33), (32, 42, 43), (42, 108, 53), (108, 118, 43), (118, 128, 33))] + \
           [LineString([(x, 30), (x, 98)]) for x in (13, 19, 25)] + [LineString([(x, 30), (x, 98)]) for x in (125, 131, 137)] + \
           [LineString([(a, z), (b, z)]) for (a, b) in ((6, 27), (123, 144)) for z in (52, 62, 72, 82, 92)] + \
           [box(58, 61, 92, 69).exterior, LineString([(52, 72), (98, 72)]), Point(75, 65).buffer(1.5, 16).exterior]
for yy in range(4):
    f3.engr.append(wavy(T + 2, 26, 33 + yy * 16, amp=0.6, per=10))

# F4 pilastras + arco con festoneado + denticulos + sillares
op4 = arch(24, 126, 26, 170, 38)
dent4 = [box(10 + 7 * i, 224, 13 + 7 * i, 227) for i in range(19)]
sc4 = scallops(75, 170, 51, 38, 6.5, 2.2, 15)
f4 = vframe('marco4_pilastras', 108, FULL, [(60, 90), (150, 180)], [(8, 20), (62, 82), (128, 140)],
            [op4] + dent4 + sc4, 'pilastras, cornisa y arco')
f4.engr += ashlar(FULL.difference(unary_union([op4.buffer(2), unary_union(sc4).buffer(2), unary_union(dent4).buffer(2)])).intersection(box(T + 1.2, 30, W - T - 1.2, 220)),
                  T, W - T, 30, 220, seed=3)
f4.engr += [LineString([(T, z), (W - T, z)]) for z in (221, 232, 234, 236)]

# F4b arco profundo con festoneado y estrias
op4b = arch(27, 123, 26, 166, 34)
sc4b = scallops(75, 166, 48, 34, 6.0, 2.0, 13)
f4b = vframe('marco4b_arco_profundo', 128, FULL, [(50, 80), (160, 190)], [(8, 20), (62, 82), (128, 140)],
             [op4b] + sc4b, 'arco profundo')
f4b.engr += [LineString([(x, 30), (x, 200)]) for x in (7, 11, 15, 19, 23)] + [LineString([(x, 30), (x, 200)]) for x in (127, 131, 135, 139, 143)] + \
            [LineString([(T, z), (W - T, z)]) for z in (226, 229)]

# F5 aro de la ventana: denticulos, anillos grabados, puerta con paneles
op5 = Point(WCX, WCZ).buffer(50, 128).union(ring_notches(WCX, WCZ, 50, 36))
door = [box(33.5, 27, 39.8, 50), box(42.2, 27, 48.5, 50), box(33.5, 53, 39.8, 76), box(42.2, 53, 48.5, 76),
        affinity.scale(Point(41, 79).buffer(1, 32), 7.5, 6).intersection(box(33.5, 79, 48.5, 90))]
f5 = vframe('marco5_aro_puerta', 146, FULL, [(40, 60), (200, 220)], [(8, 26), (60, 90), (120, 138)],
            [op5] + door, 'aro dentado de la ventana y puerta con paneles')
f5.engr += [Point(WCX, WCZ).buffer(r, 128).exterior for r in (57, 60, 63)]
f5.engr += [arch(31, 51, 24, 78, 10).exterior, Point(48, 52).buffer(0.9, 12).exterior]
f5.engr += ashlar(FULL.difference(unary_union([op5.buffer(8), arch(28, 54, 22, 78, 12)])).intersection(box(T + 1.2, 30, W - T - 1.2, 236)),
                  T, W - T, 30, 236, seed=11)

# ---------------------------------------------------------------- techo: celosia + relieve superior
cols, rows = 5, 6
gx0, gx1, gy0, gy1 = 14.0, 130.0, 6.0, 158.0
cw, ch = (gx1 - gx0) / cols, (gy1 - gy0) / rows
relief_holes = []
for r in range(rows):
    for c in range(cols):
        x0, y0 = gx0 + c * cw + 2.5, gy0 + r * ch + 2.5
        x1, y1 = x0 + cw - 5, y0 + ch - 5
        o = box(x0, y0, x1, y1)
        gam = unary_union([box(x0, y0, x0 + 2.6, y1), box(x0, y0 + (y1 - y0) * 0.55, x0 + (x1 - x0) * 0.68, y0 + (y1 - y0) * 0.55 + 2.6),
                           box(x0 + (x1 - x0) * 0.68 - 2.6, y0 + (y1 - y0) * 0.30, x0 + (x1 - x0) * 0.68, y0 + (y1 - y0) * 0.55 + 2.6)])
        if (r + c) % 2:
            gam = affinity.scale(gam, xfact=-1, origin=((x0 + x1) / 2, (y0 + y1) / 2))
        lattice.holes.append(o.difference(gam))
        # capa de relieve (pegada encima): 4 ventanas por celda separadas por cruz de 2.4 mm
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        inner = box(x0 + 1.5, y0 + 1.5, x1 - 1.5, y1 - 1.5)
        cross = unary_union([box(cx - 1.2, y0, cx + 1.2, y1), box(x0, cy - 1.2, x1, cy + 1.2)])
        d = inner.difference(cross)
        relief_holes += list(d.geoms) if hasattr(d, 'geoms') else [d]
lattice.engr += [box(gx0, gy0, gx1, gy1).exterior, box(gx0 - 3, gy0 - 3, gx1 + 3, gy1 + 3).exterior]
relief = add(Part('techo_relieve', 'Z', 243, box(12, 4, 138, 160), desc='capa de relieve del techo (se pega sobre la celosia, sin pestanas)'))
relief.holes += relief_holes
relief.engr += [box(14, 6, 136, 158).exterior]
roof.holes.append(Point(75, 180).buffer(4.0, 32))
roof.engr += [Point(75, 90).buffer(r, 96).exterior for r in (20, 24, 40, 44)] + \
             [LineString([(75 + 24 * math.cos(math.radians(a)), 90 + 24 * math.sin(math.radians(a))),
                          (75 + 40 * math.cos(math.radians(a)), 90 + 40 * math.sin(math.radians(a)))]) for a in range(0, 360, 30)]

# ---------------------------------------------------------------- piso (espiga) y paredes laterales (ventanas, paneles, vetas)
for k in range(0, 13):
    z0 = 8 + 12 * k
    pts = []
    x = T
    i = 0
    while x <= W - T + 1e-6:
        pts.append((x, z0 + (5 if i % 2 else 0)))
        x += 6; i += 1
    floor.engr.append(LineString(pts))
floor.engr.append(Point(75, 80).buffer(30, 96).exterior)
floor.engr.append(Point(75, 80).buffer(34, 96).exterior)

side_win = [(47, 67), (80, 104)]
for s in (lado, lado_d):
    for (y0, y1) in side_win:
        wy = arch(y0, y1, 110, 176, 14)
        mull = unary_union([box((y0 + y1) / 2 - 1.2, 100, (y0 + y1) / 2 + 1.2, 200), box(y0 - 2, 140, y1 + 2, 142.4), box(y0 - 2, 118, y1 + 2, 120.4)])
        wd = wy.difference(mull)
        s.holes += list(wd.geoms) if hasattr(wd, 'geoms') else [wd]
        s.engr += [arch(y0 - 3, y1 + 3, 107, 176, 17).exterior]
    for yy in range(12, 150, 36):
        s.engr += [box(yy, 24, yy + 28, 90).exterior, box(yy + 3, 27, yy + 25, 87).exterior]
        for q in range(4):
            s.engr.append(wavy(yy + 5, yy + 23, 31 + q * 14, amp=0.8, per=14, phase=q))
    for (a, b) in ((10, 40), (112, 140), (148, 164)):
        s.engr += [box(a, 100, b, 225).exterior]
    s.engr += [LineString([(0, 95), (164, 95)]), LineString([(0, 97), (164, 97)]), LineString([(0, 228), (164, 228)]),
               LineString([(0, 231), (164, 231)])]
    s.engr += [box(168, 20, 192, 235).exterior]
lado_d.engr = list(lado.engr)

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
    uw, uh = SHEET_W - 2 * MARGIN + GAP, SHEET_H - 2 * MARGIN + GAP + LABEL
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
            if n in ('lado_der', 'techo_celosia', 'techo_relieve', 'tapa_superior', 'nervio_techo_1', 'nervio_techo_2'):
                rank, op = 1000 + {'lado_der': 0, 'techo_celosia': 1, 'techo_relieve': 2, 'nervio_techo_1': 2, 'nervio_techo_2': 2, 'tapa_superior': 3}[n], 0.42
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
                if n == 'fondo_ventana':
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
            if n == 'fondo_ventana':
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
    print('hojas:', ns, '; piezas distintas:', len(parts), '; kerf', KERF, '; T', T)
    for s in stats: print('  hoja %d: %d piezas, %.0f%% de la hoja es material' % s)
    print('--- verificaciones ---')
    for r in rep + rep2: print(r)
    print('OK' if not (rep or rep2) else f'{len(rep)+len(rep2)} avisos')
