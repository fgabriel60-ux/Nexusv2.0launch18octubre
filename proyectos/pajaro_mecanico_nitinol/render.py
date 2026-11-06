"""Animación (vistas superior y lateral) + diagrama de piezas + gráficas de verificación. Uso: python3 render.py [--rapido]"""
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, Circle
import imageio.v2 as imageio
import modelo as m

AQUI = Path(__file__).resolve().parent
P, D = m.P, m.derived()
LW, R = P['L_wire'], P['R_coil']
FPS = 25
VERDE, AZUL, ROJO, GRIS, ORO = '#5aa04a', '#2c5aa0', '#c0392b', '#555555', '#c8962e'

r2 = m.phase2()
r3 = m.phase3(r2['omega_f'])
S_CL, S_OP = D['s_closed'], r2['s_open']
T_ENR, T_LANZ, T_ABRE, T_RET, T_FIN = 0.8, 1.6, 1.4, 2.0, 0.8
ESC_FLAP = max(1.0, r3['t']/4.0)             # cámara lenta del aleteo si dura más de 4 s
T_ALETEO = r3['t']/ESC_FLAP
T_TOT = T_ENR + T_LANZ + T_ABRE + T_ALETEO + T_RET + T_FIN
ESC_ABRE = T_ABRE/r2['t']
lg = r2['log']
ease = lambda u: 3*u*u - 2*u**3

def phi_f_of_q(q):
    qs = np.linspace(0, q, 200)
    u = np.clip(qs/P['ramp'], 0, 1)
    g = (3*u**2 - 2*u**3)/(P['p_lead'])
    return 2*np.pi*np.trapezoid(g, qs)

def estado(t):
    e = dict(L=0.0, s=S_CL, theta=0.0, beta=0.0, phi_f=0.0, flap=0.0, fase='1 · ENROLLADO (reposo)', nota='', esc='', roll=1.0)
    if t < T_ENR: return e
    t -= T_ENR
    if t < T_LANZ:
        u = ease(t/T_LANZ); e.update(L=LW*u, fase='2 · LANZAMIENTO: el rollo se desenrolla (como matasuegras)', nota='la cabeza T sale disparada, el carrito K es arrastrado por los puntales', roll=1-u)
        return e
    e['L'], e['roll'] = LW, 0.0
    t -= T_LANZ
    if t < T_ABRE:
        tr = t/ESC_ABRE
        k = min(np.searchsorted(lg[:, 0], tr), len(lg)-1)
        q = float(np.interp(tr, lg[:, 0], lg[:, 1]))
        s = S_CL - q
        e.update(s=s, theta=float(m.theta_of_s(s)), phi_f=phi_f_of_q(q), fase='3 · CARRITO CORRE: puntales abren las alas, surcos giran el volante',
                 nota='el seguro de bola se rompe por inercia; resorte + alas empujan a K', esc='cámara lenta ×%d' % round(ESC_ABRE))
        return e
    e.update(s=S_OP, theta=P['theta_open'])
    t -= T_ABRE
    if t < T_ALETEO:
        tr = t*ESC_FLAP
        ph = float(np.interp(tr, r3['ts'], r3['phis'])) if tr <= r3['ts'][-1] else r3['phis'][-1]
        e.update(beta=float(m.beta_of_phi(ph)), phi_f=ph*P['G'], flap=ph/(2*np.pi), fase='4 · TOPE: embrague acopla el volante a la manivela → ALETEO',
                 nota='manivela + bielas baten ambas alas en fase (arriba/abajo)', esc=('cámara lenta ×%.1f' % ESC_FLAP) if ESC_FLAP > 1 else 'tiempo real')
        return e
    e['flap'] = r3['flaps']
    t -= T_ALETEO
    if t < T_RET:
        u = ease(t/T_RET)
        e.update(theta=P['theta_open']*(1-u), L=LW*(1-u), s=S_OP + (S_CL-S_OP)*u, roll=u, beta=float(m.beta_of_phi(r3['phis'][-1]))*(1-min(1, 3*u)),
                 fase='5 · CONTADOR LIBERA EL PESTILLO: el rollo de nitinol recoge todo', nota='el embudo de H cierra las alas y devuelve a K; el rollo recupera su forma por memoria')
        return e
    e.update(theta=0.0, L=0.0, roll=1.0, s=S_CL, fase='6 · ENROLLADO otra vez (listo para otro lanzamiento)')
    return e

