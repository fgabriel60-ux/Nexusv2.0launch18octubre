"""Sonidos suaves para la tarjeta animada de Cinthia (12 s): colchón cálido, brillo al revelarse el logo, campanitas en el nombre
y al florecer la peonía, toques suaves por servicio y un «ding» en el botón de WhatsApp. Sale tarjeta/sonidos_tarjeta.wav"""
import wave
import numpy as np
from armar_logo import AQUI

SR, DUR = 44100, 12.0
N = int(SR * DUR); t = np.arange(N) / SR
mix = np.zeros((N, 2))


def nota(f):  # La4 = 440
    return 440 * 2 ** ((f - 69) / 12)


def campana(t0, midi, vol=0.18, dec=1.8, pan=0.0):
    n = int(SR * 3); tt = np.arange(n) / SR; f = nota(midi)
    s = (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt * 4) + 0.2 * np.sin(2 * np.pi * f * 5.4 * tt) * np.exp(-tt * 8))
    s *= np.exp(-tt / dec * 2.2) * np.minimum(1, tt / 0.004) * vol
    a = int(t0 * SR); b = min(N, a + n); s = s[:b - a]
    mix[a:b, 0] += s * (1 - pan) * 0.7; mix[a:b, 1] += s * (1 + pan) * 0.7


def pluck(t0, midi, vol=0.08, pan=0.0):
    n = int(SR * 1.2); tt = np.arange(n) / SR; f = nota(midi)
    s = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt)) * np.exp(-tt * 5) * np.minimum(1, tt / 0.003) * vol
    a = int(t0 * SR); b = min(N, a + n); s = s[:b - a]
    mix[a:b, 0] += s * (1 - pan); mix[a:b, 1] += s * (1 + pan)


def brillo(t0, dur, vol=0.05, sube=True):
    """Ruido suave filtrado que sube/baja (aire, como un barrido)."""
    n = int(SR * dur); rng = np.random.default_rng(3); r = rng.standard_normal(n)
    k = 60; r = np.convolve(r, np.ones(k) / k, mode='same') * 4; r = r - np.convolve(r, np.ones(600) / 600, mode='same')
    env = np.sin(np.pi * np.linspace(0, 1, n)) ** 2 * (np.linspace(0.4, 1, n) if sube else np.linspace(1, 0.4, n))
    s = r * env * vol; a = int(t0 * SR); b = min(N, a + n)
    mix[a:b, 0] += s[:b - a]; mix[a:b, 1] += s[:b - a] * 0.9


# colchón: acorde suave de Fa mayor 9 con trémolo lento
for m, v in [(53, .05), (60, .04), (65, .035), (69, .03), (72, .022), (79, .012)]:
    f = nota(m); s = np.sin(2 * np.pi * f * t) * v * (0.85 + 0.15 * np.sin(2 * np.pi * 0.18 * t + m))
    s += 0.3 * np.sin(2 * np.pi * f * 1.003 * t) * v
    mix[:, 0] += s; mix[:, 1] += s * 0.95
entrada = np.minimum(1, t / 1.5); salida = np.minimum(1, (DUR - t) / 1.2)
mix *= (entrada * salida)[:, None]

brillo(0.05, 1.5, 0.06)                                         # barrido del logo
for k, m in enumerate([77, 81, 84]): campana(1.3 + k * 0.12, m, 0.10, 2.0, pan=-0.3 + 0.3 * k)   # nombre
campana(1.75, 72, 0.07, 1.6); campana(2.05, 76, 0.06, 1.6)       # Lic. Psicología y lema
brillo(2.4, 2.2, 0.04)                                           # el tallo crece
for k, m in enumerate([84, 88, 91, 96]): campana(4.3 + k * 0.09, m, 0.07, 2.4, pan=0.5)          # la peonía florece
for k in range(5): pluck(3.4 + 0.28 * k, [65, 69, 72, 74, 77][k], 0.06, pan=-0.2)                 # servicios
campana(5.0, 69, 0.06, 1.4)                                      # Agenda tu consulta
campana(5.45, 81, 0.13, 1.2); campana(5.47, 88, 0.06, 1.0)       # ding del botón
for k in range(3): pluck(5.8 + 0.2 * k, [72, 76, 79][k], 0.04)   # dirección y cédula
for k in range(5): campana(7.0 + 0.95 * k, [84, 88][k % 2], 0.025, 1.5, pan=0.4 * (-1) ** k)      # destellos lejanos al final

# reverberación sencilla (ecos cortos que decaen)
salida_r = mix.copy()
for dly, g in [(0.031, .35), (0.047, .3), (0.071, .25), (0.11, .2), (0.17, .14), (0.26, .09)]:
    d = int(dly * SR); salida_r[d:, 0] += mix[:-d, 1] * g; salida_r[d:, 1] += mix[:-d, 0] * g
salida_r /= max(1e-9, np.abs(salida_r).max()) / 0.7
with wave.open(str(AQUI / 'tarjeta' / 'sonidos_tarjeta.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((salida_r * 32767).astype(np.int16).tobytes())
print('ok')
