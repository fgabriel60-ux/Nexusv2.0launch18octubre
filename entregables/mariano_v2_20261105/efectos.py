#!/usr/bin/env python3
"""Efectos de sonido para el gancho de Mariano, sintetizados a mano.

6 nov 2026, Carlos: «agrega efectos de sonido tú al gancho porque H3 no lo hizo bien».
Los filtros sueltos de ffmpeg sonaban a estática. Aquí cada efecto se construye con su
envolvente y su espectro, que es lo que hace que se oiga como la cosa y no como ruido.
"""
import numpy as np

SR = 44100

def _ruido_rosa(n, rng):
    """Ruido rosa por suma de octavas: la base de cualquier viento creíble."""
    blanco = rng.standard_normal(n)
    X = np.fft.rfft(blanco)
    f = np.fft.rfftfreq(n, 1 / SR)
    f[0] = f[1]
    return np.fft.irfft(X / np.sqrt(f), n)

def _suaviza(x, ventana):
    k = max(1, int(ventana))
    return np.convolve(x, np.ones(k) / k, mode="same")

def viento(seg, fuerza=0.30, altura=1.0, semilla=7):
    """Aire de altura: ruido rosa con el filtro abriéndose y cerrándose en rachas lentas."""
    rng = np.random.default_rng(semilla)
    n = int(seg * SR)
    base = _ruido_rosa(n, rng)
    # rachas: una envolvente lenta e irregular, no un tremolo mecánico
    lento = _suaviza(rng.standard_normal(n), SR * 0.35)
    lento = lento / (np.abs(lento).max() + 1e-9)
    env = 0.55 + 0.45 * (0.5 + 0.5 * lento)
    # el brillo sube con la racha: más aire = más agudos
    x = base * env
    corte_bajo = _suaviza(x, int(SR / (300 * altura)))      # cuerpo grave
    silbido = (x - corte_bajo) * 0.35 * env                  # el filo del aire
    y = corte_bajo + silbido
    y *= np.linspace(0, 1, min(n, int(0.25 * SR)) ).tolist() + [1.0] * (n - min(n, int(0.25 * SR)))
    return (y / (np.abs(y).max() + 1e-9)) * fuerza

def roce_cuerda(seg, fuerza=0.22, semilla=11):
    """La cuerda corriendo por el guante: fricción con grano, no estática plana."""
    rng = np.random.default_rng(semilla)
    n = int(seg * SR)
    x = rng.standard_normal(n)
    banda = _suaviza(x, int(SR / 2200)) - _suaviza(x, int(SR / 480))   # banda 480-2200 Hz
    # el grano: la cuerda no corre lisa, da tirones
    grano = _suaviza(rng.standard_normal(n), int(SR * 0.012))
    grano = 0.6 + 0.9 * np.clip(grano / (np.abs(grano).max() + 1e-9), -1, 1) ** 2
    y = banda * grano
    return (y / (np.abs(y).max() + 1e-9)) * fuerza

def hebilla(seg, en=0.30, fuerza=0.85, semilla=3):
    """Hebilla metálica que se zafa: parciales agudos inarmónicos con caída rápida."""
    rng = np.random.default_rng(semilla)
    n = int(seg * SR)
    y = np.zeros(n)
    t = np.arange(n) / SR
    # el clic: varios parciales metálicos, cada uno con su decaimiento
    for f0, amp, tau in ((2840, 1.0, 0.045), (4310, .70, .030), (6180, .45, .020),
                         (1470, .55, .060), (9100, .25, .012)):
        y += amp * np.sin(2 * np.pi * f0 * t + rng.random()) * np.exp(-np.maximum(t - en, 0) / tau)
    y *= (t >= en)
    # el chasquido seco del plástico-metal al soltar
    golpe = (t >= en) & (t < en + 0.004)
    y += golpe * rng.standard_normal(n) * 2.2
    # la correa que cae al suelo, un poco después: impacto sordo
    cae = en + 0.34
    sordo = np.exp(-np.maximum(t - cae, 0) / 0.055) * (t >= cae)
    y += sordo * (_suaviza(rng.standard_normal(n), int(SR / 260)) * 9.0)
    return (y / (np.abs(y).max() + 1e-9)) * fuerza

def pisada(seg, en=0.12, fuerza=0.55, semilla=5):
    """Los pies tocando el concreto al aterrizar."""
    rng = np.random.default_rng(semilla)
    n = int(seg * SR); t = np.arange(n) / SR
    y = np.zeros(n)
    for d, a in ((0.0, 1.0), (0.085, 0.72)):      # los dos pies, uno detrás del otro
        c = en + d
        cuerpo = np.exp(-np.maximum(t - c, 0) / 0.040) * (t >= c)
        y += a * cuerpo * (_suaviza(rng.standard_normal(n), int(SR / 190)) * 8.0)
        chasq = (t >= c) & (t < c + 0.006)
        y += a * chasq * rng.standard_normal(n) * 1.1
    return (y / (np.abs(y).max() + 1e-9)) * fuerza

def mezcla_estereo(pistas, seg):
    n = int(seg * SR)
    m = np.zeros(n)
    for p in pistas:
        q = np.zeros(n)
        k = min(len(p), n)
        q[:k] = p[:k]
        m += q
    pico = np.abs(m).max()
    if pico > 0.98:
        m = m / pico * 0.98
    # salida y pequeño fade para que no truene en el corte
    f = min(int(0.05 * SR), n // 4)
    m[:f] *= np.linspace(0, 1, f)
    m[-f:] *= np.linspace(1, 0, f)
    return np.stack([m, m], axis=1)

def guarda(ruta, estereo):
    import wave
    d = (np.clip(estereo, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(d.tobytes())
    return ruta


def calle(seg, fuerza=0.26, pasa_auto=None, semilla=13):
    """Ambiente de calle urbana: rumor de tráfico lejano y, si se pide, un auto que cruza.

    pasa_auto: segundo en que el auto pasa más cerca del micrófono (None = ninguno).
    """
    rng = np.random.default_rng(semilla)
    n = int(seg * SR); t = np.arange(n) / SR
    # rumor de ciudad: ruido rosa con casi todo el peso en los graves
    base = _ruido_rosa(n, rng)
    rumor = _suaviza(base, int(SR / 220))
    # el aire de la avenida, muy por debajo
    aire = (base - _suaviza(base, int(SR / 900))) * 0.18
    y = rumor + aire
    if pasa_auto is not None:
        # un auto que se acerca y se aleja: el volumen y el brillo suben al pasar
        d = np.abs(t - pasa_auto)
        cerca = np.exp(-(d ** 2) / (2 * 0.55 ** 2))
        motor = _suaviza(rng.standard_normal(n), int(SR / 320)) * 3.2
        rodada = (rng.standard_normal(n) - _suaviza(rng.standard_normal(n), int(SR / 1600))) * 0.5
        y = y + (motor + rodada * cerca) * cerca
    return (y / (np.abs(y).max() + 1e-9)) * fuerza