def espiral(ax, cx, cz, frac, n=3):
    """rollo plano visto de lado: espiral de nitinol cuyo largo es frac*LW"""
    if frac <= 0.001: return
    L = LW*frac
    ang = np.linspace(0, L/R, 200)
    rr = R - 1.6*ang/(2*np.pi)
    for k, c in enumerate([GRIS, AZUL, AZUL]):
        off = (k-1)*0.9
        ax.plot(cx - (rr+off)*np.sin(ang), cz + (rr+off)*np.cos(ang) - R, color=c, lw=1.6, solid_capstyle='round')

def dibujar(e, size=(12.0, 6.6)):
    fig = plt.figure(figsize=size, dpi=100, facecolor='white')
    ax1 = fig.add_axes([0.02, 0.09, 0.47, 0.78]); ax2 = fig.add_axes([0.51, 0.09, 0.47, 0.78])
    for ax, tit in ((ax1, 'VISTA SUPERIOR (plano de las alas)'), (ax2, 'VISTA LATERAL (rollo, volante, manivela)')):
        ax.set_aspect('equal'); ax.set_xlim(-40, 150); ax.axis('off'); ax.text(-38, ax.get_ylim()[1] if False else 0, '', fontsize=1)
    ax1.set_ylim(-125, 125); ax2.set_ylim(-75, 100)
    ax1.text(-38, 116, 'VISTA SUPERIOR (plano de las alas)', fontsize=9, color=GRIS, weight='bold')
    ax2.text(-38, 92, 'VISTA LATERAL (rollo, volante, manivela)', fontsize=9, color=GRIS, weight='bold')
    L, th, be = e['L'], e['theta'], e['beta']
    xT = L
    # --- superior
    ax1.plot([0, xT], [0, 0], color=GRIS, lw=2.4)
    Lr = L
    for sg in (+1, -1):
        tip = (xT - Lr*np.cos(th), sg*Lr*np.sin(th)*np.cos(be))
        if Lr > 1:
            ax1.add_patch(Polygon([(xT, 0), tip, (xT - Lr*0.97, 0)], closed=True, fc=VERDE, ec='none', alpha=0.45 if th > 0.05 else 0.0))
            ax1.plot([xT, tip[0]], [0, tip[1]], color=AZUL, lw=1.8)
            # espinas de la costilla
            for f in np.linspace(0.15, 0.95, 8):
                px, py = xT - f*Lr*np.cos(th), sg*f*Lr*np.sin(th)*np.cos(be)
                ax1.plot([px, px - 3*np.cos(th) + sg*0*1], [py, py + sg*3.5], color=VERDE, lw=1.0) if th > 0.05 else None
        # puntal K -> costilla
        if th > 0 or e['s'] < S_CL + 1e-6:
            a = P['a']; Px, Py = xT - a*np.cos(th), sg*a*np.sin(th)*np.cos(be)
            xK = max(24.0, xT - e['s'])
            if L > S_CL - 1: ax1.plot([xK, Px], [0, Py], color=ORO, lw=1.2)
    xK = max(24.0, xT - e['s'])
    ax1.add_patch(Rectangle((xK-3, -3.2), 6, 6.4, fc=ORO, ec='black', lw=0.8))
    ax1.add_patch(Circle((xT, 0), 2.6, fc=ROJO, ec='black', lw=0.6))
    ax1.add_patch(Polygon([(-8, -9), (-8, 9), (6, 5), (6, -5)], closed=True, fc='#bbbbbb', ec='black', lw=0.8))  # H con embudo
    ax1.text(-8, -17, 'H (cola: rollo + pestillo)', fontsize=7, color=GRIS)
    cierre = LW - 1e-6 <= L and e['fase'][0] in '34'
    ax1.add_patch(Rectangle((-30, -6), 9, 12, fc=ROJO if cierre else '#6aa84f', ec='black', lw=0.6))
    ax1.text(-38, 10, 'pestillo', fontsize=7, color=GRIS)
    if e['flap'] > 0:
        ax1.add_patch(Rectangle((-38, -112), 70, 6, fc='white', ec=GRIS, lw=0.6))
        ax1.add_patch(Rectangle((-38, -112), 70*min(1, e['flap']/P['N_target']), 6, fc=ORO, ec='none'))
        ax1.text(-38, -104, 'contador de aleteos → libera pestillo', fontsize=7, color=GRIS)
    ax1.text(xT+3, 6, 'T', fontsize=8, color=ROJO)
    # --- lateral
    ax2.plot([0, xT], [0, 0], color=GRIS, lw=2.4)
    espiral(ax2, 0, 0, e['roll'])
    ax2.add_patch(Rectangle((-8, -R-6), 16, 7, fc='#bbbbbb', ec='black', lw=0.7)) if e['roll'] > 0.01 else None
    for sg, ls in ((1, '-'), (-1, '--')):
        if L > 1:
            tip = (xT - Lr*np.cos(th), Lr*np.sin(th)*np.sin(be))
            ax2.plot([xT, tip[0]], [0, tip[1]], color=AZUL, lw=1.3, ls=ls)
    xK2 = xK
    ax2.add_patch(Rectangle((xK2-3, -3.2), 6, 6.4, fc=ORO, ec='black', lw=0.8))
    if L >= LW - 1e-6:
        # tubo con surco helicoidal + volante + manivela en T
        tube = np.linspace(xT - 60, xT, 100)
        ax2.add_patch(Rectangle((xT-60, -3), 60, 6, fc='#dddddd', ec='black', lw=0.5, zorder=0))
        ax2.plot(tube, 3*np.sin(2*np.pi*(xT - tube)/P['p_lead'] - e['phi_f']), color=GRIS, lw=0.9)
        fx = xT + 6
        ax2.add_patch(Rectangle((fx-1.5, -13), 3, 26, fc=ORO, ec='black', lw=0.6))
        ax2.plot([fx], [11*np.cos(e['phi_f'])], 'o', color=ROJO, ms=3.5)
        ax2.text(fx-12, -20, 'volante', fontsize=7, color=GRIS)
        ph = e['flap']*2*np.pi
        pin = (xT + 14, P['z0_crank'] + P['r_crank']*np.sin(ph))
        ax2.plot([xT+14, xT+14], [P['z0_crank'], P['z0_crank']], 'x', color=GRIS, ms=3)
        ax2.add_patch(Circle((xT+14, P['z0_crank']), P['r_crank'], fill=False, ec=GRIS, lw=0.6, ls=':'))
        ax2.plot([xT+14, pin[0]], [P['z0_crank'], pin[1]], color=ROJO, lw=1.5)
        b = P['b_link']; ax2.plot([pin[0], xT - b*np.cos(th)], [pin[1], b*np.sin(th)*np.sin(be)], color=ROJO, lw=0.9)
        ax2.text(xT+10, 14, 'manivela', fontsize=7, color=ROJO)
    ax2.add_patch(Circle((xT, 0), 2.6, fc=ROJO, ec='black', lw=0.6))
    # --- textos
    fig.text(0.04, 0.955, 'Pájaro mecánico de nitinol · simulación (no probado físicamente)', fontsize=10.5, weight='bold')
    fig.text(0.04, 0.915, e['fase'], fontsize=10, color=AZUL)
    fig.text(0.04, 0.045, e['nota'], fontsize=8.5, color=GRIS)
    if e['esc']: fig.text(0.97, 0.955, e['esc'], fontsize=8.5, color=ROJO, ha='right')
    if e['flap'] > 0: fig.text(0.96, 0.045, 'aleteos: %.1f / %d    alas: %+.0f°…' % (e['flap'], P['N_target'], np.degrees(e['beta'])), fontsize=9, ha='right', color=GRIS)
    fig.text(0.04, 0.012, 'apertura θ = %.0f°   carrito s = %.0f mm   nitinol Ø%.2f (espina) / Ø%.2f (costillas)' % (np.degrees(th), e['s'], P['d_spine'], P['d_rib']), fontsize=7.5, color='#888888')
    fig.canvas.draw()
    img = np.asarray(fig.canvas.buffer_rgba())[:, :, :3].copy()
    plt.close(fig)
    return img

