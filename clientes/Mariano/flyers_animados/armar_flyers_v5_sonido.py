"""Mariano · flyers animados v5: re-mezcla SOLO el audio con efectos grabados de Mixkit (licencia libre, uso comercial,
sin atribución; ver sfx_reales/LICENCIAS.md). El video se copia sin recodificar (-c:v copy).

Lo aprendido de los reels de referencia (solo análisis, nada de su audio se usa aquí):
  - texto que entra: clic/pop corto y brillante (centroide 4-6 kHz, cola < 30 ms) o pop medio (~800 Hz);
  - primera entrada / cambio fuerte: whoosh corto (~200 ms);
  - antes de la revelación: riser que corta justo en el evento; precio: campanita (ding) limpia;
  - cierre/destello: golpe medio-grave (100-400 Hz) con cola breve.
Reglas de mezcla: un solo golpe cuando varios textos entran casi a la vez (< 70 ms, gana el de mayor prioridad),
fades cortos, paso-alto en los efectos agudos, música baja (0.27), pico final < -2 dBFS medido en el AAC.

Uso:
  python3 armar_flyers_v5_sonido.py                 # los 4 flyers conocidos
  from armar_flyers_v5_sonido import render         # render(video, eventos, salida) para flyers nuevos
Eventos: lista de (segundo_visual, tipo, ganancia, pan). Tipos: whoosh|punch, texto|pop, camara, mouse|clic, riser,
ding, impacto (punch seco + sub grave en un solo golpe). 'punch' y 'mouse' se aceptan por compatibilidad con las tablas v4 / nuevos/eventos.json.
"""
import json, re, subprocess, wave
from functools import lru_cache
from pathlib import Path
import numpy as np
import imageio_ffmpeg
from scipy import signal

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
KIT = AQUI / 'sfx_reales' / 'mixkit'
MUSICA = AQUI.parents[1] / 'XV' / 'musica_suave_s7.wav'
OUT = AQUI / 'v5'; OUT.mkdir(exist_ok=True)
SR = 44100
FIN = 7.0
MUSICA_VOL = 0.27
PICO_PRE_AAC = 10 ** (-3.2 / 20)          # el AAC sube ~0.5-1 dB; objetivo final < -2 dBFS

# tipo -> (archivo, segundo del "golpe" dentro de la muestra (se alinea con el evento), recorte inicio, recorte fin, ganancia, paso-alto Hz)
KIT_DEF = {
    'whoosh':  ('whoosh_3115_fast_transitions_swoosh.mp3', 0.114, 0.0, 0.40, 0.55, 120),
    'texto':   ('pop_3005_explainer_light_pop.mp3',         0.034, 0.0, 0.20, 0.50, 150),
    'camara':  ('camara_1430_camera_shutter_hard_click.mp3', 0.115, 0.09, 0.55, 0.60, 300),
    'clic':    ('clic_2568_cool_interface_click_tone.mp3',  0.005, 0.0, 0.08, 0.60, 300),
    'riser':   ('riser_790_cinematic_trailer_riser.mp3',    2.494, 1.85, 2.52, 0.50, 60),
    'ding':    ('ding_586_attention_bell_ding.mp3',         0.008, 0.0, 0.95, 0.42, 200),
    'impacto': ('impacto_2143_hard_and_quick_punch.mp3',   0.040, 0.0, 0.30, 0.70, 60),
    'sub':     ('sub_2299_short_bass_hit.mp3',              0.080, 0.0, 0.65, 0.45, 25),    # capa grave del impacto (mismo golpe)
}
ALIAS = {'punch': 'whoosh', 'mouse': 'clic', 'pop': 'texto'}
PRIORIDAD = {'ding': 6, 'impacto': 5, 'whoosh': 4, 'camara': 3, 'texto': 2, 'clic': 1, 'riser': -1}


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True)
    if r.returncode: raise SystemExit(r.stderr.decode()[-2000:])
    return r.stdout


def leer(ruta, canales=1, t=None):
    extra = ['-t', str(t)] if t else []
    raw = ff(['-i', str(ruta), *extra, '-ac', str(canales), '-ar', str(SR), '-f', 'f32le', '-'])
    x = np.frombuffer(raw, '<f4').astype(float)
    return x.reshape(-1, canales) if canales > 1 else x


