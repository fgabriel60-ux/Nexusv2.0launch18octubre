"""Renderiza SOLO 0–TA (15.3 s) de v9b (lo que cambia) a 720x1280, sin audio; el resto se toma de v9a. Un solo proceso, sin pool (el pool se atoró)."""
import subprocess
from PIL import Image
import armar_v9b as b
from armar_v9b import *   # noqa

sal = TMP / 'v9b_parte1.mp4'
p = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '720x1280', '-r', str(FPS), '-i', '-',
                      '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', str(sal)], stdin=subprocess.PIPE)
N = int(TA * FPS)
for n in range(N):
    p.stdin.write(b.frameb(n / FPS).resize((720, 1280), Image.LANCZOS).tobytes())
    if n % 60 == 0: print(f'{n / FPS:.1f}s', flush=True)
p.stdin.close(); p.wait(); print('listo', sal)
