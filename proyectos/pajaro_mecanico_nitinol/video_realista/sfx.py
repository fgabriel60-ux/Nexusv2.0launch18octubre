"""SFX sintéticos (numpy) para el video del pájaro: whoosh, clic metálico, cliqueo/zumbido del aleteo, clic de cierre y pad musical suave.
Se usan desde armar.py: pista(eventos, duracion) -> np.ndarray estéreo float32 a 48 kHz."""
import numpy as np

SR = 48000
rng = np.random.default_rng(7)


def _env(n, a, r):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / max(r, 1e-4))


def _bp(x, f0, q=4):
    from scipy.signal import butter, sosfilt
    lo, hi = f0 / (1 + 1 / q), f0 * (1 + 1 / q)
    return sosfilt(butter(2, [lo, min(hi, SR / 2 - 100)], btype="band", fs=SR, output="sos"), x)


def whoosh(d=0.9, f1=300, f2=2500, vol=0.6):
    from scipy.signal import butter, sosfilt
    n = int(d * SR); x = rng.standard_normal(n)
    out = np.zeros(n); seg = 1024
    for i in range(0, n, seg):
        f = f1 + (f2 - f1) * np.sin(np.pi * i / n) ** 2
        out[i:i + seg] = _bp(x[max(0, i - 2048):i + seg], f, 2)[-len(out[i:i + seg]):]
    env = np.sin(np.pi * np.linspace(0, 1, n)) ** 1.5
    return vol * out * env / (np.abs(out).max() + 1e-9)


def clic(vol=0.5, f=(3200, 5100, 7400), r=0.025):
    n = int(0.12 * SR); t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * fi * t) * np.exp(-t / (r * (1 - 0.2 * k))) for k, fi in enumerate(f))
    s += 0.6 * rng.standard_normal(n) * np.exp(-t / 0.003)
    return vol * s / np.abs(s).max()


def aleteo(d, hz=2.6, vol=0.35):
    """zumbido del volante + cliqueo de trinquete + soplo de cada batido"""
    n = int(d * SR); t = np.arange(n) / SR
    zum = 0.25 * np.sin(2 * np.pi * 110 * t + 0.3 * np.sin(2 * np.pi * hz * t)) + 0.1 * np.sin(2 * np.pi * 220 * t)
    out = zum * (0.6 + 0.4 * np.sin(2 * np.pi * hz * t) ** 2)
    ck = clic(0.25, (4200, 6100), 0.01)
    for k in np.arange(0, d, 1 / (hz * 4)):           # 4 dientes por aleteo
        i = int(k * SR); out[i:i + len(ck)] += ck[:n - i]
    sop = whoosh(0.3, 200, 900, 0.5)
    for k in np.arange(0.05, d, 1 / hz):               # soplo de ala por batido
        i = int(k * SR); out[i:i + len(sop)] += sop[:n - i]
    fade = np.minimum(1, np.minimum(t / 0.15, (d - t) / 0.3))
    return vol * out * fade


def pad(d, vol=0.08):
    t = np.arange(int(d * SR)) / SR
    notas = [196.0, 246.94, 293.66, 369.99]           # Sol maj7 suave
    s = sum(np.sin(2 * np.pi * f * t + 0.2 * np.sin(2 * np.pi * 0.2 * t + i)) for i, f in enumerate(notas))
    fade = np.minimum(1, np.minimum(t / 1.5, (d - t) / 2.0))
    return vol * s / len(notas) * fade


def pista(eventos, duracion, musica=True):
    """eventos: lista de (segundo, tipo, kw)"""
    n = int(duracion * SR)
    L = np.zeros(n); R = np.zeros(n)
    for seg, tipo, kw in eventos:
        s = {"whoosh": whoosh, "clic": clic, "aleteo": aleteo}[tipo](**kw)
        i = int(seg * SR); m = min(len(s), n - i)
        if m <= 0:
            continue
        L[i:i + m] += s[:m]; R[i:i + m] += s[:m]
    if musica:
        p = pad(duracion); L += p; R += p * 0.95
    st = np.stack([L, R], 1)
    return (0.9 * st / max(1.0, np.abs(st).max())).astype(np.float32)
