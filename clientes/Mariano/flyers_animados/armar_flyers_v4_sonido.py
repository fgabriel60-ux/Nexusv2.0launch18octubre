"""Mariano · flyers animados v4: SOLO re-mezcla de audio sobre el video de v3 (video copiado sin recodificar).
Efectos sintéticos (numpy) con el carácter de un reel de referencia de SFX (clics secos y brillantes, ding limpio, riser metálico,
whoosh con golpe, impacto con cola grave). El audio del reel se usó solo para analizar; no se incrusta nada de él.
Tiempos tomados de armar_flyers_v2.py (entrada de cada elemento de texto y destello del precio).
Uso: python3 armar_flyers_v4_sonido.py"""
import subprocess, wave
from pathlib import Path
import numpy as np
import imageio_ffmpeg
from scipy import signal

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
MUSICA = AQUI.parents[1] / 'XV' / 'musica_suave_s7.wav'
SR = 44100
FIN = 7.0
OUT = AQUI / 'v4'; OUT.mkdir(exist_ok=True)
PICO_OBJ = 10 ** (-2.5 / 20)      # pico antes de AAC; el AAC puede pasarse ~1 dB, queda < -1 dBFS
MUSICA_VOL = 0.30                 # música baja; los SFX mandan


def ff(a, **k):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, **k)
    if r.returncode: raise SystemExit(r.stderr[-2000:])
    return r.stdout


def _t(dur): return np.arange(int(SR * dur)) / SR
def _rng(s): return np.random.default_rng(s)
def _hp(x, f, o=2): return signal.sosfilt(signal.butter(o, f, 'hp', fs=SR, output='sos'), x)
def _lp(x, f, o=2): return signal.sosfilt(signal.butter(o, f, 'lp', fs=SR, output='sos'), x)
def _bp(x, f1, f2, o=2): return signal.sosfilt(signal.butter(o, [f1, f2], 'bp', fs=SR, output='sos'), x)


# ---------- generadores (cada uno devuelve mono float, con su "punto de impacto" en segundos) ----------
def camera_click(seed=1):
    """Obturador seco: dos transitorios brillantes (~6-8 kHz, ~25 ms) separados 45 ms, cuerpo mecánico corto."""
    n = int(SR * 0.16); y = np.zeros(n); r = _rng(seed)
    for off, amp in ((0.0, 1.0), (0.048, 0.65)):
        m = int(SR * 0.03); tt = np.arange(m) / SR
        c = _bp(r.standard_normal(m), 3500, 10000) * np.exp(-tt * 190)
        c += 0.5 * np.sin(2 * np.pi * 1700 * tt) * np.exp(-tt * 260)   # golpecito mecánico
        i = int(off * SR); y[i:i + m] += c * amp
    return y / np.abs(y).max() * 0.8


def mouse_click(seed=2):
    """Clic de mouse suave: un 'tic' corto, centroide ~4-5 kHz, muy poca energía grave."""
    m = int(SR * 0.05); tt = np.arange(m) / SR; r = _rng(seed)
    c = _bp(r.standard_normal(m), 2500, 7500) * np.exp(-tt * 330) + 0.6 * np.sin(2 * np.pi * 2300 * tt) * np.exp(-tt * 420)
    return c / np.abs(c).max() * 0.45


def ding(f=1318.5, dur=1.1):
    """Ding limpio tipo campanita: fundamental + parciales inarmónicos suaves, ataque ~2 ms, caída ~0.5 s."""
    tt = _t(dur)
    y = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 5.5)
    y += 0.35 * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt * 9)
    y += 0.15 * np.sin(2 * np.pi * f * 5.4 * tt) * np.exp(-tt * 18)
    y *= np.minimum(tt / 0.002, 1)
    return y / np.abs(y).max() * 0.65


