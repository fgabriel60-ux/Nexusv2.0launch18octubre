"""Guillermo · campaña estilo @far12 (Dcez7AKzk01) v1 (30 oct, prioridad de Carlos): PROCESO con cortes al ritmo («La obsesión por los detalles»)
→ RESULTADOS con letrero por producto → tarjeta Vicens. Sin GPU: sus tomas ya animadas (tomas_v3) + beat propio (125 bpm). Falta: clips reales de su taller."""
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
T = AQUI.parent / 'video' / 'tomas_v3'
BEAT = AQUI.parent / 'techo_20261029/salida_v6_caen/beat_techo.wav'
FUENTE = '/workspaces/Nexusv2.0launch18octubre/visionagenciaIAV2.0-main 2/entregables/modelos_modal/fuentes/Montserrat.ttf'
TMP = AQUI / 'tmp'; TMP.mkdir(exist_ok=True)
W, H, FPS = 720, 1280, 30
VERDE = (37, 211, 102)
P, R, TARJ = 0.96, 1.92, 3.0   # v2 (Glimmer 6.5→8): 3 productos + obras, cada uno 4 golpes   # proceso: 2 golpes por corte · resultados: 3 golpes
TOMAS = [('H_zaguan_se_arma', 1.0, 'p', None), ('H_techo_se_arma', 1.6, 'p', None), ('T1_lamina', 1.0, 'p', None), ('H_pergola_se_arma', 2.2, 'p', None),
         ('T2_techumbre', 2.0, 'p', None), ('H_zaguan_se_arma', 3.6, 'p', None),
         ('N3_zaguan', 1.0, 'r', ('ZAGUANES', 'A la medida de tu casa')), ('N1_cortina', 1.0, 'r', ('CORTINAS METÁLICAS', 'Para tu negocio')),
         ('N2_puerta', 1.0, 'r', ('PUERTAS DE HERRERÍA', 'Seguridad y estilo')),
         ('T3_nave', 1.0, 'r', ('OBRAS REALES', '+15 años de experiencia'))]


def ff(a):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1500:])


def fu(t, p=900):
    f = ImageFont.truetype(FUENTE, t)
    try: f.set_variation_by_axes([p])
    except Exception: pass
    return f


def capa(tipo, txt, ruta):
    im = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(im)
    arriba = 'LA OBSESIÓN POR LOS DETALLES' if tipo == 'p' else 'LOS RESULTADOS'
    if ruta.name == 'c0.png':   # v2: gancho de beneficio desde el primer segundo
        d.text((W / 2, 560), 'ZAGUANES A LA MEDIDA', font=fu(54, 900), fill='white', anchor='mm', stroke_width=8, stroke_fill=(0, 0, 0)); d.text((W / 2, 625), 'EN PUEBLA', font=fu(46, 900), fill=VERDE, anchor='mm', stroke_width=7, stroke_fill=(0, 0, 0))
    if tipo == 'r':   # v2: WhatsApp visible desde los resultados
        d.rounded_rectangle((W / 2 - 230, 1150, W / 2 + 230, 1214), 32, fill=VERDE + (240,)); d.text((W / 2, 1182), 'Escribe COTIZAR · 231 231 1066', font=fu(28, 800), fill='white', anchor='mm')
    d.text((W / 2, 140), arriba, font=fu(30, 800), fill=(255, 255, 255, 240), anchor='mm', stroke_width=4, stroke_fill=(0, 0, 0, 180))
    if txt:
        d.text((W / 2, 1010), txt[0], font=fu(50, 900), fill='white', anchor='mm', stroke_width=7, stroke_fill=(0, 0, 0))
        d.text((W / 2, 1066), txt[1], font=fu(30, 700), fill=VERDE, anchor='mm', stroke_width=4, stroke_fill=(0, 0, 0))
    im.save(ruta)


segs = []
for i, (n, ini, tipo, txt) in enumerate(TOMAS):
    dur = P if tipo == 'p' else R
    capa(tipo, txt, TMP / f'c{i}.png'); s = TMP / f's{i}.mp4'
    z = f'scale={int(W * 1.1)}:{int(H * 1.1)},crop={W}:{H}' if i % 2 else f'scale={W}:{H}'
    ff(['-ss', str(ini), '-i', str(T / f'{n}.mp4'), '-i', str(TMP / f'c{i}.png'), '-filter_complex',
        f'[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},{z},fps={FPS},eq=contrast=1.08:saturation=1.1,setsar=1[v];[v][1:v]overlay=0:0,format=yuv420p[o]',
        '-map', '[o]', '-t', f'{dur:.3f}', '-an', '-c:v', 'libx264', '-crf', '18', str(s)])
    segs.append(s)
ff(['-loop', '1', '-t', str(TARJ), '-i', str(AQUI / 'tarjeta.png'), '-vf', f'scale={W}:{H},fps={FPS},format=yuv420p', '-c:v', 'libx264', str(TMP / 'sT.mp4')]); segs.append(TMP / 'sT.mp4')
(TMP / 'lista.txt').write_text(''.join(f"file '{s}'\n" for s in segs))
ff(['-f', 'concat', '-safe', '0', '-i', str(TMP / 'lista.txt'), '-c:v', 'libx264', '-crf', '20', '-pix_fmt', 'yuv420p', str(TMP / 'mudo.mp4')])
total = 6 * P + 4 * R + TARJ
ff(['-i', str(BEAT), '-i', str(BEAT), '-filter_complex', f'[0:a]atrim=4.99:10,asetpts=PTS-STARTPTS[a0];[1:a]atrim=4.99:10,asetpts=PTS-STARTPTS,aloop=loop=3:size=221000[l];[a0][l]concat=n=2:v=0:a=1,atrim=0:{total:.2f},afade=t=out:st={total - 1:.2f}:d=1[a]',
    '-map', '[a]', str(TMP / 'musica.wav')])
sal = AQUI / 'Vicens_far12_v2.mp4'
ff(['-i', str(TMP / 'mudo.mp4'), '-i', str(TMP / 'musica.wav'), '-c:v', 'libx264', '-profile:v', 'main', '-crf', '21', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', str(sal)])
print(sal, round(total, 1), 's')
