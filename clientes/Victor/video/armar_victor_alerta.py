"""Servilin (Víctor): los anuncios ORIGINALES (gancho normal) + franja de alerta «NO ES OFERTA DE EMPLEO» arriba, compacta y fija todo el video (no tapa la pantalla).
Uso: python3 armar_victor_alerta.py"""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/XV')
import imageio_ffmpeg
from PIL import Image, ImageDraw
from armar_xv import fu

AQUI = Path(__file__).resolve().parent
ACT = AQUI.parent / 'whatsapp' / 'anuncios_activos'
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H = 720, 1280
AM, AZ = (250, 214, 50), (10, 28, 64)


def franja(ruta):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 30, 150, W - 30, 262
    d.rounded_rectangle((x0, y0, x1, y1), 22, fill=AZ + (238,), outline=AM + (255,), width=5)
    cx, cy = x0 + 62, (y0 + y1) // 2   # triángulo de advertencia
    d.polygon([(cx, cy - 36), (cx + 42, cy + 30), (cx - 42, cy + 30)], fill=AM)
    d.rectangle((cx - 4, cy - 12, cx + 4, cy + 8), fill=AZ); d.ellipse((cx - 5, cy + 13, cx + 5, cy + 23), fill=AZ)
    def t(txt, y, tam, col, peso):
        f = fu(tam, peso); xm = x0 + 125; mx = x1 - 18
        while d.textlength(txt, font=f) > mx - xm: tam -= 1; f = fu(tam, peso)
        d.text((xm, y), txt, font=f, fill=col)
    t('NO ES OFERTA DE EMPLEO', y0 + 14, 44, (255, 255, 255), 'Black')
    t('Servicio de limpieza para EMPRESAS', y0 + 68, 27, AM, 'Bold')
    img.save(ruta)


def poner(src, nombre):
    png = AQUI / 'alerta' / 'franja.png'; franja(png)
    sal = AQUI / 'alerta' / f'{nombre}.mp4'
    fl = "[1:v]format=rgba,fade=t=in:st=0:d=0.4:alpha=1[f];[0:v][f]overlay=0:0:format=auto[v]"
    subprocess.run([FF, '-y', '-i', str(src), '-loop', '1', '-i', str(png), '-filter_complex', fl, '-map', '[v]', '-map', '0:a?', '-shortest',
                    '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p', '-crf', '22', '-preset', 'medium',
                    '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(sal)], check=True, capture_output=True)
    subprocess.run([FF, '-y', '-ss', '3', '-i', str(sal), '-frames:v', '1', str(AQUI / 'alerta' / f'{nombre}_cuadro.jpg')], capture_output=True)
    print(sal, sal.stat().st_size // 1024, 'KB')


if __name__ == '__main__':
    for n in ('servilin_v1', 'servilin_v2', 'servilin_v3_obra_fina'):
        poner(ACT / f'{n}.mp4', f'{n}_alerta')
