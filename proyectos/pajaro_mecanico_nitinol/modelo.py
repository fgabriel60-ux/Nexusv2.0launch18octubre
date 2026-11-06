"""Pájaro mecánico de nitinol: modelo cinemático + dinámico 1D (SIMULACIÓN, no probado físicamente).
Unidades: mm, N, kg, s en geometría; SI en dinámica (se convierte dentro)."""
import numpy as np

P = dict(
    E=50e3,            # N/mm² módulo NiTi austenita (supuesto 40-75 GPa)
    d_spine=0.7, d_rib=0.35,   # mm
    L_wire=120.0,      # mm longitud de los 3 alambres desenrollados
    R_coil=24.0,       # mm radio del rollo (deformación = d/2R)
    a=25.0, l=26.0,    # mm: punto de unión del puntal en la costilla / largo del puntal
    L_flex=30.0,       # mm: longitud de la zona flexible en la raíz de la costilla
    theta_rest=np.radians(70), theta_open=np.radians(80), theta_start=np.radians(5),   # ángulo de reposo (termofijado) y tope de apertura
    m_K=6e-3, F_spring=0.5, F_fric=0.03,     # carrito (kg), resorte de precarga (N), fricción (N)
    v_trig=0.3,        # m/s velocidad del carrito al disparar el seguro
    I_f=3.0e-6, p_lead=40.0, ramp=12.0,      # volante kg·m², paso del surco mm/rev, rampa de entrada del surco mm
    tau_b=1.5e-5, G=6.0, I_c=1e-7,             # par de rodamiento N·m, reducción volante→manivela, inercia de manivela
    r_crank=9.0, b_link=10.0, z0_crank=3.0,   # radio de manivela, distancia de unión de biela en costilla, sesgo del eje (mm)
    m_rib=0.5e-3, chord=0.025, cd=1.4, rho=1.2,  # costilla+membrana (kg), cuerda (m)
    N_target=12,
)

def derived(p=P):
    d = {}
    d['I_rib'] = np.pi*p['d_rib']**4/64.0           # mm⁴
    d['I_spine'] = np.pi*p['d_spine']**4/64.0
    d['k_f'] = p['E']*d['I_rib']/p['L_flex']        # N·mm/rad  rigidez de la raíz flexible
    d['s_closed'] = float(s_of_theta(p['theta_start'], p))   # el cerrado exacto (θ=0) es singular; las costillas arrancan a ~5°
    return d

def theta_of_s(s, p=P):
    a, l = p['a'], p['l']
    c = (a*a + s*s - l*l)/(2*a*np.maximum(s, 1e-9))
    return np.arccos(np.clip(c, -1, 1))

def s_of_theta(th, p=P):
    a, l = p['a'], p['l']
    return a*np.cos(th) + np.sqrt(l*l - (a*np.sin(th))**2)

def dtheta_ds(s, p=P, h=1e-4):
    return (theta_of_s(s+h, p) - theta_of_s(s-h, p))/(2*h)

def drive_force(s, p=P, k_f=None):
    """Fuerza (N) sobre el carrito hacia la cabeza por resorte + alas que tienden a abrirse (trabajo virtual)."""
    k_f = k_f if k_f is not None else derived(p)['k_f']
    th = theta_of_s(s, p)
    f_w = 2*k_f*(p['theta_rest'] - th)*np.abs(dtheta_ds(s, p))     # N·mm/rad * rad/mm = N
    return p['F_spring'] + f_w

def phase2(p=P, dt=2e-6):
    """Carrito recorre de s_closed a s_open: abre alas y gira volante por el surco (rampa de entrada). Devuelve dict."""
    D = derived(p)
    s_open = float(s_of_theta(p['theta_open'], p))
    q_end = D['s_closed'] - s_open
    g = lambda q: (1.0/(p['p_lead']*1e-3))*(3*(min(q/p['ramp'],1))**2 - 2*(min(q/p['ramp'],1))**3)   # rev/m
    gp = lambda q: (1.0/(p['p_lead']*1e-3))*(6*(q/p['ramp'])*(1-q/p['ramp'])/(p['ramp']*1e-3)) if q < p['ramp'] else 0.0
    q, v, t, phi = 0.0, p['v_trig'], 0.0, 0.0
    log = []
    while q < q_end:
        meff = p['m_K'] + p['I_f']*(2*np.pi*g(q))**2
        dmeff = 2*p['I_f']*(2*np.pi)**2*g(q)*gp(q)
        s = D['s_closed'] - q
        F = drive_force(s, p, D['k_f']) - p['F_fric'] - p['tau_b']*2*np.pi*g(q)
        a = (F - 0.5*dmeff*v*v)/meff
        v += a*dt; q += v*dt*1e3   # q en mm
        t += dt
        if v <= 0: return dict(ok=False, reason='el carrito se detiene antes del tope', q=q, t=t)
        if int(round(t/dt)) % 500 == 0: log.append((t, q, v, 2*np.pi*g(q)*v))
        if t > 0.5: return dict(ok=False, reason='timeout')
    omega = 2*np.pi*g(q_end)*v
    return dict(ok=True, t=t, v_end=v, omega_f=omega, E_fly=0.5*p['I_f']*omega**2, s_open=s_open, q_end=q_end, log=np.array(log))


def beta_of_phi(phi, p=P):
    """Ángulo de aleteo (rad, + = alas arriba) por manivela: biela vertical a distancia b de la raíz."""
    return np.arctan2(p['z0_crank'] + p['r_crank']*np.sin(phi), p['b_link'])

