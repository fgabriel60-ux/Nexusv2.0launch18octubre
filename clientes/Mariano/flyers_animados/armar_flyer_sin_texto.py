"""Mariano · flyer de Benjamina: las 4 fotos se animan (H3) sin texto y al final aparece el texto ORIGINAL nítido del flyer.
Las franjas de texto se tapan con el blanco limpio durante la animación (H3 inventa letras en el blanco). Uso: python3 armar_flyer_sin_texto.py"""
import subprocess
from pathlib import Path
import imageio_ffmpeg
from PIL import Image

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H = 1080, 1920
ARRIBA, ABAJO = 178, 812   # franjas de texto del flyer original (720×1280)
TEXTO_DESDE, TEXTO_DUR, FIN = 0.3, 0.7, 7.0
MUSICA = AQUI.parents[1] / 'XV' / 'musica_suave_s7.wav'


def franjas(origen, salida):
    im = Image.open(origen).convert('RGBA').resize((W, H), Image.LANCZOS)
    a, b = round(ARRIBA * H / 1280), round(ABAJO * H / 1280)
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    capa.paste(im.crop((0, 0, W, a)), (0, 0)); capa.paste(im.crop((0, b, W, H)), (0, b))
    capa.save(salida)


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1500:])


def main():
    tmp = AQUI / 'sin_texto'
    franjas(tmp / 'limpio_exacto.png', tmp / 'franjas_blancas.png'); franjas(AQUI / 'flyer_benjamina.jpg', tmp / 'franjas_texto.png')
    sal = AQUI / 'Mariano_flyer_Benjamina_sin_texto_animado.mp4'
    fl = (f"[0:v]scale={W}:{H}:flags=lanczos,fps=30,setsar=1,format=yuv420p,tpad=stop_mode=clone:stop_duration=3,trim=duration={FIN}[v];"
          f"[v][1:v]overlay=0:0[b];[2:v]format=rgba,fade=t=in:st={TEXTO_DESDE}:d={TEXTO_DUR}:alpha=1[t];[b][t]overlay=0:0[o];"
          f"[3:a]aresample=44100,volume=0.7,afade=t=in:st=0:d=0.5,afade=t=out:st={FIN - 1}:d=1,atrim=0:{FIN}[a]")
    ff(['-i', str(tmp / 'clip.mp4'), '-loop', '1', '-t', str(FIN), '-i', str(tmp / 'franjas_blancas.png'), '-loop', '1', '-t', str(FIN), '-i', str(tmp / 'franjas_texto.png'),
        '-i', str(MUSICA), '-filter_complex', fl, '-map', '[o]', '-map', '[a]', '-t', str(FIN), '-vf' if False else '-c:v', 'libx264', '-profile:v', 'main', '-pix_fmt', 'yuv420p',
        '-crf', '20', '-preset', 'slow', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB')


if __name__ == '__main__':
    main()
