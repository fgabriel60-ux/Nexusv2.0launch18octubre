"""Hoja de contacto de un video (n cuadros equiespaciados) para revisión. Uso: python3 hoja.py video.mp4 salida.png [n=8]"""
import subprocess, sys
import numpy as np
import imageio_ffmpeg
from PIL import Image

FF = imageio_ffmpeg.get_ffmpeg_exe()
v, out = sys.argv[1], sys.argv[2]
n = int(sys.argv[3]) if len(sys.argv) > 3 else 8
w, h = 216, 384
raw = subprocess.run([FF, "-v", "error", "-i", v, "-vf", f"scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)
idx = np.linspace(0, len(fr) - 1, n).astype(int)
cols = min(n, 8); filas = (n + cols - 1) // cols
m = Image.new("RGB", (w * cols, h * filas))
for k, i in enumerate(idx):
    m.paste(Image.fromarray(fr[i]), ((k % cols) * w, (k // cols) * h))
m.save(out)
print(len(fr), "cuadros; muestra", list(idx))