def animacion(rapido=False):
    n = int(T_TOT*FPS)
    frames = []
    for i in range(n):
        if rapido and i % 10: continue
        frames.append(dibujar(estado(i/FPS)))
    return frames

def figuras_extra():
    """diagrama de piezas (estado abierto) y gráficas de verificación"""
    e = estado(T_ENR + T_LANZ + T_ABRE + 0.1)
    fig = plt.figure(figsize=(13, 7.2), dpi=110, facecolor='white')
    ax = fig.add_axes([0.01, 0.07, 0.62, 0.86]); ax.set_aspect('equal'); ax.axis('off'); ax.set_xlim(-45, 150); ax.set_ylim(-125, 125)
    xT, th = LW, P['theta_open']
    ax.plot([0, xT], [0, 0], color=GRIS, lw=3)
    for sg in (1, -1):
        tip = (xT - LW*np.cos(th), sg*LW*np.sin(th))
        ax.add_patch(Polygon([(xT, 0), tip, (xT - LW*0.97, 0)], closed=True, fc=VERDE, ec='none', alpha=0.35))
        ax.plot([xT, tip[0]], [0, tip[1]], color=AZUL, lw=2)
        Px, Py = xT - P['a']*np.cos(th), sg*P['a']*np.sin(th)
        ax.plot([xT - e['s'], Px], [0, Py], color=ORO, lw=1.6)
    ax.add_patch(Rectangle((xT-60, -3), 60, 6, fc='#dddddd', ec='black', lw=0.6, zorder=0))
    tube = np.linspace(xT-60, xT, 100); ax.plot(tube, 3*np.sin(2*np.pi*(xT - tube)/P['p_lead']), color=GRIS, lw=0.9)
    ax.add_patch(Rectangle((xT - e['s'] - 3, -4), 6, 8, fc=ORO, ec='black', lw=0.8))
    ax.add_patch(Circle((xT, 0), 3, fc=ROJO, ec='black'))
    ax.add_patch(Polygon([(-8, -9), (-8, 9), (6, 5), (6, -5)], closed=True, fc='#bbbbbb', ec='black'))
    ax.add_patch(Rectangle((xT+5, -14), 3, 28, fc=ORO, ec='black'))
    ax.add_patch(Circle((xT+16, 3), 9, fill=False, ec=GRIS, ls=':'))
    ax.plot([xT+16, xT+16], [3, 12], color=ROJO, lw=1.6)
    ax.plot([xT+16, xT - 10*np.cos(th)], [12, 10*np.sin(th)], color=ROJO, lw=1.0)
    ax.add_patch(Rectangle((-30, -6), 9, 12, fc='#6aa84f', ec='black'))
    ax.add_patch(Circle((-18, -30), 24, fill=False, ec=AZUL, lw=2, ls='--'))
    N = [(-30, 6, 1, 'pestillo (se libera con el contador)'), (-18, -54, 2, 'rollo de 3 alambres NiTi (matasuegras)'), (-2, 9, 3, 'H: embudo de cierre'),
         (xT-30, 8, 4, 'tubo con surco helicoidal'), (xT - e['s'], 4, 5, 'carrito K (corredera de paraguas)'), (xT-40, 28, 6, 'puntales Ø0.5 (K → costilla)'),
         (xT-70, 70, 7, 'costilla = ala (NiTi Ø0.35)'), (xT+6, 14, 8, 'volante + embrague'), (xT+16, 13, 9, 'manivela'), (xT-8, 10, 10, 'biela a la costilla'),
         (xT, -4, 11, 'T: cabeza, raíz flexible de costillas'), (60, 0, 12, 'espina central NiTi Ø0.7 (con tope y detente)')]
    for x, y, n, _ in N:
        ax.add_patch(Circle((x, y+7 if y >= 0 else y-7), 4.2, fc='white', ec=ROJO, lw=1.2, zorder=5)); ax.text(x, y+7 if y >= 0 else y-7, str(n), ha='center', va='center', fontsize=8, color=ROJO, weight='bold', zorder=6)
    fig.text(0.02, 0.955, 'Diagrama de piezas — estado ABIERTO (vista superior, espina horizontal)', fontsize=12, weight='bold')
    fig.text(0.66, 0.90, 'Piezas', fontsize=11, weight='bold')
    for k, (_, _, n, t) in enumerate(N): fig.text(0.66, 0.86 - k*0.036, f'{n}  {t}', fontsize=9)
    fig.text(0.66, 0.40, 'Fases', fontsize=11, weight='bold')
    fases = ['1 enrollado  →  2 lanzamiento (desenrolla)', '3 K corre: abre alas + gira volante por surco', '4 tope: embrague → manivela → aleteo',
             '5 contador libera pestillo → recoil NiTi', '   embudo H cierra alas, K regresa', '6 enrollado, listo otra vez']
    for k, t in enumerate(fases): fig.text(0.66, 0.36 - k*0.036, t, fontsize=9)
    fig.text(0.66, 0.10, 'SIMULACIÓN · sin prototipo físico', fontsize=9, color=ROJO)
    fig.savefig(AQUI / 'diagrama_piezas.png'); plt.close(fig)

    fig, axs = plt.subplots(2, 3, figsize=(14, 7.5), dpi=100)
    s_ = np.linspace(S_OP-3, S_CL, 200)
    a0 = axs[0, 0]; a0.plot(s_, np.degrees(m.theta_of_s(s_)), color=AZUL); a0.axhline(80, color=ROJO, ls=':'); a0.set_xlabel('posición del carrito s (mm)'); a0.set_ylabel('apertura de ala θ (°)'); a0.set_title('Puntales: 0° → 80° (carrera %.0f mm)' % (S_CL - S_OP))
    a1 = axs[0, 1]; a1.plot(s_, m.drive_force(s_), color=ORO); a1.axhline(P['F_fric'], color=GRIS, ls=':'); a1.set_xlabel('s (mm)'); a1.set_ylabel('fuerza hacia T (N)'); a1.set_title('Empuje sobre K vs fricción (punteada)')
    a2 = axs[0, 2]; a2.plot(lg[:, 0]*1e3, lg[:, 2]); a2.set_xlabel('t (ms)'); a2.set_ylabel('velocidad de K (m/s)'); a2.set_title('Fase 3: K llega con %.2f m/s, volante %.0f rad/s' % (r2['v_end'], r2['omega_f']))
    a3 = axs[1, 0]; a3.plot(r3['ts'], np.degrees(r3['bs']), lw=0.8); a3.set_xlabel('t (s)'); a3.set_ylabel('ángulo de aleteo β (°)'); a3.set_title('Aleteo: %.0f° a +%.0f°, %.1f aleteos en %.1f s' % (r3['beta_min'], r3['beta_max'], r3['flaps'], r3['t']))
    a4 = axs[1, 1]; a4.plot(r3['ts'], r3['ws']/(2*np.pi)/1.0, color=ROJO); a4.set_xlabel('t (s)'); a4.set_ylabel('frecuencia de aleteo (Hz)'); a4.set_title('Frecuencia decae por aire + fricción')
    rc = m.recoil_check()
    a5 = axs[1, 2]; a5.bar(['recoil NiTi', 'cerrar alas\n+ resorte + fricción'], [rc['E_recoil']*1e3, rc['E_close']*1e3], color=[AZUL, ORO]); a5.set_ylabel('energía (mJ)'); a5.set_title('Reenrollado: margen ×%.1f' % rc['margen'])
    for a in axs.flat: a.grid(alpha=0.25)
    fig.suptitle('Verificación numérica (simulación)', fontsize=12, weight='bold'); fig.tight_layout()
    fig.savefig(AQUI / 'verificacion.png'); plt.close(fig)


if __name__ == '__main__':
    rapido = '--rapido' in sys.argv
    if '--extra' in sys.argv:
        figuras_extra(); print('figuras extra listas'); raise SystemExit
    fr = animacion(rapido)
    if rapido:
        out = AQUI / '_prev'; out.mkdir(exist_ok=True)
        for k, f in enumerate(fr): imageio.imwrite(out / f'f{k:02d}.png', f)
        print(len(fr), 'cuadros de prueba en', out)
    else:
        imageio.mimsave(AQUI / 'animacion_mecanismo.gif', fr, duration=1000/FPS, loop=0)
        imageio.mimsave(AQUI / 'animacion_mecanismo.mp4', fr, fps=FPS, codec='libx264', quality=7, macro_block_size=1)
        print('animación', len(fr), 'cuadros', T_TOT, 's')

