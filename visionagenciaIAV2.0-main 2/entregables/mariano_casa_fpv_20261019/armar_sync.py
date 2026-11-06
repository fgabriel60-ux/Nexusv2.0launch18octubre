"""Mariano · Benjamina «sync cut» al estilo del reel DcIcueXPE33: un plano por golpe del beat (~0.92 s), gancho de 3.7 s, cierre aéreo con contacto. Música original sintetizada por código (130 bpm, sin derechos)."""
import subprocess, wave
from pathlib import Path
import imageio_ffmpeg, numpy as np
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
FUENTE = AQUI.parent / 'modelos_modal' / 'fuentes' / 'Anton-Regular.ttf'
TMP = AQUI / 'tmp_sync'; TMP.mkdir(exist_ok=True)
BPM = 130; BEAT = 60 / BPM; CORTE = 2 * BEAT          # 0.923 s por plano
INTRO, OUTRO = 8 * BEAT, 8 * BEAT                       # 2 compases cada uno
RUTA = ['E1', 'E2', 'E3', 'E4', 'E5', 'E6']; POR_TOMA = 3
TOTAL = INTRO + len(RUTA) * POR_TOMA * CORTE + OUTRO
VF = 'scale=720:1280:flags=lanczos:force_original_aspect_ratio=increase,crop=720:1280,fps=30,setsar=1,eq=saturation=1.08:contrast=1.04,format=yuv420p'

# --- música ---
SR = 44100
def musica():
    n = int(TOTAL * SR) + SR; t = np.arange(n) / SR; m = np.zeros(n); rng = np.random.default_rng(3)
    bombo_env = np.ones(n)
    acordes = [(220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (261.63, 329.63, 392.0), (196.0, 246.94, 293.66)]  # Am F C G
    bajos = [55.0, 43.65, 65.41, 49.0]
    for b in range(int(TOTAL / BEAT) + 2):
        t0 = b * BEAT; i0 = int(t0 * SR)
        if i0 >= n: break
        L = min(int(0.35 * SR), n - i0); tk = np.arange(L) / SR
        fase = 2 * np.pi * (45 * tk + (110 / 38) * (1 - np.exp(-38 * tk)))
        m[i0:i0 + L] += 0.95 * np.sin(fase) * np.exp(-tk * 9)                                  # bombo
        bombo_env[i0:i0 + min(int(0.18 * SR), n - i0)] *= np.linspace(0.35, 1, min(int(0.18 * SR), n - i0))
        if b % 2 == 1:
            Lc = min(int(0.22 * SR), n - i0); tc = np.arange(Lc) / SR
            m[i0:i0 + Lc] += 0.35 * rng.standard_normal(Lc) * np.exp(-tc * 22) * (np.sin(tc * 2 * np.pi * 1800) * 0.3 + 0.7)   # aplauso
        ih = i0 + int(BEAT / 2 * SR); Lh = min(int(0.06 * SR), n - ih)
        if Lh > 0:
            th = np.arange(Lh) / SR; m[ih:ih + Lh] += 0.14 * np.diff(np.concatenate([[0], rng.standard_normal(Lh)])) * np.exp(-th * 70)   # hat
    compas = (t / (BEAT * 4)).astype(int) % 4
    pad = np.zeros(n); bajo = np.zeros(n)
    for c in range(4):
        sel = compas == c
        for f in acordes[c]:
            pad[sel] += 0.06 * np.sin(2 * np.pi * f * t[sel]) + 0.03 * np.sin(2 * np.pi * f * 2.005 * t[sel])
        bajo[sel] += 0.28 * np.sin(2 * np.pi * bajos[c] * t[sel]) * (0.6 + 0.4 * np.sin(2 * np.pi * t[sel] / BEAT * 2) ** 2)
    m += (pad * bombo_env + bajo * bombo_env)
    m *= np.minimum(1, 0.5 + 0.5 * np.minimum(1, t / INTRO * 2))                          # entra con fuerza, sin silencio
    cola = np.clip((TOTAL + 0.2 - t) / 0.6, 0, 1); m *= cola
    m = np.tanh(m * 1.4) * 0.9
    est = np.stack([m, m], 1)
    with wave.open(str(TMP / 'musica.wav'), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((est * 32767).astype('<i2').tobytes())
musica()

# --- planos ---
partes = []
def plano(clip, off, dur, nombre, extra=''):
    out = TMP / f'{nombre}.mp4'
    subprocess.run([FF, '-v', 'error', '-y', '-ss', f'{off:.3f}', '-i', str(AQUI / 'clips' / f'{clip}.mp4'), '-vf', f'{VF}{extra}', '-an', '-t', f'{dur:.4f}',
                    '-c:v', 'libx264', '-crf', '18', str(out)], check=True)
    partes.append(out)
plano('E0', 0.0, INTRO, 'intro')
for k, clip in enumerate(RUTA):
    for i in range(POR_TOMA):
        plano(clip, i * 1.55, CORTE, f'{clip}_{i}')
plano('E7', 0.0, OUTRO, 'outro')
(TMP / 'lista.txt').write_text(''.join(f"file '{p}'\n" for p in partes))

# --- textos ---
def png(nombre, lineas):
    im = Image.new('RGBA', (720, 1280), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for txt, tam, y, color in lineas:
        f = ImageFont.truetype(str(FUENTE), tam); w = d.textlength(txt, font=f)
        d.text(((720 - w) / 2, y), txt, font=f, fill=color, stroke_width=6, stroke_fill=(0, 0, 0, 215))
    im.save(TMP / f'{nombre}.png')
B, Y = (255, 255, 255, 255), (255, 210, 60, 255)
png('gancho', [('BENJAMINA', 110, 1280 * 0.60, B), ('DESDE $2.8M', 84, 1280 * 0.68, Y)])
png('pago', [('INFONAVIT', 64, 1280 * 0.72, B), ('HIPOTECARIO · CONTADO', 50, 1280 * 0.78, Y)])
png('cierre', [('ASESOR MARIANO H.', 64, 1280 * 0.58, B), ('(664) 233-4848', 84, 1280 * 0.64, Y)])
t_pago = INTRO + 9 * CORTE; t_cierre = TOTAL - OUTRO + 0.5
salida = AQUI / 'final' / 'Mariano_casa_sync_cut.mp4'
subprocess.run([FF, '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(TMP / 'lista.txt'), '-i', str(TMP / 'musica.wav'),
                '-loop', '1', '-i', str(TMP / 'gancho.png'), '-loop', '1', '-i', str(TMP / 'pago.png'), '-loop', '1', '-i', str(TMP / 'cierre.png'),
                '-filter_complex', f"[2:v]format=rgba[g];[3:v]format=rgba[p];[4:v]format=rgba[c];"
                f"[0:v][g]overlay=0:0:enable='between(t,0.1,{INTRO - 0.2:.2f})':shortest=1[v1];[v1][p]overlay=0:0:enable='between(t,{t_pago:.2f},{t_pago + 3 * CORTE:.2f})'[v2];"
                f"[v2][c]overlay=0:0:enable='gte(t,{t_cierre:.2f})',format=yuv420p[v]",
                '-map', '[v]', '-map', '1:a', '-t', f'{TOTAL:.3f}', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-crf', '21', '-maxrate', '3M', '-bufsize', '6M',
                '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', str(salida)], check=True)
print(salida, round(salida.stat().st_size / 1e6, 1), 'MB', round(TOTAL, 2), 's', len(partes), 'planos')
