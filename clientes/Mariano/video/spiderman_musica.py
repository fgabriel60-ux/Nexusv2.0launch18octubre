"""Beat propio (sin derechos de terceros) para el gancho estilo Spiderman: 124 BPM, Am–F–C–G. Intro filtrada mientras Mariano habla, riser de 1 compás
y DROP justo en la transición al dron (como la referencia), beat completo con bajo, palmas y hats, y cola al final.
Uso: from spiderman_musica import beat; beat(ruta_wav, t_drop, total)"""
import numpy as np
import wave

SR = 44100
BPM = 124
NOTAS = {'A': 57, 'F': 53, 'C': 48, 'G': 55}   # raíces MIDI
ACORDES = [('A', [0, 3, 7]), ('F', [0, 4, 7]), ('C', [0, 4, 7]), ('G', [0, 4, 7])]


def hz(m): return 440 * 2 ** ((m - 69) / 12)


def env(n, a=0.005, r=0.2):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / r)


def kick(n=int(0.45 * SR)):
    t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) * 1.0


def clap(n=int(0.25 * SR), rng=np.random.default_rng(1)):
    t = np.arange(n) / SR
    ruido = rng.standard_normal(n)
    ruido = np.convolve(ruido, np.ones(4) / 4, 'same') - np.convolve(ruido, np.ones(40) / 40, 'same')
    return ruido * (np.exp(-t * 25) + 0.6 * np.exp(-((t - 0.012) % 0.011) * 300) * (t < 0.035)) * 0.5


def hat(n=int(0.06 * SR), rng=np.random.default_rng(2)):
    r = rng.standard_normal(n); r = r - np.convolve(r, np.ones(6) / 6, 'same')
    return r * np.exp(-np.arange(n) / SR * 60) * 0.18


def saw(f, n, det=(0, 0.11, -0.09)):
    t = np.arange(n) / SR
    return sum(2 * ((t * f * 2 ** (d / 12)) % 1) - 1 for d in det) / len(det)


def lowpass(x, alfa):
    y = np.empty_like(x); acc = 0.0
    if np.isscalar(alfa): alfa = np.full(len(x), alfa)
    for i in range(len(x)):
        acc += alfa[i] * (x[i] - acc); y[i] = acc
    return y


def beat(ruta, t_drop, total):
    n = int(total * SR); mix = np.zeros(n + SR); paso = 60 / BPM
    # el drop cae en un tiempo fuerte: la rejilla arranca en t_drop
    t0 = t_drop - np.ceil(t_drop / (4 * paso)) * 4 * paso
    def pon(x, t, g=1.0):
        i = int(t * SR)
        if 0 <= i < len(mix):
            m = min(len(x), len(mix) - i); mix[i:i + m] += g * x[:m]
    pad = np.zeros_like(mix); bajo = np.zeros_like(mix)
    compas = 0; t = t0
    while t < total + 4 * paso:
        raiz, inter = ACORDES[compas % 4]
        nc = int(4 * paso * SR)
        acorde = sum(saw(hz(NOTAS[raiz] + 12 + k), nc) for k in inter) / 3
        acorde *= np.minimum(1, np.arange(nc) / (0.05 * SR)) * np.minimum(1, (nc - np.arange(nc)) / (0.08 * SR))
        i = int(t * SR)
        if i + nc > 0:
            a, b = max(0, -i), min(nc, len(pad) - i)
            if a < b: pad[i + a:i + b] += acorde[a:b] * 0.22
        for k in range(8):   # bajo en corcheas, sólo después del drop
            tb = t + k * paso / 2
            if tb >= t_drop and tb < total:
                nb = int(paso / 2 * SR * 0.9)
                x = (saw(hz(NOTAS[raiz] - 12 + (12 if k in (3, 7) else 0)), nb, (0,)) * env(nb, 0.003, 0.12))
                j = int(tb * SR); m = min(nb, len(bajo) - j); bajo[j:j + m] += x[:m] * 0.5
        for k in range(4):
            tk = t + k * paso
            if tk >= t_drop and tk < total - 0.4: pon(kick(), tk, 0.95)
            elif 0 <= tk < t_drop - 4 * paso and k in (0, 2): pon(kick(), tk, 0.35)   # pulso suave bajo la voz
            if tk >= t_drop and k in (1, 3) and tk < total - 0.4: pon(clap(), tk, 0.8)
            for h in (0.5,):
                th = tk + h * paso
                if th >= t_drop and th < total - 0.4: pon(hat(), th, 1.0)
        compas += 1; t += 4 * paso
    # pad filtrado antes del drop (se abre en el riser), abierto después
    ts = np.arange(len(pad)) / SR
    corte = np.where(ts < t_drop - 4 * paso, 0.025, np.where(ts < t_drop, 0.025 + 0.2 * (ts - (t_drop - 4 * paso)) / (4 * paso), 0.3))
    pad = lowpass(lowpass(pad, corte), corte)
    pad *= np.where(ts < t_drop, 1.3, 0.9)
    bajo = lowpass(bajo, 0.08)
    # riser de ruido 1 compás antes del drop + golpe/impacto en el drop
    nr = int(4 * paso * SR); r = np.random.default_rng(3).standard_normal(nr)
    r = lowpass(r, np.linspace(0.02, 0.6, nr)) * np.linspace(0, 1, nr) ** 2 * 0.35
    pon(r, t_drop - 4 * paso)
    pon(kick() * 1.3, t_drop)
    mix += pad + bajo
    mix = mix[:n]
    fade = int(1.2 * SR); mix[-fade:] *= np.linspace(1, 0, fade)
    mix = np.tanh(mix * 1.1) * 0.8
    est = np.stack([mix, mix], 1)
    with wave.open(str(ruta), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((est * 32767).astype('<i2').tobytes())


if __name__ == '__main__':
    import sys
    beat(sys.argv[1], float(sys.argv[2]), float(sys.argv[3]))