@lru_cache(None)
def muestra(tipo):
    """Muestra recortada, con paso-alto, fades (3 ms entrada / 25 ms salida) y pico normalizado a 1. Devuelve (audio, offset_golpe)."""
    arch, golpe, a, b, _, hp = KIT_DEF[tipo]
    x = leer(KIT / arch)
    x = x[int(a * SR):int(b * SR)]
    x = signal.sosfiltfilt(signal.butter(2, hp, 'hp', fs=SR, output='sos'), x)
    fi, fo = int(0.003 * SR), int(0.025 * SR)
    if tipo == 'riser': fi = int(0.15 * SR)          # el riser entra suave porque se corta a la mitad de su subida
    x[:fi] *= np.linspace(0, 1, fi); x[-fo:] *= np.linspace(1, 0, fo)
    return x / np.abs(x).max(), golpe - a


def poner(pista, s, t, g, pan):
    i = int(round(t * SR)); s = s[max(0, -i):]; i = max(i, 0); s = s[:max(0, len(pista) - i)]
    th = (np.clip(pan, -1, 1) + 1) * np.pi / 4
    pista[i:i + len(s), 0] += s * g * np.cos(th); pista[i:i + len(s), 1] += s * g * np.sin(th)


def depurar(eventos):
    """Normaliza tipos y fusiona entradas simultáneas (< 70 ms) en un solo golpe (el de mayor prioridad). El riser no cuenta."""
    ev = [(float(t), ALIAS.get(k, k), float(g), float(p)) for t, k, g, p in eventos]
    risers = [e for e in ev if e[1] == 'riser']
    golpes = sorted([e for e in ev if e[1] != 'riser'], key=lambda e: (e[0], -PRIORIDAD[e[1]]))
    final = []
    for e in golpes:
        if final and abs(e[0] - final[-1][0]) < 0.07:
            if PRIORIDAD[e[1]] > PRIORIDAD[final[-1][1]]: final[-1] = e
            continue
        final.append(e)
    return sorted(final + risers)


def musica():
    m = leer(MUSICA, 2, FIN)
    out = np.zeros((int(SR * FIN), 2)); out[:min(len(m), len(out))] = m[:len(out)]
    tt = np.arange(len(out)) / SR
    return out * (np.minimum(tt / 0.5, 1) * np.minimum((FIN - tt) / 1.0, 1))[:, None] * MUSICA_VOL


def escribir_wav(x, ruta):
    with wave.open(str(ruta), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype('<i2').tobytes())


def env_db(x, t0, t1):
    a = x[int(max(t0, 0) * SR):int(t1 * SR)]
    return 20 * np.log10(np.sqrt(np.mean(a ** 2)) + 1e-9) if len(a) else -120


def render(video, eventos, salida):
    """Mezcla los efectos del kit sobre la música y re-empaqueta 'video' (sin recodificar) en 'salida'."""
    video, salida = Path(video), Path(salida)
    ev = depurar(eventos)
    sfx = np.zeros((int(SR * FIN), 2))
    for t, k, g, pan in ev:
        s, off = muestra(k)
        poner(sfx, s, t - off + (0.0 if k == 'riser' else 0.03), KIT_DEF[k][4] * g, pan)   # +30 ms: el texto ya se ve
        if k == 'impacto':
            s2, off2 = muestra('sub'); poner(sfx, s2, t - off2 + 0.03, KIT_DEF['sub'][4] * g, 0.0)
    mus = musica()
    mix = mus + sfx
    esc = PICO_PRE_AAC / np.abs(mix).max(); mix *= esc
    wav = OUT / f'{salida.stem}.wav'; escribir_wav(mix, wav)
    ff(['-i', str(video), '-i', str(wav), '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
        '-t', str(FIN), '-movflags', '+faststart', str(salida)])
    # ---- verificación por señal sobre el AAC final ----
    dec = leer(salida, 2).mean(1)
    musref = (mus * esc).mean(1)
    pico = 20 * np.log10(np.abs(leer(salida, 2)).max())
    filas = []
    for t, k, g, pan in ev:
        if k == 'riser': a, b = t - 0.30, t
        else: a, b = t, t + 0.12
        sube = env_db(dec, a, b) - env_db(musref, a, b)
        filas.append({'t': round(t, 2), 'tipo': k, 'muestra': KIT_DEF[k][0], 'sobre_musica_dB': round(sube, 1)})
    rep = {'salida': salida.name, 'video_origen': video.name, 'pico_AAC_dBFS': round(pico, 2),
           'muestras_recortadas_>=0.99': int((np.abs(leer(salida, 2)) >= 0.99).sum()), 'eventos': filas}
    (OUT / f'{salida.stem}.json').write_text(json.dumps(rep, ensure_ascii=False, indent=2))
    print(f'{salida.name}: pico AAC {pico:.2f} dBFS | ' + ' '.join(f"{f['tipo']}@{f['t']}:+{f['sobre_musica_dB']}dB" for f in filas))
    assert pico < -2, f'pico demasiado alto {pico}'
    assert all(f['sobre_musica_dB'] > 3 for f in filas), 'algún evento no destaca sobre la música'
    return rep


