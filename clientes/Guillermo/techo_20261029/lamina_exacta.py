"""Guillermo · lámina de placa teja puesta EXACTAMENTE sobre la estructura de su captura (sin mover nada), animada panel por panel.
Pedido de Guillermo (30 oct): 'que encima de la estructura, así como está, se vea la lámina; no que se vea la estructura atrás ni lámina arriba'.
Uso: python3 lamina_exacta.py  → salida_v5/"""
import subprocess
from pathlib import Path
import cv2, numpy as np, imageio_ffmpeg

AQUI = Path(__file__).resolve().parent; V2 = AQUI / 'salida_v2'; S = AQUI / ('salida_v6_caen' if '--sube' not in __import__('sys').argv else 'salida_v6_suben'); S.mkdir(exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe()
T1 = cv2.cvtColor(cv2.imread(str(V2 / 'T1_estructura_limpio.png')), cv2.COLOR_BGR2RGB)
T0 = cv2.cvtColor(cv2.imread(str(V2 / 'T0_sitio.png')), cv2.COLOR_BGR2RGB)
H, W = T1.shape[:2]
# cuadrilátero de la estructura (TL, TR, BR, BL), medido sobre la captura de Guillermo
QUAD = np.float32([[128, 783], [612, 783], [546, 866], [204, 866]])   # lámina apoyada ENCIMA de las vigas (unos px más arriba)
# 1) quitar las puntas de vigas que se asoman arriba: cielo limpio del cuadro original
base = T1.copy(); y0, y1, x0, x1 = 750, 800, 120, 625
base[y0:y1, x0:x1] = T0[y0:y1, x0:x1]


lum = base.astype(np.float32).mean(2); azul = base[..., 2].astype(np.float32) - base[..., 0]
BM = ((lum < 95) & (azul < 60)).astype(np.uint8); BM[:790] = 0; BM[890:] = 0; BM[:, :118] = 0; BM[:, 622:] = 0
BM = cv2.GaussianBlur(cv2.dilate(BM, np.ones((2, 2), np.uint8)).astype(np.float32), (0, 0), 0.9)[..., None]


def textura(w=960, h=420):
    u = np.linspace(0, 1, w)[None, :]; v = np.linspace(0, 1, h)[:, None]
    ondas = 0.5 + 0.5 * np.cos(2 * np.pi * u * 30)
    sombra = 0.72 + 0.28 * ondas                      # ondas de la placa teja
    traslape = 0.88 + 0.12 * (np.mod(v * 7, 1.0) < 0.9) # líneas de traslape
    deg = 1.0 - 0.18 * v
    k = (sombra * traslape * deg)[..., None]
    rojo = np.array([198, 38, 30], np.float32)
    return np.clip(rojo * k + 18 * ondas[..., None], 0, 255).astype(np.uint8)


TEX = textura(); th, tw = TEX.shape[:2]
M = cv2.getPerspectiveTransform(np.float32([[0, 0], [tw, 0], [tw, th], [0, th]]), QUAD)
N = 6                                                  # paneles de lámina a lo ancho


def pasar(t, i):
    """progreso 0..1 del panel i en el tiempo t (s)"""
    return float(np.clip((t - 0.25 - i * 0.5) / 0.45, 0, 1))


def cuadro(t):
    out = base.copy().astype(np.float32)
    for i in range(N):
        p = pasar(t, i)
        if p <= 0: continue
        e = 1 - (1 - p) ** 3
        mask = np.zeros((th, tw), np.uint8); mask[:, int(i * tw / N):int((i + 1) * tw / N) + 1] = 255
        dy = (1 - e) * (90 if '--sube' in __import__('sys').argv else -90)
        Mi = M.copy(); Mi[1] = Mi[1] + dy * Mi[2]      # desplazar en vertical (antes de la perspectiva)
        col = cv2.warpPerspective(TEX, Mi, (W, H)); m = cv2.warpPerspective(mask, Mi, (W, H)).astype(np.float32)[..., None] / 255
        m = cv2.GaussianBlur(m, (0, 0), 0.8)[..., None] * min(1, p * 3) if m.ndim == 3 else m
        out = out * (1 - m) + col.astype(np.float32) * m
    out = out * (1 - BM) + base.astype(np.float32) * BM   # las vigas quedan visibles por debajo / delante de la lámina
    return np.clip(out, 0, 255).astype(np.uint8)


FPS, SEG = 24, 5.0
p = subprocess.Popen([FF, '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-an', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', str(S / 'T_lamina_limpio.mp4')],
                     stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
for f in range(int(FPS * SEG)): p.stdin.write(cuadro(f / FPS).tobytes())
p.stdin.close(); p.wait()
cv2.imwrite(str(S / 'T2_techo.png'), cv2.cvtColor(cuadro(SEG), cv2.COLOR_RGB2BGR))
cv2.imwrite(str(S / 'T1_base.png'), cv2.cvtColor(base, cv2.COLOR_RGB2BGR))
import shutil; shutil.copy(V2 / 'T_vigas_limpio.mp4', S / 'T_vigas_limpio.mp4')
lista = AQUI / 'lista_v5.txt'; lista.write_text(''.join(f"file '{S / (n + '_limpio.mp4')}'\n" for n in ('T_vigas', 'T_lamina')))
fin = S / 'Guillermo_techo_proceso.mp4'
subprocess.run([FF, '-y', '-f', 'concat', '-safe', '0', '-i', str(lista), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-pix_fmt', 'yuv420p', '-crf', '23', '-movflags', '+faststart', str(fin)], check=True, capture_output=True)
print(fin, fin.stat().st_size // 1024, 'KB')
