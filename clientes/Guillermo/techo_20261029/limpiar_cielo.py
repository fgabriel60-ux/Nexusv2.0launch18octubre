"""Reemplaza el cielo con ruido de T1/T2 y de los videos por el cielo limpio de T0 (foto de Guillermo) y une los 2 videos en uno.
Uso: python3 limpiar_cielo.py"""
import subprocess
from pathlib import Path
import av, cv2, numpy as np
import imageio_ffmpeg
from PIL import Image

AQUI = Path(__file__).resolve().parent; S = AQUI / 'salida'; FF = imageio_ffmpeg.get_ffmpeg_exe()
T0 = np.array(Image.open(S / 'T0_sitio.png').convert('RGB'))
H, W = T0.shape[:2]; TOPE = int(H * 0.66)   # la barda empieza ~66% de la altura


def limpiar(a):
    a = cv2.resize(a, (W, H)) if a.shape[:2] != (H, W) else a
    r, g, b = [a[..., i].astype(int) for i in range(3)]
    cielo = ((b > r + 25) & (b > 90)).astype(np.uint8)
    cielo[TOPE:] = 0
    cielo = cv2.morphologyEx(cielo, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    m = cv2.GaussianBlur(cv2.dilate(cielo, np.ones((3, 3), np.uint8)).astype(np.float32), (0, 0), 1.5)[..., None]
    return (T0 * m + a * (1 - m)).astype(np.uint8)


for n in ('T1_estructura', 'T2_techo'):
    a = np.array(Image.open(S / f'{n}.png').convert('RGB')); Image.fromarray(limpiar(a)).save(S / f'{n}_limpio.png')

procs = []
for n in ('T_vigas', 'T_lamina'):
    c = av.open(str(S / f'{n}.mp4')); fps = float(c.streams.video[0].average_rate)
    sal = S / f'{n}_limpio.mp4'
    p = subprocess.Popen([FF, '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-', '-an', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', str(sal)],
                         stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    for fr in c.decode(video=0): p.stdin.write(limpiar(fr.to_ndarray(format='rgb24')).tobytes())
    p.stdin.close(); p.wait(); print(sal)
lista = AQUI / 'lista.txt'; lista.write_text(''.join(f"file '{S / (n + '_limpio.mp4')}'\n" for n in ('T_vigas', 'T_lamina')))
fin = S / 'Guillermo_techo_proceso.mp4'
subprocess.run([FF, '-y', '-f', 'concat', '-safe', '0', '-i', str(lista), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-pix_fmt', 'yuv420p', '-crf', '23', '-movflags', '+faststart', str(fin)], check=True, capture_output=True)
subprocess.run([FF, '-y', '-ss', '9', '-i', str(fin), '-frames:v', '1', str(S / 'cuadro_final.jpg')], capture_output=True)
print(fin, fin.stat().st_size // 1024, 'KB')