def dbeta_dphi(phi, p=P):
    z = p['z0_crank'] + p['r_crank']*np.sin(phi); b = p['b_link']
    return (p['r_crank']*np.cos(phi)/b)/(1 + (z/b)**2)

def flap_inertia(phi, p=P):
    return p['I_f']*p['G']**2 + p['I_c'] + 2*(p['m_rib']*(p['L_wire']*1e-3)**2/3)*dbeta_dphi(phi, p)**2

def phase3(omega_f, p=P, dt=1e-4, t_max=20.0):
    """Aleteo: volante -> (G) -> manivela -> bielas -> alas. Lagrange 1 GDL con resorte flexible, aire y fricción."""
    D = derived(p)
    k_f = D['k_f']*1e-3                    # N·m/rad
    L = p['L_wire']*1e-3
    c_a = 0.5*p['rho']*p['cd']*p['chord']*L**4/4     # N·m·s² por ala (arrastre cuadrático)
    phi = 0.0
    J0 = flap_inertia(0.0, p)
    w = p['I_f']*p['G']**2*(omega_f/p['G'])/J0      # acople plástico del embrague (conserva momento)
    t, E0 = 0.0, 0.5*J0*w*w
    phi_end = 2*np.pi*p['N_target']
    ts, ws, bs, ph = [], [], [], []
    def acc(phi, w):
        J = flap_inertia(phi, p)
        h = 1e-5
        dJ = (flap_inertia(phi+h, p) - flap_inertia(phi-h, p))/(2*h)
        b = beta_of_phi(phi, p); db = dbeta_dphi(phi, p)
        Q = -2*k_f*b*db                                            # resorte de flexión (ambas alas)
        bd = db*w
        Q += -2*c_a*abs(bd)*bd*db                                  # arrastre aerodinámico
        Q += -p['tau_b']*p['G']*np.sign(w)                         # rodamiento del volante reflejado
        return (Q - 0.5*dJ*w*w)/J
    n = 0
    while phi < phi_end and t < t_max:
        k1p, k1w = w, acc(phi, w)
        k2p, k2w = w + .5*dt*k1w, acc(phi + .5*dt*k1p, w + .5*dt*k1w)
        k3p, k3w = w + .5*dt*k2w, acc(phi + .5*dt*k2p, w + .5*dt*k2w)
        k4p, k4w = w + dt*k3w, acc(phi + dt*k3p, w + dt*k3w)
        phi += dt*(k1p + 2*k2p + 2*k3p + k4p)/6
        w += dt*(k1w + 2*k2w + 2*k3w + k4w)/6
        t += dt
        if n % 25 == 0: ts.append(t); ws.append(w); bs.append(beta_of_phi(phi, p)); ph.append(phi)
        n += 1
        if w < 2*np.pi*0.7: break      # < 0.7 Hz se considera detenido
    return dict(t=t, flaps=phi/(2*np.pi), reached=bool(phi >= phi_end), w_end=w, ts=np.array(ts), ws=np.array(ws), bs=np.array(bs),
                phis=np.array(ph), f0=(ws[0]/(2*np.pi) if ws else 0.0), E0=E0, c_a=c_a,
                beta_max=float(np.degrees(beta_of_phi(np.pi/2, p))), beta_min=float(np.degrees(beta_of_phi(-np.pi/2, p))))

def recoil_check(p=P):
    D = derived(p)
    kappa = 1.0/p['R_coil']
    F_c = 0.5*p['E']*D['I_spine']*kappa**2                     # N: fuerza constante del rollo de la espina
    eps_coil = p['d_spine']/(2*p['R_coil'])
    eps_flex = p['d_rib']*p['theta_rest']/(2*p['L_flex'])
    E_recoil = F_c*p['L_wire']*1e-3
    E_wings = D['k_f']*1e-3*(p['theta_rest']**2)               # J: cerrar ambas alas desde el reposo (k·θ²)
    E_spring = p['F_spring']*(D['s_closed'] - float(s_of_theta(p['theta_open'], p)))*1e-3
    E_fric = p['F_fric']*p['L_wire']*1e-3*2
    tot = E_wings + E_spring + E_fric
    F_hold = float(drive_force(D['s_closed'], p))
    F_trig = p['m_K']*(3.0**2/(2*1e-3))          # N: inercia de K al frenar T de 3 m/s en 1 mm
    return dict(F_hold=F_hold, F_trig=F_trig, F_coil=F_c, eps_coil=eps_coil, eps_flex=eps_flex, E_recoil=E_recoil, E_close=tot, margen=E_recoil/tot, E_wings=E_wings, E_spring=E_spring)

if __name__ == '__main__':
    D = derived()
    r2 = phase2()
    print('derivados', {k: round(float(v), 4) for k, v in D.items()})
    print('fase2', {k: (round(float(v), 4) if not isinstance(v, (str, np.ndarray)) else v) for k, v in r2.items() if k != 'log'})
    if r2['ok']:
        r3 = phase3(r2['omega_f'])
        print('fase3 aleteos', round(r3['flaps'], 2), 'alcanzó N:', r3['reached'], 't=%.2fs' % r3['t'], 'f0=%.1f Hz' % r3['f0'], 'E0=%.4f J' % r3['E0'], 'beta', r3['beta_min'], r3['beta_max'])
    print('recoil', {k: round(float(v), 4) for k, v in recoil_check().items()})
