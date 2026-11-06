"""Reel XV v8 (Manuel): VIDEO MUSICAL sobre la canción de la referencia «GIO XV» (s 30.13 → 66.6), con cada corte en el golpe (125 BPM).
Estructura de la canción → del video:
  subida (12 golpes)   → apertura y preparación generadas en Modal (dron, vestido colgado, tiara, entrada a contraluz)
  DROP 1 (34 golpes)   → fiesta real: un corte por golpe, giros, amigas, robot, confeti (+2 escenas IA: giro con confeti y robot con CO2)
  respiro (22 golpes)  → emoción, planos largos: grupo de damas, fotos de la sesión, retrato de espalda frente al XV, giro lento
  DROP 2 (8 golpes)    → end card animado con el logo de Hunab Ku Fotografía sobre el dron (Manuel_fotografia/logo/endcard.py)
Reusa la cámara virtual / color / confeti de v6. Uso: python3 armar_xv_v8.py"""
import subprocess
from pathlib import Path
import av, numpy as np
from PIL import Image
import sys
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/Manuel_fotografia/logo')
from endcard import endcard
from armar_xv_v6 import toma, Confeti, Enc, suave, FF, W, H, FPS, ORI

AQUI = Path(__file__).resolve().parent
TMP = Path('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/d5ed233e-f882-4c9b-a96a-df1463a68d1a/scratchpad/xv8'); TMP.mkdir(parents=True, exist_ok=True)
MUSICA = AQUI / 'referencia' / 'musica_ref.wav'
BPM, T0 = 125.15, 30.13                      # medido sobre la canción (referencia/beats.txt)
G = 60 / BPM                                 # un golpe ≈ 0.479 s

# ('ia', clip v8, golpes, confeti, fracción inicial del clip) · ('real', clip, inicio, golpes, cx, zoom, velocidad, confeti) · ('foto', archivo, golpes, zoom)
PLAN = [
    # subida
    ('ia', 'M1', 4, False, 0.0), ('ia', 'M2', 2, False, 0.2), ('ia', 'M3', 2, False, 0.2), ('ia', 'M4', 4, False, 0.0),
    # DROP 1
    ('real', 'C6771', 2.0, 2, (.30, .55), (1.25, 1.10), (0.4, 0.4), False),
    ('real', 'C6755', 0.8, 2, (.42, .50), (1.00, 1.35), (1.0, 0.5), False),
    ('real', 'C6755', 12.0, 1, (.65, .40), (1.15, 1.30), (1.0, 1.0), False),
    ('real', 'C6755', 24.0, 1, (.40, .55), (1.40, 1.15), (1.0, 1.0), False),
    ('real', 'C6755', 45.0, 1, (.55, .45), (1.10, 1.30), (1.0, 1.0), False),
    ('real', 'C6755', 60.0, 1, (.35, .55), (1.30, 1.10), (1.0, 1.0), False),
    ('ia', 'M5', 2, True, 0.1),
    ('real', 'C6801', 4.0, 2, (.30, .45), (1.30, 1.10), (1.0, 0.6), True),
    ('ia', 'M7', 2, True, 0.1),
    ('real', 'C6801', 66.0, 1, (.55, .40), (1.10, 1.35), (1.0, 1.0), True),
    ('real', 'C6801', 117.0, 1, (.35, .50), (1.35, 1.15), (1.0, 1.0), True),
    ('real', 'C6801', 141.0, 1, (.40, .55), (1.30, 1.10), (1.0, 1.0), True),
    ('real', 'C6801', 177.0, 1, (.55, .40), (1.35, 1.15), (1.0, 1.0), True),
    ('real', 'C6801', 84.0, 2, (.45, .55), (1.20, 1.40), (0.8, 0.5), True),
    ('real', 'C6755', 27.0, 1, (.55, .45), (1.15, 1.30), (1.0, 1.0), False),
    ('real', 'C6755', 35.0, 1, (.45, .50), (1.30, 1.15), (1.0, 1.0), False),
    ('real', 'C6801', 50.0, 1, (.40, .50), (1.20, 1.35), (1.0, 1.0), True),
    ('real', 'C6801', 100.0, 1, (.55, .45), (1.35, 1.15), (1.0, 1.0), True),
    ('real', 'C6801', 126.0, 2, (.50, .40), (1.15, 1.35), (1.0, 0.7), True),
    ('real', 'C6801', 168.0, 2, (.45, .50), (1.10, 1.35), (0.6, 0.4), True),
    ('real', 'C6755', 15.0, 1, (.50, .50), (1.20, 1.35), (1.0, 1.0), False),
    ('real', 'C6801', 140.0, 1, (.45, .55), (1.30, 1.10), (1.0, 1.0), True),
    ('real', 'C6801', 160.0, 1, (.55, .45), (1.15, 1.30), (1.0, 1.0), True),
    ('real', 'C6801', 135.0, 1, (.40, .50), (1.35, 1.15), (1.0, 1.0), True),
    ('real', 'C6801', 145.0, 2, (.50, .45), (1.10, 1.30), (1.0, 0.6), True),
    # respiro
    ('real', 'C6752', 10.0, 4, (.50, .50), (1.00, 1.12), (0.5, 0.5), False),
    ('foto', 'BV8B6038-Editar.jpg', 4, (1.00, 1.12)),
    ('ia', 'M6', 4, False, 0.0),
    ('foto', 'BV8B6224.jpg', 4, (1.12, 1.00)),
    ('real', 'C6771', 10.0, 6, (.40, .48), (1.10, 1.40), (0.4, 0.3), False),
    # DROP 2: cierre
    ('end', 'M8', 8),                        # end card animado con el logo real de Hunab Ku Fotografía sobre el dron desenfocado
]
GOLPES = sum(p[2] if p[0] in ('ia', 'foto', 'end') else p[3] for p in PLAN)
TOTAL = GOLPES * G