def riser_metalico(dur=0.45, seed=3):
    """Riser corto: ruido filtrado paso-banda cuyo centro sube 700→7000 Hz + tono metálico (FM) ascendente, crescendo y corte seco."""
    n = int(SR * dur); u = np.linspace(0, 1, n); r = _rng(seed)
    ruido = r.standard_normal(n); y = np.zeros(n); blk = 512
    for i in range(0, n, blk):   # barrido por bloques con solape (filtro con estado propio por bloque)
        fc = 700 * (10 ** (u[min(i + blk // 2, n - 1)]))   # 700 → 7000
        seg = _bp(ruido[i:i + blk], fc * 0.7, min(fc * 1.4, 18000), 2)
        y[i:i + blk] = seg[:min(blk, n - i)]
    y /= np.abs(y).max()
    f = 500 * (1 + 5 * u ** 1.6); ph = 2 * np.pi * np.cumsum(f) / SR
    metal = np.sin(ph + 2.2 * np.sin(ph * 1.41)) * 0.5
    z = (0.8 * y + 0.35 * metal) * (u ** 2.2)
    z *= np.minimum((n - np.arange(n)) / (0.008 * SR), 1)       # corte seco al final (justo antes del evento)
    return z / np.abs(z).max() * 0.55


def punch_whoosh(dur=0.5, lead=0.22, seed=4):
    """Whoosh ascendente (ruido con paso-banda que sube y cae) que termina en un 'punch' grave (golpe 90→50 Hz).
    lead = segundos desde el inicio hasta el golpe."""
    n = int(SR * dur); u = np.linspace(0, 1, n); r = _rng(seed)
    nz = r.standard_normal(n); y = np.zeros(n); blk = 512
    for i in range(0, n, blk):
        uu = min(u[min(i + blk // 2, n - 1)] * dur / lead, 1)
        fc = 400 + 5000 * uu ** 1.5
        seg = _bp(nz[i:i + blk], fc * 0.6, min(fc * 1.6, 16000), 2)
        y[i:i + blk] = seg[:min(blk, n - i)]
    y /= np.abs(y).max(); tt = np.arange(n) / SR
    env = np.where(tt < lead, (tt / lead) ** 2.0, np.exp(-(tt - lead) * 14))
    w = y * env * 0.55
    k = int(lead * SR); m = n - k; tk = np.arange(m) / SR
    thump = np.sin(2 * np.pi * np.cumsum(50 + 60 * np.exp(-tk * 30)) / SR) * np.exp(-tk * 11) * 0.8
    thump *= np.minimum(tk / 0.003, 1)
    w[k:] += thump
    return w / np.abs(w).max() * 0.7


def impacto(dur=2.0, seed=5):
    """Impacto cinematográfico: golpe seco + sub 55→38 Hz con cola larga (~1.5 s) + ráfaga de ruido grave que cae rápido."""
    tt = _t(dur); r = _rng(seed)
    sub = np.sin(2 * np.pi * np.cumsum(38 + 40 * np.exp(-tt * 9)) / SR) * np.exp(-tt * 2.6)
    cuerpo = np.sin(2 * np.pi * 96 * tt) * np.exp(-tt * 7) * 0.4
    ruido = _lp(r.standard_normal(len(tt)), 1800) * np.exp(-tt * 14) * 0.5
    clic = _bp(r.standard_normal(len(tt)), 2000, 9000) * np.exp(-tt * 120) * 0.25
    y = (sub + cuerpo + ruido + clic) * np.minimum(tt / 0.002, 1)
    y *= np.minimum((dur - tt) / 0.3, 1)
    return y / np.abs(y).max() * 0.85


# ---------- mezcla ----------
def poner(pista, s, t, ganancia=1.0, pan=0.0):
    """Suma s (mono) en pista estéreo (n,2) en el segundo t; pan -1..1 (ley de igual potencia)."""
    i = int(round(t * SR)); a = max(0, -i); s = s[a:]; i = max(i, 0)
    s = s[:max(0, len(pista) - i)]
    th = (pan + 1) * np.pi / 4
    pista[i:i + len(s), 0] += s * ganancia * np.cos(th); pista[i:i + len(s), 1] += s * ganancia * np.sin(th)


def musica():
    raw = ff(['-i', str(MUSICA), '-t', str(FIN), '-ar', str(SR), '-ac', '2', '-f', 'f32le', '-'])
    m = np.frombuffer(raw, '<f4').reshape(-1, 2).copy()
    out = np.zeros((int(SR * FIN), 2)); out[:min(len(m), len(out))] = m[:len(out)]
    tt = np.arange(len(out)) / SR
    out *= np.minimum(tt / 0.5, 1)[:, None] * np.minimum((FIN - tt) / 1.0, 1)[:, None]
    return out * MUSICA_VOL


def construir(eventos):
    """eventos: [(segundo_del_evento_visual, tipo, ganancia, pan)]. El riser y el punch_whoosh terminan/golpean en el segundo indicado."""
    sfx = np.zeros((int(SR * FIN), 2))
    for t, k, g, pan in eventos:
        if k == 'camara': poner(sfx, camera_click(), t + 0.01, g, pan)
        elif k == 'mouse': poner(sfx, mouse_click(), t + 0.01, g, pan)
        elif k == 'ding': poner(sfx, ding(), t, g, pan)
        elif k == 'riser': poner(sfx, riser_metalico(), t - 0.45, g, pan)
        elif k == 'punch': poner(sfx, punch_whoosh(), t - 0.22, g, pan)
        elif k == 'impacto': poner(sfx, impacto(), t, g, pan)
    mix = musica() + sfx
    pico = np.abs(mix).max()
    mix *= PICO_OBJ / pico        # normaliza (nunca amplifica de más: la música baja y los SFX dominan el pico)
    return mix, pico


def escribir_wav(x, ruta):
    with wave.open(str(ruta), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype('<i2').tobytes())


def render(nombre, eventos):
    mix, pico = construir(eventos)
    wav = OUT / f'audio_{nombre}_v4.wav'; escribir_wav(mix, wav)
    v3 = AQUI / f'Mariano_flyer_{nombre}_v3.mp4'; salida = AQUI / f'Mariano_flyer_{nombre}_v4.mp4'
    ff(['-i', str(v3), '-i', str(wav), '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k',
        '-t', str(FIN), '-movflags', '+faststart', str(salida)])
    print(salida.name, salida.stat().st_size // 1024, 'KB', f'(pico previo a normalizar {20*np.log10(pico):.1f} dBFS)')


# Eventos = tiempos de entrada reales de armar_flyers_v2.py (fade-in del texto empieza ahí); destello = cierre de la reveladora del precio.
EV_BENJAMINA = [
    (0.10, 'punch', 0.9, 0.0),                      # entra titular: whoosh con golpe
    (0.10, 'camara', 0.9, -0.2),                    # titular
    (0.60, 'camara', 0.8, 0.2),                     # logo
    (1.00, 'riser', 0.8, 0.0),                      # riser corto que termina cuando entra el precio
    (1.00, 'ding', 0.8, 0.0),                       # precio
    (1.25, 'impacto', 0.95, 0.0),                   # destello = cierre de la reveladora del precio
    (1.80, 'mouse', 1.0, 0.25),                     # chips
    (2.20, 'mouse', 0.9, -0.25),                    # pie
]
EV_BUGAMBILIA = [
    (0.10, 'punch', 0.8, 0.0),                      # primera entrada (lagsa + restr)
    (0.10, 'mouse', 0.9, -0.3),                     # lagsa
    (0.10, 'mouse', 0.7, 0.3),                      # restr (leve desfase de pan; mismo instante visual)
    (0.25, 'camara', 0.8, 0.0),                     # logo
    (0.55, 'camara', 0.8, -0.2),                    # globo1
    (0.95, 'camara', 0.8, 0.2),                     # globo2
    (1.35, 'mouse', 0.9, -0.3),                     # barraL
    (1.35, 'mouse', 0.7, 0.3),                      # barraR
    (1.70, 'riser', 0.8, 0.0),                      # riser corto antes del precio
    (1.70, 'ding', 0.8, 0.0),                       # precio
    (1.95, 'impacto', 0.95, 0.0),                   # destello = cierre de la reveladora del precio
    (2.20, 'mouse', 0.9, 0.0),                      # pie
]


if __name__ == '__main__':
    render('Benjamina', EV_BENJAMINA)
    render('Bugambilia', EV_BUGAMBILIA)
