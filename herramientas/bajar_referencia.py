#!/usr/bin/env python3
"""Baja un reel de Instagram y arma dos hojas de frames: el reel completo y el GANCHO.

Usa yt-dlp, no Apify: el 5 nov 2026 la cuenta de Apify (plan gratuito) agotó sus $5 del
mes y no se reinicia hasta el 24 nov. yt-dlp no cuesta nada y bajó el mismo reel sin
problema, así que es la vía por defecto para las referencias.

Uso: python3 herramientas/bajar_referencia.py <shortCode|url> <carpeta_destino>
"""
import io, json, os, re, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont


def _ffmpeg():
    """ffmpeg del sistema, o el que trae imageio-ffmpeg.

    Este Codespace no tiene ffmpeg ni ffprobe instalados (5 nov 2026): los armadores
    corren en Modal, no aquí. imageio-ffmpeg trae un binario propio y resuelve.
    """
    h = shutil.which('ffmpeg')
    if h:
        return h
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


FF = _ffmpeg()


def duracion(video):
    """Segundos del video. Sin ffprobe: se lee del encabezado que ffmpeg manda a stderr."""
    s = subprocess.run([FF, '-i', video], capture_output=True, text=True).stderr
    m = re.search(r'Duration:\s*(\d+):(\d+):(\d+\.?\d*)', s)
    if not m:
        return 0.0
    h, mi, se = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(se)


def hoja(video, tiempos, salida, ancho=216, alto=384, cols=5):
    ims = []
    for t in tiempos:
        b = subprocess.run([FF, '-v', 'error', '-ss', str(t), '-i', video, '-frames:v', '1', '-vf',
                            f'scale={ancho}:{alto}:force_original_aspect_ratio=decrease,'
                            f'pad={ancho}:{alto}:(ow-iw)/2:(oh-ih)/2',
                            '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True).stdout
        if not b:
            continue
        im = Image.open(io.BytesIO(b))
        ImageDraw.Draw(im).text((6, 4), f'{t:.1f}s', fill='yellow', font=ImageFont.load_default(22))
        ims.append(im)
    if not ims:
        return
    filas = (len(ims) + cols - 1) // cols
    H = Image.new('RGB', (ancho * cols, alto * filas))
    for i, im in enumerate(ims):
        H.paste(im, ((i % cols) * ancho, (i // cols) * alto))
    H.save(salida, quality=88)
    print('hoja:', salida)


def main(codigo, dest):
    os.makedirs(dest, exist_ok=True)
    sc = codigo.rstrip('/').split('/')[-1] if '/' in codigo else codigo
    url = codigo if codigo.startswith('http') else f'https://www.instagram.com/reel/{sc}/'
    video = os.path.join(dest, f'ref_{sc}.mp4')
    if not os.path.exists(video):
        subprocess.run(['yt-dlp', '--no-warnings', '-f', 'best[ext=mp4]/best', '-o', video, url], check=True)
    d = duracion(video)
    print(f'{sc}: {d:.1f} s · {video}')
    hoja(video, [d * (i + .5) / 10 for i in range(10)], os.path.join(dest, f'ref_{sc}_hoja.jpg'))
    # el gancho: los primeros 3 s, uno cada 0.3 s. Ahí se decide si el video retiene.
    hoja(video, [round(i * 0.3, 1) for i in range(10)], os.path.join(dest, f'ref_{sc}_GANCHO.jpg'))
    json.dump({'shortCode': sc, 'url': url, 'duracion': round(d, 1)},
              open(os.path.join(dest, f'ref_{sc}.json'), 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else '.')
