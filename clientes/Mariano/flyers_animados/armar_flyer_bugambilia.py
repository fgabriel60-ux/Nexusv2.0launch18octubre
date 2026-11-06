"""Mariano · flyer Bugambilia animado: la pareja y la casa se animan (H3, cuadro sin texto de Qwen) y el texto ORIGINAL del flyer
(globos, logos, barra, precio, etiquetas) aparece nítido casi desde el inicio, extraído por zonas del flyer de 900×1600.
Uso: python3 armar_flyer_bugambilia.py"""
import subprocess
from pathlib import Path
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageFilter
from scipy import ndimage as ndi

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H = 1080, 1920
TEXTO_DESDE, TEXTO_DUR, FIN = 0.3, 0.7, 7.0
MUSICA = AQUI.parents[1] / 'XV' / 'musica_suave_s7.wav'
# zonas (x0, y0, x1, y1) del flyer 900×1600 y cómo se extrae cada una
ZONAS = [
    ((50, 70, 240, 150), 'claro'),              # logo Grupo Lagsa
    ((240, 100, 400, 125), 'texto_fino'),       # *APLICAN RESTRICCIONES
    ((0, 0, 0, 0), 'claro'),              # logo Grupo Lagsa + restricciones
    ((530, 80, 840, 290), 'blanco'),            # logo Vizcaíno
    ((45, 270, 470, 420), 'globo'),             # globo 1
    ((480, 350, 880, 520), 'globo'),            # globo 2
    ((85, 1075, 330, 1205), 'globo'),           # barra de mensaje, lado izquierdo (la pareja va delante)
    ((585, 1075, 815, 1205), 'globo'),          # barra de mensaje, lado derecho
    ((495, 1340, 880, 1470), 'blanco'),         # Bugambilia · desde $2.45 MDP
    ((20, 1500, 890, 1570), 'blanco_o_oscuro'),  # ubicación y etiquetas
]


def capa_texto(flyer):
    im = Image.open(flyer).convert('RGB'); a = np.asarray(im).astype(int)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    alfa = np.zeros(R.shape, bool)
    for (x0, y0, x1, y1), modo in ZONAS:
        caja = np.zeros_like(alfa); caja[y0:y1, x0:x1] = True
        if modo == 'blanco':
            k = (a.min(2) > (170 if x0 < 520 and y0 > 1300 else 205))
        elif modo == 'texto_fino':
            k = (R > 105)
        elif modo == 'claro':       # texto fino blanco y logo amarillo-verde sobre el cielo
            k = (B - R < 45) | (R > 150)
        elif modo == 'globo':      # globo beige + su texto oscuro: se rellenan los huecos
            beige = (R > 215) & (G > 205) & (B > 180) & (R - B < 60)
            k = ndi.binary_fill_holes(ndi.binary_closing(beige & caja, iterations=6))
        else:                      # etiquetas: blanco, beige o letras oscuras sobre el camino
            k = (a.min(2) > 205) | ((R > 215) & (G > 205)) | (a.max(2) < 110)
        alfa |= k & caja
    alfa = ndi.binary_dilation(alfa, iterations=2)
    m = Image.fromarray((alfa * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.0))
    capa = im.convert('RGBA'); capa.putalpha(m)
    return capa.resize((W, H), Image.LANCZOS)


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1500:])


def main():
    d = AQUI / 'bugambilia'
    capa_texto(AQUI / 'flyer_bugambilia.jpg').save(d / 'texto.png')
    sal = AQUI / 'Mariano_flyer_Bugambilia_animado.mp4'
    fl = (f"[0:v]scale={W}:{H}:flags=lanczos,fps=30,setsar=1,format=yuv420p,tpad=stop_mode=clone:stop_duration=3,trim=duration={FIN}[v];"
          f"[1:v]format=rgba,fade=t=in:st={TEXTO_DESDE}:d={TEXTO_DUR}:alpha=1[t];[v][t]overlay=0:0[o];"
          f"[2:a]aresample=44100,volume=0.7,afade=t=in:st=0:d=0.5,afade=t=out:st={FIN - 1}:d=1,atrim=0:{FIN}[a]")
    ff(['-i', str(d / 'clip.mp4'), '-loop', '1', '-t', str(FIN), '-i', str(d / 'texto.png'), '-i', str(MUSICA), '-filter_complex', fl,
        '-map', '[o]', '-map', '[a]', '-t', str(FIN), '-c:v', 'libx264', '-profile:v', 'main', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'slow',
        '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB')


if __name__ == '__main__':
    main()
