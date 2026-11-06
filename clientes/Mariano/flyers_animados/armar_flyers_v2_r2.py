"""Mariano · flyers animados v2 (mejoras de Glimmer): texto escalonado con deslizamiento, push-in digital continuo, color cálido + viñeta,
destello al revelar el precio y SFX sincronizados sobre la música. El texto es SIEMPRE el original del flyer (extraído por elementos), nunca reescrito.
Uso: python3 armar_flyers_v2.py [benjamina|bugambilia] [--clip RUTA]"""
import subprocess, sys, wave
from pathlib import Path
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H = 1080, 1920
FIN = 7.0
MUSICA = AQUI.parents[1] / 'XV' / 'musica_suave_s7.wav'
V2 = AQUI / 'v2'; V2.mkdir(exist_ok=True)
SR = 44100


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-2000:])


# ---------- sonido sintético ----------
def whoosh(dur=0.45):
    n = int(SR * dur); t = np.linspace(0, 1, n); rng = np.random.default_rng(3)
    ruido = rng.standard_normal(n)
    y = np.zeros(n); lp = 0.0
    for i in range(n):   # paso bajo cuya frecuencia sube y baja (barrido)
        a = 0.02 + 0.5 * np.sin(np.pi * t[i]) ** 2
        lp += a * (ruido[i] - lp); y[i] = lp
    return y / np.abs(y).max() * np.sin(np.pi * t) ** 1.5 * 0.5


def pop(f=520, dur=0.16):
    n = int(SR * dur); t = np.arange(n) / SR
    return np.sin(2 * np.pi * (f + 600 * np.exp(-t * 40)) * t) * np.exp(-t * 28) * 0.7


def chime(f=1320, dur=0.7):
    n = int(SR * dur); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.01 * t)) * np.exp(-t * 5) * 0.35


