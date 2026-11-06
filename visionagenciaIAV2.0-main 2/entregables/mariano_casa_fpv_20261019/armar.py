"""Mariano · recorrido de casa estilo four horsemen: cortes rápidos de su video real, voz clonada, subtítulos palabra por palabra, cierre con su contacto y filtro premium."""
import json, subprocess
from pathlib import Path
import imageio_ffmpeg

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
FUENTE = AQUI.parent / 'modelos_modal' / 'fuentes' / 'Anton-Regular.ttf'
SRC = Path('/workspaces/Nexusv2.0launch18octubre/clientes/Mariano/whatsapp/del_cliente/20261017_173518_video.mp4')
TMP = AQUI / 'tmp'
VOZ = AQUI / 'voz' / 'guion.mp3'
CORRECCION = {'cociné': 'cocina', 'terrasa': 'terraza', 'recamaras': 'recámaras', 'iluminosa': 'luminosa', 'infonávit,': 'Infonavit,',
              'manda': 'mándame', 'buscas': '¿Buscas'}  # whisper las escribe distinto al guion
PAL = []
for w, s, e in json.loads((AQUI / 'voz' / 'palabras.json').read_text()):
    if w == '.8' or w == 'mi':
        continue                                                   # «2 .8» -> «$2.8M», «manda mi» -> «mándame»
    PAL.append(('$2.8M' if w == '2' else CORRECCION.get(w.lower(), w), s, e))
FIN_VOZ = PAL[-1][2]
TOTAL = round(FIN_VOZ + 2.6, 2)                      # cola de cierre con el contacto
VF = 'scale=720:1280:flags=lanczos:force_original_aspect_ratio=increase,crop=720:1280,fps=30,format=yuv420p,setsar=1'

def t_palabra(prefijo):
    return next(s for w, s, e in PAL if w.lower().strip('.,').startswith(prefijo))
# toma de Modal (clips/E*.mp4) que arranca cuando se nombra la palabra ancla
ANCLAS = [(0.0, 'E0'), (t_palabra('sala') - 0.15, 'E1'), (t_palabra('cocina') - 0.15, 'E2'), (t_palabra('comedor') - 0.15, 'E3'),
          (t_palabra('patio') - 0.15, 'E4'), (t_palabra('recámaras') - 0.15, 'E5'), (t_palabra('terraza') - 0.25, 'E6'), (t_palabra('acepta') - 0.4, 'E7')]
partes = []
for k, (ini, clip) in enumerate(ANCLAS):
    dur = (ANCLAS[k + 1][0] if k + 1 < len(ANCLAS) else TOTAL) - ini
    src = AQUI / 'clips' / f'{clip}.mp4'
    err = subprocess.run([FF, '-i', str(src)], capture_output=True, text=True).stderr.split('Duration: ')[1].split(',')[0].split(':')
    largo = int(err[0]) * 3600 + int(err[1]) * 60 + float(err[2])
    ajuste = f'setpts=PTS*{dur / largo:.4f}' if dur > largo else 'setpts=PTS-STARTPTS'   # si falta clip, cámara lenta
    out = TMP / f's{k}.mp4'
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(src), '-vf', f'{VF},{ajuste}', '-an', '-t', str(round(dur, 3)), '-c:v', 'libx264', '-crf', '18', str(out)], check=True)
    partes.append(out)
(TMP / 'lista.txt').write_text(''.join(f"file '{p}'\n" for p in partes))

from PIL import Image, ImageDraw, ImageFont
FPS = 30
T_CIERRE = FIN_VOZ + 0.5

def capa(texto_principal, linea_cierre=None):
    """RGBA 720x1280 con la palabra grande (o el contacto de cierre), borde negro."""
    im = Image.new('RGBA', (720, 1280), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    def poner(txt, tam, y, color):
        f = ImageFont.truetype(str(FUENTE), tam); w = d.textlength(txt, font=f)
        d.text(((720 - w) / 2, y), txt, font=f, fill=color, stroke_width=6, stroke_fill=(0, 0, 0, 220))
    if linea_cierre:
        poner('ASESOR MARIANO H.', 64, 1280 * 0.57, (255, 255, 255, 255)); poner(linea_cierre, 84, 1280 * 0.63, (255, 210, 60, 255))
    elif texto_principal:
        poner(texto_principal, 96, 1280 * 0.64, (255, 255, 255, 255))
    return im.tobytes()

VACIA = capa(None)
CACHE = {}
def cuadro(t):
    if t >= T_CIERRE:
        return CACHE.setdefault('cierre', capa(None, '(664) 233-4848'))
    for w, s, e in PAL:
        if s <= t < max(e, s + 0.18):
            return CACHE.setdefault(w, capa(w.strip('.,').upper()))
    return VACIA

bruto = TMP / 'bruto.mp4'
enc = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(TMP / 'lista.txt'), '-i', str(VOZ),
                        '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', '720x1280', '-r', str(FPS), '-i', '-',
                        '-filter_complex', '[0:v][2:v]overlay=0:0:format=auto,format=yuv420p[v]', '-map', '[v]', '-map', '1:a', '-t', str(TOTAL),
                        '-c:v', 'libx264', '-crf', '18', '-c:a', 'aac', '-b:a', '160k', str(bruto)], stdin=subprocess.PIPE)
for i in range(int(TOTAL * FPS) + 1):
    enc.stdin.write(cuadro(i / FPS))
enc.stdin.close(); assert enc.wait() == 0
salida = AQUI / 'final' / 'Mariano_casa_recorrido_v1.mp4'
subprocess.run([FF, '-v', 'error', '-y', '-i', str(bruto), '-filter_complex',
                "[0:v]eq=saturation=0.78:contrast=1.07:gamma=0.97,curves=all='0/0.035 0.25/0.22 0.5/0.5 0.78/0.80 1/0.96',colorbalance=rs=-0.04:bs=0.05:rh=0.05:bh=-0.04,split[a][b];"
                "[b]gblur=sigma=18,eq=brightness=0.02[g];[a][g]blend=all_mode=screen:all_opacity=0.18,vignette=PI/5,noise=alls=5:allf=t,format=yuv420p[v]",
                '-map', '[v]', '-map', '0:a', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-crf', '21', '-maxrate', '3M', '-bufsize', '6M',
                '-c:a', 'copy', '-movflags', '+faststart', str(salida)], check=True)
print(salida, round(salida.stat().st_size / 1e6, 1), 'MB', TOTAL, 's')