# Tiempos reales (de armar_flyers_v2.py / v4): entrada de cada texto y destello del precio.
EV_BENJAMINA = [
    (0.10, 'whoosh', 1.0, 0.0),     # titular
    (0.60, 'camara', 1.0, 0.15),    # logo
    (1.00, 'riser', 1.0, 0.0),      # sube y corta justo cuando entra el precio
    (1.00, 'ding', 1.0, 0.0),       # precio
    (1.25, 'impacto', 1.0, 0.0),    # destello (cierre de la reveladora del precio)
    (1.80, 'texto', 1.0, 0.2),      # chips
    (2.20, 'clic', 1.0, -0.2),      # pie
]
EV_BUGAMBILIA = [
    (0.10, 'whoosh', 1.0, 0.0),     # lagsa + restricciones entran juntos: un solo golpe
    (0.25, 'camara', 0.8, 0.0),     # logo
    (0.55, 'texto', 1.0, -0.2),     # globo 1
    (0.95, 'texto', 1.0, 0.2),      # globo 2
    (1.35, 'clic', 1.0, 0.0),       # barras izq + der (juntas: un golpe)
    (1.70, 'riser', 1.0, 0.0),
    (1.70, 'ding', 1.0, 0.0),       # precio
    (1.95, 'impacto', 1.0, 0.0),    # destello
    (2.20, 'clic', 0.9, 0.0),       # pie
]


def eventos_nuevos(nombre, tabla):
    """Adapta la tabla de nuevos/eventos.json: añade el riser antes del precio (si hay hueco >= 0.6 s) y las capas sin sonido."""
    ev = [tuple(e) for e in tabla]
    extra = {'Bugambilia_mejor_opcion': [(0.40, 'clic', 0.8, 0.0)]}     # banda inferior (capa a 0.4 s en armar_flyers_pendientes.py)
    ev += extra.get(nombre, [])
    for t, k, g, p in list(ev):
        if ALIAS.get(k, k) == 'ding' and all(not (t - 0.6 < u < t) for u, *_ in ev): ev.append((t, 'riser', 1.0, 0.0))
    return ev


def ultima_version(nombre, hasta=5):
    vs = [(int(m.group(1)), p) for p in AQUI.glob(f'Mariano_flyer_{nombre}_v*.mp4')
          if (m := re.fullmatch(rf'Mariano_flyer_{re.escape(nombre)}_v(\d+)\.mp4', p.name)) and int(m.group(1)) < hasta]
    return max(vs)[1] if vs else None


if __name__ == '__main__':
    render(AQUI / 'Mariano_flyer_Benjamina_v4.mp4', EV_BENJAMINA, AQUI / 'Mariano_flyer_Benjamina_v5.mp4')
    render(AQUI / 'Mariano_flyer_Bugambilia_v4.mp4', EV_BUGAMBILIA, AQUI / 'Mariano_flyer_Bugambilia_v5.mp4')
    tabla = AQUI / 'nuevos' / 'eventos.json'
    if tabla.exists():
        for nombre, ev in json.loads(tabla.read_text()).items():
            v = ultima_version(nombre)
            if v: render(v, eventos_nuevos(nombre, ev), AQUI / f'Mariano_flyer_{nombre}_v5.mp4')
