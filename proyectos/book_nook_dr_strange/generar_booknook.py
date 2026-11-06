#!/usr/bin/env python3
"""Book nook Sanctum Sanctorum (Dr. Strange) - generador de piezas para corte laser en MDF.
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


# ---------------------------------------------------------------- piezas estructurales
YI = [(15, 45), (85, 115), (155, 185)]
Z_BOT, Z_FLOOR, Z_LAT, Z_ROOF = 0.0, 15.0, 240.0, 252.0
FLOOR_TOP, LAT_BOT = Z_FLOOR + T, Z_LAT

lado = add(Part('lado_izq', 'X', 0, box(0, 0, D, H), desc='pared lateral izquierda'))
lado_d = add(Part('lado_der', 'X', W - T, box(0, 0, D, H), desc='pared lateral derecha (espejo)'))
bottom = add(Part('base_fondo', 'Z', Z_BOT, box(T, 0, W - T, D), desc='tapa inferior del compartimento LED'))
floor = add(Part('piso', 'Z', Z_FLOOR, box(T, 0, W - T, 194), desc='piso (grabado parquet)'))
lattice = add(Part('techo_celosia', 'Z', Z_LAT, box(T, 0, W - T, 194), desc='techo con celosia (luz LED desde arriba)'))
roof = add(Part('tapa_superior', 'Z', Z_ROOF, box(T, 0, W - T, D), desc='tapa superior'))
for p, z in ((bottom, Z_BOT), (floor, Z_FLOOR), (lattice, Z_LAT), (roof, Z_ROOF)):
    j_H_sides(p, z, YI)

# nervios del compartimento LED (piso) y camara de luz (techo)
for i, xr in enumerate((36.0, 108.0)):
    r = add(Part(f'nervio_piso_{i+1}', 'X', xr, box(15, 3, 175, 15), desc='separador compartimento LED inferior'))
    j_rib(r, xr, floor, [(20, 40), (90, 110), (150, 170)], 15, True)
    j_rib(r, xr, bottom, [(20, 40), (90, 110), (150, 170)], 3, False)
for i, xr in enumerate((6.0, 141.0)):
    r = add(Part(f'nervio_techo_{i+1}', 'X', xr, box(15, 243, 175, 252), desc='separador camara LED superior'))
    j_rib(r, xr, roof, [(20, 40), (90, 110), (150, 170)], 252, True)
    j_rib(r, xr, lattice, [(20, 40), (90, 110), (150, 170)], 243, False)

# tapa trasera (camara de luz de la ventana) y pared de fondo con ventana
cover = add(Part('tapa_trasera', 'Y', 194, box(T, 3, W - T, 252), desc='tapa trasera (camara de luz)'))
j_V_sides(cover, 194, [(30, 60), (110, 140), (190, 220)])
j_V_H(cover, bottom, 194, [(10, 30), (60, 90), (120, 140)], 3, False)
j_V_H(cover, roof, 194, [(10, 30), (60, 90), (120, 140)], 252, True)
cover.holes.append(Point(75, 30).buffer(4.0, 32))

backw = add(Part('fondo_ventana', 'Y', 164, box(T, FLOOR_TOP, W - T, LAT_BOT), desc='pared de fondo con ventana circular'))
j_V_sides(backw, 164, [(40, 70), (110, 140), (190, 220)])
BX = [(14, 30), (60, 90), (120, 134)]
j_V_H(backw, floor, 164, BX, FLOOR_TOP, False)
j_V_H(backw, lattice, 164, BX, LAT_BOT, True)

# ---- ventana del Sanctum (circular, barras curvas) centro (75,140)
WCX, WCZ, RG = 75.0, 140.0, 37.0
bars = []
for pts, wd in [(((-18, 40), (-4, 16), (-7, -14), (-20, -40)), 2.3),
                (((40, 16), (14, -4), (-10, 6), (-40, -8)), 2.3),
                (((22, 40), (28, 16), (14, -16), (26, -40)), 1.8)]:
    bars.append(LineString(bez(*pts)).buffer(wd, cap_style=1))
bars = unary_union(bars)
fine = [Point(0, 0).buffer(25 + 1.2).difference(Point(0, 0).buffer(25 - 1.2))]
for i in range(8):
    fine.append(affinity.rotate(box(7, -1.2, RG + 1, 1.2), 22.5 + 45 * i, origin=(0, 0)))
hub = Point(0, 0).buffer(7.5).difference(Point(0, 0).buffer(4.2))
glass = Point(0, 0).buffer(RG, 96).difference(unary_union([bars, hub] + fine))
glass = unary_union([q for q in (glass.geoms if hasattr(glass, 'geoms') else [glass]) if q.area >= 12.0])   # sin astillas diminutas
glass = affinity.translate(glass, WCX, WCZ)
backw.holes.append(glass)
backw.engr += [Point(WCX, WCZ).buffer(RG + 3.5, 96).exterior, Point(WCX, WCZ).buffer(RG + 6.5, 96).exterior]
GLASS = glass

# ---------------------------------------------------------------- marcos de profundidad
def frame(name, y0, ztop, sz, bx, body_holes, desc, zb=FLOOR_TOP):
    f = add(Part(name, 'Y', y0, box(T, zb, W - T, ztop), desc=desc))
    j_V_sides(f, y0, sz)
    j_V_H(f, floor, y0, bx, zb, False)
    f.holes += body_holes
    return f

# F1 portico frontal: columnas + arco + denticulos
op1 = arch(22, 128, 26, 186, 34)
dent = [box(10 + 8 * i, 229, 14 + 8 * i, 233) for i in range(17)]
f1 = frame('marco1_portico', 8, 240, [(50, 80), (150, 180)], [(10, 30), (58, 86), (114, 134)],
           [op1] + dent, 'portico frontal')
f1.engr += [LineString([(x, 30), (x, 225)]) for x in (7, 11, 15, 19)] + \
           [LineString([(x, 30), (x, 225)]) for x in (131, 135, 139, 143)] + \
           [LineString([(T, 236), (W - T, 236)]), LineString([(T, 222), (W - T, 222)])]

# F2 baranda dorada (balcon / escalera)
bal = []
n = 17
pitch = (W - 2 * T - 20) / (n - 1)
for i in range(n):
    xc = T + 10 + i * pitch
    wbar = 3.0 if i % 4 else 5.0
    bal.append(box(xc - wbar / 2, 24, xc + wbar / 2, 62))
op2 = box(T + 10, 24, W - T - 10, 62).difference(unary_union(bal))
f2 = frame('marco2_baranda', 38, 68, [(30, 48)], [(10, 30), (58, 86), (114, 134)], [op2],
           'baranda (riel y balaustres)')
f2.engr += [LineString([(T, 65), (W - T, 65)])]

# F3 escalones, cofre y pedestales con cuencos
steps = unary_union([box(T, FLOOR_TOP, W - T, 28), box(22, 28, 128, 40), box(36, 40, 114, 52)])
chest = unary_union([box(52, 52, 98, 68), affinity.scale(Point(75, 68).buffer(1, 48), 23, 10)])
chest = chest.difference(unary_union([box(52, 52, 56, 55), box(94, 52, 98, 55)]))
ped = unary_union([box(T, 28, 29, 100), box(121, 28, W - T, 100)])
bowl = unary_union([Polygon([(3, 100), (31, 100), (27, 110), (7, 110)]),
                    Polygon([(119, 100), (147, 100), (143, 110), (123, 110)])])
f3 = add(Part('marco3_escalon_cofre', 'Y', 72, unary_union([steps, chest, ped, bowl]), desc='escalones, cofre y pedestales'))
j_V_sides(f3, 72, [(45, 60), (72, 87)])
j_V_H(f3, floor, 72, [(8, 26), (60, 90), (120, 138)], FLOOR_TOP, False)
f3.engr += [LineString([(x, 30), (x, 98)]) for x in (11, 17, 23)] + [LineString([(x, 30), (x, 98)]) for x in (127, 133, 139)] + \
           [LineString([(a, z), (b, z)]) for (a, b) in ((6, 26), (124, 144)) for z in (40, 55, 70, 85)] + \
           [box(58, 56, 92, 64).exterior, LineString([(52, 68), (98, 68)])]

# F4 pilastras + cornisa en arco
op4 = arch(26, 124, 26, 172, 40)
f4 = frame('marco4_pilastras', 108, 240, [(60, 90), (150, 180)], [(8, 20), (62, 82), (128, 140)],
           [op4] + [box(10 + 7 * i, 226, 13 + 7 * i, 230) for i in range(19)], 'pilastras y cornisa')
f4.engr += [LineString([(x, 30), (x, 200)]) for x in (7, 12, 17)] + [LineString([(x, 30), (x, 200)]) for x in (133, 138, 143)]

# F5 aro de la ventana con denticulos
op5 = Point(WCX, WCZ).buffer(50, 128).union(ring_notches(WCX, WCZ, 50, 36))
f5 = frame('marco5_aro', 146, 240, [(40, 60), (200, 220)], [(8, 26), (60, 90), (120, 138)],
           [op5], 'aro dentado de la ventana')
f5.engr += [Point(WCX, WCZ).buffer(60, 128).exterior, Point(WCX, WCZ).buffer(63, 128).exterior]

# ---------------------------------------------------------------- techo con celosia
cols, rows = 5, 6
gx0, gx1, gy0, gy1 = 14.0, 130.0, 6.0, 158.0
cw, ch = (gx1 - gx0) / cols, (gy1 - gy0) / rows
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
lattice.engr += [box(gx0, gy0, gx1, gy1).exterior]
roof.holes.append(Point(75, 180).buffer(4.0, 32))
roof.engr += [Point(75, 90).buffer(r, 96).exterior for r in (20, 24)] + \
             [LineString([(75 + 24 * math.cos(math.radians(a)), 90 + 24 * math.sin(math.radians(a))),
                          (75 + 30 * math.cos(math.radians(a)), 90 + 30 * math.sin(math.radians(a)))]) for a in range(0, 360, 30)]

# ---------------------------------------------------------------- piso (parquet) y paredes (boiseries)
for k in range(1, 12):
    floor.engr.append(LineString([(T, 14 * k), (W - T, 14 * k)]))
for k in range(1, 10):
    floor.engr.append(LineString([(T + 16 * k, 0), (T + 16 * k, 164)]))
floor.engr.append(Point(75, 80).buffer(30, 96).exterior)
for s in (lado, lado_d):
    for yy in range(12, 150, 36):
        s.engr += [box(yy, 24, yy + 28, 90).exterior, box(yy + 3, 27, yy + 25, 87).exterior,
                   box(yy, 100, yy + 28, 225).exterior]
    s.engr += [LineString([(0, 95), (164, 95)]), LineString([(0, 97), (164, 97)]), LineString([(0, 228), (164, 228)]),
               LineString([(0, 231), (164, 231)])]
    s.engr += [box(168, 20, 192, 235).exterior]

lado_d.engr = list(lado.engr)   # mismas coordenadas de diseno; en la hoja se espeja (vista desde el interior)

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


# --------------------------------------------------------------- hojas de corte
def norm_sheet(p, g):
    """(u,v) -> coords de hoja (v invertido), origen en 0,0. devuelve (cut, engr[list], w, h)"""
    items = [g] + p.engr
    if p.name == 'lado_der':
        items = [affinity.scale(i, xfact=-1, origin=(D / 2, 0)) for i in items]
    fl = [affinity.scale(i, yfact=-1, origin=(0, 0)) for i in items]
    mnx, mny, mxx, mxy = fl[0].bounds
    fl = [affinity.translate(i, -mnx, -mny) for i in fl]
    return fl[0], fl[1:], mxx - mnx, mxy - mny


def pack(G):
    items = []
    for n, p in parts.items():
        cut, eng, w, h = norm_sheet(p, G[n])
        for q in range(p.qty):
            items.append(dict(name=n, cut=cut, eng=eng, w=w, h=h))
    items.sort(key=lambda i: -(i['w'] * i['h']))
    sheets = []
    uw, uh = SHEET_W - 2 * MARGIN, SHEET_H - 2 * MARGIN
    for it in items:
        placed = False
        for sh in sheets:
            for rot in (False, True):
                w, h = (it['h'], it['w']) if rot else (it['w'], it['h'])
                bw, bh = w + GAP, h + GAP + LABEL
                for shelf in sh['shelves']:
                    if shelf['h'] >= bh and shelf['x'] + bw <= uw:
                        sh['items'].append((it, shelf['x'], shelf['y'], rot)); shelf['x'] += bw; placed = True; break
                if placed: break
            if placed: break
            for rot in (False, True):
                w, h = (it['h'], it['w']) if rot else (it['w'], it['h'])
                bw, bh = w + GAP, h + GAP + LABEL
                ny = sum(s['h'] for s in sh['shelves'])
                if ny + bh <= uh and bw <= uw:
                    sh['shelves'].append(dict(x=bw, y=ny, h=bh)); sh['items'].append((it, 0, ny, rot)); placed = True; break
            if placed: break
        if not placed:
            sheets.append(dict(shelves=[], items=[]))
            sh = sheets[-1]
            rot = it['w'] > uw or it['h'] > uh
            w, h = (it['h'], it['w']) if rot else (it['w'], it['h'])
            sh['shelves'].append(dict(x=w + GAP, y=0, h=h + GAP + LABEL)); sh['items'].append((it, 0, 0, rot))
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
    sheets = pack(G)
    comp = []
    allsheet = []
    for si, sh in enumerate(sheets, 1):
        svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{SHEET_W}mm" height="{SHEET_H}mm" viewBox="0 0 {SHEET_W} {SHEET_H}">',
               f'<rect width="{SHEET_W}" height="{SHEET_H}" fill="white" stroke="none"/>',
               '<g id="CORTE" fill="none" stroke="#ff0000" stroke-width="0.1">']
        eng, lab, cuts_nom = [], [], []
        import ezdxf
        doc = ezdxf.new('R2010', setup=True); doc.units = 4
        doc.layers.add('CORTE', color=1); doc.layers.add('GRABADO', color=5)
        msp = doc.modelspace()
        placed = []
        for it, x, y, rot in sh['items']:
            cut, en = place(it, x, y, rot)
            placed.append((it['name'], cut))
            ccut = cut.buffer(KERF / 2, join_style=MITRE)       # compensacion de kerf
            for r in rings(ccut):
                svg.append(f'<path d="{path_d(r, True)}"/>')
                msp.add_lwpolyline([(a, SHEET_H - b) for a, b in r], close=True, dxfattribs={'layer': 'CORTE'})
            for e in en:
                for r in rings(e):
                    eng.append(f'<path d="{path_d(r, False)}"/>')
                    msp.add_lwpolyline([(a, SHEET_H - b) for a, b in r], dxfattribs={'layer': 'GRABADO'})
            mnx, mny = cut.bounds[:2]
            lab.append(f'<text x="{mnx:.2f}" y="{mny-1.5:.2f}" font-size="2.8" font-family="sans-serif" fill="#0000ff" stroke="none">{it["name"]}</text>')
        svg.append('</g><g id="GRABADO" fill="none" stroke="#0000ff" stroke-width="0.1">' + ''.join(eng) + '</g>')
        svg.append(''.join(lab) + '</svg>')
        with open(os.path.join(OUT, f'hoja_{si}_corte.svg'), 'w') as f: f.write('\n'.join(svg))
        doc.saveas(os.path.join(OUT, f'hoja_{si}_corte.dxf'))
        comp.append(placed)
    # solapes entre piezas en la hoja (con kerf)
    rep = []
    for si, placed in enumerate(comp, 1):
        for (a, ga), (b, gb) in itertools.combinations(placed, 2):
            d = ga.distance(gb)
            if d < 2.0:
                rep.append(f'hoja {si}: {a} y {b} a {d:.2f} mm')
        for n, g in placed:
            mnx, mny, mxx, mxy = g.bounds
            if mnx < 5 or mny < 5 or mxx > SHEET_W - 5 or mxy > SHEET_H - 5:
                rep.append(f'hoja {si}: {n} fuera de margen')
    return len(sheets), rep


# --------------------------------------------------------------- previsualizaciones
def p3(p, u, v):
    x = {'X': (p.c + T / 2, u, v), 'Y': (u, p.c + T / 2, v), 'Z': (u, v, p.c + T / 2)}[p.kind]
    return x


def svg_path_from(poly, proj):
    d = ''
    for r in rings(poly):
        d += 'M' + ' L'.join('%.2f,%.2f' % proj(c) for c in r) + ' Z '
    return d


def color(t):   # t 0 (cerca) .. 1 (lejos)
    a = (176, 132, 82); b = (70, 44, 28)
    return '#%02x%02x%02x' % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def preview(G, mode, path):
    if mode == 'front':
        sx = lambda x, y, z: (x * 3, (H - z) * 3 + 20)
        vw, vh = W * 3, H * 3 + 40
    else:
        k1, k2 = 0.62, 0.42
        sx = lambda x, y, z: (x + k1 * y + 20, (H - z) + (-k2 * y) * -1 * 0 - k2 * y * -1 + 0)
        sx = lambda x, y, z: (1.9 * (x + k1 * y) + 20, 1.9 * ((H - z) + k2 * (D - y) * 0 + (-k2 * y)) + 1.9 * k2 * D + 20)
        vw, vh = 1.9 * (W + k1 * D) + 40, 1.9 * (H + k2 * D) + 40
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{vw:.0f}" height="{vh:.0f}" viewBox="0 0 {vw:.0f} {vh:.0f}">',
           f'<rect width="100%" height="100%" fill="#1b1612"/>']
    order = []
    for n, p in parts.items():
        if mode == 'obl' and n in ('techo_celosia', 'tapa_superior', 'nervio_techo_1', 'nervio_techo_2', 'lado_der'): continue
        if mode == 'front':
            depth = 1000 if p.kind == 'X' else p.c
            order.append((-depth, n))
        else:
            rank = {'lado_izq': -100, 'base_fondo': -90, 'nervio_piso_1': -80, 'nervio_piso_2': -80, 'piso': -70}.get(n, -p.c)
            order.append((rank, n))
    order.sort()
    for depth, n in order:
        p = parts[n]; g = G[n]
        if mode == 'front':
            if p.kind == 'Y':
                proj = (lambda c, p=p: sx(c[0], p.c, c[1]))
                t = min(1, p.c / 200.0)
                if n == 'fondo_ventana':
                    out.append(f'<path d="{svg_path_from(GLASS, proj)}" fill="#ffe3a0" fill-rule="evenodd"/>')
                out.append(f'<path d="{svg_path_from(g, proj)}" fill="{color(t)}" fill-rule="evenodd" stroke="#2a1a10" stroke-width="0.8"/>')
            else:
                bx = p.kind
                if bx == 'X': r = (p.c, 0, p.c + T, H)
                else: r = (T, p.c, W - T, p.c + T)
                if p.kind == 'X': pts = [(p.c, 0), (p.c + T, 0), (p.c + T, H), (p.c, H)]
                else: pts = [(T, p.c), (W - T, p.c), (W - T, p.c + T), (T, p.c + T)]
                if p.kind == 'X': pts = [sx(p.c, 0, 0), sx(p.c + T, 0, 0), sx(p.c + T, 0, H), sx(p.c, 0, H)]
                else: pts = [sx(T, 0, p.c), sx(W - T, 0, p.c), sx(W - T, 0, p.c + T), sx(T, 0, p.c + T)]
                out.append('<path d="M' + ' L'.join('%.1f,%.1f' % q for q in pts) + ' Z" fill="#5b3b25" stroke="#2a1a10" stroke-width="0.8"/>')
        else:
            proj = (lambda c, p=p: sx(*p3(p, c[0], c[1])))
            t = 0.2 if p.kind in 'XZ' else min(1, p.c / 200.0)
            if n == 'fondo_ventana':
                out.append(f'<path d="{svg_path_from(GLASS, proj)}" fill="#ffe3a0" fill-rule="evenodd"/>')
            out.append(f'<path d="{svg_path_from(g, proj)}" fill="{color(t)}" fill-opacity="0.96" fill-rule="evenodd" stroke="#2a1a10" stroke-width="0.7"/>')
    out.append('</svg>')
    with open(path, 'w') as f: f.write('\n'.join(out))


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    G = final_geoms()
    rep = run_checks(G)
    ns, rep2 = write_outputs(G)
    preview(G, 'front', os.path.join(OUT, 'vista_frontal.svg'))
    preview(G, 'obl', os.path.join(OUT, 'vista_capas.svg'))
    import cairosvg
    for n in ('vista_frontal', 'vista_capas'):
        cairosvg.svg2png(url=os.path.join(OUT, n + '.svg'), write_to=os.path.join(OUT, n + '.png'))
    for i in range(1, ns + 1):
        s = open(os.path.join(OUT, f'hoja_{i}_corte.svg')).read().replace('stroke-width="0.1"', 'stroke-width="0.4"')
        cairosvg.svg2png(bytestring=s.encode(), write_to=os.path.join(OUT, f'hoja_{i}_preview.png'), output_width=1800)
    print('hojas:', ns)
    print('piezas:', len(parts), '; kerf', KERF, '; T', T)
    print('--- verificaciones ---')
    for r in rep + rep2: print(r)
    print('OK' if not (rep or rep2) else f'{len(rep)+len(rep2)} avisos')