def sfx_wav(eventos, salida):
    """eventos: [(segundo, 'whoosh'|'pop'|'chime')] → wav estéreo FIN s."""
    pista = np.zeros(int(SR * FIN))
    gen = {'whoosh': whoosh, 'pop': pop, 'chime': chime}
    for t, k in eventos:
        s = gen[k](); i = int(t * SR); pista[i:i + len(s)] += s[:len(pista) - i]
    pista = np.clip(pista, -1, 1)
    with wave.open(str(salida), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((pista * 32767).astype('<i2').tobytes())


# ---------- capas de texto por elemento ----------
def capa_por_alfa(im_rgb, alfa, escala_a=(W, H)):
    capa = im_rgb.convert('RGBA'); capa.putalpha(Image.fromarray((alfa * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.8)))
    return capa.resize(escala_a, Image.LANCZOS)


def capas_benjamina():
    """Elementos del flyer de Benjamina (720×1280): el texto oscuro/color sobre blanco se convierte en alfa."""
    im = Image.open(AQUI / 'flyer_benjamina.jpg').convert('RGB'); a = np.asarray(im).astype(int)
    filas = [('titular', 0, 178), ('logo', 812, 985), ('precio', 985, 1095), ('chips', 1095, 1150), ('pie', 1150, 1280)]
    out = {}
    for n, y0, y1 in filas:
        alfa = np.clip((255 - a.min(2)) / 45.0, 0, 1); m = np.zeros_like(alfa); m[y0:y1] = 1
        out[n] = capa_por_alfa(im, alfa * m)
    return out


ZONAS_B = [   # (nombre, caja del flyer 900×1600, modo)
    ('lagsa', (50, 70, 240, 150), 'claro'), ('restr', (240, 100, 400, 125), 'texto_fino'),
    ('logo', (530, 80, 840, 290), 'blanco'),
    ('globo1', (45, 270, 470, 420), 'globo'), ('globo2', (480, 350, 880, 520), 'globo'),
    ('barraL', (85, 1075, 330, 1205), 'pastilla'), ('barraR', (585, 1075, 815, 1205), 'pastilla'),
    ('precio', (495, 1340, 880, 1470), 'blanco'), ('pie', (20, 1500, 890, 1570), 'pie'),
]


def capas_bugambilia():
    im = Image.open(AQUI / 'flyer_bugambilia.jpg').convert('RGB'); a = np.asarray(im).astype(int)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    out = {}
    for n, (x0, y0, x1, y1), modo in ZONAS_B:
        caja = np.zeros(R.shape, bool); caja[y0:y1, x0:x1] = True
        if modo == 'blanco': k = a.min(2) > (170 if x0 < 520 and y0 > 1300 else 205)
        elif modo == 'texto_fino': k = R > 105
        elif modo == 'claro': k = (B - R < 45) | (R > 150)
        elif modo in ('globo', 'pastilla'):
            beige = (R > 215) & (G > 205) & (B > 180) & (R - B < 60)
            k = ndi.binary_fill_holes(ndi.binary_closing(beige & caja, iterations=6))
        else: k = (a.min(2) > 205) | ((R > 215) & (G > 205)) | (a.max(2) < 110)
        k = ndi.binary_dilation(k & caja, iterations=2)
        if modo == 'pastilla':   # extremos redondos: dos píldoras junto a la pareja, no una barra cortada
            pm = Image.new('L', R.shape[::-1], 0); ImageDraw.Draw(pm).rounded_rectangle((x0, y0, x1, y1), radius=(y1 - y0) // 2, fill=255)
            k &= np.asarray(pm) > 0
        out[n] = capa_por_alfa(im, k.astype(float), (W, H))
    return out


# ---------- ensamblado ----------
def armar(nombre, clip, capas, tiempos, strips_blancas, eventos, destello, salida, zoom=0.03, ancla_abajo=False):
    """capas: {nombre: RGBA full-frame}; tiempos: {nombre: segundo de entrada}; strips_blancas: png RGBA opcional que tapa letras inventadas por H3."""
    entradas = ['-i', str(clip)]; filtros = []; ult = 'v0'; idx = 1
    filtros.append(f"[0:v]scale={W}:{H}:flags=lanczos,fps=30,setsar=1,tpad=stop_mode=clone:stop_duration=3,trim=duration={FIN},"
                   f"eq=saturation=1.08:contrast=1.03,vignette=PI/7:eval=init,format=yuv420p[v0]")
    if strips_blancas:
        entradas += ['-loop', '1', '-t', str(FIN), '-i', str(strips_blancas)]
        filtros.append(f"[{ult}][{idx}:v]overlay=0:0[v1]"); ult = 'v1'; idx += 1
    for n, t0 in tiempos.items():
        p = V2 / f'capa_{nombre}_{n}.png'; capas[n].save(p)
        entradas += ['-loop', '1', '-t', str(FIN), '-i', str(p)]
        filtros.append(f"[{idx}:v]format=rgba,fade=t=in:st={t0}:d=0.3:alpha=1[c{idx}]")
        filtros.append(f"[{ult}][c{idx}]overlay=x=0:y='if(lt(t,{t0}),60,max(0,60*(1-(t-{t0})/0.35)))':eval=frame:format=auto[o{idx}]")
        ult = f'o{idx}'; idx += 1
    yexpr = f'in_h-{H}' if ancla_abajo else f'(in_h-{H})/2'
    # destello suave al revelar el precio + push-in digital continuo 1.00→1.03
    filtros.append(f"[{ult}]eq=brightness=0.10:enable='between(t,{destello},{destello + 0.14})'[f]")
    filtros.append(f"[f]scale=w='{W}*(1+{zoom}*t/{FIN})':h='{H}*(1+{zoom}*t/{FIN})':eval=frame:flags=bicubic,crop={W}:{H}:x='(in_w-{W})/2':y='{yexpr}'"
                   f"[z]")
    sfx = V2 / f'sfx_{nombre}.wav'; sfx_wav(eventos, sfx)
    entradas += ['-i', str(MUSICA), '-i', str(sfx)]
    filtros.append(f"[{idx}:a]aresample=44100,volume=0.55,afade=t=in:st=0:d=0.5,afade=t=out:st={FIN - 1}:d=1,atrim=0:{FIN}[m];"
                   f"[{idx + 1}:a]aresample=44100,volume=1.0[s];[m][s]amix=inputs=2:duration=first:normalize=0[a]")
    ff(entradas + ['-filter_complex', ';'.join(filtros), '-map', '[z]', '-map', '[a]', '-t', str(FIN), '-c:v', 'libx264', '-profile:v', 'main',
                   '-pix_fmt', 'yuv420p', '-crf', '21', '-preset', 'slow', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(salida)])
    print(salida, salida.stat().st_size // 1024, 'KB')


def main():
    quien = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else 'ambos'
    clip_b = AQUI / 'bugambilia' / 'clip_v2.mp4'
    if '--clip' in sys.argv: clip_b = Path(sys.argv[sys.argv.index('--clip') + 1])
    if quien in ('benjamina', 'ambos'):
        tmp = AQUI / 'sin_texto'
        armar('benjamina', tmp / 'clip.mp4', capas_benjamina(),
              {'titular': 0.2, 'logo': 0.7, 'precio': 1.1, 'chips': 1.7, 'pie': 2.1}, tmp / 'franjas_blancas.png',
              [(0.2, 'whoosh'), (0.5, 'pop'), (0.7, 'chime'), (1.1, 'whoosh'), (1.35, 'pop'), (1.7, 'pop'), (2.1, 'pop')], 1.35,
              AQUI / 'Mariano_flyer_Benjamina_v2.mp4', zoom=0.02, ancla_abajo=True)
    if quien in ('bugambilia', 'ambos'):
        armar('bugambilia', clip_b, capas_bugambilia(),
              {'lagsa': 0.2, 'restr': 0.2, 'logo': 0.4, 'globo1': 0.7, 'globo2': 1.1, 'barraL': 1.5, 'barraR': 1.5, 'precio': 1.8, 'pie': 2.3}, None,
              [(0.4, 'chime'), (0.7, 'whoosh'), (0.95, 'pop'), (1.1, 'whoosh'), (1.35, 'pop'), (1.5, 'pop'), (1.8, 'whoosh'), (2.05, 'pop'), (2.3, 'pop')], 2.05,
              AQUI / 'Mariano_flyer_Bugambilia_v2.mp4', zoom=0.012)


if __name__ == '__main__':
    main()