def destello(im, k, n=3, f=0.4):
    return Image.blend(im, Image.new('RGBA', (W, H), (255, 255, 255, 255)), f * (1 - k / n)) if k < n else im


def escribe(enc, im, conf, confeti):
    if confeti: conf.dibuja(im, enc.k)
    enc.k += 1; enc.p.stdin.write(np.asarray(im.convert('RGB')).tobytes())


def toma_ia(enc, clip, nf, confeti, ini, conf):
    c = av.open(str(AQUI / 'v8' / 'clips' / f'{clip}.mp4'))
    frames = [f.to_image().convert('RGB') for f in c.decode(video=0)]; c.close()
    i0 = int(len(frames) * ini)
    for k in range(nf):
        im = frames[min(len(frames) - 1, i0 + int(k * 24 / FPS))].resize((W, H), Image.LANCZOS).convert('RGBA')   # a velocidad real
        escribe(enc, destello(im, k), conf, confeti)


def toma_end(enc, clip, nf):
    c = av.open(str(AQUI / 'v8' / 'clips' / f'{clip}.mp4'))
    frames = [f.to_image().convert('RGB') for f in c.decode(video=0)]; c.close()
    for k in range(nf):
        enc.k += 1; enc.p.stdin.write(np.asarray(endcard(k / FPS, frames[min(len(frames) - 1, int(k * 24 / FPS))])).tobytes())


def toma_foto(enc, archivo, nf, zz, conf):
    base = Image.open(ORI / archivo).convert('RGB'); base.thumbnail((2400, 2400))
    bw, bh = base.size
    for k in range(nf):
        z = zz[0] + (zz[1] - zz[0]) * suave(k / max(1, nf - 1))
        ch = min(bh, bw * 16 / 9) / z; cw = ch * 9 / 16
        x0, y0 = (bw - cw) / 2, (bh - ch) * 0.35
        im = base.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.BICUBIC).convert('RGBA')
        escribe(enc, im, conf, False)


def main():
    mudo = TMP / 'mudo.mp4'; e = Enc(mudo); conf = Confeti()
    golpe, k_total = 0, 0
    for n, p in enumerate(PLAN):
        g = p[2] if p[0] in ('ia', 'foto', 'end') else p[3]
        nf = round((golpe + g) * G * FPS) - round(golpe * G * FPS); golpe += g   # cada corte cae exactamente en su golpe
        if p[0] == 'end': toma_end(e, p[1], nf)
        elif p[0] == 'ia': toma_ia(e, p[1], nf, p[3], p[4], conf)
        elif p[0] == 'foto': toma_foto(e, p[1], nf, p[3], conf)
        else: toma(e, n, p[1], p[2], nf / FPS, p[4], p[5], p[6], p[7], conf)
        print(n, p[0], p[1], f'{golpe * G:.2f}s', flush=True)
    e.p.stdin.close(); e.p.wait()
    fl = (f"[0:v]scale=720:1280:flags=lanczos[v];"
          f"[1:a]afade=t=in:st=0:d=0.15,afade=t=out:st={TOTAL - 1.4:.2f}:d=1.4,loudnorm=I=-14:TP=-1.5[a]")
    sal = AQUI / 'final' / 'XV_reel_v9_endcard_hunabku.mp4'
    r = subprocess.run([FF, '-v', 'error', '-y', '-i', str(mudo),
                        '-ss', f'{T0}', '-t', f'{TOTAL:.2f}', '-i', str(MUSICA), '-filter_complex', fl,
                        '-map', '[v]', '-map', '[a]', '-t', f'{TOTAL:.2f}', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p', '-crf', '23',
                        '-maxrate', '3.2M', '-bufsize', '6M', '-preset', 'slow', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', str(sal)], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1500:])
    print(sal, sal.stat().st_size // 1024, 'KB', f'{TOTAL:.1f}s', GOLPES, 'golpes')


if __name__ == '__main__':
    main()
