"""Lisbeth v8 = v7b + etiqueta fija «TOMATLÁN, JALISCO» arriba todo el video (lo pidió ella el 22 oct y Glimmer el 29). H.264 Main 720p <16 MB.
Uso: python3 armar_lisbeth_v8.py"""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/XV')
import imageio_ffmpeg
from PIL import Image, ImageDraw
from armar_xv import fu

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H = 720, 1280
CREMA, VERDE = (255, 255, 255), (16, 64, 48)


def etiqueta(ruta):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    f = fu(40, 'ExtraBold'); t = 'TOMATLÁN, JALISCO'; w = d.textlength(t, font=f); ancho = w + 120
    x0 = (W - ancho) / 2; y0, y1 = 140, 214
    d.rounded_rectangle((x0, y0, x0 + ancho, y1), 37, fill=VERDE + (232,), outline=(236, 200, 90, 255), width=4)
    cx, cy = x0 + 44, (y0 + y1) / 2   # pin de ubicación dibujado
    d.ellipse((cx - 15, cy - 24, cx + 15, cy + 6), fill=(236, 200, 90)); d.polygon([(cx - 13, cy - 2), (cx + 13, cy - 2), (cx, cy + 24)], fill=(236, 200, 90))
    d.ellipse((cx - 6, cy - 15, cx + 6, cy - 3), fill=VERDE)
    d.text((x0 + 72, y0 + 14), t, font=f, fill=CREMA)
    img.save(ruta)


def main():
    png = AQUI / 'v8_etiqueta.png'; etiqueta(png)
    sal = AQUI / 'Lisbeth_v8_tomatlan.mp4'
    fl = "[1:v]format=rgba,fade=t=in:st=0:d=0.4:alpha=1[e];[0:v][e]overlay=0:0:format=auto[v]"
    subprocess.run([FF, '-y', '-i', str(AQUI / 'Lisbeth_v7b_un_solo_brazo.mp4'), '-loop', '1', '-i', str(png), '-filter_complex', fl, '-map', '[v]', '-map', '0:a', '-shortest',
                    '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p', '-crf', '24', '-preset', 'medium', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(sal)],
                   check=True, capture_output=True)
    subprocess.run([FF, '-y', '-ss', '6', '-i', str(sal), '-frames:v', '1', str(AQUI / 'v8_cuadro.jpg')], capture_output=True)
    print(sal, sal.stat().st_size // 1024, 'KB')


if __name__ == '__main__':
    main()
