"""Guillermo · far12 v4 (1 nov 2026, pedido de Carlos): v3 + CLICK en cada cambio de imagen del gancho (6 primeras tomas)
+ subtitulado mejorado (franja inferior, texto por toma, mayor contraste). No toca v3.
Lo genera: armar_far12_v4_click.py → Vicens_far12_v9_fotos_nuevas.mp4 (9:16, 720x1280). Requiere ffmpeg en PATH."""
import math, struct, subprocess, wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
T = AQUI.parent / "fotos_nuevas_20261101"
BEAT = AQUI.parent / 'techo_20261029/salida_v6_caen/beat_techo.wav'
FUENTE = '/workspaces/Nexusv2.0launch18octubre/visionagenciaIAV2.0-main 2/entregables/modelos_modal/fuentes/Montserrat.ttf'
TMP = AQUI / 'tmp_v9'; TMP.mkdir(exist_ok=True)
W, H, FPS = 720, 1280, 30
VERDE = (37, 211, 102)
P, R, TARJ = 0.96, 1.92, 2.0
GANCHO = 6          # tomas del gancho (proceso) que llevan click al cambiar de imagen
CLICK_VOL = 0.55    # volumen relativo del click frente a la música

# (archivo, inicio, tipo, texto_arriba_o_None, subtítulo_de_toma)
TOMAS = [
    ('194146_0.jpg', 0, 'p', None, 'Portón a la medida'),
    ('194148_3.jpg', 0, 'p', None, 'Celosía de corte láser'),
    ('194149_5.jpg', 0, 'p', None, 'Cortina lista para instalar'),
    ('194153_11.jpg', 0, 'p', None, 'Portón terminado'),
    ('194154_21.jpg', 0, 'p', None, 'Puerta de herrería'),
    ('194154_24.jpg', 0, 'p', None, 'Cada pieza, a tu medida'),
    ('194153_16.jpg', 0, 'r', ('PORTONES', 'Trabajos reales en Puebla'), 'Portones'),
    ('194148_3.jpg', 0, 'r', ('CELOSÍAS', 'Corte láser y acabado real'), 'Celosías'),
    ('194152_8.jpg', 0, 'r', ('PUERTAS DE HERRERÍA', 'Seguridad y estilo'), 'Puertas'),
    ('194154_29.jpg', 0, 'r', ('CORTINAS Y PÉRGOLAS', '+15 años de experiencia'), 'Cortinas y pérgolas'),
]


def ff(a):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1500:])


def fu(t, p=900):
    f = ImageFont.truetype(FUENTE, t)
    try: f.set_variation_by_axes([p])
    except Exception: pass
    return f


def capa(tipo, txt, sub, ruta):
    im = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(im)
    # Franja inferior para que el subtítulo se lea sobre cualquier fondo
    for y in range(H - 330, H):
        a = int(170 * (y - (H - 330)) / 330)
        d.line([(0, y), (W, y)], fill=(0, 0, 0, a))
    arriba = 'LA OBSESIÓN POR LOS DETALLES' if tipo == 'p' else 'LOS RESULTADOS'
    if ruta.name == 'c0.png':   # gancho de beneficio desde el primer segundo
        d.text((W / 2, 490), '¿TU CASA NECESITA ZAGUÁN?', font=fu(42, 900), fill=(255, 214, 60), anchor='mm', stroke_width=7, stroke_fill=(0, 0, 0))
        d.text((W / 2, 560), 'ZAGUANES A LA MEDIDA', font=fu(54, 900), fill='white', anchor='mm', stroke_width=8, stroke_fill=(0, 0, 0))
        d.text((W / 2, 625), 'EN PUEBLA', font=fu(46, 900), fill=VERDE, anchor='mm', stroke_width=7, stroke_fill=(0, 0, 0))
    if tipo == 'r':
        d.rounded_rectangle((W / 2 - 300, 1150, W / 2 + 300, 1214), 32, fill=VERDE + (240,))
        d.text((W / 2, 1182), 'COTIZAR · 231 231 1066 · Puebla y alrededores', font=fu(25, 800), fill='white', anchor='mm')
    d.text((W / 2, 140), arriba, font=fu(30, 800), fill=(255, 255, 255, 240), anchor='mm', stroke_width=4, stroke_fill=(0, 0, 0, 180))
    # Subtítulo: frase de la toma, en blanco con contorno, dentro de la zona segura inferior
    d.text((W / 2, H - 210), sub, font=fu(40, 900), fill='white', anchor='mm', stroke_width=6, stroke_fill=(0, 0, 0))
    if txt:
        d.text((W / 2, 1010), txt[0], font=fu(50, 900), fill='white', anchor='mm', stroke_width=7, stroke_fill=(0, 0, 0))
        d.text((W / 2, 1066), txt[1], font=fu(30, 700), fill=VERDE, anchor='mm', stroke_width=4, stroke_fill=(0, 0, 0))
    im.save(ruta)


segs, dur_seg = [], []
for i, (n, ini, tipo, txt, sub) in enumerate(TOMAS):
    dur = P if tipo == 'p' else R
    capa(tipo, txt, sub, TMP / f'c{i}.png'); s = TMP / f's{i}.mp4'
    z = f'scale={int(W * 1.1)}:{int(H * 1.1)},crop={W}:{H}' if i % 2 else f'scale={W}:{H}'
    ff(['-loop', '1', '-t', f'{dur:.3f}', '-i', str(T / n), '-i', str(TMP / f'c{i}.png'), '-filter_complex',
        f'[0:v]scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},zoompan=z=\'min(1+on*0.0015,1.12)\':x=\'iw/2-(iw/zoom/2)\':y=\'ih/2-(ih/zoom/2)\':d={int(dur*FPS)}:s={W}x{H}:fps={FPS},eq=contrast=1.06:saturation=1.08,setsar=1[v];[v][1:v]overlay=0:0,format=yuv420p[o]',
        '-map', '[o]', '-t', f'{dur:.3f}', '-an', '-c:v', 'libx264', '-crf', '18', str(s)])
    segs.append(s); dur_seg.append(dur)
ff(['-loop', '1', '-t', str(TARJ), '-i', str(AQUI / 'tarjeta.png'), '-vf', f"scale={W*2}:{H*2},zoompan=z='min(1+on*0.0012,1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},format=yuv420p", '-c:v', 'libx264', str(TMP / 'sT.mp4')])
segs.append(TMP / 'sT.mp4'); dur_seg.append(TARJ)
(TMP / 'lista.txt').write_text(''.join(f"file '{s}'\n" for s in segs))
ff(['-f', 'concat', '-safe', '0', '-i', str(TMP / 'lista.txt'), '-c:v', 'libx264', '-crf', '20', '-pix_fmt', 'yuv420p', str(TMP / 'mudo.mp4')])
total = sum(dur_seg)

# Click: pulso corto (≈12 ms, 2 kHz con caída rápida) en cada corte del gancho
SR = 44100
clicks = [0.0] * int(total * SR + SR)
cortes = [sum(dur_seg[:k]) for k in range(1, GANCHO + 1)]
for t in cortes:
    i0 = int(t * SR)
    for j in range(int(0.012 * SR)):
        if i0 + j < len(clicks):
            env = math.exp(-j / (0.0025 * SR))
            clicks[i0 + j] += CLICK_VOL * env * math.sin(2 * math.pi * 2000 * j / SR)
clic_wav = TMP / 'clicks.wav'
with wave.open(str(clic_wav), 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(b''.join(struct.pack('<h', int(max(-1, min(1, c)) * 32767)) for c in clicks))

# Música (beat propio de v3) + clics mezclados
ff(['-i', str(BEAT), '-i', str(BEAT), '-filter_complex', f'[0:a]atrim=4.99:10,asetpts=PTS-STARTPTS[a0];[1:a]atrim=4.99:10,asetpts=PTS-STARTPTS,aloop=loop=3:size=221000[l];[a0][l]concat=n=2:v=0:a=1,atrim=0:{total:.2f},afade=t=out:st={total - 1:.2f}:d=1[a]',
    '-map', '[a]', str(TMP / 'musica.wav')])
sal = AQUI / 'Vicens_far12_v9_fotos_nuevas.mp4'
ff(['-i', str(TMP / 'mudo.mp4'), '-i', str(TMP / 'musica.wav'), '-i', str(clic_wav), '-filter_complex', '[1:a][2:a]amix=inputs=2:normalize=0[a]',
    '-map', '0:v', '-map', '[a]', '-c:v', 'libx264', '-profile:v', 'main', '-crf', '21', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', str(sal)])
print(sal, round(total, 1), 's', 'cortes con click:', [round(c, 2) for c in cortes])
